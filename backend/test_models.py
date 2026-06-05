import pytest
import sys
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from datetime import date

# Agregar el directorio actual al path
sys.path.insert(0, os.path.dirname(__file__))

from models import Base, Inventario, Venta, VariableExterna

# Database setup para tests
SQLALCHEMY_TEST_DATABASE_URL = "sqlite:///./test.db"

engine = create_engine(
    SQLALCHEMY_TEST_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="function")
def db_session():
    """Fixture que proporciona una sesión de DB para tests"""
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    yield session
    session.close()
    Base.metadata.drop_all(bind=engine)


class TestInventarioModel:
    """Tests para modelo Inventario"""
    
    def test_crear_ingrediente(self, db):
        """Test crear un ingrediente en inventario"""
        ingrediente = Inventario(
            ingrediente="Harina de maíz",
            cantidad_actual=50.0,
            unidad="kg"
        )
        db.add(ingrediente)
        db.commit()
        db.refresh(ingrediente)
        
        assert ingrediente.id is not None
        assert ingrediente.ingrediente == "Harina de maíz"
        assert ingrediente.cantidad_actual == 50.0
        assert ingrediente.unidad == "kg"
    
    def test_leer_inventario(self, db):
        """Test leer ingredientes del inventario"""
        # Crear varios ingredientes
        ing1 = Inventario(ingrediente="Harina", cantidad_actual=50.0, unidad="kg")
        ing2 = Inventario(ingrediente="Sal", cantidad_actual=10.0, unidad="kg")
        db.add_all([ing1, ing2])
        db.commit()
        
        # Leer todos
        inventario = db.query(Inventario).all()
        assert len(inventario) == 2
        assert inventario[0].ingrediente == "Harina"
    
    def test_actualizar_cantidad(self, db):
        """Test actualizar cantidad de ingrediente"""
        ing = Inventario(ingrediente="Harina", cantidad_actual=50.0, unidad="kg")
        db.add(ing)
        db.commit()
        
        # Actualizar cantidad
        ing.cantidad_actual = 30.0
        db.commit()
        db.refresh(ing)
        
        assert ing.cantidad_actual == 30.0
    
    def test_eliminar_ingrediente(self, db):
        """Test eliminar ingrediente"""
        ing = Inventario(ingrediente="Harina", cantidad_actual=50.0, unidad="kg")
        db.add(ing)
        db.commit()
        ing_id = ing.id
        
        db.delete(ing)
        db.commit()
        
        # Verificar que fue eliminado
        ing_eliminado = db.query(Inventario).filter(Inventario.id == ing_id).first()
        assert ing_eliminado is None


class TestVentaModel:
    """Tests para modelo Venta"""
    
    def test_crear_venta(self, db):
        """Test crear una venta"""
        venta = Venta(
            fecha=date.today(),
            tipo_arepa="Arepa de Queso",
            cantidad=10,
            precio_unitario=2.5
        )
        db.add(venta)
        db.commit()
        db.refresh(venta)
        
        assert venta.id is not None
        assert venta.tipo_arepa == "Arepa de Queso"
        assert venta.cantidad == 10
        assert venta.precio_unitario == 2.5
    
    def test_calcular_total_venta(self, db):
        """Test verificar datos de venta"""
        venta = Venta(
            fecha=date.today(),
            tipo_arepa="Arepa Reina Pepiada",
            cantidad=5,
            precio_unitario=3.0
        )
        db.add(venta)
        db.commit()
        
        total_esperado = 5 * 3.0
        total_actual = venta.cantidad * venta.precio_unitario
        assert total_actual == total_esperado
    
    def test_listar_ventas(self, db):
        """Test listar todas las ventas"""
        venta1 = Venta(fecha=date.today(), tipo_arepa="Queso", cantidad=5, precio_unitario=2.5)
        venta2 = Venta(fecha=date.today(), tipo_arepa="Reina Pepiada", cantidad=3, precio_unitario=3.0)
        db.add_all([venta1, venta2])
        db.commit()
        
        ventas = db.query(Venta).all()
        assert len(ventas) == 2


class TestVariableExternaModel:
    """Tests para modelo VariableExterna"""
    
    def test_crear_variable_externa(self, db):
        """Test crear variable externa"""
        var = VariableExterna(
            fecha=date.today(),
            clima="soleado",
            es_festivo=False
        )
        db.add(var)
        db.commit()
        db.refresh(var)
        
        assert var.id is not None
        assert var.clima == "soleado"
        assert var.es_festivo == False
    
    def test_variable_con_festivo(self, db):
        """Test variable con día festivo"""
        var = VariableExterna(
            fecha=date.today(),
            clima="lluvioso",
            es_festivo=True
        )
        db.add(var)
        db.commit()
        db.refresh(var)
        
        assert var.es_festivo == True
        assert var.clima == "lluvioso"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
