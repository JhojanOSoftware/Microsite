from pydantic import BaseModel, Field, constr, conint
from typing import Optional

class Proyectos(BaseModel):
    id: Optional[int] = Field(None, description="ID del proyecto (autogenerado)")
    nombre: constr(strip_whitespace=True, min_length=1, max_length=100) = Field(..., description="Nombre del proyecto")
    description: Optional[constr(strip_whitespace=True, max_length=300)] = Field(None, description="Descripción opcional")
    imagen: conint(ge=100, le=500) = Field(..., description="agrega la ruta de la imagen que se encuentre ubicada en ActividadMicrosite/Frontend/Images")
    fecha: constr(strip_whitespace=True, min_length=10, max_length=10) = Field(..., description="Fecha en formato YYYY-MM-DD")
    linkgithub: constr(strip_whitespace=True, min_length=5, max_length=200) = Field(..., description="Link del repositorio en GitHub")
    linkvideo: Optional[constr(strip_whitespace=True, max_length=200)] = Field(None, description="Link del video del proyecto (opcional)")

class Contactos(BaseModel):
    id: Optional[int] = Field(None, description="ID del contacto (autogenerado)")
    nombre: constr(strip_whitespace=True, min_length=1, max_length=100) = Field(..., description="Nombre del contacto")
    telefono: constr(strip_whitespace=True, min_length=7, max_length=15) = Field(..., description="Número de teléfono del contacto")
    email: constr(strip_whitespace=True, min_length=5, max_length=100) = Field(..., description="Correo electrónico del contacto")
    mensaje: constr(strip_whitespace=True, min_length=1, max_length=500) = Field(..., description="Mensaje del contacto")


class Map(BaseModel):
    id: Optional[int] = Field(None, description="ID del lugar (autogenerado)")
    placename: constr(strip_whitespace=True, min_length=1, max_length=100) = Field(..., description="Nombre del lugar")
    description: Optional[constr(strip_whitespace=True, max_length=300)] = Field(None, description="Descripción opcional del lugar")
    latitud: float = Field(..., description="Latitud del lugar")
    longitud: float = Field(..., description="Longitud del lugar")
    addresplace: Optional[constr(strip_whitespace=True, max_length=300)] = Field(None, description="Dirección del lugar (opcional)")