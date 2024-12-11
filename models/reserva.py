from sqlalchemy import Column, Date, Integer, String, ForeignKey, Time
from sqlalchemy.orm import relationship
from ..database import db_instance, ORMBase

class ReservaDB(ORMBase):
    __tablename__ = "reservas"  # Nombre de la tabla en la base de datos

    id = Column(Integer, primary_key=True, index=True)
    dia = Column(Date, nullable=False)
    horario =  Column(Time, nullable=False)
    duracionHs = Column(Integer, nullable=False) 
    nombre_contacto = Column(String(50), nullable=False)
    telefono_contacto = Column(String(50), nullable=False)

    # Llave foránea que conecta con la tabla Canchas
    cancha_id = Column(Integer, ForeignKey("canchas.id"), nullable=False)

    # Relación inversa: Una ReservaDB pertenece a una única cancha
    cancha = relationship("CanchaDB",foreign_keys=[cancha_id], back_populates="reservas")  
    # Usa el nombre de la clase correctamente

db_instance.create_all()