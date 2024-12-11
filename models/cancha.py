from sqlalchemy import Column, Integer, String, Boolean
from sqlalchemy.orm import relationship
from ..database import db_instance, ORMBase

class CanchaDB(ORMBase):
    __tablename__ = "canchas" # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String(50), unique=True, nullable=False)
    techada = Column(Boolean, default=False)

    # Tiene que tener el nombre de la clase con la cual tiene relacion, en este caso es la reserva
    reservas = relationship(
        "ReservaDB",  # Nombre del modelo relacionado
        back_populates="cancha",  # Relación inversa
        cascade="all, delete-orphan",  # Borra reservas si se elimina la cancha
    )


db_instance.create_all()