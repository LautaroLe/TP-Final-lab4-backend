# routers/reserva.py
from fastapi import APIRouter, Depends, HTTPException, Path, Query
from sqlalchemy.orm import Session
from ..service import ReservasRepo
from datetime import date, datetime
from ..database import db_instance
from ..schemas import ReservaBase
from ..models.reserva import ReservaDB

router = APIRouter()

reservasRepo = ReservasRepo()

@router.get("/get-Reservas")
def obtener_reservas( 
    db: Session = Depends(db_instance.get_db)):
    try:
        result =  reservasRepo.get_all_reservas(db)
        print(result)
        return result
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@router.get("/get-Reserva/{id}")
def obtener_reserva_id(
    id:int, 
    db: Session = Depends(db_instance.get_db)):
    try:
        reserva = reservasRepo.get_reserva_by_id(id, db)
        if reserva:
            return reserva   
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error inesperado: {str(e)}")


@router.get("/filtrar-Reserva")
def filtrar_reservas(
    dia: date = Query(None, description="Fecha para filtrar las reservas (formato: YYYY-MM-DD)"),
    id: int = Query(None, description="ID de la cancha para filtrar las reservas"),
    db: Session = Depends(db_instance.get_db)):
    try:
        return reservasRepo.filtrar_reservas(dia,id,db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al agregar la reserva: {str(e)}"
        )

@router.post("/add-Reservas")
def agregar_reservas( 
    r:ReservaBase , 
    db: Session = Depends(db_instance.get_db)):

    try:
        # Crear la instancia del modelo para guardar en la base de datos
        nueva_reserva = ReservaDB( 
            dia = r.dia,
            horario = r.horario,
            duracionHs = r.duracionHs,
            nombre_contacto = r.nombre_contacto,
            telefono_contacto = r.telefono_contacto,
            cancha_id = r.cancha_id,
        )

        # Guardar en la base de datos utilizando el repositorio
        reservasRepo.agregar_reserva(nueva_reserva, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al agregar la reserva: {str(e)}"
        )

@router.put("/modificar-Reserva/{id}")
def modification_of_reserva( 
    id: int, 
    r: ReservaBase,
    db: Session = Depends(db_instance.get_db)):
    try:
        return reservasRepo.modificacion_reserva(id, r, db)
    except HTTPException as e:
        raise e
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al modificar la reserva: {str(e)}"
        )

@router.delete("/delete-reserva/{id}")
def Borrar_reserva( 
    id: int ,
    db: Session = Depends(db_instance.get_db)):
    try:
        reservasRepo.eliminar_reserva_by_id(id,db)
    except HTTPException as e:
        raise e  
    except Exception as e:
        raise HTTPException(
            status_code=500, detail=f"Error al eliminar la reserva: {str(e)}"
        )
