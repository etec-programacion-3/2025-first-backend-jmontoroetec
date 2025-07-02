from fastapi import APIRouter, Depends, HTTPException
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from passlib.context import CryptContext
from jose import JWTError, jwt
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timedelta

# Crear el router para usuarios
router = APIRouter()

# Encriptación
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Configuración del token
SECRET_KEY = "clave-super-secreta"
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

# Almacenamiento en memoria de los usuarios
usuarios_db = {}

# Modelos de datos
class Usuario(BaseModel):
    username: str
    nombre: str
    rol: str
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

# Funciones de utilidad para manejo de contraseñas y autenticación
def encriptar_password(password: str):
    return pwd_context.hash(password)

def verificar_password(password: str, hashed: str):
    return pwd_context.verify(password, hashed)

def autenticar_usuario(username: str, password: str):
    user = usuarios_db.get(username)
    if not user or not verificar_password(password, user.hashed_password):
        return None
    return user

def crear_token_acceso(data: dict, expires_delta: Optional[timedelta] = None):
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=15))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def obtener_usuario_actual(token: str = Depends(OAuth2PasswordBearer(tokenUrl="token"))):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username = payload.get("sub")
        if username is None:
            raise HTTPException(status_code=401, detail="Token inválido")
    except JWTError:
        raise HTTPException(status_code=401, detail="Token inválido")

    user = usuarios_db.get(username)
    if user is None:
        raise HTTPException(status_code=404, detail="Usuario no encontrado")
    return user

# 📌 Ruta: REGISTRAR USUARIO
@router.post("/registrar")
def registrar(usuario: UsuarioRegistro):
    if usuario.username in usuarios_db:
        raise HTTPException(status_code=400, detail="Usuario ya existe")
    hashed_password = encriptar_password(usuario.password)
    usuario_db = UsuarioEnDB(**usuario.dict(), hashed_password=hashed_password)
    usuarios_db[usuario.username] = usuario_db
    return {"mensaje": "Usuario creado correctamente"}

# 📌 Ruta: LOGIN Y OBTENER TOKEN
@router.post("/token", response_model=Token)
def login(form_data: OAuth2PasswordRequestForm = Depends()):
    user = autenticar_usuario(form_data.username, form_data.password)
    if not user:
        raise HTTPException(status_code=401, detail="Credenciales inválidas")
    access_token = crear_token_acceso(data={"sub": user.username})
    return {"access_token": access_token, "token_type": "bearer"}

# 📌 Ruta: OBTENER PERFIL DEL USUARIO
@router.get("/usuarios/me", response_model=Usuario)
def leer_usuario_actual(usuario: Usuario = Depends(obtener_usuario_actual)):
    return usuario
