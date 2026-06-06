#!/bin/sh
# =============================================================================
# Docker Entrypoint para el Frontend (Nginx)
# Inyecta la variable de entorno BACKEND_URL en el archivo de configuración
# de JavaScript antes de que Nginx arranque.
# =============================================================================

set -e

# Valor por defecto:
#   - Docker Compose: el servicio backend se llama 'backend' en la red interna
#   - Render / prod:  set BACKEND_URL=https://arepia-backend.onrender.com
BACKEND_URL="${BACKEND_URL:-http://backend:8000}"

echo "🔧 Configurando frontend..."
echo "   BACKEND_URL = ${BACKEND_URL}"

# 1. Reemplazar el placeholder en env-config.js (usado por el JS del browser)
sed -i "s|BACKEND_URL_PLACEHOLDER|${BACKEND_URL}|g" /usr/share/nginx/html/env-config.js

# 2. Reemplazar el placeholder en nginx.conf (usado por el proxy server-side /api/)
#    BACKEND_PROXY_URL es el placeholder definido en nginx.conf
sed -i "s|BACKEND_PROXY_URL|${BACKEND_URL}|g" /etc/nginx/nginx.conf

echo "✅ Configuración de frontend lista"
echo "   Iniciando Nginx..."

# Ejecutar el comando original de Nginx
exec "$@"
