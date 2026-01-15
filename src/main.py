from fastapi import FastAPI
from src.shop.db import Base, engine
from src.shop.models import *
from src.shop.endpoints.products import router as products_router



# Crear la aplicación
app = FastAPI(title="Mixshop")

# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app.include_router(products_router)
# Endpoints de prueba
@app.get("/")
def home():
    return {"mensaje": "Bienvenido a mi tienda online"}

@app.get("/test")
def test():
    return {"status": "funcionando", "database": "shop.db creada"}