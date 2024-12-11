# Back/service.py

from fastapi import HTTPException

from .schemas import ReservaBase
from .models.cancha import CanchaDB
from .models.reserva import ReservaDB
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import date, datetime, timedelta



class NotFoundError(Exception):

    def __init__(self, message):
        super().__init__(message)
        self._status_code = 404
        self.message = message

    @property
    def status_code(self):
        # Codigo de estado (solo lectura)
        return self._status_code
    

# Funciones para canchas
class CanchasRepo:
    def get_all_canchas(self, db:Session ):
        result = db.query(CanchaDB).all()
        objetos = []
        if len(result) > 0:  # Comprueba si hay registros
            return result
        else:
            return {"message": "No se encontraron registros de canchas."}
        
    def get_cancha_by_id(self,id:int,db:Session):
        result = db.query(CanchaDB).get(id)
        if not result:
            raise HTTPException(status_code=404, detail="id no encontrado")
        return result
    
    def Registrar_Cancha( self, canchar:CanchaDB, db:Session):
        db.add(canchar)
        db.commit()

    def borrar_cancha(self,id,db:Session):
        cancha = db.get(CanchaDB, id)
        if not cancha:
            raise HTTPException(status_code=404, detail="id no encontrado")
        db.delete(cancha)
        db.commit()
        return {"message": f"Cancha con id {id} eliminada correctamente."}
        

# Funciones para Reservas

class ReservasRepo:
    #trae todas las reservas
    def get_all_reservas(self, db:Session):
        query = (
            db.query(ReservaDB, CanchaDB)
            .join(CanchaDB, ReservaDB.cancha_id == CanchaDB.id).order_by(ReservaDB.id)
            .all()
        )
        #podria agregar los filtros directamente en el getall reservas, y si no se especifica nincun parametro que devuelva todo solamente
        if not query:
            raise HTTPException(status_code=404, detail="No se encontraron reservas.")
        
        try:
            reservas_formateadas = formatear_Reservas(query)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Error inesperado en el formateo: {str(e)}")
        return reservas_formateadas
        
#filtra las reservas (falta probar)
    def filtrar_reservas(self,date1:date,id:int,db:Session):
        
        if not date1 and not id:
            raise HTTPException(status_code=500, detail="Se debe proporcionar una fecha válida o el ID de la cancha.")
        
        # se filtran las reservas segun la cancha y el dia 
        query = (db.query(ReservaDB, CanchaDB).join(CanchaDB, ReservaDB.cancha_id == CanchaDB.id))
                 
        if date1:
            query = query.filter(ReservaDB.dia == date1)
        if id:
            query = query.filter(ReservaDB.cancha_id == id)
        
        query = query.order_by(ReservaDB.horario).all()
        # se formatea la info
        reserva_formateada = formatear_Reservas(query)
        return reserva_formateada


    #obtiene una reserva via id 
    def get_reserva_by_id(self, id , db:Session):
        
        cto = (
        db.query(ReservaDB, CanchaDB)
        .join(CanchaDB, ReservaDB.cancha_id == CanchaDB.id)
        .filter(ReservaDB.id == id)  # Filtro para buscar por el ID de la reserva
        .first()  # Obtén el primer resultado
        )

        # Si no se encuentra la reserva, lanza un error
        if not cto:
            raise HTTPException(status_code=404, detail="Reserva con el ID proporcionado no encontrada")
        

        # Formatea la reserva
        reserva_formateada = formatear_Reservas([cto])  # Pasar la tupla como lista
        return reserva_formateada[0]  # Devuelve la primera y única reserva

    # Agrega una reserva
    def agregar_reserva(self, r:ReservaDB, db:Session):
       
        # verifica si la cancha seleccionada existe para descartar posibles errores
        result = db.query(CanchaDB).filter_by(id=r.cancha_id).first()
        if not result:
            raise HTTPException(status_code=404, detail="El ID de la cancha no existe.")
    
        horario_inicio = datetime.combine(datetime.min, r.horario)
        horario_fin = horario_inicio + timedelta(hours=r.duracionHs)

        # busco las reservas que sean en el mismo dia de la cancha seleccionada
        search = (db.query(ReservaDB)
                 .filter(ReservaDB.cancha_id == r.cancha_id)
                 .filter(ReservaDB.dia == r.dia)
                 .all())
        
        # despues itero entre los resultados de las reservas del dia para ver si hay conflicto entre los horarios y el horario entrante
        verificar_conflictos(horario_inicio,horario_fin,search)
        
        db.add(r)
        db.commit()
        return {"message": f"Reserva agregada correctamente."}


    def modificacion_reserva(self, iid: int, r: ReservaBase, db: Session):
        # Verificar si la reserva existe, si no exite manda excepción
        reserva_existente = db.query(ReservaDB).filter_by(id=iid).first()
        if not reserva_existente:
            raise HTTPException(status_code=404, detail="Reserva no encontrada.")
        
        # Verificar si la cancha existe, si no exite manda excepción
        cancha_existente = db.query(CanchaDB).filter_by(id=r.cancha_id).first()
        if not cancha_existente:
            raise HTTPException(status_code=404, detail="El ID de la cancha no existe.")
        
        # Validar conflictos de horarios, excluyendo la misma reserva que estamos modificando
        horario_inicio = datetime.combine(datetime.min, r.horario)
        horario_fin = horario_inicio + timedelta(hours=r.duracionHs)
        
        reservas_en_dia = (db.query(ReservaDB)
                        .filter(ReservaDB.cancha_id == r.cancha_id)
                        .filter(ReservaDB.dia == r.dia)
                        .filter(ReservaDB.id != iid)  # Excluir la misma reserva
                        .all())
        
        verificar_conflictos(horario_inicio,horario_fin,reservas_en_dia)
        
        
        # Actualizar los datos de la reserva
        reserva_existente.dia = r.dia
        reserva_existente.horario = r.horario
        reserva_existente.duracionHs = r.duracionHs
        reserva_existente.nombre_contacto = r.nombre_contacto
        reserva_existente.telefono_contacto = r.telefono_contacto
        reserva_existente.cancha_id = r.cancha_id
        
        db.commit()
        return {"message": "Reserva actualizada correctamente."}

    def eliminar_reserva_by_id(self, id:int, db:Session):
        """
        elimina una reserva en base a un id
        Args:
            ID (datetime): De la reserva a eliminar.
        Raises:
            NotFoundError: si no existe la reserva a eliminar.
        """
        cto = (
        db.query(ReservaDB)
        .filter(ReservaDB.id == id)  # Filtro para buscar por el ID de la reserva
        .first())

        # Si no se encuentra la reserva, lanza un error
        if not cto:
            raise NotFoundError(status_code=404, detail="Reserva con el ID proporcionado no encontrada")
        else:
            db.delete(cto)
            db.commit()
            return {"message": f"Reserva con id {id} eliminada correctamente."}



def verificar_conflictos(entrante_horario_ini, entrante_horario_fin, search):
    """
    Verifica conflictos de horario entre una reserva entrante y las reservas existentes.

    Args:
        horario_ini (datetime): Hora de inicio de la reserva entrante.
        horario_fin (datetime): Hora de fin de la reserva entrante.
        reservas (list[ReservaDB]): Lista de reservas existentes para comparar.

    Raises:
        HTTPException: Si se detecta un conflicto con otra reserva.
    """
    
    for reserva in search:
        reserva_inicio = datetime.combine(datetime.min, reserva.horario)
        reserva_fin = reserva_inicio + timedelta(hours=reserva.duracionHs)
        
        if not (entrante_horario_fin <= reserva_inicio or entrante_horario_ini >= reserva_fin):
            raise HTTPException(
            status_code=400,
            detail=(
            f"Conflicto con otra reserva desde {reserva_inicio.time()} hasta {reserva_fin.time()} "
            f"en la fecha {reserva.dia}."
        )
    )
    
def formatear_Reservas(reserv):
    reserva_formateada = [
        {
            "id": reserva.ReservaDB.id,
            "dia": reserva.ReservaDB.dia,
            "horario": reserva.ReservaDB.horario,
            "duracionHs": reserva.ReservaDB.duracionHs,
            "nombre_contacto": reserva.ReservaDB.nombre_contacto,
            "telefono_contacto": reserva.ReservaDB.telefono_contacto,
            "cancha": {
                "id": reserva.CanchaDB.id,
                "nombre": reserva.CanchaDB.nombre,
                "techada": reserva.CanchaDB.techada,
            }
        }for reserva in reserv
    ]
    return reserva_formateada
    
