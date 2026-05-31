# Implementación: Reintentos Automáticos con Backoff

**Fecha de implementación:** 2025-05-31  
**Mejora:** Fase 2 - Reintentos automáticos con backoff (mejora #3)  
**Estado:** ✅ Completada

---

## 📋 Resumen

Se ha implementado un sistema de reintentos automáticos con backoff exponencial que permite manejar fallos temporales de red automáticamente, mejorando la robustez del scraper sin requerir intervención manual.

---

## 🎯 Objetivos

1. ✅ Implementar decorador de reintentos con backoff
2. ✅ Configurar delays exponenciales (2s, 4s, 8s...)
3. ✅ Agregar jitter para evitar sincronización
4. ✅ Logging de cada intento
5. ✅ Configuración predefinida para API y base de datos
6. ✅ Excepción personalizada para todos los intentos fallidos

---

## 📦 Componentes Implementados

### 1. Decorador `retry_with_backoff`

**Módulo:** `apd_scrap/utils/retry.py`

**Características:**
- Backoff exponencial (1s, 2s, 4s, 8s, ...)
- Jitter aleatorio (80-120% del delay calculado)
- Número configurable de reintentos
- Delay máximo configurable
- Exceptions configurables por tipo

```python
@retry_with_backoff(
    max_retries=3,
    initial_delay=2.0,
    max_delay=30.0,
    backoff_factor=2.0,
    jitter=True,
    exceptions=(Timeout, ConnectionError, RequestException)
)
def fetch_data(url: str) -> dict:
    return requests.get(url, timeout=10)
```

**Algoritmo de Backoff:**
```
Intento 1: 1s delay
Intento 2: 2s delay (1 * 2.0)
Intento 3: 4s delay (2 * 2.0)
Intento 4: 8s delay (4 * 2.0)
Intento 5: 16s delay (8 * 2.0)...
Máximo: 30s
```

### 2. Excepción `RetryError`

**Propósito:** Indica que todos los intentos fallaron

```python
class RetryError(Exception):
    def __init__(self, message: str, attempts: int, last_exception: Optional[Exception] = None):
        self.message = message
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(self.message)
```

**Uso:**
```python
try:
    data = scraper.fetch_all_records('MERLO')
except RetryError as e:
    logger.critical(f"Error tras {e.attempts} intentos: {e.last_exception}")
```

### 3. Configuración `RetryConfig`

**Clase centralizada para reintentos:**

```python
class RetryConfig:
    API_HTTP: dict = {
        'max_retries': 3,
        'initial_delay': 2.0,
        'max_delay': 30.0,
        'backoff_factor': 2.0,
        'jitter': True
    }
    
    DATABASE: dict = {
        'max_retries': 3,
        'initial_delay': 1.0,
        'max_delay': 10.0,
        'backoff_factor': 2.0,
        'jitter': True
    }
```

---

## 🔧 Integración en el Scraper

### Modificación en `apd_scrap/scrapers/apd_scraper.py`

**Cambios:**

1. Import del decorador:
```python
from apd_scrap.utils.retry import retry_with_backoff, RetryError, RetryConfig
```

2. Decorador en `_fetch_data`:
```python
@retry_with_backoff(
    max_retries=3,
    initial_delay=2.0,
    max_delay=30.0,
    exceptions=(
        Timeout,
        ConnectionError,
        RequestException
    )
)
def _fetch_data(self, params: dict[str, Any]) -> Optional[dict[str, Any]]:
```

**Funcionalidad:**
- Reintenta automáticamente en timeout de red
- Reintenta en errores de conexión
- Jitter evita sincronización de reintentos
- Logging de cada intento para debugging

---

## 🚀 Uso del Sistema de Reintentos

### Ejemplo de Uso del Decorador

```python
from apd_scrap.utils.retry import retry_with_backoff, RetryError

# Uso simple
@retry_with_backoff(max_retries=3)
def obtener_datos_api(url: str) -> dict:
    return requests.get(url, timeout=10)

# Uso con configuración personalizada
@retry_with_backoff(
    max_retries=5,
    initial_delay=1.0,
    max_delay=60.0,
    backoff_factor=2.0,
    jitter=True,
    exceptions=(Timeout, ConnectionError)
)
def obtener_datos_api(url: str) -> dict:
    return requests.get(url, timeout=10)
```

### Ejemplo de Manejo de Errores

```python
from apd_scrap.utils.retry import retry_with_backoff, RetryError

try:
    data = fetch_data('https://api.example.com')
except RetryError as e:
    print(f"Fallo tras {e.attempts} intentos: {e.last_exception}")
```

---

## 📊 Logs de Reintentos

### Ejemplo de salida con reintentos:

```
2025-05-31 13:43:55 - APD_scrap - INFO - Distrito MORON seleccionado
2025-05-31 13:43:55 - apd_scrap.scrapers.apd_scraper - INFO - Distrito MORON: se encontraron 3600 registros.
2025-05-31 13:43:55 - apd_scrap.scrapers.apd_scraper - INFO - Obteniendo todos...
```

### En caso de fallo de red (ejemplo simulado):

```
Intento 1/3 falló para fetch_all_records: ConnectionError('...')
Reintentando en 2.0s...
Intento 2/3 falló para fetch_all_records: ConnectionError('...')
Reintentando en 4.0s...
Intento 3/3 falló para fetch_all_records: ConnectionError('...')
```

---

## 🎯 Casos de Uso

### 1. Fallos de Timeout

```python
@retry_with_backoff(
    max_retries=3,
    initial_delay=2.0,
    max_delay=30.0,
    exceptions=(requests.Timeout,)
)
def fetch_data(url: str) -> dict:
    return requests.get(url, timeout=10)
```

### 2. Conexiones Inestables

```python
@retry_with_backoff(
    max_retries=3,
    exceptions=(requests.ConnectionError,)
)
def establish_connection(url: str):
    return requests.get(url)
```

### 3. Reintentos para Base de Datos

```python
from apd_scrap.utils.retry import retry_with_backoff, RetryConfig

@retry_with_backoff(**RetryConfig.DATABASE)
def save_to_db(data: dict) -> bool:
    with sqlite3.connect('apd.db') as conn:
        # ... lógica de guardado
        pass
```

---

## 🔧 Configuración

### Configuración de API HTTP

```python
RetryConfig.API_HTTP = {
    'max_retries': 3,
    'initial_delay': 2.0,    # 2 segundos iniciales
    'max_delay': 30.0,      # Máximo 30 segundos
    'backoff_factor': 2.0,  # Duplicar delay cada intento
    'jitter': True          # Añadir aleatoriedad
}
```

### Configuración de Base de Datos

```python
RetryConfig.DATABASE = {
    'max_retries': 3,
    'initial_delay': 1.0,    # 1 segundo inicial
    'max_delay': 10.0,      # Máximo 10 segundos
    'backoff_factor': 2.0,      # Duplicar delay cada intento
    'jitter': True          # Añadir aleatoriedad
}
```

---

## 📊 Progreso Fase 2

| Mejora | Estado |
|--------|--------|
| 1. Type hints y docstrings | ✅ Completado |
| 2. Pre-commit hooks y linting | ✅ Completado |
| 3. Reintentos automáticos con backoff | ✅ Completado |
| 4. Variables de entorno | ✅ Ya implementado (Fase 1) |
| 5. CLI mejorado | ⏳ Próximo |
| 6. Índices en base de datos | ⏳ Pendiente |
| 7. CI/CD con GitHub Actions | ⏳ Pendiente |

**Fase 2:** 3/7 mejoras completadas

---

## 📝 Archivos Creados

### Nuevos archivos:
- `apd_scrap/utils/retry.py` - Sistema de reintentos
- `docs/IMPLEMENTACION_REINTENTOS.md` - Esta documentación

### Modificados:
- `apd_scrap/utils/__init__.py` - Exportaciones actualizadas
- `apd_scrap/scrapers/apd_scraper.py` - Integración de reintentos en scraper

---

## 🎯 Beneficios Logrados

| Aspecto | Mejora |
|---------|--------|
| **Robustez** | Reintentos automáticos por fallos temporales |
| **Logging** | Cada intento es loggeado para debugging |
| **Jitter** | Evita sincronización en reintentos |
| **Configurable** | Diferentes configuraciones por componente |
| **Excepciones** | RetryError para manejo centralizado |
| **Backoff** 1s, 2s, 4s, 8s, 16s... 30s máximo |
| **Manejo de errores** | Centralizado y consistente |

---

## ✨ Conclusión

La implementación de reintentos automáticos con backoff ha sido **exitosa**. El proyecto ahora cuenta con:

- **Decorador @retry_with_backoff** configurable
- **RetryException** para fallos tras reintentos
- **RetryConfig** para configuración centralizada
- **Backoff exponencial** (1s → 2s → 4s → 8s → 16s...)
- **Jitter aleatorio** (80-120%)
- **Logging de intentos** para debugging

**Funcionalidad probada:**
- ✅ Scraper funciona correctamente
- ✅ Sistema de reintentos en su lugar
- ✅ Prueba exitosa con distrito MORON (3600 registros)

**Estado:** ✅ **LISTO PARA LA SIGUIENTE MEJORA (CLI mejorado)**

---

**Generado:** 2025-05-31  
**Versión:** 2.4.0