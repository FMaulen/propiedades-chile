# Manual de Usuario

Guía pa instalar y correr el proyecto de predicción de precios de propiedades en Santiago.

## Requisitos Previos

Antes de empezar necesitas tener instalado:

- **Python 3.11** o superior
- **pip** (viene con Python)
- **Git** para clonar el repo
- **Docker y Docker Compose** (opcional, pero recomendado)

Para verificar que tengas todo:

```bash
python --version
pip --version
git --version
docker --version          # opcional
docker-compose --version  # opcional
```

## Instalación Paso a Paso

### 1. Clonar el repositorio

```bash
git clone https://github.com/tu-usuario/propiedades-chile.git
cd propiedades-chile
```

### 2. Crear entorno virtual

```bash
python -m venv venv

# En Windows:
venv\Scripts\activate

# En Linux/Mac:
source venv/bin/activate
```

### 3. Instalar dependencias

```bash
pip install -r requirements.txt
```

Si hay requirements separados por módulo:

```bash
pip install -r api/requirements.txt
pip install -r dashboards/requirements.txt
```

## Cómo Ejecutar el ETL

El pipeline ETL limpia los datos crudos y los deja listos pa usar.

```bash
# Asegurate de tener los CSVs en data/raw/
python etl/etl_pipeline.py
```

Esto va a:
1. Leer los CSV de `data/raw/`
2. Obtener el valor de la UF actual
3. Limpiar y procesar los datos
4. Guardar el resultado en `data/processed/`

> **Nota**: Necesitas conexión a internet pa obtener el valor de la UF desde mindicador.cl

## Cómo Levantar la API

```bash
python api/api_app.py
```

La API va a quedar corriendo en `http://localhost:8000`

Para probar que funcione, abre en el navegador:
- `http://localhost:8000/` - Info del proyecto
- `http://localhost:8000/health` - Health check
- `http://localhost:8000/docs` - Documentación interactiva (Swagger)

## Cómo Levantar el Dashboard

```bash
streamlit run dashboards/dashboard.py
```

El dashboard va a abrir automáticamente en `http://localhost:8501`

> **Importante**: La API tiene que estar corriendo primero si el dashboard la usa pa predicciones.

## Cómo Usar Docker Compose

Si preferis no instalar nada localmente, podis usar Docker:

### 1. Configurar variables de entorno

```bash
cd docker
cp .env.example .env
```

Edita el `.env` si necesitas cambiar algo (generalmente no es necesario).

### 2. Levantar todo

```bash
cd docker
docker-compose up --build
```

Esto levanta la API y el dashboard juntos. La primera vez va a demorar un poco porque tiene que construir las imágenes.

### 3. Acceder a los servicios

- API: `http://localhost:8000`
- Dashboard: `http://localhost:8501`

### 4. Para bajar los servicios

```bash
docker-compose down
```

## Troubleshooting Básico

### "ModuleNotFoundError: No module named ..."

Probablemente no instalaste las dependencias. Asegúrate de tener el venv activado y corre:

```bash
pip install -r requirements.txt
```

### "No se pudo obtener el valor de la UF"

Revisa tu conexión a internet. La API de mindicador.cl tiene que estar accesible. Si no funciona, el sistema usa un valor por defecto de UF (definido en .env como `UF_DEFAULT`).

### "FileNotFoundError: data/raw/..."

No tienes los archivos CSV de datos. Pídelos al equipo o córrelos desde el scraper si existe.

### El dashboard no conecta con la API

Verifica que la API esté corriendo primero. Si usas Docker, revisa que ambos contenedores estén up con:

```bash
docker-compose ps
```

### Puerto ocupado

Si el puerto 8000 u 8501 ya está en uso:

```bash
# En Windows, busca qué lo está usando:
netstat -ano | findstr :8000

# Mata el proceso o cambia el puerto en el .env
```

### Docker no encuentra los archivos

Asegurate de correr `docker-compose` desde la carpeta `docker/` y que los datos estén en su lugar.
