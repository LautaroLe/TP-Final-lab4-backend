from fastapi import FastAPI
from .database import db_instance
from .routers import canchas_api, reservas_api
from .models.cancha import CanchaDB
from .models.reserva import ReservaDB
from fastapi.middleware.cors import CORSMiddleware


# Crear tablas
db_instance.create_all()

app = FastAPI()
# Configurar CORS

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Cambia esto al puerto de tu frontend
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],)

# Incluir rutas
app.include_router(canchas_api.router, prefix="/cancha",tags=["canchas"])
app.include_router(reservas_api.router, prefix="/reserva",tags=["reservas"])
