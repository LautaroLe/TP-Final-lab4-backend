#Back/database
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
import json

# Configuración de la base de datos

with open("db.json") as config_file:
    config = json.load(config_file)

DATABASE_URL = config["database_url"]

class Database():
    def __init__(self, connection_string: str = DATABASE_URL, echo: bool = True):
        try:
            self.engine = create_engine(connection_string, echo=echo)
        except Exception as e:
            print(f"Error al conectar a la base de datos: {e}")
            raise
        

    @property
    def SessionLocal(self):
        return sessionmaker(autocommit=False, autoflush=False, bind=self.engine)
    
    
    def get_db(self):
        db_Session = self.SessionLocal()
        try:
            yield db_Session
        finally:
            db_Session.close()

    #usa la base para generar las tablas que son representadas por clases las cuales heredan de ORMBase en cierto modo de declarative_base()
    def create_all(self):
        ORMBase.metadata.create_all(self.engine)

    #usa la base para eliminar las tablas que son representadas por clases las cuales heredan de ORMBase en cierto modo de declarative_base()
    def drop_all(self): 
        ORMBase.metadata.drop_all(bind=self.engine)



# Se crea un objeto para las clases bases del modelo
# esto quiere decir que todas las clases del modelo deben heredar de esta clase
ORMBase = declarative_base()

# Variable global para la instancia de la base de datos
db_instance = Database()


