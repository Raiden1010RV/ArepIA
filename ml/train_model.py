import pandas as pd
from sklearn.linear_model import LinearRegression
import joblib
import os

DATASET_PATH = os.getenv("DATASET_PATH", "dataset_example.csv")
MODEL_PATH = os.getenv("MODEL_PATH", "model.joblib")

print(f"DEBUG: Buscando dataset en: {os.path.abspath(DATASET_PATH)}")
print(f"DEBUG: Archivos en carpeta actual: {os.listdir('.')}")

def main():
    df = pd.read_csv(DATASET_PATH)

    X = df[["temperatura", "es_festivo", "dia_semana"]]
    y = df["ventas_totales"]

    model = LinearRegression()
    model.fit(X, y)

    dir_name = os.path.dirname(MODEL_PATH)
    if dir_name != "":
        os.makedirs(dir_name, exist_ok=True)
    joblib.dump(model, MODEL_PATH)
    print(f"Modelo entrenado y guardado en {MODEL_PATH}")

if __name__ == "__main__":
    main()
