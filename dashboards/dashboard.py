# dashboard.py - Dashboard principal del proyecto Propiedades Chile
# Fabian Maulen, Evan Mardones, Joaquin Pastenes
# SCY1101 - Programacion para la Ciencia de Datos

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import os
import numpy as np

# --- Config de la pagina ---
st.set_page_config(
    page_title="Propiedades Chile - Dashboard",
    layout="wide",
    page_icon="🏠"
)

# paths relativos al proyecto (subimos un nivel desde /dashboards)
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA_PATH = os.path.join(BASE_DIR, "data", "processed", "casas_rm_integrated.csv")
MODEL_PATH = os.path.join(BASE_DIR, "models", "trained_models", "forest_model.pkl")
DB_PATH = os.path.join(BASE_DIR, "data", "comunas.db")

# URL de la API
API_URL = "http://localhost:8000"

# valor UF por defecto
UF_DEFAULT = 38000


# --- Funcion para cargar datos ---
@st.cache_data
def cargar_datos():
    """Carga el CSV con los datos de propiedades"""
    try:
        df = pd.read_csv(DATA_PATH)
        print(f"Datos cargados: {len(df)} filas")
        return df
    except FileNotFoundError:
        return None
    except Exception as e:
        print(f"Error cargando datos: {e}")
        return None


# --- Titulo principal ---
st.title("🏠 Propiedades Chile - Dashboard")
st.markdown("**Predicción de precios de casas en la Región Metropolitana de Santiago**")
st.markdown("---")

# --- Tabs ---
tab1, tab2, tab3 = st.tabs(["📊 Vista Ejecutiva", "🧮 Calculadora de Tasación", "🔬 Vista Técnica"])

# ==========================================
# TAB 1: VISTA EJECUTIVA
# ==========================================
with tab1:
    st.header("Resumen del Mercado Inmobiliario RM")

    # cargar datos
    df = cargar_datos()

    if df is None:
        st.error(f"❌ No se encontró el archivo de datos en: {DATA_PATH}")
        st.info("Asegúrate de haber ejecutado el pipeline de datos primero.")
    else:
        # --- Metricas principales ---
        st.subheader("📈 Indicadores Generales")

        col1, col2, col3, col4 = st.columns(4)

        # calcular metricas basicas
        total_props = len(df)
        # intentamos buscar la columna de precio en UF
        # puede llamarse 'Price_UF', 'price_uf', 'Precio_UF', etc
        precio_col = None
        for col_name in df.columns:
            if 'price' in col_name.lower() or 'precio' in col_name.lower():
                if 'uf' in col_name.lower():
                    precio_col = col_name
                    break
        # si no encontramos con UF, buscamos cualquier columna de precio
        if precio_col is None:
            for col_name in df.columns:
                if 'price' in col_name.lower() or 'precio' in col_name.lower():
                    precio_col = col_name
                    break

        # buscar columna de comuna
        comuna_col = None
        for col_name in df.columns:
            if 'comuna' in col_name.lower():
                comuna_col = col_name
                break

        with col1:
            st.metric("Total Propiedades", f"{total_props:,}")
        with col2:
            if precio_col:
                promedio = df[precio_col].mean()
                st.metric("Precio Promedio UF", f"{promedio:,.0f}")
            else:
                st.metric("Precio Promedio UF", "N/A")
        with col3:
            if precio_col:
                mediana = df[precio_col].median()
                st.metric("Precio Mediana UF", f"{mediana:,.0f}")
            else:
                st.metric("Precio Mediana UF", "N/A")
        with col4:
            if comuna_col:
                n_comunas = df[comuna_col].nunique()
                st.metric("Comunas Cubiertas", n_comunas)
            else:
                st.metric("Comunas Cubiertas", "N/A")

        st.markdown("---")

        # --- Graficos ---
        if precio_col and comuna_col:
            col_izq, col_der = st.columns(2)

            with col_izq:
                st.subheader("🏘️ Top 15 Comunas por Precio Promedio")
                # agrupar por comuna y sacar promedio
                precios_comuna = df.groupby(comuna_col)[precio_col].mean().sort_values(ascending=False).head(15)
                fig_bar = px.bar(
                    x=precios_comuna.values,
                    y=precios_comuna.index,
                    orientation='h',
                    labels={'x': 'Precio Promedio (UF)', 'y': 'Comuna'},
                    title='Precio Promedio por Comuna (Top 15)',
                    color=precios_comuna.values,
                    color_continuous_scale='Blues'
                )
                fig_bar.update_layout(yaxis={'categoryorder': 'total ascending'}, height=500)
                st.plotly_chart(fig_bar, use_container_width=True)

            with col_der:
                st.subheader("📊 Distribución de Precios")
                fig_hist = px.histogram(
                    df,
                    x=precio_col,
                    nbins=50,
                    title='Distribución de Precios (UF)',
                    labels={precio_col: 'Precio (UF)'},
                    color_discrete_sequence=['#636EFA']
                )
                fig_hist.update_layout(height=500)
                st.plotly_chart(fig_hist, use_container_width=True)
        else:
            st.warning("No se encontraron las columnas de precio o comuna en el dataset.")
            st.write("Columnas disponibles:", list(df.columns))

        st.info(
            "ℹ️ Los datos provienen de web scraping de portales inmobiliarios chilenos "
            "(portalinmobiliario.com y similares), complementados con datos del INE y "
            "el observatorio de la Universidad Alberto Hurtado. Última actualización del dataset "
            "corresponde al periodo 2024."
        )


# ==========================================
# TAB 2: CALCULADORA DE TASACION
# ==========================================
with tab2:
    st.header("Estima el precio de tu propiedad")
    st.markdown("Ingresa las características de la propiedad y obtén una estimación de precio.")

    # cargar datos para obtener la lista de comunas
    df = cargar_datos()

    # obtener lista de comunas
    if df is not None:
        comuna_col = None
        for col_name in df.columns:
            if 'comuna' in col_name.lower():
                comuna_col = col_name
                break
        if comuna_col:
            lista_comunas = sorted(df[comuna_col].dropna().unique().tolist())
        else:
            lista_comunas = ["Santiago", "Providencia", "Las Condes", "Ñuñoa", "La Florida",
                             "Maipú", "Puente Alto", "Vitacura", "Lo Barnechea", "La Reina"]
    else:
        # comunas por defecto si no hay datos
        lista_comunas = ["Santiago", "Providencia", "Las Condes", "Ñuñoa", "La Florida",
                         "Maipú", "Puente Alto", "Vitacura", "Lo Barnechea", "La Reina"]

    # --- Inputs ---
    st.subheader("📝 Características de la Propiedad")

    col1, col2, col3 = st.columns(3)

    with col1:
        built_area = st.number_input("Superficie Construida (m²)", min_value=20, max_value=500, value=120, step=5)
        total_area = st.number_input("Superficie Total (m²)", min_value=20, max_value=5000, value=150, step=10)

    with col2:
        dorms = st.number_input("Dormitorios", min_value=1, max_value=10, value=3, step=1)
        baths = st.number_input("Baños", min_value=1, max_value=5, value=2, step=1)

    with col3:
        parking = st.number_input("Estacionamientos", min_value=0, max_value=5, value=1, step=1)
        comuna = st.selectbox("Comuna", options=lista_comunas)

    st.markdown("---")

    # --- Boton de prediccion ---
    if st.button("🔮 Calcular Precio", type="primary", use_container_width=True):
        # preparar datos
        datos_input = {
            "Built_Area": float(built_area),
            "Total_Area": float(total_area),
            "Dorms": int(dorms),
            "Baths": int(baths),
            "Parking": int(parking),
            "Comuna": comuna
        }

        precio_uf = None
        precio_clp = None
        metodo_usado = ""

        # primero intentamos con la API
        try:
            with st.spinner("Consultando API..."):
                response = requests.post(
                    f"{API_URL}/predict",
                    json=datos_input,
                    timeout=10
                )
                if response.status_code == 200:
                    resultado = response.json()
                    precio_uf = resultado["precio_uf"]
                    precio_clp = resultado["precio_clp"]
                    metodo_usado = "API"
                else:
                    st.warning(f"⚠️ La API respondió con error: {response.status_code}")
                    raise Exception("API error")

        except Exception as e:
            # si la API no esta disponible, cargamos el modelo directo
            st.warning("⚠️ API no disponible, intentando cargar modelo directamente...")

            try:
                import joblib

                if not os.path.exists(MODEL_PATH):
                    st.error(f"❌ Modelo no encontrado en: {MODEL_PATH}")
                    st.info("Entrena el modelo primero ejecutando el pipeline de entrenamiento.")
                else:
                    modelo = joblib.load(MODEL_PATH)

                    # crear dataframe con los datos
                    # ojo: el modelo usa columnas con espacios
                    input_df = pd.DataFrame([{
                        "Built Area": datos_input["Built_Area"],
                        "Total Area": datos_input["Total_Area"],
                        "Dorms": datos_input["Dorms"],
                        "Baths": datos_input["Baths"],
                        "Parking": datos_input["Parking"],
                        "Comuna": datos_input["Comuna"]
                    }])
                    prediccion = modelo.predict(input_df)[0]
                    precio_uf = round(float(prediccion), 2)
                    precio_clp = round(precio_uf * UF_DEFAULT, 0)
                    metodo_usado = "modelo local"

            except Exception as e2:
                st.error(f"❌ Error al cargar el modelo: {str(e2)}")

        # mostrar resultados
        if precio_uf is not None:
            st.markdown("---")
            st.subheader("💰 Resultado de la Estimación")

            res_col1, res_col2 = st.columns(2)
            with res_col1:
                st.success(f"**Precio estimado: {precio_uf:,.2f} UF**")
            with res_col2:
                st.success(f"**Precio estimado: ${precio_clp:,.0f} CLP**")

            st.caption(f"Estimación realizada usando: {metodo_usado}")
            st.caption(f"Propiedad en {comuna}: {built_area}m² construidos, "
                       f"{total_area}m² totales, {dorms} dormitorios, {baths} baños, "
                       f"{parking} estacionamientos")


# ==========================================
# TAB 3: VISTA TECNICA
# ==========================================
with tab3:
    st.header("Performance de los Modelos")
    st.markdown("Comparación de los modelos entrenados para predecir precios de casas.")

    # --- Tabla de resultados ---
    st.subheader("📋 Resultados de los Modelos")

    # datos hardcodeados de los resultados conocidos
    resultados_modelos = pd.DataFrame({
        "Modelo": [
            "Linear Regression",
            "Random Forest",
            "Gradient Boosting",
            "Random Forest Mejorado",
            "KNN"
        ],
        "R² Score": [-1.777, 0.848, 0.837, 0.688, 0.654],
        "Interpretación": [
            "❌ Muy malo - peor que predecir la media",
            "✅ Mejor modelo - buena capacidad predictiva",
            "✅ Muy bueno - similar al Random Forest",
            "⚠️ Aceptable - rendimiento moderado",
            "⚠️ Aceptable - rendimiento básico"
        ]
    })

    st.dataframe(resultados_modelos, use_container_width=True, hide_index=True)

    st.markdown("---")

    # --- Grafico de comparacion ---
    st.subheader("📊 Comparación de R² Score")

    # solo modelos con R2 positivo para que el grafico se vea bien
    df_grafico = resultados_modelos.copy()

    fig_r2 = px.bar(
        df_grafico,
        x="Modelo",
        y="R² Score",
        title="Comparación de R² Score por Modelo",
        color="R² Score",
        color_continuous_scale="RdYlGn",
        text="R² Score"
    )
    fig_r2.update_traces(texttemplate='%{text:.3f}', textposition='outside')
    fig_r2.update_layout(height=450)
    # linea de referencia en 0
    fig_r2.add_hline(y=0, line_dash="dash", line_color="gray",
                     annotation_text="Baseline (predecir la media)")

    st.plotly_chart(fig_r2, use_container_width=True)

    st.markdown("---")

    # --- Feature importance ---
    st.subheader("🔍 Importancia de las Variables")

    st.markdown("""
    Según el análisis del modelo **Random Forest** (mejor modelo), las variables más 
    importantes para predecir el precio de una casa son:

    1. **Superficie Construida (Built_Area)**: La variable más relevante. A mayor superficie 
       construida, mayor es el precio de la propiedad.
    2. **Superficie Total (Total_Area)**: El tamaño total del terreno también influye 
       significativamente en el precio.
    3. **Comuna**: La ubicación geográfica es determinante. Comunas como Vitacura, Lo Barnechea 
       y Las Condes tienen precios considerablemente más altos.
    4. **Dormitorios y Baños**: Más habitaciones y baños se correlacionan con precios más altos, 
       aunque con menor impacto que la superficie.
    5. **Estacionamientos**: Tiene un impacto menor pero no despreciable, especialmente en 
       comunas céntricas donde el estacionamiento es escaso.
    """)

    st.markdown("---")

    # --- Estado del pipeline ---
    st.subheader("⚙️ Estado del Pipeline")

    with st.status("Verificando archivos del proyecto...", expanded=True) as status:
        # verificar archivos de datos
        st.write("🔍 Verificando datos...")
        if os.path.exists(DATA_PATH):
            st.write(f"✅ Dataset encontrado: {DATA_PATH}")
        else:
            st.write(f"❌ Dataset no encontrado: {DATA_PATH}")

        # verificar modelo
        st.write("🔍 Verificando modelo...")
        if os.path.exists(MODEL_PATH):
            st.write(f"✅ Modelo encontrado: {MODEL_PATH}")
        else:
            st.write(f"❌ Modelo no encontrado: {MODEL_PATH}")

        # verificar base de datos
        st.write("🔍 Verificando base de datos...")
        if os.path.exists(DB_PATH):
            st.write(f"✅ Base de datos encontrada: {DB_PATH}")
        else:
            st.write(f"❌ Base de datos no encontrada: {DB_PATH}")

        # verificar API
        st.write("🔍 Verificando API...")
        try:
            r = requests.get(f"{API_URL}/health", timeout=3)
            if r.status_code == 200:
                st.write("✅ API disponible y respondiendo")
            else:
                st.write("⚠️ API respondió con error")
        except:
            st.write("❌ API no disponible (no se pudo conectar)")

        # definir estado final
        todo_ok = (os.path.exists(DATA_PATH) and os.path.exists(MODEL_PATH) and os.path.exists(DB_PATH))
        if todo_ok:
            status.update(label="✅ Pipeline completo", state="complete")
        else:
            status.update(label="⚠️ Pipeline incompleto - faltan archivos", state="error")


# --- Footer ---
st.markdown("---")
st.caption("Propiedades Chile v1.0 | SCY1101 - Programación para la Ciencia de Datos | "
           "Fabian Maulen, Evan Mardones, Joaquin Pastenes")
