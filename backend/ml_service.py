import os
import joblib
import pandas as pd
from datetime import date

# ── Resolución de ruta del modelo ─────────────────────────────────────────────
# El script puede ejecutarse desde:
#   - Docker (/app/ml_service.py)      → modelo en /app/ml/model.joblib
#   - Local  (backend/ml_service.py)   → modelo en repo_root/ml/model.joblib
#
# Estrategia: buscar en el directorio del archivo primero, luego un nivel arriba.
_file_dir = os.path.dirname(os.path.abspath(__file__))
_candidate_same_level   = os.path.join(_file_dir, "ml", "model.joblib")
_candidate_parent_level = os.path.join(os.path.dirname(_file_dir), "ml", "model.joblib")
_default_model_path = (
    _candidate_same_level
    if os.path.exists(_candidate_same_level)
    else _candidate_parent_level
)
MODEL_PATH = os.getenv("MODEL_PATH", _default_model_path)

def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    return model

# Mapa clima → temperatura aproximada (Colombia, zona cafetera/ciudades principales)
_TEMP_POR_CLIMA = {
    "soleado":  28,
    "templado": 22,
    "nublado":  17,
    "lluvioso": 13,
}


def construir_features(fecha: date, clima: str, es_festivo: bool):
    dia_semana = fecha.weekday()  # 0=lunes … 6=domingo
    # Temperatura estimada según clima (mejora la predicción vs. valor fijo)
    temperatura_aprox = _TEMP_POR_CLIMA.get(clima.lower(), 18)

    df = pd.DataFrame([{
        "temperatura": temperatura_aprox,
        "es_festivo": 1 if es_festivo else 0,
        "dia_semana": dia_semana
    }])
    return df

def predecir_ventas(fecha: date, clima: str, es_festivo: bool):
    model = cargar_modelo()
    if model is None:
        return None

    X = construir_features(fecha, clima, es_festivo)
    pred = model.predict(X)[0]
    return max(0, float(pred))
