import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from sklearn.metrics import confusion_matrix, classification_report
import matplotlib.pyplot as plt
import seaborn as sns
import joblib

def crear_categorias_precio(df):
    """Crear categorias de precio para clasificacion"""
    # Crear rangos de precio
    df['Categoria_Precio'] = pd.cut(df['Price_UF'],
                                   bins=[0, 3000, 6000, 10000, float('inf')],
                                   labels=['Economica', 'Media', 'Alta', 'Premium'])
    return df

def matriz_confusion_precios():
    """Crear matriz de confusion para categorias de precio"""
    print("MATRIZ DE CONFUSION - CATEGORIAS DE PRECIO")
    print("=" * 45)

    # Cargar datos
    df = pd.read_csv('../data/processed/casas_rm_integrated.csv')

    # Crear categorias
    df = crear_categorias_precio(df)

    # Features y target
    features = ['Built Area', 'Total Area', 'Dorms', 'Baths', 'Parking']
    X = df[features]
    y = df['Categoria_Precio']

    # Dividir datos
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Modelo de clasificacion
    rf_classifier = RandomForestClassifier(n_estimators=100, random_state=42)
    rf_classifier.fit(X_train, y_train)

    # Predicciones
    y_pred = rf_classifier.predict(X_test)

    # Matriz de confusion
    cm = confusion_matrix(y_test, y_pred, labels=['Economica', 'Media', 'Alta', 'Premium'])

    print("Distribucion real:")
    print(y_test.value_counts())

    # Crear heatmap
    plt.figure(figsize=(10, 8))
    sns.heatmap(cm,
                annot=True,
                fmt='d',
                cmap='Blues',
                xticklabels=['Economica', 'Media', 'Alta', 'Premium'],
                yticklabels=['Economica', 'Media', 'Alta', 'Premium'])
    plt.title('Matriz de Confusion - Categorias de Precio')
    plt.xlabel('Prediccion')
    plt.ylabel('Real')
    plt.tight_layout()
    plt.savefig('../results/plots/confusion_matrix.png', dpi=300)
    # plt.show()

    # Reporte detallado
    report = classification_report(y_test, y_pred)
    print("\nReporte de clasificacion:")
    print(report)

    # Guardar modelo
    joblib.dump(rf_classifier, '../models/trained_models/classifier.pkl')

    return cm, y_test, y_pred

def simular_cambio_datos():
    """Simular cambio de datos en vivo"""
    print("\nSIMULACION CAMBIO DE DATOS")
    print("=" * 30)

    # Cargar modelo entrenado
    knn = joblib.load('../models/trained_models/knn.pkl')
    scaler = joblib.load('../models/trained_models/scaler_knn.pkl')

    # Ejemplo de casa
    casa_ejemplo = [[120, 150, 3, 2, 1]]  # [Built Area, Total Area, Dorms, Baths, Parking]

    # Prediccion original
    casa_scaled = scaler.transform(casa_ejemplo)
    precio_original = knn.predict(casa_scaled)[0]

    print(f"Casa original: 120m2, 3 dorms, 2 banos")
    print(f"Precio predicho: {precio_original:.0f} UF")

    # Simular cambios
    cambios = [
        [140, 150, 3, 2, 1],  # +20m2
        [120, 150, 4, 2, 1],  # +1 dormitorio
        [120, 150, 3, 3, 1],  # +1 bano
        [120, 150, 3, 2, 2],  # +1 estacionamiento
    ]

    descripciones = [
        "Aumentar 20m2",
        "Agregar 1 dormitorio",
        "Agregar 1 bano",
        "Agregar 1 estacionamiento"
    ]

    print("\nEfecto de cambios:")
    for i, (cambio, desc) in enumerate(zip(cambios, descripciones)):
        cambio_scaled = scaler.transform([cambio])
        nuevo_precio = knn.predict(cambio_scaled)[0]
        diferencia = nuevo_precio - precio_original
        print(f"  {desc}: {nuevo_precio:.0f} UF (+{diferencia:.0f} UF)")

if __name__ == "__main__":
    cm, y_test, y_pred = matriz_confusion_precios()
    simular_cambio_datos()