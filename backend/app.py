from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import List

from .database import Base, engine, get_db
from .models import Inventario, Venta, VariableExterna
from .ml_service import predecir_ventas
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="ArepIA - Gestión e IA para producción de arepas")
origins = [
    "http://localhost",
    "http://localhost:8000",
    "http://127.0.0.1:8000",
    # Agrega aquí otros orígenes si es necesario
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # permite POST, GET, OPTIONS, etc.
    allow_headers=["*"],
)

# --------- Schemas Pydantic ---------

class InventarioCreate(BaseModel):
    ingrediente: str
    cantidad_actual: float
    unidad: str

class InventarioRead(BaseModel):
    id: int
    ingrediente: str
    cantidad_actual: float
    unidad: str

    class Config:
        orm_mode = True

class VentaCreate(BaseModel):
    fecha: date
    tipo_arepa: str
    cantidad: int
    precio_unitario: float

class VariableExternaCreate(BaseModel):
    fecha: date
    clima: str
    es_festivo: bool = False

class PrediccionRequest(BaseModel):
    fecha: date
    clima: str
    es_festivo: bool = False

class PrediccionResponse(BaseModel):
    fecha: date
    produccion_recomendada: float


# --------- Rutas Inventario ---------

@app.post("/inventario", response_model=InventarioRead)
def crear_ingrediente(item: InventarioCreate, db: Session = Depends(get_db)):
    obj = Inventario(
        ingrediente=item.ingrediente,
        cantidad_actual=item.cantidad_actual,
        unidad=item.unidad
    )
    db.add(obj)
    db.commit()
    db.refresh(obj)
    return obj

@app.get("/inventario", response_model=List[InventarioRead])
def listar_inventario(db: Session = Depends(get_db)):
    return db.query(Inventario).all()


# --------- Rutas Ventas ---------

@app.post("/ventas")
def registrar_venta(venta: VentaCreate, db: Session = Depends(get_db)):
    obj = Venta(
        fecha=venta.fecha,
        tipo_arepa=venta.tipo_arepa,
        cantidad=venta.cantidad,
        precio_unitario=venta.precio_unitario
    )
    db.add(obj)
    db.commit()
    return {"status": "ok"}


# --------- Rutas Variables Externas ---------

@app.post("/variables")
def registrar_variables(vars: VariableExternaCreate, db: Session = Depends(get_db)):
    obj = VariableExterna(
        fecha=vars.fecha,
        clima=vars.clima,
        es_festivo=vars.es_festivo
    )
    db.add(obj)
    db.commit()
    return {"status": "ok"}


# --------- Predicción de producción ---------

@app.post("/prediccion", response_model=PrediccionResponse)
def obtener_prediccion(body: PrediccionRequest):
    pred = predecir_ventas(body.fecha, body.clima, body.es_festivo)
    if pred is None:
        raise HTTPException(
            status_code=500,
            detail="Modelo de IA no entrenado. Entrena el modelo en /ml/train_model.py y guarda model.joblib."
        )
    return PrediccionResponse(
        fecha=body.fecha,
        produccion_recomendada=pred
    )
