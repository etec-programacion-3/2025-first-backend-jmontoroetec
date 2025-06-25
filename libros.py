from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

# Crear el router
router = APIRouter()

# Modelo de datos
class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    disponible: bool = True

# Base de datos simulada en memoria
libros = []

# Obtener todos los libros
@router.get("/libros", response_model=List[Libro])
def obtener_libros():
    return libros

# Crear un nuevo libro
@router.post("/libros", response_model=Libro)
def crear_libro(libro: Libro):
    libros.append(libro)
    return libro

# Obtener un libro por ID
@router.get("/libros/{id}", response_model=Libro)
def obtener_libro(id: int):
    for libro in libros:
        if libro.id == id:
            return libro
    return {"error": "Libro no encontrado"}

# Eliminar un libro por ID
@router.delete("/libros/{id}")
def borrar_libro(id: int):
    global libros
    libros = [l for l in libros if l.id != id]
    return {"mensaje": "Libro eliminado"}
