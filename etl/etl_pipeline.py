# -*- coding: utf-8 -*-
"""
Pipeline ETL para el proyecto de prediccion de precios de propiedades en Santiago.
Carga datos crudos, limpia, enriquece con datos de comunas y guarda dataset procesado.
"""

import pandas as pd
import sqlite3
import requests
import os
import glob
from datetime import datetime


# ruta base del proyecto (un nivel arriba de etl/)
BASE_DIR = os.path.normpath(os.path.join(os.path.dirname(__file__), '..'))


def escribir_log(mensaje, log_path):
    """Escribe un mensaje con timestamp en el archivo de log."""
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{timestamp}] {mensaje}\n"
    with open(log_path, "a", encoding="utf-8") as f:
        f.write(linea)


def obtener_valor_uf():
    """
    Consulta la API de mindicador.cl para obtener el valor actual de la UF.
    Si falla, usa un valor por defecto.
    """
    url = "https://mindicador.cl/api/uf"
    valor_default = 38000  # valor aprox por si falla la API

    try:
        print("Consultando API de mindicador.cl para valor UF...")
        response = requests.get(url, timeout=10)
        response.raise_for_status()

        data = response.json()
        # la api devuelve una lista de valores, el primero es el mas reciente
        valor_uf = data["serie"][0]["valor"]
        print(f"Valor UF obtenido: ${valor_uf:,.2f} CLP")
        return valor_uf

    except requests.exceptions.RequestException as e:
        print(f"Error al consultar API: {e}")
        print(f"Usando valor por defecto: ${valor_default:,.2f} CLP")
        return valor_default
    except (KeyError, IndexError) as e:
        print(f"Error parseando respuesta de API: {e}")
        print(f"Usando valor por defecto: ${valor_default:,.2f} CLP")
        return valor_default


def cargar_csvs(raw_dir):
    """Carga todos los CSV de la carpeta data/raw/ y los concatena."""
    archivos = glob.glob(os.path.join(raw_dir, "*.csv"))

    if not archivos:
        print(f"ERROR: No se encontraron CSVs en {raw_dir}")
        return None

    print(f"Se encontraron {len(archivos)} archivos CSV:")
    dataframes = []

    for archivo in archivos:
        nombre = os.path.basename(archivo)
        # probamos distintos encodings porque los CSV chilenos a veces vienen raros
        df = None
        for enc in ["utf-8", "latin-1", "cp1252"]:
            try:
                df = pd.read_csv(archivo, encoding=enc)
                break
            except (UnicodeDecodeError, UnicodeError):
                continue

        if df is None:
            print(f"  - ERROR: no se pudo leer {nombre} con ningun encoding")
            continue

        print(f"  - {nombre}: {len(df)} filas, {len(df.columns)} columnas")
        dataframes.append(df)

    if not dataframes:
        return None

    # concatenar todos los dataframes
    df_total = pd.concat(dataframes, ignore_index=True)
    print(f"Total combinado: {len(df_total)} filas")
    return df_total


def cargar_datos_comunas(db_path):
    """Lee la tabla de comunas desde SQLite."""
    if not os.path.exists(db_path):
        print(f"ADVERTENCIA: No se encontro la BD de comunas en {db_path}")
        print("Ejecuta primero init_db.py para crear la base de datos.")
        return None

    conn = sqlite3.connect(db_path)
    df_comunas = pd.read_sql_query("SELECT * FROM comunas", conn)
    conn.close()
    print(f"Datos de comunas cargados: {len(df_comunas)} comunas")
    return df_comunas


def limpiar_comunas(df):
    """
    Arregla problemas de encoding en los nombres de comunas.
    Los CSV a veces traen caracteres rotos en vez de tildes normales.
    """
    import unicodedata

    def quitar_acentos(texto):
        """Quita tildes y acentos de un string usando unicode normalization."""
        # NFD descompone los caracteres acentuados (ej: 'é' -> 'e' + accent)
        # luego filtramos los combining marks (los acentos sueltos)
        nfkd = unicodedata.normalize('NFKD', texto)
        return ''.join(c for c in nfkd if not unicodedata.combining(c))

    # mapeo extra por si quedan casos raros despues de normalizar
    mapeo_post = {
        "EstaciónCentral": "EstacionCentral",
        "EstacionCentral": "EstacionCentral",
        "Nunoa": "Nunoa",
        "PenaloLen": "PenaloLen",
        "Penalolen": "PenaloLen",
    }

    def fix_comuna(nombre):
        if pd.isna(nombre):
            return nombre
        nombre = str(nombre).strip()

        # quitar acentos y tildes con unicodedata
        nombre = quitar_acentos(nombre)

        # aplicar mapeo extra si existe
        if nombre in mapeo_post:
            nombre = mapeo_post[nombre]

        return nombre

    df["Comuna"] = df["Comuna"].apply(fix_comuna)
    return df


def limpiar_datos(df):
    """Limpieza general del dataframe."""
    filas_inicial = len(df)
    print(f"\nIniciando limpieza de datos ({filas_inicial} filas)...")

    # 1. arreglar nombres de comunas
    df = limpiar_comunas(df)
    print("  - Nombres de comunas normalizados")

    # 2. eliminar filas con valores nulos en columnas importantes
    cols_requeridas = ["Baths", "Built Area", "Total Area"]
    for col in cols_requeridas:
        if col in df.columns:
            antes = len(df)
            df = df.dropna(subset=[col])
            eliminadas = antes - len(df)
            if eliminadas > 0:
                print(f"  - Eliminadas {eliminadas} filas por {col} nulo")

    # 3. filtrar outliers
    if "Total Area" in df.columns:
        antes = len(df)
        df = df[(df["Total Area"] >= 20) & (df["Total Area"] <= 5000)]
        print(f"  - Filtro Total Area [20-5000]: eliminadas {antes - len(df)} filas")

    if "Price_UF" in df.columns:
        antes = len(df)
        df = df[df["Price_UF"] > 200]
        print(f"  - Filtro Price_UF > 200: eliminadas {antes - len(df)} filas")

    # 4. convertir columnas a int (primero llenar NaN con 0 donde corresponda)
    cols_int = ["Baths", "Dorms", "Parking"]
    for col in cols_int:
        if col in df.columns:
            df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0).astype(int)

    print(f"  - Columnas Baths/Dorms/Parking convertidas a int")

    # 5. eliminar duplicados por id si existe
    if "id" in df.columns:
        antes = len(df)
        df = df.drop_duplicates(subset=["id"], keep="first")
        eliminadas = antes - len(df)
        if eliminadas > 0:
            print(f"  - Eliminados {eliminadas} duplicados por id")

    filas_final = len(df)
    print(f"Limpieza completada: {filas_inicial} -> {filas_final} filas ({filas_inicial - filas_final} eliminadas)")

    return df


def main():
    print("=" * 60)
    print("  PIPELINE ETL - Propiedades Region Metropolitana")
    print(f"  Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 60)

    # configurar rutas
    raw_dir = os.path.join(BASE_DIR, "data", "raw")
    processed_dir = os.path.join(BASE_DIR, "data", "processed")
    db_path = os.path.join(BASE_DIR, "data", "comunas.db")
    log_dir = os.path.join(BASE_DIR, "etl")
    log_path = os.path.join(log_dir, "etl.log")

    # crear directorios si no existen
    os.makedirs(processed_dir, exist_ok=True)
    os.makedirs(log_dir, exist_ok=True)

    escribir_log("Inicio del pipeline ETL", log_path)

    # --- PASO 1: Cargar CSVs ---
    print("\n[PASO 1] Cargando datos crudos...")
    df = cargar_csvs(raw_dir)
    if df is None:
        escribir_log("ERROR: No se pudieron cargar los CSVs", log_path)
        print("Abortando pipeline.")
        return
    escribir_log(f"CSVs cargados: {len(df)} filas totales", log_path)

    # --- PASO 2: Obtener valor UF ---
    print("\n[PASO 2] Obteniendo valor UF actual...")
    valor_uf = obtener_valor_uf()
    escribir_log(f"Valor UF: {valor_uf}", log_path)

    # --- PASO 3: Cargar datos de comunas ---
    print("\n[PASO 3] Cargando datos de comunas desde SQLite...")
    df_comunas = cargar_datos_comunas(db_path)
    if df_comunas is not None:
        escribir_log(f"Datos de comunas cargados: {len(df_comunas)} comunas", log_path)
    else:
        escribir_log("ADVERTENCIA: No se cargaron datos de comunas", log_path)

    # --- PASO 4: Limpieza de datos ---
    print("\n[PASO 4] Limpiando datos...")
    df = limpiar_datos(df)
    escribir_log(f"Limpieza completada: {len(df)} filas restantes", log_path)

    # --- PASO 5: Join con datos de comunas ---
    print("\n[PASO 5] Integrando datos de comunas...")
    if df_comunas is not None:
        filas_antes = len(df)
        df = df.merge(df_comunas, left_on="Comuna", right_on="nombre", how="left")

        # ver cuantas comunas hicieron match
        con_datos = df["nombre"].notna().sum()
        sin_datos = df["nombre"].isna().sum()
        print(f"  - Con datos de comuna: {con_datos} filas")
        print(f"  - Sin datos de comuna: {sin_datos} filas")

        # mostrar comunas que no hicieron match (pa debuggear)
        if sin_datos > 0:
            comunas_sin_match = df[df["nombre"].isna()]["Comuna"].unique()
            print(f"  - Comunas sin match: {list(comunas_sin_match[:10])}")
            if len(comunas_sin_match) > 10:
                print(f"    ... y {len(comunas_sin_match) - 10} mas")

        # eliminar columna 'nombre' que es redundante con 'Comuna'
        df = df.drop(columns=["nombre"], errors="ignore")
        escribir_log(f"Join con comunas: {con_datos} matches, {sin_datos} sin match", log_path)
    else:
        print("  - Saltando join (no hay datos de comunas)")

    # --- PASO 6: Calcular precio CLP actualizado ---
    print("\n[PASO 6] Calculando precio CLP actualizado...")
    if "Price_UF" in df.columns:
        df["Precio_CLP_Actual"] = df["Price_UF"] * valor_uf
        df["Precio_CLP_Actual"] = df["Precio_CLP_Actual"].round(0).astype(int)
        print(f"  - Columna 'Precio_CLP_Actual' creada (UF * {valor_uf:,.0f})")
        # estadisticas basicas
        print(f"  - Precio promedio: ${df['Precio_CLP_Actual'].mean():,.0f} CLP")
        print(f"  - Precio mediana:  ${df['Precio_CLP_Actual'].median():,.0f} CLP")
    escribir_log(f"Precio CLP calculado con UF={valor_uf}", log_path)

    # --- PASO 7: Guardar dataset procesado ---
    print("\n[PASO 7] Guardando dataset integrado...")
    output_path = os.path.join(processed_dir, "casas_rm_integrated.csv")
    df.to_csv(output_path, index=False, encoding="utf-8")
    tamaño_mb = os.path.getsize(output_path) / (1024 * 1024)
    print(f"  - Archivo guardado: {output_path}")
    print(f"  - Tamaño: {tamaño_mb:.2f} MB")
    print(f"  - Filas: {len(df)}, Columnas: {len(df.columns)}")
    escribir_log(f"Dataset guardado: {output_path} ({len(df)} filas, {tamaño_mb:.2f} MB)", log_path)

    # resumen final
    print("\n" + "=" * 60)
    print("  PIPELINE ETL COMPLETADO EXITOSAMENTE")
    print(f"  Filas procesadas: {len(df)}")
    print(f"  Columnas: {list(df.columns)}")
    print("=" * 60)
    escribir_log("Pipeline ETL completado exitosamente", log_path)


if __name__ == "__main__":
    main()
