import pandas as pd
import numpy as np
from sklearn.cluster import KMeans
from sklearn.neighbors import KNeighborsRegressor
from sklearn.preprocessing import StandardScaler
from sklearn.model_selection import train_test_split
from sklearn.metrics import mean_absolute_error, r2_score
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

def clustering_propiedades():
    """K-Means para agrupar propiedades similares"""
    print("CLUSTERING DE PROPIEDADES")
    print("=" * 30)

    # Cargar datos
    df = pd.read_csv('../data/processed/casas_rm_integrated.csv')

    # Variables para agrupar
    features = ['Built Area', 'Total Area', 'Dorms', 'Baths', 'Price_UF']
    X = df[features]

    # Normalizar datos
    scaler = StandardScaler()
    X_scaled = scaler.fit_transform(X)

    # K-Means con 4 grupos
    kmeans = KMeans(n_clusters=4, random_state=42)
    clusters = kmeans.fit_predict(X_scaled)

    # Agregar clusters al DataFrame
    df['Grupo'] = clusters

    # Ver caracteristicas de cada grupo
    for i in range(4):
        grupo = df[df['Grupo'] == i]
        print(f"\nGrupo {i+1}: {len(grupo)} propiedades")
        print(f"  Precio promedio: {grupo['Price_UF'].mean():.0f} UF")
        print(f"  Area promedio: {grupo['Built Area'].mean():.0f} m2")
        print(f"  Dorms promedio: {grupo['Dorms'].mean():.1f}")

    # Guardar
    joblib.dump(kmeans, '../models/trained_models/kmeans.pkl')
    df.to_csv('../results/metrics/propiedades_grupos.csv', index=False)

    return df

def modelo_knn():
    """KNN para predecir precios"""
    print("\nMODELO KNN")
    print("=" * 15)

    # Cargar datos
    df = pd.read_csv('../data/processed/casas_rm_integrated.csv')

    # Features y target
    features = ['Built Area', 'Total Area', 'Dorms', 'Baths', 'Parking']
    X = df[features]
    y = df['Price_UF']

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Normalizar
    scaler = StandardScaler()
    X_train_scaled = scaler.fit_transform(X_train)
    X_test_scaled = scaler.transform(X_test)

    # KNN con k=5
    knn = KNeighborsRegressor(n_neighbors=5)
    knn.fit(X_train_scaled, y_train)

    # Predecir
    y_pred = knn.predict(X_test_scaled)

    # Evaluar
    r2 = r2_score(y_test, y_pred)
    mae = mean_absolute_error(y_test, y_pred)

    print(f"R2: {r2:.3f}")
    print(f"Error promedio: {mae:.0f} UF")

    # Guardar
    joblib.dump(knn, '../models/trained_models/knn.pkl')
    joblib.dump(scaler, '../models/trained_models/scaler_knn.pkl')

    return knn, X_test, y_test, y_pred

if __name__ == "__main__":
    df_grupos = clustering_propiedades()
    knn_model, X_test, y_test, y_pred = modelo_knn()