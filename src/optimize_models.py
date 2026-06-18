import pandas as pd
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.ensemble import RandomForestRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.metrics import r2_score, mean_absolute_error
import joblib
import json

def optimize_best_model():
    """Optimizar el Random Forest que gano"""
    print("OPTIMIZANDO RANDOM FOREST")
    print("=" * 30)

    # Cargar datos
    df = pd.read_csv('../data/processed/casas_rm_integrated.csv')

    # Features y target
    numeric_features = ['Built Area', 'Total Area', 'Dorms', 'Baths', 'Parking']
    X = df[numeric_features + ['Comuna']]
    y = df['Price_UF']

    # Split datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Pipeline
    preprocessor = ColumnTransformer([
        ('num', StandardScaler(), numeric_features),
        ('cat', OneHotEncoder(handle_unknown='ignore'), ['Comuna'])
    ])

    pipeline = Pipeline([
        ('prep', preprocessor),
        ('model', RandomForestRegressor(random_state=42))
    ])

    # Parametros a probar
    param_grid = {
        'model__n_estimators': [100, 200, 300],
        'model__max_depth': [10, 20, None],
        'model__min_samples_split': [2, 5]
    }

    print("Buscando mejores parametros...")

    # Grid Search
    grid = GridSearchCV(pipeline, param_grid, cv=3, scoring='r2')
    grid.fit(X_train, y_train)

    # Evaluar
    y_pred = grid.best_estimator_.predict(X_test)
    r2_nuevo = r2_score(y_test, y_pred)
    mae_nuevo = mean_absolute_error(y_test, y_pred)

    print(f"Mejor R2: {r2_nuevo:.3f}")
    print(f"Mejor MAE: {mae_nuevo:.2f} UF")

    # Guardar modelo optimizado
    joblib.dump(grid.best_estimator_, '../models/trained_models/forest_optimized.pkl')

    # Guardar resultados
    results = {
        'best_params': grid.best_params_,
        'r2_score': float(r2_nuevo),
        'mae': float(mae_nuevo)
    }

    with open('../results/metrics/optimization_results.json', 'w') as f:
        json.dump(results, f, indent=2)

    print("Optimizacion completa")

if __name__ == "__main__":
    optimize_best_model()