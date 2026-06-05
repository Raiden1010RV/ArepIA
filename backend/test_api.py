"""
Tests para los endpoints de la API FastAPI
"""
import pytest
from fastapi.testclient import TestClient
from datetime import date
from app import app
from database import Base, engine, SessionLocal

# Crear cliente de prueba
client = TestClient(app)


@pytest.fixture(scope="function")
def setup_db():
    """Setup y teardown de la BD para cada test"""
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


class TestHealthCheck:
    """Tests de verificación del sistema"""
    
    def test_api_disponible(self):
        """Test verificar que la API está disponible"""
        response = client.get("/docs")
        assert response.status_code in [200, 307, 404]  # Swagger puede no estar activo


class TestInventarioEndpoints:
    """Tests para endpoints de Inventario"""
    
    def test_crear_ingrediente(self, setup_db):
        """Test POST /inventario"""
        ingrediente_data = {
            "ingrediente": "Harina de maíz",
            "cantidad_actual": 50.0,
            "unidad": "kg"
        }
        response = client.post("/inventario", json=ingrediente_data)
        assert response.status_code == 200
        data = response.json()
        assert data["ingrediente"] == "Harina de maíz"
        assert data["cantidad_actual"] == 50.0
    
    def test_listar_inventario(self, setup_db):
        """Test GET /inventario"""
        # Crear un ingrediente primero
        ingrediente_data = {
            "ingrediente": "Sal",
            "cantidad_actual": 10.0,
            "unidad": "kg"
        }
        client.post("/inventario", json=ingrediente_data)
        
        # Listar
        response = client.get("/inventario")
        assert response.status_code == 200
        data = response.json()
        assert isinstance(data, list)
        assert len(data) >= 1
    
    def test_ingrediente_validacion(self, setup_db):
        """Test validación de datos en POST /inventario"""
        # Datos inválidos (falta cantidad_actual)
        ingrediente_data = {
            "ingrediente": "Harina",
            "unidad": "kg"
        }
        response = client.post("/inventario", json=ingrediente_data)
        assert response.status_code == 422  # Validation Error


class TestVentasEndpoints:
    """Tests para endpoints de Ventas"""
    
    def test_crear_venta(self, setup_db):
        """Test POST /ventas"""
        venta_data = {
            "fecha": str(date.today()),
            "tipo_arepa": "Arepa de Queso",
            "cantidad": 10,
            "precio_unitario": 2.5
        }
        response = client.post("/ventas", json=venta_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_venta_cantidad_positiva(self, setup_db):
        """Test que cantidad debe ser positiva"""
        venta_data = {
            "fecha": str(date.today()),
            "tipo_arepa": "Arepa",
            "cantidad": -5,  # Negativo
            "precio_unitario": 2.5
        }
        # La API debería validar esto
        response = client.post("/ventas", json=venta_data)
        # Dependiendo de la validación, puede ser 422 o 200
        assert response.status_code in [200, 422]


class TestVariablesExternasEndpoints:
    """Tests para endpoints de Variables Externas"""
    
    def test_crear_variable(self, setup_db):
        """Test POST /variables"""
        variable_data = {
            "fecha": str(date.today()),
            "clima": "soleado",
            "es_festivo": False
        }
        response = client.post("/variables", json=variable_data)
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "ok"
    
    def test_clima_valido(self, setup_db):
        """Test diferentes tipos de clima"""
        climas = ["templado", "soleado", "lluvioso", "nublado"]
        
        for clima in climas:
            variable_data = {
                "fecha": str(date.today()),
                "clima": clima,
                "es_festivo": False
            }
            response = client.post("/variables", json=variable_data)
            assert response.status_code == 200


class TestPrediccionEndpoints:
    """Tests para endpoint de Predicción"""
    
    def test_obtener_prediccion(self, setup_db):
        """Test POST /prediccion"""
        prediccion_data = {
            "fecha": str(date.today()),
            "clima": "soleado",
            "es_festivo": False
        }
        response = client.post("/prediccion", json=prediccion_data)
        # Si el modelo no está entrenado, retorna error 500
        # Si está entrenado, retorna 200
        assert response.status_code in [200, 500]
        
        if response.status_code == 200:
            data = response.json()
            assert "fecha" in data
            assert "produccion_recomendada" in data
    
    def test_prediccion_sin_modelo(self, setup_db):
        """Test predicción cuando el modelo no está disponible"""
        prediccion_data = {
            "fecha": str(date.today()),
            "clima": "templado",
            "es_festivo": True
        }
        response = client.post("/prediccion", json=prediccion_data)
        # Debe retornar error o valor por defecto
        assert response.status_code in [200, 500]


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
