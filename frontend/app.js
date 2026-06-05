const form = document.getElementById("prediccion-form");
const resultado = document.getElementById("resultado");

// Ajusta la URL del backend según donde corra FastAPI
const BASE_URL = "http://localhost:8000";

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  const fecha = document.getElementById("fecha").value;
  const clima = document.getElementById("clima").value;
  const esFestivo = document.getElementById("es_festivo").checked;

  const body = {
    fecha,
    clima,
    es_festivo: esFestivo
  };

  try {
    const res = await fetch(`${BASE_URL}/prediccion`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    });

    const data = await res.json();
    resultado.textContent = JSON.stringify(data, null, 2);
  } catch (err) {
    resultado.textContent = "Error: " + err;
  }
});
