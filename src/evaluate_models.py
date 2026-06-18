import pandas as pd
import numpy as np
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
import joblib
import json
import matplotlib.pyplot as plt
import seaborn as sns

def load_test_data():
    """Cargar datos de prueba"""
    from train_models import load_data, prepare_features
    from sklearn.model_selection import train_test_split

    df = load_data()
    X, y, _, _ = prepare_features(df)

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    return X_test, y_test

def calculate_metrics(y_true, y_pred):
    """Calcular metricas de evaluacion"""
    mae = mean_absolute_error(y_true, y_pred)
    mse = mean_squared_error(y_true, y_pred)
    rmse = np.sqrt(mse)
    r2 = r2_score(y_true, y_pred)

    return {
        'MAE': round(mae, 2),
        'MSE': round(mse, 2),
        'RMSE': round(rmse, 2),
        'R2': round(r2, 3)
    }

def evaluate_all_models():
    """Evaluar todos los modelos entrenados"""
    print("EVALUANDO MODELOS")
    print("=" * 30)

    # Cargar datos de prueba
    X_test, y_test = load_test_data()

    # Modelos a evaluar
    model_names = ['linear', 'forest', 'gradient']
    results = {}

    for name in model_names:
        print(f"\nEvaluando {name}...")

        # Cargar modelo
        model_path = f'../models/trained_models/{name}_model.pkl'
        model = joblib.load(model_path)

        # Predicciones
        y_pred = model.predict(X_test)

        # Calcular metricas
        metrics = calculate_metrics(y_test, y_pred)
        results[name] = metrics

        print(f"  R2: {metrics['R2']}")
        print(f"  MAE: {metrics['MAE']} UF")
        print(f"  RMSE: {metrics['RMSE']} UF")

    # Guardar resultados
    with open('../results/metrics/model_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    # Crear tabla comparativa
    df_results = pd.DataFrame(results).T
    df_results.to_csv('../results/metrics/comparison.csv')

    print("\nRESUMEN COMPARATIVO:")
    print(df_results)

    return results

def create_comparison_plot():
    """Crear grafico de comparacion"""
    # Cargar resultados
    with open('../results/metrics/model_results.json', 'r') as f:
        results = json.load(f)

    # Preparar datos para grafico
    models = list(results.keys())
    r2_scores = [results[model]['R2'] for model in models]

    # Crear grafico
    plt.figure(figsize=(10, 6))
    bars = plt.bar(models, r2_scores, color=['blue', 'green', 'orange'])
    plt.title('Comparacion de Modelos - R2 Score')
    plt.ylabel('R2 Score')
    plt.xlabel('Modelos')
    plt.ylim(0, 1)

    # Agregar valores en las barras
    for bar, score in zip(bars, r2_scores):
        plt.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.01,
                f'{score:.3f}', ha='center', va='bottom')

    plt.tight_layout()
    plt.savefig('../results/plots/model_comparison.png', dpi=300, bbox_inches='tight')
    # plt.show()

if __name__ == "__main__":
    results = evaluate_all_models()
    create_comparison_plot()