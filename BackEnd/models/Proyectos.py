from typing import Optional, Annotated
from pydantic import BaseModel, Field, validator


class Proyectos(BaseModel):
    id: Optional[int] = Field(None, description="ID del proyecto (autogenerado)")
    nombre: Annotated[str, Field(..., min_length=1, max_length=500, description="Nombre del proyecto")]
    description: Optional[Annotated[str, Field(None, max_length=1000, description="Descripción opcional")]] = None
    imagen: Annotated[str, Field(..., min_length=1, max_length=1000, description="Ruta relativa o URL de la imagen en Frontend/Images")]
    fecha: Annotated[str, Field(..., min_length=10, max_length=10, description="Fecha en formato YYYY-MM-DD")]
    linkgithub: Annotated[str, Field(..., min_length=5, max_length=1000, description="Link del repositorio en GitHub")]
    linkvideo: Optional[Annotated[str, Field(None, max_length=1000, description="Link del video del proyecto (opcional)")]] = None

    @validator('*', pre=True)
    def _strip_strings(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class Contactos(BaseModel):
    id: Optional[int] = Field(None, description="ID del contacto (autogenerado)")
    nombre: Annotated[str, Field(..., min_length=1, max_length=500, description="Nombre del contacto")]
    telefono: Annotated[str, Field(..., min_length=5, max_length=30, description="Número de teléfono del contacto")]
    email: Annotated[str, Field(..., min_length=5, max_length=320, description="Correo electrónico del contacto")]
    mensaje: Annotated[str, Field(..., min_length=1, max_length=2000, description="Mensaje del contacto")]

    @validator('*', pre=True)
    def _strip_strings_contact(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v


class Map(BaseModel):
    id: Optional[int] = Field(None, description="ID del mapa (autogenerado)")
    placename: Annotated[str, Field(..., min_length=1, max_length=150, description="Nombre del lugar")]
    description: Annotated[str, Field(..., min_length=1, max_length=400, description="Descripción del lugar")]
    latitud: Annotated[str, Field(..., min_length=1, max_length=50, description="Latitud (string)")]
    longitud: Annotated[str, Field(..., min_length=1, max_length=50, description="Longitud (string)")]
    addresplace: Annotated[str, Field(..., min_length=1, max_length=250, description="Dirección del lugar")]

    @validator('*', pre=True)
    def _strip_strings_map(cls, v):
        if isinstance(v, str):
            return v.strip()
        return v
    
