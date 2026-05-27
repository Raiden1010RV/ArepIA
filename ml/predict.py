import joblib
import pandas as pd

MODEL_PATH = "./ml/model.joblib"

def main():
    model = joblib.load(MODEL_PATH)
    X_test = pd.DataFrame([{
        "temperatura": 18,
        "es_festivo": 0,
        "dia_semana": 4
    }])
    pred = model.predict(X_test)[0]
    print(f"Predicción de ventas: {pred}")

if __name__ == "__main__":
    main()
