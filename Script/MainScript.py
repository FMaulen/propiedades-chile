import os
from data_loader import cargar_datos
from data_cleaner import limpiar_datos

def preparar_estructura_carpetas():
    """
    Crea la estructura de carpetas necesaria para guardar resultados
    Si las carpetas ya existen, no hace nada

    Estructura creada:
        outputs/
         datos_procesados/    # CSVs limpios
         reportes/           # Reportes de procesamiento
    """
    carpetas_necesarias = [
        '../outputs',
        '../outputs/datos_procesados',
        '../outputs/reportes'
    ]

    # Crear cada carpeta si no existe
    for ruta_carpeta in carpetas_necesarias:
        if not os.path.exists(ruta_carpeta):
            os.makedirs(ruta_carpeta)

def exportar_dataset_limpio(dataframe, nombre_archivo):
    """
    Guarda un dataset procesado como archivo CSV

    Args:
        dataframe (DataFrame): Dataset limpio para guardar
        nombre_archivo (str): Nombre del archivo CSV de salida

    El archivo se guarda en: outputs/datos_procesados/nombre_archivo
    """
    ruta_completa = os.path.join('..', 'outputs', 'datos_procesados', nombre_archivo)

    # Guardar sin indices de fila (index=False)
    dataframe.to_csv(ruta_completa, index=False)

def generar_reporte_procesamiento(df_original, df_procesado):
    """
    Crea un archivo de texto con estadisticas del procesamiento

    Args:
        df_original (DataFrame): Dataset antes del procesamiento
        df_procesado (DataFrame): Dataset despues del procesamiento

    Genera: outputs/reportes/reporte_procesamiento.txt
    """
    # Calcular estadisticas del procesamiento
    filas_originales = df_original.shape[0]
    columnas_originales = df_original.shape[1]
    filas_finales = df_procesado.shape[0]
    columnas_finales = df_procesado.shape[1]
    filas_eliminadas = filas_originales - filas_finales
    porcentaje_eliminado = (filas_eliminadas / filas_originales) * 100
    porcentaje_conservado = 100 - porcentaje_eliminado

    # Construir contenido del reporte
    lineas_reporte = [
        "REPORTE DE PROCESAMIENTO - PROPIEDADES CHILE",
        "=" * 50,
        "",
        "DATOS ORIGINALES:",
        f"  Filas: {filas_originales:,}",
        f"  Columnas: {columnas_originales}",
        "",
        "DATOS PROCESADOS:",
        f"  Filas: {filas_finales:,}",
        f"  Columnas: {columnas_finales}",
        "",
        "RESUMEN DEL PROCESAMIENTO:",
        f"  Filas eliminadas: {filas_eliminadas:,} ({porcentaje_eliminado:.1f}%)",
        f"  Filas conservadas: {filas_finales:,} ({porcentaje_conservado:.1f}%)",
        "",
        "MOTIVOS DE ELIMINACION:",
        "  - Filas con datos faltantes en columnas criticas",
        "  - Propiedades con areas fuera de rangos realistas",
        "  - Propiedades con precios fuera de rangos realistas"
    ]

    # Guardar reporte en archivo
    ruta_reporte = os.path.join('..', 'outputs', 'reportes', 'reporte_procesamiento.txt')
    with open(ruta_reporte, 'w', encoding='utf-8') as archivo:
        for linea in lineas_reporte:
            archivo.write(linea + '\n')

def mostrar_header():
    """
    Muestra el header visual del programa con casita ASCII y titulo
    """
    print("    ___")
    print("   /   \\")
    print("  /     \\")
    print(" /_______\\")
    print(" |  | |  |")
    print(" |__|_|__|")
    print("")
    print("PIPELINE PROPIEDADES CHILE")
    print("=" * 40)

def mostrar_roadmap():
    """
    Muestra el plan de ejecucion del pipeline
    """
    print("\nROADMAP:")
    print("1. Preparar estructura de carpetas")
    print("2. Cargar datasets desde archivos CSV")
    print("3. Limpiar y procesar datos")
    print("4. Exportar datasets limpios")
    print("5. Generar reporte de procesamiento")
    print("\n" + "-" * 40)

def main():
    # Mostrar header
    mostrar_header()
    mostrar_roadmap()

    # 1. Preparar carpetas
    print("\n1. Preparando carpetas")
    preparar_estructura_carpetas()

    # 2. Cargar datos
    print("2. Cargando datos")
    df1, df2 = cargar_datos()

    if df1 is None or df2 is None:
        print("[ERROR] No se pudieron cargar los datos")
        return

    # 3. Limpiar datos
    print("3. Procesando datos")
    df1_limpio = limpiar_datos(df1)
    df2_limpio = limpiar_datos(df2)

    # 4. Guardar resultados
    print("4. Guardando resultados")
    exportar_dataset_limpio(df1_limpio, 'casas_rm_limpio.csv')
    exportar_dataset_limpio(df2_limpio, 'web_scrape_limpio.csv')

    # 5. Crear reporte
    print("5. Generando reporte")
    generar_reporte_procesamiento(df1, df1_limpio)

    # Mensaje final
    print("\n" + "=" * 40)
    print("PROCESAMIENTO COMPLETADO!")
    print("\nRESULTADOS DISPONIBLES EN:")
    print("   outputs/datos_procesados/")
    print("   outputs/reportes/")
    print("=" * 40)

# Ejecutar el programa
if __name__ == "__main__":
    main()