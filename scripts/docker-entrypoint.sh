#!/bin/sh
# =============================================================================
# Docker Entrypoint para el Frontend (Nginx)
# Inyecta la variable de entorno BACKEND_URL en el archivo de configuración
# de JavaScript antes de que Nginx arranque.
# =============================================================================

set -e

# Valor por defecto si no se provee la variable de entorno
BACKEND_URL="${BACKEND_URL:-http://localhost:8000}"

echo "🔧 Configurando frontend..."
echo "   BACKEND_URL = ${BACKEND_URL}"

# Reemplazar el placeholder en env-config.js con el valor real de la variable de entorno
# El archivo /usr/share/nginx/html/env-config.js contiene: BACKEND_URL_PLACEHOLDER
sed -i "s|BACKEND_URL_PLACEHOLDER|${BACKEND_URL}|g" /usr/share/nginx/html/env-config.js

echo "✅ Configuración de frontend lista"
echo "   Iniciando Nginx..."

# Ejecutar el comando original de Nginx
exec "$@"
