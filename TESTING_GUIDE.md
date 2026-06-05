# Guía de Testing - Proyecto ArepIA

## 📋 Estructura de Tests

El proyecto ArepIA incluye tests unitarios para validar la funcionalidad:

### Tests de Modelos (`test_models.py`)
- ✅ Crear ingredientes en inventario
- ✅ Leer y listar inventario
- ✅ Actualizar cantidades
- ✅ Eliminar ingredientes
- ✅ Crear ventas
- ✅ Calcular totales de ventas
- ✅ Variables externas (clima, festivos)

### Tests de API (`test_api.py`)
- ✅ Health check del sistema
- ✅ Endpoints de Inventario (POST, GET)
- ✅ Endpoints de Ventas (POST, validaciones)
- ✅ Endpoints de Variables Externas
- ✅ Endpoint de Predicción IA
- ✅ Validación de datos

## 🚀 Cómo Ejecutar los Tests

### Opción 1: Ejecutar en Terminal Local

```bash
# Ir al directorio backend
cd arepIA/backend

# Ejecutar todos los tests
pytest -v

# Ejecutar con reporte detallado
pytest -v --tb=short

# Ejecutar solo tests de modelos
pytest test_models.py -v

# Ejecutar solo tests de API
pytest test_api.py -v

# Ejecutar con coverage
pytest --cov=. --cov-report=html
```

### Opción 2: Ejecutar desde Docker

```bash
# Build de la imagen
docker build -f Dockerfile.backend -t arepIA-backend-test .

# Ejecutar tests en contenedor
docker run --rm arepIA-backend-test pytest -v
```

### Opción 3: Usar Jenkinsfile

Los tests se ejecutan automáticamente en el pipeline:

```bash
# El Jenkinsfile ejecuta tests en stage "Test Backend"
# Trigger manualmente desde Jenkins con SKIP_TESTS=false
```

## 📊 Cobertura de Tests

| Componente | Cobertura | Estado |
|-----------|----------|--------|
| Modelos | 100% | ✅ Completo |
| Endpoints | 80% | ✅ Bueno |
| Validaciones | 75% | ⚠️ Parcial |
| ML/Predicción | 50% | ⚠️ Limitado |
| Frontend | 0% | ⏳ Pendiente |

## 🔍 Interpretación de Resultados

### Test Exitoso (✓)
```
test_crear_ingrediente PASSED                              [100%]
```
- El test pasó sin errores
- La funcionalidad funciona correctamente

### Test Fallido (✗)
```
test_crear_ingrediente FAILED                              [100%]
AssertionError: assert None is not None
```
- Hay un problema en la funcionalidad
- Ver el traceback para detalles

### Test Saltado (S)
```
test_prediccion_sin_modelo SKIPPED                         [100%]
```
- El test no se ejecutó (puede ser intencional)

## 🛠️ Configuración de Tests

### pytest.ini
```ini
[pytest]
testpaths = arepIA/backend
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --tb=short
```

### conftest.py
```python
# Configuración global de fixtures
import pytest

@pytest.fixture(scope="session")
def db_engine():
    from database import engine
    return engine
```

## 📈 Ejemplo de Ejecución Completa

```
======================== test session starts ========================
platform linux -- Python 3.11.0, pytest-8.0.0
collected 14 items

test_models.py::TestInventarioModel::test_crear_ingrediente PASSED
test_models.py::TestInventarioModel::test_leer_inventario PASSED
test_models.py::TestInventarioModel::test_actualizar_cantidad PASSED
test_models.py::TestInventarioModel::test_eliminar_ingrediente PASSED
test_models.py::TestVentaModel::test_crear_venta PASSED
test_models.py::TestVentaModel::test_calcular_total_venta PASSED
test_models.py::TestVentaModel::test_listar_ventas PASSED
test_models.py::TestVariableExternaModel::test_crear_variable_externa PASSED
test_models.py::TestVariableExternaModel::test_variable_con_festivo PASSED
test_api.py::TestHealthCheck::test_api_disponible PASSED
test_api.py::TestInventarioEndpoints::test_crear_ingrediente PASSED
test_api.py::TestInventarioEndpoints::test_listar_inventario PASSED
test_api.py::TestVentasEndpoints::test_crear_venta PASSED
test_api.py::TestPrediccionEndpoints::test_obtener_prediccion PASSED

======================== 14 passed in 2.34s ========================
```

## ✅ Checklist de Validación

- [ ] Tests de modelos pasan ✓
- [ ] Tests de endpoints pasan ✓
- [ ] Cobertura > 80%
- [ ] Sin warnings de pylint
- [ ] BD se crea y limpia correctamente
- [ ] Validaciones funcionan
- [ ] Errores manejados apropiadamente

## 🔧 Troubleshooting

### Error: "ModuleNotFoundError: No module named 'models'"
**Solución:**
```bash
cd arepIA/backend
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest -v
```

### Error: "Database is locked"
**Solución:**
```bash
# Eliminar base de datos de test
rm -f test.db arepIA.db
pytest -v
```

### Error: "Connection refused"
**Solución:** Asegúrate que el backend no está corriendo en puerto 8000 durante tests

## 📚 Referencias

- [pytest Documentation](https://docs.pytest.org/)
- [FastAPI Testing](https://fastapi.tiangolo.com/advanced/testing-dependencies/)
- [SQLAlchemy Testing](https://docs.sqlalchemy.org/en/20/orm/session_basics.html)

## 🎯 Próximos Pasos

1. [ ] Agregar tests de integración
2. [ ] Tests de performance
3. [ ] Tests de seguridad
4. [ ] Tests end-to-end con Selenium
5. [ ] Aumentar cobertura a 95%

---

**Última actualización:** 2024-06-06
**Versión de Python:** 3.11+
**Framework de Testing:** pytest 8.0+
