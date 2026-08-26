from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from src.shop.db import Base, engine
from src.shop.models import *
from src.shop.endpoints.products import router as products_router
from src.shop.endpoints.categories import router as categories_router


# Crear la aplicación
app = FastAPI(title="Mixshop")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# Crear las tablas en la base de datos
Base.metadata.create_all(bind=engine)

app.include_router(products_router)
app.include_router(categories_router)
# Endpoints de prueba
@app.get("/")
def home():
    return {"mensaje": "Bienvenido a mi tienda online"}

@app.get("/test")
def test():
    return {"status": "funcionando", "database": "shop.db creada"}