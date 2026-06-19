# Guía de Ejecución — Computador de la Universidad (U)

Esta guía explica paso a paso cómo clonar, configurar y ejecutar el proyecto completo en las computadoras de la universidad. Dado que las PC de los laboratorios suelen tener restricciones de permisos, se presentan dos métodos: **Método A (Recomendado sin Docker)** y **Método B (Con Docker)**.

---

## Preparación Inicial

1. **Abrir la terminal:**
   * En Windows: Presiona `Windows + R`, escribe `powershell` o `cmd` y presiona Enter.

2. **Clonar el repositorio:**
   ```bash
   git clone https://github.com/FMaulen/propiedades-chile.git
   cd propiedades-chile
   ```

---

## Método A: Ejecución Directa (Recomendado por si no hay Docker)

Este método solo requiere que la computadora tenga **Python 3.10+** instalado (habitual en laboratorios de computación).

### Paso 1: Crear y Activar un Entorno Virtual (Opcional pero Recomendado)
Esto evita problemas de permisos al instalar librerías.
```bash
# Crear entorno virtual llamado "env"
python -m venv env

# Activar el entorno
# En Windows (PowerShell):
.\env\Scripts\Activate.ps1
# En Windows (CMD):
.\env\Scripts\activate.bat
```

### Paso 2: Instalar las dependencias
```bash
pip install -r requirements.txt
```

### Paso 3: Inicializar la Base de Datos y ejecutar el ETL (Si es necesario)
*Nota: El repositorio ya incluye la base de datos y el dataset limpio, pero si te piden demostrar el funcionamiento del pipeline en vivo:*
```bash
# 1. Crear base de datos de comunas
python etl/init_db.py

# 2. Correr el pipeline ETL (limpieza, descarga de UF actual y combinación)
python etl/etl_pipeline.py
```

### Paso 4: Levantar la API REST
Abre una terminal activa (con el entorno activado) y ejecuta:
```bash
python api/api_app.py
```
* **Acceso:** Deja esta ventana abierta. La API estará corriendo en `http://localhost:8000`.
* **Documentación interactiva (Swagger):** Abre tu navegador en `http://localhost:8000/docs` para ver y probar los endpoints.

### Paso 5: Levantar el Dashboard Interactiva
Abre **otra terminal nueva**, entra a la carpeta del proyecto, activa el entorno (`.\env\Scripts\Activate.ps1`) y ejecuta:
```bash
streamlit run dashboards/dashboard.py
```
* **Acceso:** El navegador se abrirá automáticamente en `http://localhost:8501` mostrando el dashboard con todas sus vistas operativas.

---

## Método B: Ejecución con Docker (Si la PC de la U tiene Docker Desktop)

Este método es el más rápido ya que no requiere configurar Python ni instalar librerías en la máquina host.

1. **Asegúrate de que Docker Desktop esté abierto y corriendo.**
2. **Navegar a la carpeta `docker`:**
   ```bash
   cd docker
   ```
3. **Levantar los servicios:**
   ```bash
   docker-compose up --build
   ```
   *(Este comando descargará las imágenes base, instalará dependencias dentro de los contenedores y levantará la API y el Dashboard en paralelo).*
4. **Acceder a las aplicaciones:**
   * **Dashboard:** Abre en el navegador: `http://localhost:8501`
   * **API REST & Swagger:** Abre en el navegador: `http://localhost:8000/docs`
5. **Apagar los servicios al terminar:**
   Presiona `Ctrl + C` en la terminal, o corre:
   ```bash
   docker-compose down
   ```

---

## Solución de Problemas Comunes (Troubleshooting en la U)

* **Error de permisos en PowerShell (`Script Execution Policy`):**
  Si al intentar activar el entorno virtual te aparece un error rojo de permisos, ejecuta este comando en PowerShell para habilitar la ejecución en tu sesión actual:
  ```powershell
  Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
  ```
  Luego vuelve a intentar activar el entorno: `.\env\Scripts\Activate.ps1`

* **Puerto ocupado (8000 o 8501):**
  Si otra persona usó la computadora antes y dejó los puertos ocupados, puedes forzar el cierre de los procesos o cambiar los puertos.
  * *Para Streamlit:* Puedes cambiar el puerto al ejecutarlo:
    ```bash
    streamlit run dashboards/dashboard.py --server.port 8502
    ```
