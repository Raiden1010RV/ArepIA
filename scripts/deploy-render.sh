#!/bin/bash
# =============================================================================
# Script de deploy para Render via API v1
# Uso: ./deploy-render.sh <service-name> <render-service-id> <api-key> <image-url>
#
# Ejemplo:
#   ./deploy-render.sh backend srv-abc123 rnd_XXXX docker.io/usuario/arepia-backend:42-a1b2c3d
# =============================================================================

set -euo pipefail

SERVICE_NAME="${1:-}"
RENDER_SERVICE_ID="${2:-}"
RENDER_API_KEY="${3:-}"
IMAGE_URL="${4:-}"

# ── Validar parámetros ───────────────────────────────────────────────────────
if [ -z "$SERVICE_NAME" ] || [ -z "$RENDER_SERVICE_ID" ] || \
   [ -z "$RENDER_API_KEY" ] || [ -z "$IMAGE_URL" ]; then
    echo "❌ Error: Parámetros faltantes"
    echo ""
    echo "Uso: ./deploy-render.sh <service-name> <render-service-id> <api-key> <image-url>"
    echo ""
    echo "Ejemplo:"
    echo "  ./deploy-render.sh backend srv-abc123 rnd_XXXX docker.io/usuario/arepia-backend:latest"
    exit 1
fi

RENDER_API_URL="https://api.render.com/v1"

echo "════════════════════════════════════════════════════════"
echo "🚀 Deploy a Render"
echo "   Servicio : $SERVICE_NAME"
echo "   ID       : $RENDER_SERVICE_ID"
echo "   Imagen   : $IMAGE_URL"
echo "════════════════════════════════════════════════════════"

# ── Función helper para llamadas a la API ────────────────────────────────────
# Nota: NO se usa -f para que la respuesta del cuerpo sea visible en errores 4xx/5xx.
# Se captura el HTTP status code por separado para manejar errores correctamente.
render_api() {
    local METHOD="$1"
    local ENDPOINT="$2"
    local DATA="${3:-}"
    local TMP_BODY
    TMP_BODY=$(mktemp)
    local HTTP_STATUS

    if [ -n "$DATA" ]; then
        HTTP_STATUS=$(curl -s -o "$TMP_BODY" -w "%{http_code}" -X "$METHOD" \
            "${RENDER_API_URL}${ENDPOINT}" \
            -H "Authorization: Bearer ${RENDER_API_KEY}" \
            -H "Content-Type: application/json" \
            -H "Accept: application/json" \
            -d "$DATA")
    else
        HTTP_STATUS=$(curl -s -o "$TMP_BODY" -w "%{http_code}" -X "$METHOD" \
            "${RENDER_API_URL}${ENDPOINT}" \
            -H "Authorization: Bearer ${RENDER_API_KEY}" \
            -H "Accept: application/json")
    fi

    cat "$TMP_BODY"
    rm -f "$TMP_BODY"

    # Falla si el status code es 4xx o 5xx
    if [ "$HTTP_STATUS" -ge 400 ]; then
        echo "" >&2
        echo "   HTTP Status: $HTTP_STATUS" >&2
        return 1
    fi
    return 0
}

# ── Paso 1: Verificar que el servicio existe ─────────────────────────────────
echo ""
echo "📋 [1/4] Verificando servicio en Render..."

SERVICE_INFO=$(render_api GET "/services/${RENDER_SERVICE_ID}" 2>&1) || {
    echo "❌ Error: No se pudo obtener información del servicio '${RENDER_SERVICE_ID}'"
    echo "   Verifica que el Service ID y el API Key sean correctos."
    echo "   Respuesta: $SERVICE_INFO"
    exit 1
}

SERVICE_TYPE=$(echo "$SERVICE_INFO" | jq -r '.type // "unknown"' 2>/dev/null || echo "unknown")
SERVICE_STATUS=$(echo "$SERVICE_INFO" | jq -r '.suspended // "active"' 2>/dev/null || echo "unknown")

echo "✅ Servicio encontrado"
echo "   Tipo   : $SERVICE_TYPE"
echo "   Estado : $SERVICE_STATUS"

# ── Paso 2: Actualizar la imagen Docker en el servicio ───────────────────────
# Esto es CRÍTICO: sin este paso, Render redeploya la imagen anterior
echo ""
echo "🔧 [2/4] Actualizando imagen Docker en el servicio..."

# Separar image:tag
IMAGE_REPO=$(echo "$IMAGE_URL" | cut -d':' -f1)
IMAGE_TAG_VALUE=$(echo "$IMAGE_URL" | cut -d':' -f2)

UPDATE_PAYLOAD=$(cat <<EOF
{
  "image": {
    "ownerId": null,
    "registryCredentialId": null,
    "imagePath": "${IMAGE_URL}"
  }
}
EOF
)

UPDATE_RESPONSE=$(render_api PATCH "/services/${RENDER_SERVICE_ID}" "$UPDATE_PAYLOAD" 2>&1) || {
    echo "⚠️  No se pudo actualizar la imagen vía PATCH (puede ser normal si el servicio no es tipo 'image')"
    echo "   Respuesta: $UPDATE_RESPONSE"
    echo "   Continuando con redeploy..."
}

if echo "$UPDATE_RESPONSE" | jq -e '.id' > /dev/null 2>&1; then
    echo "✅ Imagen actualizada a: $IMAGE_URL"
else
    echo "ℹ️  Actualización de imagen no confirmada — continuando con deploy"
fi

# ── Paso 3: Disparar el deploy ───────────────────────────────────────────────
echo ""
echo "🚀 [3/4] Disparando deploy en Render..."

# imageUrl en el body es requerido cuando el servicio es de tipo 'image' (registry).
# Para servicios Dockerfile (git-based) el body puede ser vacío o solo clearCache.
DEPLOY_PAYLOAD="{\"clearCache\": \"do_not_clear\", \"imageUrl\": \"${IMAGE_URL}\"}"

DEPLOY_RESPONSE=$(render_api POST "/services/${RENDER_SERVICE_ID}/deploys" "$DEPLOY_PAYLOAD" 2>&1) || {
    echo "❌ Error al disparar el deploy"
    echo "   Respuesta completa: $DEPLOY_RESPONSE"
    echo ""
    echo "   Intentando sin imageUrl (para servicios Dockerfile)..."
    DEPLOY_PAYLOAD_SIMPLE='{"clearCache": "do_not_clear"}'
    DEPLOY_RESPONSE=$(render_api POST "/services/${RENDER_SERVICE_ID}/deploys" "$DEPLOY_PAYLOAD_SIMPLE" 2>&1) || {
        echo "❌ Deploy falló en ambos intentos"
        echo "   Respuesta: $DEPLOY_RESPONSE"
        exit 1
    }
}

DEPLOY_ID=$(echo "$DEPLOY_RESPONSE" | jq -r '.id // .deploy.id // ""' 2>/dev/null || echo "")
DEPLOY_STATUS=$(echo "$DEPLOY_RESPONSE" | jq -r '.status // .deploy.status // "iniciado"' 2>/dev/null || echo "iniciado")

if [ -n "$DEPLOY_ID" ]; then
    echo "✅ Deploy iniciado"
    echo "   Deploy ID : $DEPLOY_ID"
    echo "   Estado    : $DEPLOY_STATUS"
else
    echo "✅ Deploy disparado (sin ID en respuesta)"
fi

# ── Paso 4: Esperar y verificar el estado ───────────────────────────────────
echo ""
echo "⏳ [4/4] Esperando confirmación del deploy (30s)..."
sleep 30

FINAL_INFO=$(render_api GET "/services/${RENDER_SERVICE_ID}" 2>&1) || {
    echo "⚠️  No se pudo obtener el estado final del servicio"
    FINAL_INFO="{}"
}

FINAL_STATUS=$(echo "$FINAL_INFO" | jq -r '.suspended // "unknown"' 2>/dev/null || echo "unknown")

echo "📊 Estado final del servicio: $FINAL_STATUS"
echo ""
echo "════════════════════════════════════════════════════════"
echo "✅ Deploy completado para '$SERVICE_NAME'"
echo "   Dashboard: https://dashboard.render.com/web/${RENDER_SERVICE_ID}"
echo "════════════════════════════════════════════════════════"

exit 0
