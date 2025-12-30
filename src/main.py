from fastapi import FastAPI
from src.shop.models.db import Base, engine
from src.shop.categories.models import Category

# Crear la aplicación
app = FastAPI(title="Mi Tienda Online")

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

# Endpoints de prueba
@app.get("/")
def home():
    return {"mensaje": "Bienvenido a mi tienda online"}

@app.get("/test")
def test():
    return {"status": "funcionando", "database": "shop.db creada"}