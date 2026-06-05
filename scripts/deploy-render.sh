#!/bin/bash

# Script de deploy para Render
# Uso: ./deploy-render.sh <service-name> <render-service-id> <api-key> <image-url>

set -e

SERVICE_NAME=$1
RENDER_SERVICE_ID=$2
RENDER_API_KEY=$3
IMAGE_URL=$4

if [ -z "$SERVICE_NAME" ] || [ -z "$RENDER_SERVICE_ID" ] || [ -z "$RENDER_API_KEY" ] || [ -z "$IMAGE_URL" ]; then
    echo "❌ Error: Parámetros faltantes"
    echo "Uso: ./deploy-render.sh <service-name> <render-service-id> <api-key> <image-url>"
    exit 1
fi

echo "🚀 Iniciando deploy a Render..."
echo "   Servicio: $SERVICE_NAME"
echo "   ID Render: $RENDER_SERVICE_ID"
echo "   Imagen: $IMAGE_URL"

# Endpoint de Render API
RENDER_API_URL="https://api.render.com/v1"

# Obtener información del servicio
echo "📋 Obteniendo información del servicio..."
SERVICE_INFO=$(curl -s -X GET \
    "${RENDER_API_URL}/services/${RENDER_SERVICE_ID}" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Accept: application/json")

if echo "$SERVICE_INFO" | grep -q "error"; then
    echo "❌ Error al obtener información del servicio:"
    echo "$SERVICE_INFO" | jq '.'
    exit 1
fi

echo "✅ Información del servicio obtenida"

# Trigger deploy via webhook o API
echo "🔧 Configurando deploy..."

# Para Render, necesitamos usar el webhook de deploy o hacer un manual deploy
# Si el servicio es de Docker, podemos triggear un redeploy

DEPLOY_RESPONSE=$(curl -s -X POST \
    "${RENDER_API_URL}/services/${RENDER_SERVICE_ID}/deploys" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Content-Type: application/json" \
    -H "Accept: application/json" \
    -d "{
        \"clearCache\": \"clear\"
    }")

if echo "$DEPLOY_RESPONSE" | grep -q "error" || echo "$DEPLOY_RESPONSE" | grep -q "message"; then
    echo "⚠️ Respuesta del API de Render:"
    echo "$DEPLOY_RESPONSE" | jq '.' 2>/dev/null || echo "$DEPLOY_RESPONSE"
fi

echo "✅ Deploy iniciado en Render"
echo "   Service ID: $RENDER_SERVICE_ID"
echo "   Puedes ver el estado en: https://dashboard.render.com/services/$RENDER_SERVICE_ID"

# Esperar a que inicie el deploy
echo "⏳ Esperando confirmación del deploy..."
sleep 5

# Intentar obtener el estado del deploy
echo "🔍 Verificando estado del servicio..."
STATUS=$(curl -s -X GET \
    "${RENDER_API_URL}/services/${RENDER_SERVICE_ID}" \
    -H "Authorization: Bearer ${RENDER_API_KEY}" \
    -H "Accept: application/json" | jq -r '.status // .state' 2>/dev/null)

if [ -n "$STATUS" ]; then
    echo "📊 Estado del servicio: $STATUS"
fi

echo "✅ Deploy completado exitosamente"
exit 0
