import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
import joblib
import os

def load_data():
    """Cargar datos limpios"""
    df = pd.read_csv('../outputs/datos_procesados/casas_rm_limpio.csv')
    return df

def prepare_features(df):
    """Preparar features para el modelo"""
    # Features numericas
    numeric_features = ['Built Area', 'Total Area', 'Dorms', 'Baths', 'Parking']

    # Features categoricas
    categorical_features = ['Comuna']

    # Target
    X = df[numeric_features + categorical_features]
    y = df['Price_UF']

    return X, y, numeric_features, categorical_features

def create_pipeline(numeric_features, categorical_features, model):
    """Crear pipeline de preprocessing + modelo"""
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', StandardScaler(), numeric_features),
            ('cat', OneHotEncoder(drop='first'), categorical_features)
        ]
    )

    pipeline = Pipeline([
        ('preprocessor', preprocessor),
        ('model', model)
    ])

    return pipeline

def train_models():
    """Entrenar modelos predictivos"""
    print("PREDICTOR DE PRECIOS - ENTRENANDO MODELOS")
    print("=" * 45)

    # Cargar datos
    df = load_data()
    X, y, numeric_features, categorical_features = prepare_features(df)

    print(f"Dataset: {len(df)} propiedades")
    print(f"Features: {len(X.columns)}")

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )

    # Modelos a entrenar
    models = {
        'linear': LinearRegression(),
        'forest': RandomForestRegressor(n_estimators=100, random_state=42),
        'gradient': GradientBoostingRegressor(n_estimators=100, random_state=42)
    }

    trained_models = {}

    print("\nEntrenando modelos...")
    for name, model in models.items():
        print(f"  - {name}...")

        # Crear pipeline
        pipeline = create_pipeline(numeric_features, categorical_features, model)

        # Entrenar
        pipeline.fit(X_train, y_train)

        # Guardar modelo
        model_path = f'../models/trained_models/{name}_model.pkl'
        joblib.dump(pipeline, model_path)

        trained_models[name] = pipeline

    print(f"\nModelos entrenados: {len(trained_models)}")
    return trained_models, X_test, y_test

if __name__ == "__main__":
    models, X_test, y_test = train_models()