from sqlalchemy import Column, Integer, String, Numeric, Boolean, Date
from database import Base


class Inventario(Base):
    __tablename__ = "inventario"

    id = Column(Integer, primary_key=True, index=True)
    ingrediente = Column(String(50), nullable=False)
    cantidad_actual = Column(Numeric(10, 2), nullable=False)
    unidad = Column(String(20), nullable=False)


class Venta(Base):
    __tablename__ = "ventas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    tipo_arepa = Column(String(50), nullable=False)
    cantidad = Column(Integer, nullable=False)
    precio_unitario = Column(Numeric(10, 2), nullable=False)


class VariableExterna(Base):
    __tablename__ = "variables_externas"

    id = Column(Integer, primary_key=True, index=True)
    fecha = Column(Date, nullable=False)
    clima = Column(String(50))
    es_festivo = Column(Boolean, default=False)
