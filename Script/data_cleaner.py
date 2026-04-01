# Limpia y procesa datos de propiedades
import pandas as pd

def eliminar_nulos(df):
    # Eliminar filas sin datos en columnas importantes
    columnas_importantes = ['Baths', 'Built Area', 'Total Area']
    return df.dropna(subset=columnas_importantes)

def filtrar_outliers(df):
    # Filtrar areas realistas (20-5000 m2) y precios realistas (>200 UF)
    df_filtrado = df.copy()
    df_filtrado = df_filtrado[(df_filtrado['Total Area'] >= 20) &
                             (df_filtrado['Total Area'] <= 5000)]
    df_filtrado = df_filtrado[df_filtrado['Price_UF'] > 200]
    return df_filtrado

def arreglar_tipos(df):
    # Convertir decimales a enteros: 2.0 → 2
    df_limpio = df.copy()

    if 'Baths' in df_limpio.columns:
        df_limpio['Baths'] = df_limpio['Baths'].fillna(1).astype(int)

    if 'Dorms' in df_limpio.columns:
        df_limpio['Dorms'] = df_limpio['Dorms'].fillna(1).astype(int)

    if 'Parking' in df_limpio.columns:
        df_limpio['Parking'] = df_limpio['Parking'].fillna(0).astype(int)

    return df_limpio

def limpiar_datos(df):
    # Proceso completo de limpieza
    filas_originales = df.shape[0]

    # 1. Quitar nulos
    df = eliminar_nulos(df)

    # 2. Filtrar outliers
    df = filtrar_outliers(df)

    # 3. Arreglar tipos de datos
    df = arreglar_tipos(df)

    # Mostrar resumen
    filas_finales = df.shape[0]
    eliminadas = filas_originales - filas_finales
    print(f"    {filas_originales} → {filas_finales} filas ({eliminadas} eliminadas)")

    return df

