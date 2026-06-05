import os
import joblib
import pandas as pd
from datetime import date

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MODEL_PATH = os.getenv("MODEL_PATH", os.path.join(BASE_DIR, "ml/model.joblib"))
  # Debug: Verificar la ruta del modelo
def cargar_modelo():
    if not os.path.exists(MODEL_PATH):
        return None
    model = joblib.load(MODEL_PATH)
    return model

def construir_features(fecha: date, clima: str, es_festivo: bool):
    # Codificación muy simple para MVP
    dia_semana = fecha.weekday()  # 0=lunes ... 6=domingo
    temperatura_aprox = 18  # placeholder, podrías traerla de API de clima real

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
