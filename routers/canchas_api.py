# Back/routers/cancha.py
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..service import CanchasRepo,NotFoundError
from ..database import db_instance
from ..schemas import CanchaBase
from ..models.cancha import CanchaDB

router = APIRouter()

canchaRepo = CanchasRepo()

@router.get("/get-canchas")
def listar_canchas(db: Session = Depends(db_instance.get_db)):
    
    return canchaRepo.get_all_canchas(db)

@router.get("/get_cancha/{id}")
def buscar_cancha_por_id(  id:int  ,  db: Session = Depends(db_instance.get_db)):
    
    return canchaRepo.get_cancha_by_id(id,db)

@router.post("/Agregar_canchas")
def Agregar_Cancha(  c:CanchaBase  ,  db: Session = Depends(db_instance.get_db)):
    print(f"Datos recibidos: {c}")
    cancha_db = CanchaDB()
    cancha_db.nombre = c.nombre
    cancha_db.techada = c.techada
    try:
        canchaRepo.Registrar_Cancha(cancha_db,db)
    except NotFoundError as e:
        raise HTTPException(e.status_code, "id no encontrado")
    except HTTPException as e:
        raise e
    
@router.delete("/BorrarCancha/{id}")
def Eliminar_cancha(  id:int  ,  db: Session = Depends(db_instance.get_db)):   
    try:
        canchaRepo.borrar_cancha(id,db)
    except NotFoundError as e:
        raise HTTPException(e.status_code, "id no encontrado")
    
    return {"code": "funciona"}