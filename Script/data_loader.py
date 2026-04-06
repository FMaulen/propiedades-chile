# Carga datos desde archivos CSV
import pandas as pd
import os

def cargar_datos():
    # Rutas de los archivos (desde carpeta Script/)

    BASE_DIR = os.path.dirname(os.path.abspath(__file__))

    BASE_ROUTE = os.path.join(BASE_DIR,'..','data','raw')
    archivo1 = os.path.join('..', 'data', 'raw', '2023-03-08 Precios Casas RM.csv')
    archivo2 = os.path.join('..', 'data', 'raw', '2023-07-18 Propiedades Web Scrape.csv')

    try:
        # Cargar ambos datasets
        df1 = pd.read_csv(archivo1)
        df2 = pd.read_csv(archivo2)

        # Mostrar cuantas filas se cargaron
        print(f"    Dataset 1: {df1.shape[0]} filas | Dataset 2: {df2.shape[0]} filas")

        return df1, df2

    except:
        print("    [ERROR] No se pudieron cargar los archivos")
        return None, None