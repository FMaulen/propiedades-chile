import pandas as pd

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()

    # Eliminar filas con datos criticos faltantes
    df = df.dropna(subset=['Baths', 'Built Area', 'Total Area', 'Dorms']).copy()

    # Imputaciones
    df['Parking'] = df['Parking'].fillna(0)
    df['Realtor'] = df['Realtor'].fillna('Desconocido')

    # Validamos que todos los precios sean sobre 0
    df = df[df['Price_UF'] > 0]
    df = df[df['Parking'] != 0]

    # Dropeamos columnas innecesarias
    cols_to_drop = ['Price_CLP','Price_USD','id','Ubicacion']
    df = df.drop(columns=[col for col in cols_to_drop if col in df.columns])

    # Eliminar duplicados
    df = df.drop_duplicates()

    # Resetear indice
    df.reset_index(drop=True, inplace=True)

    return df