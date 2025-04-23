from fastapi import Depends, HTTPException, status
from pydantic import BaseModel
from passlib.context import CryptContext
from jose import JWTError, jwt
from typing import Optional
from datetime import datetime, timedelta

# Encriptación de contraseñas
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Clave secreta y configuración del token
SECRET_KEY = "clave-super-secreta"  # en producción usá una variable de entorno
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Usuarios guardados en memoria (por ahora)
usuarios_db = {}

class Usuario(BaseModel):
    username: str
    nombre: str
    rol: str  # puede ser 'admin' o 'lector'
    disabled: Optional[bool] = False

class UsuarioEnDB(Usuario):
    hashed_password: str

class UsuarioRegistro(BaseModel):
    username: str
    nombre: str
    rol: str
    password: str

class Token(BaseModel):
    access_token: str
    token_type: str

class DatosToken(BaseModel):
    username: Optional[str] = None

from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def verificar_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def encriptar_password(password):
    return pwd_context.hash(password)

def autenticar_usuario(username: str, password: str):
    usuario = usuarios_db.get(username)
    if not usuario:
        return False
    if not verificar_password(password, usuario.hashed_password):
        return False
    return usuario

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

# Registro
@app.post("/registrar")
def registrar(usuario: UsuarioRegistro):
    if usuario.username in usuarios_db:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    hashed_password = encriptar_password(usuario.password)
    usuario_db = UsuarioEnDB(**usuario.dict(), hashed_password=hashed_password)
    usuarios_db[usuario.username] = usuario_db
    return {"mensaje": "Usuario creado correctamente"}

# Login
@app.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    usuario = autenticar_usuario(form_data.username, form_data.password)
    if not usuario:
        raise HTTPException(status_code=401, detail="Credenciales incorrectas")
    access_token = crear_token_acceso(data={"sub": usuario.username})
    return {"access_token": access_token, "token_type": "bearer"}
