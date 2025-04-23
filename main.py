# main.py
from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def leer_root():
    return {"mensaje": "bienvenido a la biblioteca"}
from pydantic import BaseModel
from typing import List, Optional

# Modelo de datos
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    anio: int
    categoria: Optional[str] = None

# Base de datos temporal
libros: List[Libro] = []

# Crear libro
@app.post("/libros/")
def crear_libro(libro: Libro):
    libros.append(libro)
    return libro

# Leer todos los libros
@app.get("/libros/")
def obtener_libros():
    return libros

# Leer libro por ID
@app.get("/libros/{libro_id}")
def obtener_libro(libro_id: int):
    for libro in libros:
        if libro.id == libro_id:
            return libro
    return {"error": "Libro no encontrado"}

# Actualizar libro
@app.put("/libros/{libro_id}")
def actualizar_libro(libro_id: int, datos: Libro):
    for i, libro in enumerate(libros):
        if libro.id == libro_id:
            libros[i] = datos
            return datos
    return {"error": "Libro no encontrado"}

# Eliminar libro
@app.delete("/libros/{libro_id}")
def eliminar_libro(libro_id: int):
    for libro in libros:
        if libro.id == libro_id:
            libros.remove(libro)
            return {"mensaje": "Libro eliminado"}
    return {"error": "Libro no encontrado"}