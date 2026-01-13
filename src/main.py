from fastapi import FastAPI
from src.shop.db import Base, engine
from src.shop.models import *


# Crear la aplicación
app = FastAPI(title="Mixshop")

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Endpoints de prueba
@app.get("/")
def home():
    return {"mensaje": "Bienvenido a mi tienda online"}

@app.get("/test")
def test():
    return {"status": "funcionando", "database": "shop.db creada"}