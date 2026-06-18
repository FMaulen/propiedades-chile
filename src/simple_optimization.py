import pandas as pd
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import json

def simple_optimization():
    """Optimizacion simple del Random Forest"""
    print("OPTIMIZANDO RANDOM FOREST")
    print("=" * 30)

    # Cargar datos
    df = pd.read_csv('../data/processed/casas_rm_integrated.csv')

    # Solo usar features numericas (sin Comuna para evitar problemas)
    features = ['Built Area', 'Total Area', 'Dorms', 'Baths', 'Parking']
    X = df[features]
    y = df['Price_UF']

    # Split datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modelo original
    rf_original = RandomForestRegressor(n_estimators=100, random_state=42)
    rf_original.fit(X_train, y_train)
    y_pred_original = rf_original.predict(X_test)
    r2_original = r2_score(y_test, y_pred_original)

    print(f"Modelo original: R2 = {r2_original:.3f}")

    # Modelo optimizado manualmente
    rf_optimized = RandomForestRegressor(
        n_estimators=200,
        max_depth=20,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42
    )

    rf_optimized.fit(X_train, y_train)
    y_pred_optimized = rf_optimized.predict(X_test)

    r2_optimized = r2_score(y_test, y_pred_optimized)
    mae_optimized = mean_absolute_error(y_test, y_pred_optimized)

    print(f"Modelo optimizado: R2 = {r2_optimized:.3f}")
    print(f"MAE optimizado: {mae_optimized:.2f} UF")
    print(f"Mejora: +{r2_optimized - r2_original:.3f}")

    # Guardar modelo optimizado
    joblib.dump(rf_optimized, '../models/trained_models/forest_optimized.pkl')

    # Guardar resultados
    results = {
        'r2_original': float(r2_original),
        'r2_optimized': float(r2_optimized),
        'mae_optimized': float(mae_optimized),
        'mejora': float(r2_optimized - r2_original)
    }

    with open('../results/metrics/optimization_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Optimizacion completa")

if __name__ == "__main__":
    simple_optimization()