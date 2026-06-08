from fastapi import FastAPI, Depends, HTTPException
from pydantic import BaseModel
from datetime import date
from typing import List

from database import Base, engine, get_db
from models import Inventario, Venta, VariableExterna
from ml_service import predecir_ventas
from sqlalchemy.orm import Session
from fastapi.middleware.cors import CORSMiddleware


Base.metadata.create_all(bind=engine)

app = FastAPI(title="ArepIA - Gestión e IA para producción de arepas")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


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
        from_attributes = True


class VentaCreate(BaseModel):
    fecha: date
    tipo_arepa: str
    cantidad: int
    precio_unitario: float


class VentaRead(BaseModel):
    id: int
    fecha: date
    tipo_arepa: str
    cantidad: int
    precio_unitario: float

    class Config:
        from_attributes = True


class VariableExternaCreate(BaseModel):
    fecha: date
    clima: str
    es_festivo: bool = False


class VariableExternaRead(BaseModel):
    id: int
    fecha: date
    clima: str
    es_festivo: bool

    class Config:
        from_attributes = True


class PrediccionRequest(BaseModel):
    fecha: date
    clima: str
    es_festivo: bool = False


class PrediccionResponse(BaseModel):
    fecha: date
    produccion_recomendada: float


@app.get("/")
def root():
    from database import DATABASE_URL
    if DATABASE_URL.startswith("postgresql"):
        db_type = "PostgreSQL"
        db_host = DATABASE_URL.split("@")[-1].split("/")[0] if "@" in DATABASE_URL else "remote"
    elif DATABASE_URL.startswith("sqlite"):
        db_type = "SQLite (local/temporal)"
        db_host = DATABASE_URL.replace("sqlite:///", "")
    else:
        db_type = DATABASE_URL.split(":")[0]
        db_host = "unknown"
    return {
        "message": "ArepIA API funcionando",
        "docs": "/docs",
        "database": db_type,
        "db_host": db_host,
    }


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


@app.get("/ventas", response_model=List[VentaRead])
def listar_ventas(db: Session = Depends(get_db)):
    return db.query(Venta).order_by(Venta.fecha.desc()).all()


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


@app.get("/variables", response_model=List[VariableExternaRead])
def listar_variables(db: Session = Depends(get_db)):
    return db.query(VariableExterna).order_by(VariableExterna.fecha.desc()).all()


@app.post("/variables")
def registrar_variables(var_externa: VariableExternaCreate, db: Session = Depends(get_db)):
    obj = VariableExterna(
        fecha=var_externa.fecha,
        clima=var_externa.clima,
        es_festivo=var_externa.es_festivo
    )
    db.add(obj)
    db.commit()
    return {"status": "ok"}


@app.delete("/inventario/{item_id}")
def eliminar_ingrediente(item_id: int, db: Session = Depends(get_db)):
    obj = db.query(Inventario).filter(Inventario.id == item_id).first()
    if not obj:
        raise HTTPException(status_code=404, detail="Ingrediente no encontrado")
    db.delete(obj)
    db.commit()
    return {"status": "ok", "deleted_id": item_id}


@app.post("/prediccion", response_model=PrediccionResponse)
def obtener_prediccion(body: PrediccionRequest):
    pred = predecir_ventas(body.fecha, body.clima, body.es_festivo)
    if pred is None:
        raise HTTPException(
            status_code=500,
            detail="Modelo de IA no entrenado. Entrena el modelo en ml/train_model.py"
        )
    return PrediccionResponse(
        fecha=body.fecha,
        produccion_recomendada=pred
    )
