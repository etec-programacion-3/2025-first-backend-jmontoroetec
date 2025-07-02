from fastapi import FastAPI
from libros import router as libros_router
from usuario import router as usuario_router

# Crear la aplicación FastAPI
app = FastAPI()

# Incluir los routers (libros y usuarios)
app.include_router(libros_router)
app.include_router(usuario_router)
