"""
Script para crear la base de datos de comunas de la Region Metropolitana.
Guarda datos demograficos y socioeconomicos en SQLite.
"""

import sqlite3
import os


def main():
    # ruta de la base de datos
    db_path = os.path.join(os.path.dirname(__file__), '..', 'data', 'comunas.db')
    db_path = os.path.normpath(db_path)

    # crear directorio data si no existe
    os.makedirs(os.path.dirname(db_path), exist_ok=True)

    print("=" * 50)
    print("Creando base de datos de comunas RM...")
    print(f"Ruta: {db_path}")
    print("=" * 50)

    # si ya existe la bd, la borramos pa crearla de nuevo
    if os.path.exists(db_path):
        os.remove(db_path)
        print("BD anterior eliminada.")

    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # crear tabla comunas
    cursor.execute("""
        CREATE TABLE comunas (
            nombre TEXT PRIMARY KEY,
            poblacion INTEGER,
            icvu REAL,
            ingreso_promedio INTEGER
        )
    """)
    print("Tabla 'comunas' creada.")

    # datos de comunas de la RM
    # nombre, poblacion aprox, icvu (indice calidad vida urbana), ingreso promedio hogar CLP
    # los datos son aproximados basados en fuentes publicas (censo, estudios ICVU, etc)
    datos_comunas = [
        # --- sector oriente (alto ingreso) ---
        ("Vitacura",        85000,  78.5, 3200000),
        ("LasCondes",      310000,  76.2, 2800000),
        ("LoBarnechea",    120000,  74.8, 2600000),
        ("Providencia",    155000,  75.1, 2400000),
        ("LaReina",        100000,  70.3, 1900000),
        ("Nunoa",          250000,  68.7, 1700000),

        # --- sector centro ---
        ("Santiago",       505000,  62.4, 1200000),
        ("Independencia",  105000,  52.1,  850000),
        ("Recoleta",       180000,  48.5,  780000),
        ("QuintaNormal",   130000,  47.2,  750000),
        ("EstacionCentral", 200000, 46.8,  720000),
        ("SanMiguel",      120000,  55.3,  900000),

        # --- sector sur ---
        ("LaFlorida",      400000,  53.6,  950000),
        ("Macul",          135000,  56.2,  980000),
        ("PenaloLen",      260000,  52.8,  870000),
        ("PuenteAlto",     650000,  42.1,  680000),
        ("SanBernardo",    320000,  40.5,  620000),
        ("LaCisterna",     100000,  51.4,  820000),
        ("ElBosque",       185000,  39.8,  580000),
        ("LaGranja",       140000,  37.5,  540000),
        ("LaPintana",      200000,  33.2,  450000),
        ("SanJoaquin",     110000,  45.6,  700000),
        ("SanRamon",        95000,  36.8,  520000),
        ("PedroAguirreCerda", 115000, 41.2, 620000),
        ("LoEspejo",       115000,  35.9,  490000),

        # --- sector poniente ---
        ("Maipu",          580000,  50.2,  850000),
        ("Pudahuel",       260000,  44.3,  710000),
        ("CerroNavia",     160000,  36.1,  500000),
        ("LoPrado",        110000,  38.4,  550000),
        ("Cerrillos",       90000,  48.7,  760000),
        ("Renca",          160000,  40.8,  600000),

        # --- sector norte ---
        ("Quilicura",      250000,  47.5,  780000),
        ("Conchali",       145000,  42.6,  650000),
        ("Huechuraba",     110000,  49.3,  800000),
        ("Colina",         180000,  53.1,  920000),
        ("Lampa",          120000,  43.7,  670000),

        # --- comunas perifericas ---
        ("Buin",            90000,  44.2,  680000),
        ("Paine",           80000,  41.5,  610000),
        ("Talagante",       75000,  45.8,  700000),
        ("Penaflor",        95000,  44.9,  690000),
        ("PadreHurtado",    65000,  42.3,  640000),
        ("Melipilla",      120000,  43.1,  660000),
        ("Tiltil",          18000,  39.5,  550000),
        ("ElMonte",         38000,  40.1,  580000),
        ("CaleradeTango",   30000,  46.2,  750000),
        ("Curacavi",        40000,  43.8,  640000),
        ("SanJosedeMaipo",  20000,  48.5,  720000),
        ("SanPedro",        12000,  38.0,  520000),
        ("Pirque",          25000,  52.5,  900000),
        ("MariaPinto",      15000,  37.5,  510000),
        ("Alhue",            8000,  35.0,  480000),
        ("IsladeMaipo",     40000,  42.0,  620000),
        ("Penalolen",      260000,  52.8,  870000),
    ]

    # insertar datos
    cursor.executemany(
        "INSERT INTO comunas (nombre, poblacion, icvu, ingreso_promedio) VALUES (?, ?, ?, ?)",
        datos_comunas
    )

    conn.commit()
    print(f"Se insertaron {len(datos_comunas)} comunas en la base de datos.")

    # verificar que se guardaron bien
    cursor.execute("SELECT COUNT(*) FROM comunas")
    count = cursor.fetchone()[0]
    print(f"Verificacion: {count} registros en tabla 'comunas'.")

    # mostrar algunas comunas de ejemplo
    print("\nEjemplo de datos guardados:")
    print("-" * 70)
    cursor.execute("SELECT * FROM comunas ORDER BY icvu DESC LIMIT 5")
    rows = cursor.fetchall()
    for row in rows:
        print(f"  {row[0]:25s} | Pob: {row[1]:>8,} | ICVU: {row[2]:5.1f} | Ingreso: ${row[3]:>12,}")

    conn.close()
    print("\nBase de datos creada exitosamente!")
    print("=" * 50)


if __name__ == "__main__":
    main()
