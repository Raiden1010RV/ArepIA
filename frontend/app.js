/**
 * ArepIA - Frontend JavaScript
 * Sistema de Gestión Inteligente de Producción de Arepas
 *
 * API_URL se lee desde env-config.js (inyectado por Docker en runtime).
 * Fallback a localhost:8000 para desarrollo local sin Docker.
 */

// ── Configuración dinámica de la URL del backend ──────────────────────────
const API_URL = (window.APP_CONFIG && window.APP_CONFIG.API_URL &&
                 window.APP_CONFIG.API_URL !== 'BACKEND_URL_PLACEHOLDER')
  ? window.APP_CONFIG.API_URL
  : 'http://localhost:8000';

const CONFIG = {
  API_URL,
  STORAGE_KEY: 'arepIA_data'
};

const APP_STATE = {
  inventario: [],
  ventas: [],
  variables: [],
  predicciones: [],
  activeTab: 'dashboard',
  backendOnline: false
};

// ── Helpers HTTP ────────────────────────────────────────────────────────────
async function apiGet(path) {
  const res = await fetch(`${CONFIG.API_URL}${path}`);
  if (!res.ok) throw new Error(`GET ${path} → HTTP ${res.status}`);
  return res.json();
}

async function apiPost(path, body) {
  const res = await fetch(`${CONFIG.API_URL}${path}`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(body)
  });
  if (!res.ok) {
    const err = await res.text();
    throw new Error(`POST ${path} → HTTP ${res.status}: ${err}`);
  }
  return res.json();
}

// ── Verificar conexión con el backend ───────────────────────────────────────
async function checkBackendStatus() {
  try {
    await apiGet('/');
    APP_STATE.backendOnline = true;
    const dot = document.querySelector('.status-dot');
    const label = document.getElementById('systemStatus');
    if (dot) dot.style.background = '#06D6A0';
    if (label) label.textContent = 'Backend Conectado';
    console.log(`✅ Backend conectado en: ${CONFIG.API_URL}`);
  } catch (e) {
    APP_STATE.backendOnline = false;
    const dot = document.querySelector('.status-dot');
    const label = document.getElementById('systemStatus');
    if (dot) dot.style.background = '#EF476F';
    if (label) label.textContent = 'Modo Offline';
    console.warn(`⚠️ Backend no disponible (${CONFIG.API_URL}). Usando datos locales.`);
  }
}

// ========== INICIALIZACIÓN ==========
document.addEventListener('DOMContentLoaded', async function () {
  console.log(`🥖 ArepIA v1.0 — Backend: ${CONFIG.API_URL}`);

  initializeEventListeners();
  await checkBackendStatus();

  if (APP_STATE.backendOnline) {
    await loadInventarioFromAPI();
  } else {
    loadDataFromStorage();
  }

  showTab('dashboard');
  updateMetrics();
  renderChartDefault();

  console.log('✅ ArepIA lista');
});

// ========== NAVEGACIÓN ==========
function initializeEventListeners() {
  document.querySelectorAll('.nav-item').forEach(button => {
    button.addEventListener('click', function () {
      showTab(this.getAttribute('data-tab'));
    });
  });

  document.getElementById('ingredienteForm')?.addEventListener('submit', handleAddIngredient);
  document.getElementById('ventaForm')?.addEventListener('submit', handleAddVenta);
  document.getElementById('prediccionForm')?.addEventListener('submit', handlePrediction);
  document.getElementById('variablesForm')?.addEventListener('submit', handleAddVariable);
}

function showTab(tabName) {
  document.querySelectorAll('.tab-content').forEach(tab => tab.classList.remove('active'));
  document.querySelectorAll('.nav-item').forEach(btn => {
    btn.classList.remove('active');
    if (btn.getAttribute('data-tab') === tabName) btn.classList.add('active');
  });
  const selectedTab = document.getElementById(tabName + 'Tab');
  if (selectedTab) selectedTab.classList.add('active');
  APP_STATE.activeTab = tabName;
}

// ========== INVENTARIO ==========
async function loadInventarioFromAPI() {
  try {
    const data = await apiGet('/inventario');
    APP_STATE.inventario = data;
    renderInventario();
    console.log(`📦 Inventario cargado desde API: ${data.length} items`);
  } catch (e) {
    console.warn('No se pudo cargar inventario desde la API:', e.message);
    loadDataFromStorage();
  }
}

async function handleAddIngredient(e) {
  e.preventDefault();
  const nombre = document.getElementById('ingredienteName').value.trim();
  const cantidad = parseFloat(document.getElementById('ingredienteCantidad').value);
  const unidad = document.getElementById('ingredienteUnidad').value;

  if (!nombre || !cantidad || cantidad <= 0) {
    showToast('Por favor completa todos los campos correctamente', 'error');
    return;
  }

  const payload = { ingrediente: nombre, cantidad_actual: cantidad, unidad };

  if (APP_STATE.backendOnline) {
    try {
      const saved = await apiPost('/inventario', payload);
      APP_STATE.inventario.push(saved);
      showToast(`✅ Ingrediente "${nombre}" guardado en el servidor`, 'success');
    } catch (err) {
      console.error('Error al guardar en API:', err.message);
      showToast(`⚠️ Error al guardar en servidor. Guardado localmente.`, 'error');
      APP_STATE.inventario.push({ id: Date.now(), ...payload });
      saveDataToStorage();
    }
  } else {
    APP_STATE.inventario.push({ id: Date.now(), ...payload });
    saveDataToStorage();
    showToast(`✅ Ingrediente "${nombre}" guardado localmente`, 'success');
  }

  renderInventario();
  e.target.reset();
}

function renderInventario() {
  const tbody = document.getElementById('inventarioBody');
  if (!tbody) return;

  if (APP_STATE.inventario.length === 0) {
    tbody.innerHTML = '<tr class="empty-state"><td colspan="5">Sin ingredientes registrados</td></tr>';
    return;
  }

  tbody.innerHTML = APP_STATE.inventario.map(item => {
    const estado = item.cantidad_actual < 10 ? '⚠️ Bajo' : '✅ OK';
    const estadoColor = item.cantidad_actual < 10 ? 'color:#EF476F' : 'color:#06D6A0';
    return `<tr>
      <td>${item.ingrediente}</td>
      <td>${item.cantidad_actual}</td>
      <td>${item.unidad}</td>
      <td style="${estadoColor}">${estado}</td>
      <td><button onclick="deleteIngredient(${item.id})"
          style="background:#EF476F;color:white;border:none;padding:4px 10px;border-radius:4px;cursor:pointer;font-size:12px;">
          Eliminar
      </button></td>
    </tr>`;
  }).join('');

  updateMetrics();
}

function deleteIngredient(id) {
  APP_STATE.inventario = APP_STATE.inventario.filter(i => i.id !== id);
  saveDataToStorage();
  renderInventario();
  showToast('Ingrediente eliminado localmente', 'success');
}

// ========== VENTAS ==========
async function handleAddVenta(e) {
  e.preventDefault();
  const fecha = document.getElementById('ventaFecha').value;
  const tipo = document.getElementById('ventaTipo').value.trim();
  const cantidad = parseInt(document.getElementById('ventaCantidad').value);
  const precio = parseFloat(document.getElementById('ventaPrecio').value);

  if (!fecha || !tipo || cantidad <= 0 || precio <= 0) {
    showToast('Por favor completa todos los campos correctamente', 'error');
    return;
  }

  const payload = { fecha, tipo_arepa: tipo, cantidad, precio_unitario: precio };

  if (APP_STATE.backendOnline) {
    try {
      await apiPost('/ventas', payload);
      showToast(`✅ Venta registrada en el servidor: ${cantidad} ${tipo}`, 'success');
    } catch (err) {
      console.error('Error al guardar venta en API:', err.message);
      showToast(`⚠️ Error al guardar en servidor. Guardado localmente.`, 'error');
    }
  } else {
    showToast(`✅ Venta registrada localmente: ${cantidad} ${tipo}`, 'success');
  }

  APP_STATE.ventas.push({ id: Date.now(), ...payload, total: cantidad * precio });
  saveDataToStorage();
  renderVentas();
  renderChartDefault();
  e.target.reset();
}

function renderVentas() {
  const tbody = document.getElementById('ventasBody');
  if (!tbody) return;

  if (APP_STATE.ventas.length === 0) {
    tbody.innerHTML = '<tr class="empty-state"><td colspan="5">Sin ventas registradas</td></tr>';
    return;
  }

  tbody.innerHTML = APP_STATE.ventas.map(item => `<tr>
    <td>${item.fecha}</td>
    <td>${item.tipo_arepa}</td>
    <td>${item.cantidad}</td>
    <td>$${parseFloat(item.precio_unitario).toFixed(2)}</td>
    <td><strong>$${parseFloat(item.total).toFixed(2)}</strong></td>
  </tr>`).join('');

  updateMetrics();
}

// ========== PREDICCIÓN IA (llama al backend real) ==========================
async function handlePrediction(e) {
  e.preventDefault();
  const fecha = document.getElementById('predFecha').value;
  const clima = document.getElementById('predClima').value;
  const esFestivo = document.getElementById('predFestivo').checked;

  const btn = e.target.querySelector('button[type="submit"]');
  if (btn) { btn.disabled = true; btn.textContent = '⏳ Consultando IA...'; }

  let prediccion = null;

  if (APP_STATE.backendOnline) {
    try {
      const result = await apiPost('/prediccion', { fecha, clima, es_festivo: esFestivo });
      prediccion = Math.round(result.produccion_recomendada);
      showToast(`🤖 IA recomienda: ${prediccion} arepas para ${fecha}`, 'success');
    } catch (err) {
      console.warn('API de predicción falló, usando cálculo local:', err.message);
      prediccion = calcularPrediccionLocal(clima, esFestivo);
      showToast(`⚠️ Usando predicción local: ${prediccion} arepas`, 'info');
    }
  } else {
    prediccion = calcularPrediccionLocal(clima, esFestivo);
    showToast(`🤖 Predicción local: ${prediccion} arepas para ${fecha}`, 'success');
  }

  if (btn) { btn.disabled = false; btn.textContent = '🤖 Obtener Predicción'; }

  document.getElementById('aiRecommendation').textContent = `${prediccion} arepas`;
  renderChartWithPrediction(fecha, prediccion);
  showTab('dashboard');
}

function calcularPrediccionLocal(clima, esFestivo) {
  let base = 100;
  if (clima === 'soleado') base += 30;
  if (clima === 'lluvioso') base -= 20;
  if (clima === 'nublado') base -= 5;
  if (esFestivo) base += 50;
  return Math.round(base);
}

// ========== VARIABLES EXTERNAS =============================================
async function handleAddVariable(e) {
  e.preventDefault();
  const fecha = document.getElementById('varFecha').value;
  const clima = document.getElementById('varClima').value;
  const esFestivo = document.getElementById('varFestivo').checked;

  if (!fecha) {
    showToast('Selecciona una fecha', 'error');
    return;
  }

  const payload = { fecha, clima, es_festivo: esFestivo };

  if (APP_STATE.backendOnline) {
    try {
      await apiPost('/variables', payload);
      showToast(`✅ Variables del ${fecha} guardadas en el servidor`, 'success');
    } catch (err) {
      console.error('Error al guardar variables en API:', err.message);
      showToast(`⚠️ Error al guardar en servidor. Guardado localmente.`, 'error');
    }
  } else {
    showToast(`✅ Variables del ${fecha} guardadas localmente`, 'success');
  }

  APP_STATE.variables.push({ id: Date.now(), ...payload });
  saveDataToStorage();
  renderVariables();
  e.target.reset();
}

function renderVariables() {
  const tbody = document.getElementById('variablesBody');
  if (!tbody) return;

  if (APP_STATE.variables.length === 0) {
    tbody.innerHTML = '<tr class="empty-state"><td colspan="3">Sin variables registradas</td></tr>';
    return;
  }

  tbody.innerHTML = APP_STATE.variables.map(item => `<tr>
    <td>${item.fecha}</td>
    <td>${item.clima}</td>
    <td>${item.es_festivo ? '🎉 Sí' : 'No'}</td>
  </tr>`).join('');
}

// ========== GRÁFICA =========================================================
function renderChartDefault() {
  const canvas = document.getElementById('chartCanvas');
  if (!canvas) return;
  const dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const produccionBase = [80, 95, 70, 100, 110, 150, 130];
  const prediccionIA = [85, 98, 75, 105, 115, 155, 135];
  drawChart(canvas, dias, produccionBase, prediccionIA);
  document.getElementById('chartEmpty').style.display = 'none';
}

function renderChartWithPrediction(fecha, valor) {
  const canvas = document.getElementById('chartCanvas');
  if (!canvas) return;
  const dias = ['Lun', 'Mar', 'Mié', 'Jue', 'Vie', 'Sáb', 'Dom'];
  const produccionReal = dias.map((d, i) => {
    const venta = APP_STATE.ventas.find((v, j) => j % 7 === i);
    return venta ? venta.cantidad : [80, 95, 70, 100, 110, 150, 130][i];
  });
  const factores = [0.8, 0.95, 0.7, 1.0, 1.1, 1.4, 1.2];
  const prediccion = factores.map(f => Math.round(valor * f));

  APP_STATE.predicciones.push({ fecha, valor, prediccion });
  saveDataToStorage();

  drawChart(canvas, dias, produccionReal, prediccion);
  document.getElementById('chartEmpty').style.display = 'none';
}

function drawChart(canvas, labels, dataReal, dataPrediccion) {
  const ctx = canvas.getContext('2d');
  const W = canvas.width;
  const H = canvas.height;
  const padding = { top: 30, right: 20, bottom: 40, left: 50 };

  ctx.clearRect(0, 0, W, H);

  const allValues = [...dataReal, ...dataPrediccion];
  const maxVal = Math.max(...allValues) * 1.2;
  const minVal = 0;

  const chartW = W - padding.left - padding.right;
  const chartH = H - padding.top - padding.bottom;
  const barW = chartW / labels.length;

  // Fondo
  ctx.fillStyle = '#f8f9fa';
  ctx.fillRect(padding.left, padding.top, chartW, chartH);

  // Líneas guía horizontales
  ctx.strokeStyle = '#e0e0e0';
  ctx.lineWidth = 1;
  for (let i = 0; i <= 4; i++) {
    const y = padding.top + chartH - (i / 4) * chartH;
    ctx.beginPath();
    ctx.moveTo(padding.left, y);
    ctx.lineTo(W - padding.right, y);
    ctx.stroke();
    ctx.fillStyle = '#999';
    ctx.font = '11px Inter, sans-serif';
    ctx.textAlign = 'right';
    ctx.fillText(Math.round((maxVal * i) / 4), padding.left - 5, y + 4);
  }

  // Barras de producción real
  dataReal.forEach((val, i) => {
    const x = padding.left + i * barW + barW * 0.1;
    const barHeight = ((val - minVal) / (maxVal - minVal)) * chartH;
    const y = padding.top + chartH - barHeight;
    ctx.fillStyle = 'rgba(255, 107, 53, 0.7)';
    ctx.fillRect(x, y, barW * 0.35, barHeight);
  });

  // Línea de predicción IA
  ctx.beginPath();
  ctx.strokeStyle = '#004E89';
  ctx.lineWidth = 2.5;
  ctx.setLineDash([5, 3]);
  dataPrediccion.forEach((val, i) => {
    const x = padding.left + i * barW + barW * 0.5;
    const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
    if (i === 0) ctx.moveTo(x, y);
    else ctx.lineTo(x, y);
  });
  ctx.stroke();
  ctx.setLineDash([]);

  // Puntos en línea predicción
  dataPrediccion.forEach((val, i) => {
    const x = padding.left + i * barW + barW * 0.5;
    const y = padding.top + chartH - ((val - minVal) / (maxVal - minVal)) * chartH;
    ctx.beginPath();
    ctx.arc(x, y, 4, 0, Math.PI * 2);
    ctx.fillStyle = '#004E89';
    ctx.fill();
  });

  // Etiquetas eje X
  ctx.fillStyle = '#555';
  ctx.font = '12px Inter, sans-serif';
  ctx.textAlign = 'center';
  labels.forEach((label, i) => {
    const x = padding.left + i * barW + barW * 0.5;
    ctx.fillText(label, x, H - padding.bottom + 18);
  });

  // Título
  ctx.fillStyle = '#333';
  ctx.font = 'bold 13px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Arepas', 5, padding.top + 10);

  // Leyenda
  const legendX = W - padding.right - 200;
  const legendY = padding.top - 15;
  ctx.fillStyle = 'rgba(255, 107, 53, 0.7)';
  ctx.fillRect(legendX, legendY, 14, 14);
  ctx.fillStyle = '#333';
  ctx.font = '11px Inter, sans-serif';
  ctx.textAlign = 'left';
  ctx.fillText('Producción Real', legendX + 18, legendY + 11);

  ctx.strokeStyle = '#004E89';
  ctx.lineWidth = 2;
  ctx.setLineDash([4, 2]);
  ctx.beginPath();
  ctx.moveTo(legendX + 100, legendY + 7);
  ctx.lineTo(legendX + 114, legendY + 7);
  ctx.stroke();
  ctx.setLineDash([]);
  ctx.fillStyle = '#333';
  ctx.fillText('Predicción IA', legendX + 118, legendY + 11);
}

// ========== MÉTRICAS =========================================================
function updateMetrics() {
  const totalProd = APP_STATE.ventas.reduce((s, v) => s + v.cantidad, 0);
  const totalRev  = APP_STATE.ventas.reduce((s, v) => s + v.total, 0);
  const totalItems = APP_STATE.inventario.length;
  const lowStock   = APP_STATE.inventario.filter(i => i.cantidad_actual < 10).length;

  const el = id => document.getElementById(id);
  if (el('totalProduction')) el('totalProduction').textContent = totalProd;
  if (el('todayProduction'))  el('todayProduction').textContent = totalProd;
  if (el('totalRevenue'))     el('totalRevenue').textContent = `$${totalRev.toFixed(2)}`;
  if (el('totalItems'))       el('totalItems').textContent = totalItems;
  if (el('lowStock'))         el('lowStock').textContent = lowStock;
}

// ========== ALMACENAMIENTO LOCAL =============================================
function saveDataToStorage() {
  try {
    localStorage.setItem(CONFIG.STORAGE_KEY, JSON.stringify({
      inventario:   APP_STATE.inventario,
      ventas:       APP_STATE.ventas,
      variables:    APP_STATE.variables,
      predicciones: APP_STATE.predicciones
    }));
  } catch (e) {
    console.warn('No se pudo guardar en localStorage:', e.message);
  }
}

function loadDataFromStorage() {
  try {
    const stored = localStorage.getItem(CONFIG.STORAGE_KEY);
    if (stored) {
      const data = JSON.parse(stored);
      APP_STATE.inventario   = data.inventario   || [];
      APP_STATE.ventas       = data.ventas       || [];
      APP_STATE.variables    = data.variables    || [];
      APP_STATE.predicciones = data.predicciones || [];
      renderInventario();
      renderVentas();
      renderVariables();
      console.log('📂 Datos cargados del almacenamiento local');
    }
  } catch (e) {
    console.warn('No se pudo leer localStorage:', e.message);
  }
}

// ========== NOTIFICACIONES ===================================================
function showToast(message, type = 'info') {
  const toast = document.createElement('div');
  toast.textContent = message;
  const colors = { success: '#06D6A0', error: '#EF476F', info: '#1AC8ED' };
  toast.style.cssText = `
    position:fixed;bottom:20px;right:20px;padding:14px 20px;
    background:${colors[type] || colors.info};color:white;border-radius:8px;
    box-shadow:0 8px 24px rgba(0,0,0,0.15);z-index:1000;
    font-family:Inter,sans-serif;font-size:14px;max-width:350px;
    animation:fadeInUp 0.3s ease;
  `;
  document.body.appendChild(toast);
  setTimeout(() => toast.remove(), 3500);
}

// ── Exponer funciones globales ──────────────────────────────────────────────
window.deleteIngredient = deleteIngredient;
window.showTab = showTab;

console.log(`🥖 ArepIA v1.0 cargado — API: ${CONFIG.API_URL}`);
