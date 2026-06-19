# api_app.py - API principal del proyecto Propiedades Chile
# Fabian Maulen, Evan Mardones, Joaquin Pastenes
# Materia: Programacion para la Ciencia de Datos SCY1101

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
import uvicorn
import sqlite3
import os
import joblib
import requests
import pandas as pd
import numpy as np

# --- Configuracion de la app ---
app = FastAPI(
    title="Propiedades Chile API",
    description="API para prediccion de precios de casas en Santiago",
    version="1.0"
)

# Paths relativos al proyecto (subimos un nivel desde /api)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DB_PATH = os.path.join(BASE_DIR, "data", "comunas.db")
MODEL_PATH = os.path.join(BASE_DIR, "models", "trained_models", "forest_model.pkl")

# valor por defecto de la UF por si falla la api
UF_DEFAULT = 38000


# --- Modelos Pydantic ---
class PredictionInput(BaseModel):
    """Datos de entrada para la prediccion"""
    Built_Area: float
    Total_Area: float
    Dorms: int
    Baths: int
    Parking: int
    Comuna: str


class PredictionOutput(BaseModel):
    """Resultado de la prediccion"""
    precio_uf: float
    precio_clp: float
    uf_usada: float
    comuna: str


# --- Funcion auxiliar para obtener UF ---
def obtener_uf():
    """Intenta obtener el valor actual de la UF desde mindicador.cl"""
    try:
        response = requests.get("https://mindicador.cl/api/uf", timeout=5)
        if response.status_code == 200:
            datos = response.json()
            # el primer valor de la serie es el mas reciente
            valor_uf = datos["serie"][0]["valor"]
            print(f"UF obtenida desde API: {valor_uf}")
            return valor_uf
        else:
            print(f"Error en API mindicador, status: {response.status_code}")
            return UF_DEFAULT
    except Exception as e:
        print(f"No se pudo conectar a mindicador: {e}")
        return UF_DEFAULT


# ==========================================
# ENDPOINTS
# ==========================================

@app.get("/")
def root():
    """Info basica del proyecto"""
    return {
        "title": "Prediccion de Precios de Propiedades - Region Metropolitana",
        "authors": ["Fabian Maulen", "Evan Mardones", "Joaquin Pastenes"],
        "version": "1.0",
        "materia": "Programacion para la Ciencia de Datos SCY1101",
        "descripcion": "API para consultar datos y predecir precios de casas en Santiago de Chile"
    }


@app.get("/health")
def health_check():
    """Verifica el estado de la API, la base de datos y el modelo"""
    # revisar si la db existe
    db_ok = os.path.exists(DB_PATH)
    # revisar si el modelo existe
    model_ok = os.path.exists(MODEL_PATH)

    return {
        "status": "ok",
        "db_status": "disponible" if db_ok else "no encontrada",
        "db_path": DB_PATH,
        "model_status": "disponible" if model_ok else "no encontrado",
        "model_path": MODEL_PATH
    }


@app.get("/indicators")
def get_indicators():
    """Obtiene indicadores economicos (UF) desde mindicador.cl"""
    try:
        response = requests.get("https://mindicador.cl/api/uf", timeout=5)
        if response.status_code == 200:
            datos = response.json()
            valor_actual = datos["serie"][0]["valor"]
            fecha = datos["serie"][0]["fecha"]
            return {
                "indicador": "UF",
                "valor": valor_actual,
                "fecha": fecha,
                "fuente": "mindicador.cl"
            }
        else:
            # si falla la api, retornamos el default
            return {
                "indicador": "UF",
                "valor": UF_DEFAULT,
                "fecha": "N/A",
                "fuente": "valor por defecto (API no disponible)"
            }
    except Exception as e:
        return {
            "indicador": "UF",
            "valor": UF_DEFAULT,
            "fecha": "N/A",
            "fuente": f"valor por defecto (error: {str(e)})"
        }


@app.get("/communes")
def get_communes():
    """Lee todas las comunas desde la base de datos SQLite"""
    if not os.path.exists(DB_PATH):
        raise HTTPException(
            status_code=404,
            detail=f"Base de datos no encontrada en {DB_PATH}"
        )

    try:
        conn = sqlite3.connect(DB_PATH)
        conn.row_factory = sqlite3.Row
        cursor = conn.cursor()

        # intentamos leer la tabla de comunas
        cursor.execute("SELECT * FROM comunas")
        filas = cursor.fetchall()
        conn.close()

        # convertir a lista de diccionarios
        resultado = [dict(fila) for fila in filas]
        print(f"Se encontraron {len(resultado)} comunas en la BD")

        return {
            "total": len(resultado),
            "comunas": resultado
        }

    except sqlite3.OperationalError as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error al leer la base de datos: {str(e)}"
        )
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail=f"Error inesperado: {str(e)}"
        )


@app.post("/predict", response_model=PredictionOutput)
def predict_price(datos: PredictionInput):
    """Predice el precio de una propiedad usando el modelo Random Forest"""

    # verificar que el modelo existe
    if not os.path.exists(MODEL_PATH):
        raise HTTPException(
            status_code=404,
            detail=f"Modelo no encontrado en {MODEL_PATH}. Entrena el modelo primero."
        )

    try:
        # cargar el modelo
        modelo = joblib.load(MODEL_PATH)
        print(f"Modelo cargado desde {MODEL_PATH}")

        # preparar los datos de entrada como dataframe
        # OJO: el modelo fue entrenado con columnas con espacios (ej: 'Built Area')
        # asi que hay que mapear los nombres
        input_data = pd.DataFrame([{
            "Built Area": datos.Built_Area,
            "Total Area": datos.Total_Area,
            "Dorms": datos.Dorms,
            "Baths": datos.Baths,
            "Parking": datos.Parking,
            "Comuna": datos.Comuna
        }])

        # hacer la prediccion
        prediccion_uf = modelo.predict(input_data)[0]
        prediccion_uf = float(np.round(prediccion_uf, 2))

        # obtener UF para convertir a CLP
        valor_uf = obtener_uf()
        precio_clp = round(prediccion_uf * valor_uf, 0)

        print(f"Prediccion: {prediccion_uf} UF = ${precio_clp:,.0f} CLP")

        return PredictionOutput(
            precio_uf=prediccion_uf,
            precio_clp=precio_clp,
            uf_usada=valor_uf,
            comuna=datos.Comuna
        )

    except HTTPException:
        raise
    except Exception as e:
        print(f"Error en prediccion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Error al hacer la prediccion: {str(e)}"
        )


# --- Punto de entrada ---
if __name__ == "__main__":
    print("Iniciando API de Propiedades Chile...")
    print(f"Base de datos: {DB_PATH}")
    print(f"Modelo: {MODEL_PATH}")
    uvicorn.run(app, host="0.0.0.0", port=8000)
