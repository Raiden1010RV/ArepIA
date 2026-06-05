# Configuración de CI/CD con Jenkins y Render

Documentación completa para configurar el pipeline de Jenkins y desplegar la aplicación ArepIA en Render.

## 📋 Archivos Creados

- **Jenkinsfile** - Pipeline principal de CI/CD
- **Dockerfile.backend** - Imagen Docker para FastAPI backend
- **Dockerfile.frontend** - Imagen Docker para frontend con nginx
- **nginx.conf** - Configuración de Nginx
- **scripts/deploy-render.sh** - Script de deployment a Render

## 🔧 Configuración de Jenkins

### 1. Plugins Requeridos

Instala los siguientes plugins en Jenkins:
- Pipeline
- Docker Pipeline
- Git
- Credentials Binding
- Email Extension (opcional, para notificaciones)
- Slack Notification (opcional)

Navega a: **Manage Jenkins** → **Manage Plugins** → **Available** → Buscar e instalar

### 2. Configurar Credenciales

En **Manage Jenkins** → **Manage Credentials** → **System** → **Global credentials**:

#### a) Docker Registry Credentials
- **ID**: `docker-registry-url`
- **Type**: Secret text
- **Secret**: Tu URL del registro (ej: `docker.io`)

- **ID**: `docker-username`
- **Type**: Secret text
- **Secret**: Tu usuario de Docker Hub

- **ID**: `docker-password`
- **Type**: Secret text
- **Secret**: Tu token/contraseña de Docker

#### b) GitHub Token
- **ID**: `github-token`
- **Type**: Secret text
- **Secret**: Token de acceso personal de GitHub

- **ID**: `github-credentials`
- **Type**: Username with password
- **Username**: Tu usuario de GitHub
- **Password**: Tu token de acceso personal

#### c) Render API
- **ID**: `render-api-key`
- **Type**: Secret text
- **Secret**: Tu API key de Render (obtén desde https://dashboard.render.com/account/api-tokens)

- **ID**: `render-service-id-backend`
- **Type**: Secret text
- **Secret**: ID del servicio backend en Render

- **ID**: `render-service-id-frontend`
- **Type**: Secret text
- **Secret**: ID del servicio frontend en Render

### 3. Crear Job en Jenkins

1. Click en **New Item**
2. Nombre: `arepIA-pipeline`
3. Seleccionar **Pipeline**
4. Click **OK**

### 4. Configurar Pipeline

En la sección **Pipeline**:

```groovy
pipeline {
    agent any
    
    options {
        buildDiscarder(logRotator(numToKeepStr: '30'))
    }
    
    triggers {
        githubPush()  // Trigger automático en push
    }
    
    stages {
        stage('Checkout') {
            steps {
                checkout scm
            }
        }
    }
}
```

**Script Path**: `arepIA/Jenkinsfile`

### 5. Configurar Webhook en GitHub

1. Ve a tu repositorio en GitHub
2. **Settings** → **Webhooks** → **Add webhook**
3. **Payload URL**: `http://tu-servidor-jenkins/github-webhook/`
4. **Content type**: `application/json`
5. **Events**: Selecciona "Just the push event"
6. Click **Add webhook**

## 🚀 Pasos de Deployment

### Antes del primer deploy:

1. **Crear servicios en Render**
   - Backend: Web Service (Docker)
   - Frontend: Static Site o Web Service (Docker)

2. **Obtener Service IDs**
   - De la URL: `https://dashboard.render.com/services/{SERVICE_ID}`

3. **Configurar variables de entorno en Render**

### Durante el deploy:

1. El Jenkinsfile automáticamente:
   - ✅ Clona el código
   - ✅ Construye imágenes Docker
   - ✅ Ejecuta tests
   - ✅ Analiza código
   - ✅ Sube imágenes a Docker Hub
   - ✅ Despliega a Render
   - ✅ Verifica salud de la aplicación

## 📊 Stages del Pipeline

| Stage | Descripción | Condición |
|-------|-------------|-----------|
| Checkout | Clona el repo desde GitHub | Siempre |
| Build Backend | Construye imagen Docker del backend | Siempre |
| Build Frontend | Construye imagen Docker del frontend | Siempre |
| Test Backend | Ejecuta tests de Python | Si `SKIP_TESTS` es falso |
| Code Analysis | Linting y análisis de código | Siempre |
| Push to Registry | Sube imágenes a Docker Hub | Siempre |
| Deploy to Dev | Deploy a desarrollo | Si `DEPLOY_ENV=dev` |
| Deploy to Staging | Deploy a staging (requiere aprobación) | Si `DEPLOY_ENV=staging` |
| Deploy to Production | Deploy a producción (requiere aprobación) | Si `DEPLOY_ENV=prod` y branch=main |
| Health Check | Verifica que los servicios estén sanos | Siempre |

## 🔑 Variables de Entorno Requeridas

En el Jenkinsfile o en Render:

```bash
# Backend
DATABASE_URL=postgresql://user:pass@host:5432/db
ENVIRONMENT=production
LOG_LEVEL=info

# Frontend
REACT_APP_API_URL=https://backend.ejemplo.com/api
REACT_APP_ENV=production
```

## 🧪 Testing Localmente

### Construir imágenes localmente:

```bash
# Backend
cd arepIA
docker build -f Dockerfile.backend -t arepIA-backend:latest .

# Frontend
docker build -f Dockerfile.frontend -t arepIA-frontend:latest .
```

### Ejecutar localmente con Docker Compose:

```yaml
# docker-compose.yml
version: '3.8'
services:
  backend:
    image: arepIA-backend:latest
    ports:
      - "8000:8000"
    environment:
      - DATABASE_URL=postgresql://user:pass@db:5432/arepIA
  
  frontend:
    image: arepIA-frontend:latest
    ports:
      - "80:80"
    depends_on:
      - backend
```

```bash
docker-compose up -d
```

## 📝 Logs y Monitoreo

- **Logs de Jenkins**: Dashboard de Jenkins → Build → Console Output
- **Logs de Render**: https://dashboard.render.com/services/{SERVICE_ID}/logs
- **Health checks**: El pipeline verifica automáticamente `/health` endpoints

## 🆘 Troubleshooting

### Error: "Address already in use"
```bash
# Matar procesos en puerto 8000
lsof -i :8000
kill -9 <PID>
```

### Error: Docker: permission denied
```bash
# Agregar usuario a grupo docker
sudo usermod -aG docker $USER
newgrp docker
```

### Deploy falla en Render
1. Verifica que los Service IDs sean correctos
2. Confirma que la API key de Render sea válida
3. Revisa los logs en dashboard.render.com

## 📚 Referencias

- [Jenkins Docs](https://www.jenkins.io/doc/)
- [Docker Docs](https://docs.docker.com/)
- [Render Docs](https://render.com/docs)
- [FastAPI Docs](https://fastapi.tiangolo.com/)

---

**Último actualizado**: 2024-06-04
**Versión**: 1.0
