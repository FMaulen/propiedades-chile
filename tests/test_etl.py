# tests para el pipeline ETL
# verificamos que los datos se limpien bien y que la BD funcione

import pytest
import pandas as pd
import sqlite3
import os

# ruta base del proyecto (subimos un nivel desde tests/)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_RAW = os.path.join(BASE_DIR, "data", "raw")
DB_PATH = os.path.join(BASE_DIR, "data", "comunas.db")


class TestCSVFiles:
    """Tests pa verificar que los archivos CSV existen"""

    def test_csv_files_exist(self):
        """Revisa que haya al menos un CSV en data/raw/"""
        if not os.path.exists(DATA_RAW):
            pytest.skip("No existe la carpeta data/raw/, saltando test")

        archivos_csv = [f for f in os.listdir(DATA_RAW) if f.endswith(".csv")]
        assert len(archivos_csv) > 0, "No hay archivos CSV en data/raw/"


class TestDataCleaning:
    """Tests de limpieza de datos"""

    def test_clean_data_no_nulls(self):
        """Verifica que despues de limpiar no hayan nulls en columnas criticas"""
        # creamos un dataframe de ejemplo simulando datos crudos
        df = pd.DataFrame({
            "Precio_UF": [2500, None, 3200, 4100, None],
            "Superficie_Total": [80, 65, None, 120, 90],
            "Dormitorios": [3, 2, 2, 4, None],
            "Banos": [2, 1, 1, 3, 2],
            "Comuna": ["Santiago", "Providencia", "Las Condes", "Nunoa", "Santiago"]
        })

        # limpieza basica: dropeamos filas con nulls en columnas criticas
        columnas_criticas = ["Precio_UF", "Dormitorios", "Banos"]
        df_limpio = df.dropna(subset=columnas_criticas)

        for col in columnas_criticas:
            assert df_limpio[col].isnull().sum() == 0, f"Hay nulls en {col} despues de limpiar"

    def test_filter_outliers(self):
        """Verifica que se filtren los outliers de precio"""
        # datos con outliers super obvios
        df = pd.DataFrame({
            "Precio_UF": [2500, 3000, 2800, 150000, 3200, 1, 2700],
            "Comuna": ["Santiago"] * 7
        })

        # filtro basico: sacamos precios menores a 500 UF o mayores a 50000 UF
        precio_min = 500
        precio_max = 50000
        df_filtrado = df[(df["Precio_UF"] >= precio_min) & (df["Precio_UF"] <= precio_max)]

        assert df_filtrado["Precio_UF"].min() >= precio_min, "Hay precios muy bajos todavia"
        assert df_filtrado["Precio_UF"].max() <= precio_max, "Hay precios muy altos todavia"
        assert len(df_filtrado) == 5, "No se filtraron bien los outliers"

    def test_column_types(self):
        """Verifica que Banos, Dormitorios y Estacionamientos sean int"""
        df = pd.DataFrame({
            "Banos": [2.0, 1.0, 3.0],
            "Dormitorios": [3.0, 2.0, 4.0],
            "Estacionamientos": [1.0, 0.0, 2.0]
        })

        # convertimos a int como se hace en el ETL
        for col in ["Banos", "Dormitorios", "Estacionamientos"]:
            df[col] = df[col].astype(int)

        assert df["Banos"].dtype == int or str(df["Banos"].dtype).startswith("int")
        assert df["Dormitorios"].dtype == int or str(df["Dormitorios"].dtype).startswith("int")
        assert df["Estacionamientos"].dtype == int or str(df["Estacionamientos"].dtype).startswith("int")


class TestDatabase:
    """Tests pa la base de datos SQLite"""

    def test_db_connection(self):
        """Intenta conectarse a comunas.db y verifica que exista la tabla comunas"""
        if not os.path.exists(DB_PATH):
            pytest.skip("No existe comunas.db, saltando test")

        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()

        # verificamos que exista la tabla comunas
        cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='comunas'")
        resultado = cursor.fetchone()
        conn.close()

        assert resultado is not None, "La tabla 'comunas' no existe en la BD"
