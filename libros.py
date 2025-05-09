from fastapi import APIRouter
from pydantic import BaseModel
from typing import List

router = APIRouter()

class Libro(BaseModel):
    id: int
    titulo: str
    autor: str
    disponible: bool = True

libros = []

@router.get("/libros", response_model=List[Libro])
def obtener_libros():
    return libros

@router.post("/libros", response_model=Libro)
def crear_libro(libro: Libro):
    libros.append(libro)
    return libro

@router.get("/libros/{id}", response_model=Libro)
def obtener_libro(id: int):
    for libro in libros:
        if libro.id == id:
            return libro
    return {"error": "Libro no encontrado"}

@router.delete("/libros/{id}")
def borrar_libro(id: int):
    global libros
    libros = [l for l in libros if l.id != id]
    return {"mensaje": "Libro eliminado"}
