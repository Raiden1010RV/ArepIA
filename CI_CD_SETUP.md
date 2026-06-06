# 🚀 Guía Completa de Despliegue — arepIA con Jenkins + Docker + Render

## 📋 Archivos del Proyecto (CI/CD)

| Archivo | Descripción |
|---|---|
| `Jenkinsfile` | Pipeline CI/CD principal |
| `Dockerfile.backend` | Imagen Docker para FastAPI + ML |
| `Dockerfile.frontend` | Imagen Docker para frontend con Nginx |
| `.dockerignore` | Exclusiones del contexto Docker |
| `nginx.conf` | Configuración de Nginx (proxy, gzip, SPA) |
| `render.yaml` | Blueprint de infraestructura para Render |
| `scripts/deploy-render.sh` | Script de deployment vía Render API |

---

## 🏗️ Arquitectura de Despliegue

```
Developer → git push → GitHub
                           ↓ webhook
                       Jenkins Pipeline
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
    Build Backend Image       Build Frontend Image
              ↓                         ↓
         Run Tests               Code Analysis
              └────────────┬────────────┘
                           ↓
                    Push → Docker Hub
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
     Deploy Backend             Deploy Frontend
     (Render API)               (Render API)
              └────────────┬────────────┘
                           ↓
                    Health Check
                           ↓
              ┌────────────┴────────────┐
              ↓                         ↓
  arepia-backend.onrender.com  arepia-frontend.onrender.com
              ↓
    PostgreSQL (Render DB)
```

---

## ✅ FASE 0 — Prerrequisitos

Antes de comenzar, asegúrate de tener:

- [ ] Cuenta en **GitHub** con el repositorio `arepIA` en rama `main`
- [ ] Cuenta en **Docker Hub** → https://hub.docker.com
- [ ] Cuenta en **Render** → https://render.com
- [ ] Servidor **Jenkins** con Docker instalado
- [ ] El modelo ML entrenado (`ml/model.joblib`) — ejecutar `python ml/train_model.py` si no existe

---

## FASE 1 — Configurar Render

### 1.1 Opción A: Usar Blueprint (Recomendado)

```bash
# En Render Dashboard:
# New → Blueprint → Connect GitHub Repo → seleccionar el repo de arepIA
# Render leerá render.yaml y creará todos los servicios automáticamente
```

> **Importante:** Edita `render.yaml` y reemplaza `TU_USUARIO_DOCKER` por tu usuario real de Docker Hub.

### 1.2 Opción B: Creación manual (paso a paso)

#### Paso 1: Crear la base de datos PostgreSQL

```
Dashboard Render → New → PostgreSQL
  Nombre     : arepia-db
  Region     : Oregon (US West)
  Plan       : Free
  DB Name    : arepia
  DB User    : arepia_user
```

> Guarda el **Internal Database URL** — lo usarás como `DATABASE_URL` del backend.

#### Paso 2: Crear Web Service — Backend

```
Dashboard Render → New → Web Service
  Nombre         : arepia-backend
  Runtime        : Docker Image
  Image URL      : docker.io/TU_USUARIO/arepia-backend:latest
  Region         : Oregon
  Plan           : Free
  Puerto         : 8000
  Health Check   : /
```

**Variables de entorno del backend:**
```
DATABASE_URL     = [Internal Database URL de arepia-db]
PYTHONUNBUFFERED = 1
ENVIRONMENT      = production
PORT             = 8000
```

> Copia el **Service ID** de la URL del dashboard: `https://dashboard.render.com/web/srv-XXXXXXXXXX`
> → Guárdalo como `RENDER_SERVICE_ID_BACKEND`

#### Paso 3: Crear Web Service — Frontend

```
Dashboard Render → New → Web Service
  Nombre         : arepia-frontend
  Runtime        : Docker Image
  Image URL      : docker.io/TU_USUARIO/arepia-frontend:latest
  Region         : Oregon
  Plan           : Free
  Puerto         : 80
  Health Check   : /health
```

**Variables de entorno del frontend:**
```
BACKEND_URL = https://arepia-backend.onrender.com
```

> Copia el **Service ID**: `srv-YYYYYYYYYY`
> → Guárdalo como `RENDER_SERVICE_ID_FRONTEND`

---

## FASE 2 — Configurar Jenkins

### 2.1 Plugins requeridos

En **Manage Jenkins → Manage Plugins → Available**, instala:

| Plugin | Propósito |
|---|---|
| Pipeline | Soporte a Jenkinsfile declarativo |
| Docker Pipeline | Comandos `docker` en pipeline |
| Git | Checkout desde GitHub |
| Credentials Binding | Inyección segura de secretos |
| GitHub Integration | Webhooks automáticos |
| HTML Publisher | Reportes de cobertura (opcional) |

### 2.2 Configurar credenciales

Ve a: **Manage Jenkins → Credentials → System → Global credentials → Add Credential**

Crea las siguientes credenciales con exactamente estos IDs:

| Credential ID | Tipo | Valor |
|---|---|---|
| `docker-registry-url` | Secret text | `docker.io` |
| `docker-username` | Secret text | Tu usuario de Docker Hub |
| `docker-password` | Secret text | Tu token de acceso de Docker Hub |
| `github-repo` | Secret text | `tu-usuario/arepIA` (usuario/repo) |
| `github-token` | Secret text | Personal Access Token de GitHub |
| `github-credentials` | Username + Password | user=tu-usuario, pass=PAT de GitHub |
| `render-api-key` | Secret text | API Key de Render (ver abajo) |
| `render-service-id-backend` | Secret text | `srv-XXXXXXXXXX` |
| `render-service-id-frontend` | Secret text | `srv-YYYYYYYYYY` |
| `render-backend-url` | Secret text | `https://arepia-backend.onrender.com` |
| `render-frontend-url` | Secret text | `https://arepia-frontend.onrender.com` |

**Cómo obtener el API Key de Render:**
```
Render Dashboard → Account Settings → API Keys → Create API Key
```

**Cómo obtener un PAT de GitHub:**
```
GitHub → Settings → Developer Settings → Personal access tokens → Tokens (classic)
Permisos requeridos: repo, admin:repo_hook
```

### 2.3 Crear el Pipeline Job

1. **New Item** → Nombre: `arepIA-pipeline` → Tipo: **Pipeline** → OK
2. En la sección **Build Triggers**: marcar ✅ **GitHub hook trigger for GITScm polling**
3. En la sección **Pipeline**:
   - Definition: **Pipeline script from SCM**
   - SCM: **Git**
   - Repository URL: `https://github.com/TU_USUARIO/arepIA.git`
   - Credentials: `github-credentials`
   - Branch: `*/main`
   - Script Path: `Jenkinsfile` ← (si el repo tiene arepIA/ como raíz)
     > Si el Jenkinsfile está en subcarpeta, usa: `arepIA/Jenkinsfile`
4. **Save**

### 2.4 Configurar Webhook en GitHub

```
GitHub Repo → Settings → Webhooks → Add webhook
  Payload URL  : http://TU_SERVIDOR_JENKINS:8080/github-webhook/
  Content type : application/json
  Events       : Just the push event
  Active       : ✅
```

> Si Jenkins no es accesible desde internet, usa **ngrok** para exponer el puerto:
> ```bash
> ngrok http 8080
> # Usa la URL de ngrok como Payload URL
> ```

---

## FASE 3 — Primer Deploy

### 3.1 Entrenar el modelo ML (si no existe)

```bash
cd arepIA
python ml/train_model.py
# Genera: ml/model.joblib
```

### 3.2 Construir y verificar imágenes localmente

```bash
cd arepIA

# Backend
docker build -f Dockerfile.backend -t arepia-backend:local .
docker run -p 8000:8000 arepia-backend:local
curl http://localhost:8000/
# Respuesta esperada: {"message": "ArepIA API funcionando", "docs": "/docs"}

# Frontend
docker build -f Dockerfile.frontend -t arepia-frontend:local .
docker run -p 8080:80 arepia-frontend:local
curl http://localhost:8080/health
# Respuesta esperada: healthy
```

### 3.3 Ejecutar el pipeline en Jenkins

```
Jenkins → arepIA-pipeline → Build with Parameters
  DEPLOY_ENV  : dev
  SKIP_TESTS  : false (marcar solo si necesitas acelerar el primer deploy)
→ Build
```

### 3.4 Monitorear el pipeline

```
Jenkins → arepIA-pipeline → #1 → Console Output
```

Verás la secuencia:
```
🔄 Clonando repositorio...
🏗️  Construyendo imagen Backend...
🏗️  Construyendo imagen Frontend...
🧪 Ejecutando tests...
🔍 Analizando código...
📤 Subiendo imágenes a Docker Hub...
🚀 Desplegando a Render...
🏥 Health Check...
✅ Pipeline completado exitosamente
```

---

## FASE 4 — Verificar el despliegue

```bash
# API Backend
curl https://arepia-backend.onrender.com/
# → {"message": "ArepIA API funcionando", "docs": "/docs"}

# Documentación interactiva
open https://arepia-backend.onrender.com/docs

# Frontend
open https://arepia-frontend.onrender.com

# Test endpoint de inventario
curl -X GET https://arepia-backend.onrender.com/inventario
```

---

## 🔄 Flujo de Trabajo Diario (después del setup)

```bash
# 1. Desarrollar y hacer commit
git add .
git commit -m "feat: nueva funcionalidad"
git push origin main

# 2. GitHub dispara el webhook → Jenkins inicia automáticamente
# 3. El pipeline construye, testea y despliega
# 4. Verificar en: https://arepia-backend.onrender.com
```

---

## 📊 Stages del Pipeline

| Stage | Descripción | Condición |
|---|---|---|
| Checkout | Clona el repo desde GitHub | Siempre |
| Build Backend | Construye imagen Docker del backend | Siempre |
| Build Frontend | Construye imagen Docker del frontend | Siempre |
| Test Backend | Ejecuta pytest con cobertura | Si `SKIP_TESTS=false` |
| Code Analysis | flake8 linting | Siempre |
| Push to Registry | Sube imágenes a Docker Hub | Siempre |
| Deploy to Dev | Deploy automático | Si `DEPLOY_ENV=dev` |
| Deploy to Staging | Deploy con aprobación manual | Si `DEPLOY_ENV=staging` |
| Deploy to Production | Deploy con aprobación (solo rama main) | Si `DEPLOY_ENV=prod` |
| Health Check | Verifica `/` (backend) y `/health` (frontend) | Siempre |

---

## 🆘 Troubleshooting

### Error: "docker: permission denied"
```bash
sudo usermod -aG docker jenkins
sudo systemctl restart jenkins
```

### Error: "credentials not found"
Verifica que los IDs en Jenkins coincidan exactamente con los del Jenkinsfile:
- `docker-username`, `docker-password`, `docker-registry-url`
- `github-repo`, `github-token`, `github-credentials`
- `render-api-key`, `render-service-id-backend`, `render-service-id-frontend`
- `render-backend-url`, `render-frontend-url`

### Error: "model.joblib not found" en la imagen Docker
```bash
cd arepIA
python ml/train_model.py   # Genera el modelo
# Luego vuelve a ejecutar el pipeline
```

### Backend no inicia en Render (SQLite → PostgreSQL)
El `database.py` detecta automáticamente el tipo de DB:
```python
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./arepIA.db")
```
Asegúrate de que la variable `DATABASE_URL` esté configurada en Render con la URL de PostgreSQL.

### Render plan free — tiempo de arranque lento
El plan Free hace "spin down" después de 15 min de inactividad.
El primer request puede tardar 30-60 segundos. Es normal.

### Frontend no conecta al backend en producción
El `nginx.conf` hace proxy de `/api/` a `http://backend:8000` (para docker-compose local).
En Render, los servicios son independientes. El frontend debe usar la URL pública del backend.
El `app.js` del frontend debe leer la variable de entorno `BACKEND_URL` o usar una URL absoluta.

---

## 📚 Referencias

- [Jenkins Pipeline Syntax](https://www.jenkins.io/doc/book/pipeline/syntax/)
- [Docker Hub](https://hub.docker.com)
- [Render Docs — Blueprint](https://render.com/docs/blueprint-spec)
- [Render Docs — Deploy API](https://api-docs.render.com/reference/create-deploy)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

**Versión**: 2.0 — Actualizado con correcciones de producción
