# Predictor de Precios de Casas - Region Metropolitana

Proyecto de analisis y prediccion de precios de propiedades en la Region Metropolitana de Santiago usando machine learning.

**Asignatura:** Programacion para la Ciencia de Datos (SCY1101)

**Integrantes:**
- Fabian Maulen
- Evan Mardones
- Joaquin Pastenes

## Estructura del Proyecto

```
├── data/
│   ├── raw/                          # Datos originales (CSVs)
│   ├── processed/                    # Datos integrados y limpios
│   └── comunas.db                    # Base de datos SQLite de comunas
├── etl/
│   ├── init_db.py                    # Crear base de datos de comunas
│   └── etl_pipeline.py              # Pipeline ETL completo
├── notebooks/
│   ├── EDA_Analysis.ipynb            # Analisis exploratorio
│   ├── ML_Complete_Analysis.ipynb    # Analisis de ML
│   └── Presentacion_Final.ipynb      # Presentacion
├── src/
│   ├── train_models.py               # Entrenar modelos
│   ├── evaluate_models.py            # Evaluar modelos
│   ├── simple_optimization.py        # Optimizar modelos
│   ├── unsupervised_models.py        # Clustering y KNN
│   └── confusion_matrix.py           # Matriz de confusion
├── api/
│   └── api_app.py                    # API REST con FastAPI
├── dashboards/
│   └── dashboard.py                  # Dashboard Streamlit
├── docker/
│   ├── Dockerfile.api                # Contenedor API
│   ├── Dockerfile.dashboard          # Contenedor Dashboard
│   └── docker-compose.yml            # Orquestacion
├── tests/
│   ├── test_etl.py                   # Tests del ETL
│   └── test_api.py                   # Tests de la API
├── docs/
│   ├── architecture.md               # Arquitectura del proyecto
│   └── user_manual.md                # Manual de usuario
├── repo/
│   └── colaboracion_git.md           # Evidencia trabajo en equipo
├── models/trained_models/            # Modelos guardados (.pkl)
├── results/                          # Resultados y graficos
├── environment.yml                   # Entorno Conda
├── requirements.txt                  # Dependencias pip
└── README.md
```

## Requisitos

- Python 3.11+
- pip o conda

## Instalacion rapida

```bash
# Clonar el repo
git clone https://github.com/FMaulen/propiedades-chile.git
cd propiedades-chile

# Instalar dependencias
pip install -r requirements.txt
```

## Como ejecutar el proyecto

### 1. Preparar la base de datos de comunas
```bash
python etl/init_db.py
```

### 2. Ejecutar el pipeline ETL
```bash
python etl/etl_pipeline.py
```
Esto carga los CSVs, consulta la API de indicadores (UF), limpia los datos y genera el dataset integrado en `data/processed/`.

### 3. Entrenar los modelos
```bash
cd src
python train_models.py
python evaluate_models.py
python simple_optimization.py
python unsupervised_models.py
python confusion_matrix.py
cd ..
```

### 4. Levantar la API
```bash
python api/api_app.py
```
La API queda disponible en http://localhost:8000. Documentacion interactiva en http://localhost:8000/docs

### 5. Levantar el Dashboard
```bash
streamlit run dashboards/dashboard.py
```
El dashboard queda en http://localhost:8501

### 6. Con Docker (opcional)
```bash
cd docker
docker-compose up --build
```
Levanta la API y el Dashboard juntos en contenedores.

## Fuentes de datos del ETL

El pipeline integra 3 fuentes de datos diferentes:

1. **Archivos CSV**: Datos de propiedades obtenidos por web scraping de portales inmobiliarios (2023)
2. **API REST externa**: Valor actual de la UF desde [mindicador.cl](https://mindicador.cl/api/uf)
3. **Base de datos SQL**: Datos socioeconomicos de comunas de la RM (SQLite)

## Modelos implementados

### Supervisados (predicen precios)
| Modelo | R2 Score | Error Promedio (UF) |
|--------|----------|---------------------|
| Regresion Lineal | -1.777 | 3,652 |
| Random Forest | 0.848 | 1,989 |
| Gradient Boosting | 0.837 | 2,182 |
| Random Forest Mejorado | 0.688 | 2,917 |
| KNN | 0.654 | 3,350 |

### No supervisados
- **K-Means**: Agrupa propiedades en 4 clusters por precio y caracteristicas
- **Clasificador**: Random Forest para categorias de precio (Economica, Media, Alta, Premium)

## Endpoints de la API

| Metodo | Ruta | Descripcion |
|--------|------|-------------|
| GET | `/` | Info del proyecto y autores |
| GET | `/health` | Estado del sistema |
| GET | `/indicators` | Valor actual de la UF |
| GET | `/communes` | Datos de comunas de la RM |
| POST | `/predict` | Predecir precio de una propiedad |

## Tests

```bash
pytest tests/ -v
```

## Informacion del dataset

- **Fuente**: Web scraping de portales inmobiliarios de la RM
- **Periodo**: Marzo - Julio 2023
- **Propiedades**: ~7,268 (despues de limpieza)
- **Variables**: Precio UF, Area construida, Area total, Dormitorios, Banos, Estacionamientos, Comuna