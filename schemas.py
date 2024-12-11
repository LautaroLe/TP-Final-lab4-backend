from pydantic import BaseModel
from datetime import date,time

class CanchaBase(BaseModel):
    nombre: str
    techada: bool

class ReservaBase(BaseModel):
    dia: date
    horario: time
    duracionHs: int
    nombre_contacto: str
    telefono_contacto: str
    cancha_id: int
