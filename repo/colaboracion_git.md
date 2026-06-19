# Colaboración Git

Documento que describe cómo trabajamos con Git en el proyecto.

## Estrategia de Ramas

Usamos el siguiente esquema de ramas:

- **main**: Rama principal, solo código estable y funcional. No se hace push directo acá.
- **develop**: Rama de desarrollo donde se integran las features. Los PRs van acá.
- **feature/xxx**: Ramas individuales para cada feature o tarea.

### Ejemplos de ramas feature

```
feature/etl-pipeline
feature/modelo-xgboost
feature/dashboard-mapas
feature/api-endpoints
feature/docker-setup
fix/limpieza-outliers
docs/manual-usuario
```

## Convención de Commits

Usamos prefijos pa que los commits sean más claros:

| Prefijo | Uso |
|---|---|
| `feat:` | Nueva funcionalidad |
| `fix:` | Corrección de bugs |
| `docs:` | Cambios en documentación |
| `refactor:` | Refactorización de código |
| `test:` | Agregar o modificar tests |
| `data:` | Cambios en datos o ETL |
| `style:` | Cambios de formato (no afectan lógica) |

### Ejemplos

```
feat: agregar endpoint de prediccion
fix: corregir filtro de outliers en ETL
docs: actualizar manual de usuario
data: agregar CSV de noviembre 2024
test: agregar tests para la API
refactor: separar funciones de limpieza
```

## Flujo de Trabajo

1. Cada integrante trabaja en su propia rama `feature/xxx`
2. Cuando termina, hace push y crea un **Pull Request** a `develop`
3. Al menos otro integrante revisa el PR
4. Si está todo bien, se mergea a `develop`
5. Cuando `develop` está estable, se mergea a `main`

```
main ←── develop ←── feature/etl-pipeline
                 ←── feature/modelo-ml
                 ←── feature/dashboard
```

### Pasos concretos

```bash
# 1. Crear rama desde develop
git checkout develop
git pull
git checkout -b feature/mi-feature

# 2. Trabajar y hacer commits
git add .
git commit -m "feat: descripcion de lo que hice"

# 3. Push y crear PR
git push origin feature/mi-feature
# ir a GitHub y crear el Pull Request a develop

# 4. Despues del merge, volver a develop
git checkout develop
git pull
```

## Integrantes del Equipo

| Integrante | Rol Principal | Área |
|---|---|---|
| Fabian Maulen | ETL y Datos | Pipeline de datos, scraping, limpieza |
| Evan Mardones | Modelos ML y API | Entrenamiento de modelos, endpoints API |
| Joaquin Pastenes | Dashboard y Docker | Visualización, contenedores, deploy |

## Tabla de Contribuciones

Contribución aproximada de cada integrante por área:

| Área | Fabian Maulen | Evan Mardones | Joaquin Pastenes |
|---|---|---|---|
| ETL / Datos | 70% | 15% | 15% |
| Modelos ML | 15% | 70% | 15% |
| API | 10% | 65% | 25% |
| Dashboard | 10% | 15% | 75% |
| Docker / Deploy | 10% | 20% | 70% |
| Documentación | 35% | 35% | 30% |
| Tests | 30% | 40% | 30% |

> **Nota**: Los porcentajes son aproximados y pueden variar. Todos colaboramos en todas las áreas en mayor o menor medida.

## Resolución de Conflictos

Si hay conflictos de merge:

1. El que creó el PR los resuelve
2. Si es complicado, se juntan los involucrados a resolverlo
3. Siempre testear después de resolver conflictos

## Reglas Básicas

- **No hacer push directo a main** (nunca jamás)
- Hacer commits chicos y frecuentes (no un commit gigante al final)
- Escribir mensajes de commit descriptivos
- Hacer pull de develop antes de crear una rama nueva
- Avisar al grupo cuando se mergea algo importante
