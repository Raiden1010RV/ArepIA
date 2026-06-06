/**
 * env-config.js — Configuración de entorno en runtime
 *
 * Este archivo es modificado automáticamente por scripts/docker-entrypoint.sh
 * al arrancar el contenedor Docker. El placeholder BACKEND_URL_PLACEHOLDER
 * es reemplazado por el valor de la variable de entorno BACKEND_URL.
 *
 * En desarrollo local (sin Docker) usa http://localhost:8000 como fallback.
 */
window.APP_CONFIG = {
  API_URL: 'BACKEND_URL_PLACEHOLDER'
};
