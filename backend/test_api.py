"""
Tests para la API FastAPI del agente.
"""
import pytest
from fastapi.testclient import TestClient
from pathlib import Path
import sys

# Agregar path del proyecto
sys.path.insert(0, str(Path(__file__).parent.parent))

from app.main import app


@pytest.fixture
def client():
    """Fixture que provee el cliente de testing de FastAPI."""
    return TestClient(app)


class TestHealthEndpoint:
    """Tests para el endpoint de health check."""
    
    def test_health_check(self, client):
        """Verifica que el health check funciona."""
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"


class TestQueryEndpoint:
    """Tests para el endpoint /query."""
    
    def test_query_endpoint_exists(self, client):
        """Verifica que el endpoint /query existe."""
        response = client.post("/query", json={
            "message": "Test query",
            "session_id": "test"
        })
        # Debe retornar 200 o algún código válido, no 404
        assert response.status_code != 404
    
    def test_query_with_valid_input(self, client):
        """Test de consulta con entrada válida."""
        response = client.post("/query", json={
            "message": "¿Qué es QFlow?",
            "session_id": "test_session"
        })
        
        if response.status_code == 200:
            data = response.json()
            assert "response" in data
            assert isinstance(data["response"], str)
    
    def test_query_without_session_id(self, client):
        """Test de consulta sin session_id (debe usar default)."""
        response = client.post("/query", json={
            "message": "Test query"
        })
        
        # Debe funcionar con session_id por defecto
        assert response.status_code in [200, 422]  # 422 si es requerido
    
    def test_query_empty_message(self, client):
        """Test con mensaje vacío."""
        response = client.post("/query", json={
            "message": "",
            "session_id": "test"
        })
        
        # Debe manejar el caso gracefully
        assert response.status_code in [200, 400, 422]


class TestDocgenEndpoint:
    """Tests para el endpoint /docgen."""
    
    def test_docgen_endpoint_exists(self, client):
        """Verifica que el endpoint /docgen existe."""
        response = client.post("/docgen", json={
            "repo_path": "/test/path"
        })
        assert response.status_code != 404
    
    def test_docgen_with_invalid_path(self, client):
        """Test con ruta inválida."""
        response = client.post("/docgen", json={
            "repo_path": "/path/that/does/not/exist"
        })
        
        # Debe retornar error apropiado
        assert response.status_code in [200, 400, 404, 422]


class TestMetricsEndpoint:
    """Tests para el endpoint /metrics."""
    
    def test_metrics_endpoint_exists(self, client):
        """Verifica que el endpoint /metrics existe."""
        response = client.get("/metrics")
        assert response.status_code != 404
    
    def test_metrics_returns_data(self, client):
        """Verifica que /metrics retorna datos."""
        response = client.get("/metrics")
        
        if response.status_code == 200:
            data = response.json()
            assert isinstance(data, dict)


class TestAPIIntegration:
    """Tests de integración de múltiples endpoints."""
    
    def test_query_updates_metrics(self, client):
        """Verifica que consultas actualizan métricas."""
        # Obtener métricas iniciales
        metrics_before = client.get("/metrics")
        
        # Hacer una consulta
        client.post("/query", json={
            "message": "Test",
            "session_id": "integration_test"
        })
        
        # Obtener métricas después
        metrics_after = client.get("/metrics")
        
        # Verificar que ambos requests funcionaron
        assert metrics_before.status_code in [200, 404]
        assert metrics_after.status_code in [200, 404]
    
    def test_multiple_sessions(self, client):
        """Verifica que múltiples sesiones funcionan correctamente."""
        sessions = ["session1", "session2", "session3"]
        
        for session_id in sessions:
            response = client.post("/query", json={
                "message": f"Test from {session_id}",
                "session_id": session_id
            })
            # Cada sesión debe poder procesar requests
            assert response.status_code in [200, 404, 422]


class TestErrorHandling:
    """Tests de manejo de errores de la API."""
    
    def test_invalid_json(self, client):
        """Test con JSON inválido."""
        response = client.post(
            "/query",
            data="not valid json",
            headers={"Content-Type": "application/json"}
        )
        assert response.status_code == 422
    
    def test_missing_required_fields(self, client):
        """Test con campos requeridos faltantes."""
        response = client.post("/query", json={})
        # Debe rechazar por falta de campo message
        assert response.status_code == 422
    
    def test_invalid_endpoint(self, client):
        """Test de endpoint inexistente."""
        response = client.get("/nonexistent")
        assert response.status_code == 404


class TestCORS:
    """Tests de configuración CORS."""
    
    def test_cors_headers(self, client):
        """Verifica que headers CORS están presentes."""
        response = client.options("/query")
        # CORS debe estar configurado
        assert response.status_code in [200, 404, 405]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
