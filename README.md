# ArepIA - Gestión Inteligente de Producción de Arepas

Sistema de gestión de inventario y predicción de producción con IA para producción de arepas.

## 🚀 Comenzar Rápido (Desarrollo Local)

### Requisitos Previos
- Python 3.11+
- pip (gestor de paquetes Python)
- Git
- Navegador web moderno

### Opción 1: Ejecución Simple (Recomendado para Principiantes)

```bash
# 1. Clonar el repositorio
git clone <URL-REPOSITORIO>
cd arepIA

# 2. Ir al directorio del backend
cd backend

# 3. Instalar dependencias
pip install -r requirements.txt

# 4. Ejecutar el servidor FastAPI
python -m app

# Output esperado:
# INFO:     Uvicorn running on http://127.0.0.1:8000
```

**El backend está corriendo en:** `http://localhost:8000`

### Opción 2: Ejecución con Uvicorn Directo

```bash
cd arepIA/backend

# Instalar dependencias
pip install -r requirements.txt

# Ejecutar con uvicorn
uvicorn app:app --reload --host 0.0.0.0 --port 8000

# Parámetros:
# --reload: Reinicia automáticamente al cambiar archivos
# --host 0.0.0.0: Accesible desde otros equipos
# --port 8000: Puerto de escucha
```

### Opción 3: Usando Make (si tienes Makefile)

```bash
cd arepIA

# Ver comandos disponibles
make help

# Ejecutar el servidor
make run-api
```

## 🌐 Acceder a la Aplicación

### Backend (API)
```
URL: http://localhost:8000
Swagger UI: http://localhost:8000/docs
ReDoc: http://localhost:8000/redoc
```

### Frontend (Interfaz)
1. **Opción A:** Abrir archivo directamente
   ```bash
   # En macOS
   open arepIA/frontend/index.html
   
   # En Linux
   xdg-open arepIA/frontend/index.html
   
   # En Windows
   start arepIA/frontend/index.html
   ```

2. **Opción B:** Usar navegador
   - Abrir: `file:///ruta/absoluta/arepIA/frontend/index.html`

3. **Opción C:** Servidor HTTP local (Python 3+)
   ```bash
   cd arepIA/frontend
   python -m http.server 8001
   
   # Luego acceder a: http://localhost:8001
   ```

## 📊 Estructura de Carpetas

```
arepIA/
├── backend/
│   ├── app.py              # API principal
│   ├── models.py           # Modelos de BD
│   ├── database.py         # Conexión BD
│   ├── requirements.txt    # Dependencias
│   ├── test_models.py      # Tests
│   └── test_api.py         # Tests API
├── frontend/
│   ├── index.html          # Dashboard
│   ├── styles.css          # Estilos
│   └── app.js              # JavaScript
├── scripts/
│   └── deploy-render.sh    # Deploy automation
├── Dockerfile*             # Dockerfiles
├── Jenkinsfile             # Pipeline CI/CD
└── .gitignore              # Archivos ignorados
```

## 🧪 Ejecutar Tests

```bash
cd arepIA/backend

# Todos los tests
pytest -v

# Solo tests de modelos
pytest test_models.py -v

# Solo tests de API
pytest test_api.py -v

# Con coverage
pytest --cov=. --cov-report=html
```

## 🐳 Usando Docker

### Build de Imágenes

```bash
cd arepIA

# Build backend
docker build -f Dockerfile.backend -t arepIA-backend:latest .

# Build frontend
docker build -f Dockerfile.frontend -t arepIA-frontend:latest .
```

### Ejecutar en Contenedor

```bash
# Backend
docker run -p 8000:8000 arepIA-backend:latest

# Frontend
docker run -p 80:80 arepIA-frontend:latest
```

### Docker Compose (Opcional)

```bash
docker-compose up -d

# Esto levanta backend en :8000 y frontend en :80
```

## 📝 Workflow de Desarrollo

### 1. Cambiar Backend

```bash
# El backend tiene --reload, se actualiza automáticamente
# Editar archivos en backend/ y guardar
# La API se recargará automáticamente
```

### 2. Cambiar Frontend

```bash
# Opción A: Si usas servidor Python
cd frontend
python -m http.server 8001
# Luego refrescar navegador (Ctrl+R o Cmd+R)

# Opción B: Si abres HTML directamente
# Refrescar navegador (Ctrl+R o Cmd+R)
```

## 🔍 Verificar que Todo Funciona

### Verificación del Backend

```bash
# En otra terminal
curl http://localhost:8000/docs

# Deberías ver: Swagger UI en HTML
```

### Verificación del Frontend

1. Abre `http://localhost:8000/docs` en navegador
2. Verifica que ves "ArepIA" en página
3. Intenta crear un ingrediente en el formulario

## ⚠️ Troubleshooting

### Error: Puerto 8000 en uso

```bash
# Encontrar proceso usando puerto 8000
lsof -i :8000

# Matar el proceso
kill -9 <PID>

# O usar otro puerto
uvicorn app:app --port 8001
```

### Error: ModuleNotFoundError

```bash
# Asegurar que estás en directorio correcto
cd arepIA/backend

# Reinstalar dependencias
pip install -r requirements.txt

# Verificar Python version
python --version  # Debe ser 3.11+
```

### Error: Database Locked

```bash
# Eliminar bases de datos de test
rm -f test.db arepIA.db

# Ejecutar de nuevo
python -m app
```

### Frontend no actualiza

```bash
# Limpiar caché del navegador
# Presionar: Ctrl+Shift+Delete (Windows/Linux) o Cmd+Shift+Delete (Mac)

# O forzar recarga
# Presionar: Ctrl+F5 (Windows/Linux) o Cmd+Shift+R (Mac)
```

## 📚 APIs Disponibles

### Endpoints Principales

```
GET  /inventario              # Listar ingredientes
POST /inventario              # Crear ingrediente
POST /ventas                  # Registrar venta
POST /variables               # Registrar variable externa
POST /prediccion              # Obtener predicción IA
```

### Ejemplo de Request

```bash
# Crear ingrediente
curl -X POST "http://localhost:8000/inventario" \
  -H "Content-Type: application/json" \
  -d '{
    "ingrediente": "Harina de maíz",
    "cantidad_actual": 50.0,
    "unidad": "kg"
  }'
```

## 🎯 Próximos Pasos

1. **Entrenar modelo ML**
   ```bash
   python ml/train_model.py
   ```

2. **Ejecutar con PostgreSQL**
   - Cambiar DATABASE_URL en .env

3. **Agregar autenticación**
   - Implementar JWT en backend

4. **Deploy a Render**
   - Ver `CI_CD_SETUP.md`

## 📖 Documentación Adicional

- **[TESTING_GUIDE.md](./TESTING_GUIDE.md)** - Guía de testing
- **[GAPS_ANALYSIS.md](./GAPS_ANALYSIS.md)** - Análisis de brechas
- **[CI_CD_SETUP.md](./CI_CD_SETUP.md)** - Configuración Jenkins
- **[Jenkinsfile](./Jenkinsfile)** - Pipeline CI/CD

## 🤝 Contribuciones

1. Fork el proyecto
2. Crea una rama (`git checkout -b feature/mejora`)
3. Commit cambios (`git commit -m 'Añade mejora'`)
4. Push a la rama (`git push origin feature/mejora`)
5. Abre Pull Request

## 📄 Licencia

Este proyecto está bajo licencia MIT.

## 📞 Soporte

Para problemas o preguntas:
1. Revisar [TESTING_GUIDE.md](./TESTING_GUIDE.md)
2. Consultar [GAPS_ANALYSIS.md](./GAPS_ANALYSIS.md)
3. Ver logs: `cat uvicorn.log`

---

**Última actualización:** 2024-06-06
**Versión:** 1.0.0
**Python:** 3.11+
**FastAPI:** 0.100+
