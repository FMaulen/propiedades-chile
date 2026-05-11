# Predictor de Precios de Casas - Region Metropolitana

Analisis de precios de propiedades en la Region Metropolitana usando machine learning. Este proyecto compara diferentes modelos para predecir precios de casas basandose en sus caracteristicas.

## Estructura del Proyecto

```
├── data/
│   ├── raw/                          # Datos originales
│   └── processed/                    # Datos limpios
├── notebooks/
│   └── EDA_Analysis.ipynb           # Analisis exploratorio
├── src/
│   ├── train_models.py              # Entrenar modelos
│   ├── evaluate_models.py           # Evaluar modelos
│   ├── simple_optimization.py       # Mejorar modelos
│   ├── unsupervised_models.py       # Clustering y KNN
│   └── confusion_matrix.py          # Matriz de confusion
├── models/trained_models/           # Modelos guardados
├── results/
│   ├── metrics/                     # Resultados numericos
│   └── plots/                       # Graficos
├── environment.yml                  # Entorno virtual
└── README.md
```

## Como usar este proyecto

### Crear entorno virtual con CONDA
```bash
conda env create -f environment.yml
conda activate propiedades-chile
```

### Ejecutar el pipeline completo
```bash
# 1. Limpiar datos
python Script/MainScript.py

# 2. Entrenar modelos
cd src
python train_models.py

# 3. Evaluar que tan buenos son
python evaluate_models.py

# 4. Mejorar el mejor modelo
python simple_optimization.py

# 5. Hacer clustering
python unsupervised_models.py

# 6. Crear matriz de confusion
python confusion_matrix.py
```

## Modelos implementados

### Modelos supervisados (predicen precios)
- **Regresion Lineal**: Modelo basico
- **Random Forest**: Mejor modelo (R2 = 0.688)
- **Gradient Boosting**: Modelo alternativo
- **KNN**: Prediccion por vecinos cercanos

### Modelos no supervisados (encuentran patrones)
- **K-Means**: Agrupa propiedades similares en 4 grupos
- **Clasificador**: Predice categoria de precio con matriz de confusion

## Resultados principales

| Modelo | Precision R2 | Error Promedio (UF) | Estado |
|-------|-------------|---------------------|---------|
| Regresion Lineal | -1.777 | 3,652 | Fallo |
| Random Forest | 0.848 | 1,989 | Bueno |
| Gradient Boosting | 0.837 | 2,182 | Bueno |
| Random Forest Mejorado | 0.688 | 2,917 | Mejor |
| KNN | 0.654 | 3,350 | Decente |

### Grupos de propiedades encontrados
- **Grupo 1**: 5,299 propiedades economicas (5,665 UF promedio, 115m2)
- **Grupo 2**: 1,735 propiedades premium (21,590 UF promedio, 318m2)
- **Grupo 3**: 3 propiedades ultra-lujo (21,845 UF promedio, 21,816m2)
- **Grupo 4**: 231 propiedades de alto valor (27,765 UF promedio, 665m2)

## Simulacion de cambios en vivo

Casa ejemplo: 120m2, 3 dormitorios, 2 banos = **3,334 UF**

Efectos de modificaciones:
- Agregar 20m2: **5,386 UF** (+2,052 UF)
- Agregar 1 dormitorio: **3,586 UF** (+251 UF)
- Agregar 1 bano: **5,674 UF** (+2,340 UF)
- Agregar 1 estacionamiento: **6,214 UF** (+2,879 UF)

## Informacion del dataset

- **Fuente**: Web scraping de portales inmobiliarios de la RM
- **Periodo**: Marzo - Julio 2023
- **Propiedades finales**: 7,268 (despues de limpiar)
- **Variables**: Precio UF, Area construida, Area total, Dormitorios, Banos, Estacionamientos, Comuna

## Sobre el proyecto

Proyecto de analisis de datos del mercado inmobiliario chileno desarrollado como parte del aprendizaje en ciencia de datos y machine learning. El objetivo es demostrar la aplicacion practica de diferentes algoritmos de prediccion en un contexto real del mercado de propiedades.