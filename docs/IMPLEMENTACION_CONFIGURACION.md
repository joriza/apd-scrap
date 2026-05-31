# Implementación: Configuración Externa

**Fecha de implementación:** 2025-05-31  
**Mejora:** Fase 1 - Configuración externa  
**Estado:** ✅ Completada y probada

---

## 📋 Resumen

Se ha implementado un sistema de configuración flexible que permite configurar la aplicación desde múltiples fuentes: archivos YAML, variables de entorno y valores por defecto, con una prioridad clara: **Entorno > YAML > Default**.

---

## 🎯 Objetivos

1. ✅ Soportar configuración desde archivos YAML
2. ✅ Soportar configuración desde variables de entorno (.env)
3. ✅ Mantener compatibilidad con código existente
4. ✅ Implementar validación de configuración
5. ✅ Soportar múltiples entornos (development, staging, production)
6. ✅ Mantener secretos fuera del código

---

## 📦 Componentes Implementados

### 1. Archivo de Configuración YAML

**`config.yaml`:**
```yaml
# API Configuration
api:
  base_url: "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
  timeout: 60

# Database Configuration
database:
  path: "apd.db"
  batch_size: 1000

# Logging Configuration
logging:
  name: "apd_scrap"
  level: "INFO"
  file: "apd_scrap.log"
  max_bytes: 5242880  # 5MB
  backup_count: 3
  console_output: true

# Output Configuration
output:
  directory: "."
  format: "json"
  pretty_print: true

# SSL Configuration
ssl:
  ciphers: "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:..."

# Environment
environment: "development"
```

### 2. Archivo de Variables de Entorno

**`.env.example`:**
```bash
# API Configuration
APD_API_URL=https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select
APD_API_TIMEOUT=60

# Database Configuration
APD_DB_PATH=apd.db

# Logging Configuration
APD_LOG_NAME=apd_scrap
APD_LOG_LEVEL=INFO
APD_LOG_FILE=apd_scrap.log
APD_LOG_MAX_BYTES=5242880
APD_LOG_BACKUP_COUNT=3
APD_LOG_CONSOLE_OUTPUT=true

# Output Configuration
APD_OUTPUT_DIR=.

# Environment
APD_ENVIRONMENT=development
```

### 3. Clase Config Mejorada

**`apd_scrap/config.py`:**

**Nuevas características:**

- **Carga desde múltiples fuentes:**
  - Valores por defecto
  - Archivo YAML
  - Variables de entorno (.env)

- **Prioridad de configuración:**
  ```
  Entorno > YAML > Default
  ```

- **Método `get()` con notación de puntos:**
  ```python
  config.get('api.timeout')  # Devuelve 60
  config.get('database.path')  # Devuelve "apd.db"
  ```

- **Validación de configuración:**
  ```python
  config.validate()  # Lanza ConfigError si hay problemas
  ```

- **Clase `ConfigError` personalizada:**
  ```python
  from apd_scrap.config import ConfigError
  ```

---

## 🔧 Uso del Sistema de Configuración

### Básico

```python
from apd_scrap.config import Config

# Usa valores por defecto, config.yaml y .env
config = Config()

print(config.API_BASE_URL)
print(config.API_TIMEOUT)
```

### Con Archivo YAML Personalizado

```python
# Usa config_personalizado.yaml en lugar de config.yaml
config = Config(config_path="config_personalizado.yaml")
```

### Solo Variables de Entorno

```python
# Solo usa variables de entorno (sin YAML)
config = Config(config_path=None)
```

### Sobrescritura con Variables de Entorno

```bash
# En archivo .env
APD_API_TIMEOUT=120
APD_LOG_LEVEL=DEBUG

# En código
config = Config()
# config.API_TIMEOUT será 120 (ENV > YAML > Default)
```

---

## 📊 Prioridad de Configuración

### Ejemplo Práctico

**Valores definidos:**
```yaml
# config.yaml
api:
  timeout: 90
```

```bash
# .env
APD_API_TIMEOUT=45
```

```python
# Código (valores por defecto)
DEFAULT_CONFIG = {
    'api': {'timeout': 60}
}
```

**Resultado:**
```python
config = Config()
print(config.API_TIMEOUT)  # 45 (ENV tiene prioridad)
```

### Prioridad Explícita

```
1. Variables de entorno (.env)        [MAYOR]
2. Archivo YAML (config.yaml)
3. Valores por defecto                [MENOR]
```

---

## 🧪 Pruebas Implementadas

### `test_config.py` - Suite de Pruebas de Configuración

| Test | Estado | Descripción |
|------|--------|-------------|
| Configuración por Defecto | ✅ | Valores hardcoded funcionan |
| Configuración desde YAML | ✅ | Carga y fusión desde YAML |
| Sobrescritura con Variables de Entorno | ✅ | ENV sobrescribe YAML |
| Método get() con Notación de Puntos | ✅ | Acceso anidado a config |
| Validación de Configuración | ✅ | Detección de valores inválidos |
| Prioridad de Configuración | ✅ | ENV > YAML > Default |
| Compatibilidad con Código Existente | ✅ | Atributos expuestos correctamente |

**Resultado:** 7/7 pruebas pasadas exitosamente.

---

## 📝 Métodos Disponibles

### `get(key, default=None)`

Obtiene un valor usando notación de puntos.

```python
config.get('api.timeout')           # 60
config.get('database.path')         # "apd.db"
config.get('logging.level')         # "INFO"
config.get('nonexistent', 'default') # "default"
```

### `validate()`

Valida la configuración actual.

```python
try:
    config.validate()
    print("Configuración válida")
except ConfigError as e:
    print(f"Error: {e}")
```

### `get_api_query_params(distrito, rows=0)`

Genera parámetros de consulta para la API.

```python
params = config.get_api_query_params('merlo', rows=10)
# {'q': '*:*', 'fq': 'descdistrito:MERLO', 'wt': 'json', 'rows': 10}
```

### `get_output_filename(distrito)`

Genera nombre de archivo de salida.

```python
filename = config.get_output_filename('merlo')
# "output_merlo.json"
```

---

## 🔐 Seguridad

### Variables de Entorno

Las variables de entorno tienen la **mayor prioridad** y son ideales para:

- **Secretos:** Tokens, contraseñas, claves API
- **Configuración por entorno:** Diferentes settings para dev/staging/prod
- **Override rápido:** Cambios sin modificar archivos

### Archivo .env

**Estructura:**
```bash
# Copia .env.example a .env
cp .env.example .env

# Editar .env con tus valores
APD_DB_PATH=/path/to/database.db
APD_LOG_LEVEL=DEBUG
```

**Ignorado por Git:**
```gitignore
.env
.env.*
!.env.example
```

---

## 🌍 Configuración por Entorno

### Development

**`config.yaml`:**
```yaml
environment: "development"
logging:
  level: "DEBUG"
  console_output: true
```

### Production

**`.env`:**
```bash
APD_ENVIRONMENT=production
APD_LOG_LEVEL=WARNING
APD_LOG_CONSOLE_OUTPUT=false
APD_DB_PATH=/var/lib/apd-scrap/apd.db
```

### Staging

**`config_staging.yaml`:**
```yaml
environment: "staging"
database:
  path: "/tmp/apd_staging.db"
logging:
  level: "INFO"
```

```python
# Usar configuración específica de staging
config = Config(config_path="config_staging.yaml")
```

---

## 📋 Variables de Entorno Soportadas

| Variable | Descripción | Default |
|----------|-------------|---------|
| `APD_API_URL` | URL base de la API | URL del gobierno |
| `APD_API_TIMEOUT` | Timeout de solicitudes (segundos) | 60 |
| `APD_DB_PATH` | Ruta a la base de datos | `apd.db` |
| `APD_LOG_NAME` | Nombre del logger | `apd_scrap` |
| `APD_LOG_LEVEL` | Nivel de logging | `INFO` |
| `APD_LOG_FILE` | Archivo de log | `apd_scrap.log` |
| `APD_LOG_MAX_BYTES` | Tamaño máximo de log (bytes) | 5242880 |
| `APD_LOG_BACKUP_COUNT` | Número de backups de log | 3 |
| `APD_LOG_CONSOLE_OUTPUT` | Output a consola | `true` |
| `APD_OUTPUT_DIR` | Directorio de salida | `.` |
| `APD_ENVIRONMENT` | Entorno actual | `development` |

---

## ✅ Compatibilidad con Código Existente

Todos los atributos existentes siguen funcionando:

```python
config = Config()

# Estos atributos siguen existiendo
config.API_BASE_URL
config.API_TIMEOUT
config.DB_PATH
config.LOG_NAME
config.LOG_LEVEL
config.LOG_FILE
config.LOG_MAX_BYTES
config.LOG_BACKUP_COUNT
config.LOG_CONSOLE_OUTPUT
config.OUTPUT_DIR
config.CIPHERS
config.ENVIRONMENT
```

---

## 🔄 Dependencias Agregadas

**`requirements.txt`:**
```txt
requests>=2.31.0
pyyaml>=6.0.1
python-dotenv>=1.0.0
```

---

## 📊 Comparación Antes/Después

### Antes

```python
# Configuración hardcoded en código
API_BASE_URL = "https://servicios3.abc.gob.ar/..."
API_TIMEOUT = 60
LOG_LEVEL = logging.INFO
# ...
```

**Problemas:**
- ❌ Difícil cambiar configuración
- ❌ Sin soporte para múltiples entornos
- ❌ Valores sensibles en código
- ❌ Requiere recompilar para cambios

### Después

```python
# Configuración flexible desde múltiples fuentes
config = Config()
# Carga automáticamente desde config.yaml y .env

# O configuración personalizada
config = Config(config_path="prod.yaml")
```

**Beneficios:**
- ✅ Fácil cambiar configuración sin código
- ✅ Soporte para múltiples entornos
- ✅ Secretos fuera del código
- ✅ Cambios en tiempo de ejecución

---

## 🧪 Ejemplos de Uso

### Cambiar Nivel de Logging

**Opción 1: YAML**
```yaml
logging:
  level: "DEBUG"
```

**Opción 2: .env**
```bash
APD_LOG_LEVEL=DEBUG
```

**Opción 3: Código**
```python
config = Config()
# config.LOG_LEVEL será el valor más alto de prioridad
```

### Usar Base de Datos Personalizada

```bash
# .env
APD_DB_PATH=/custom/path/database.db
```

### Desactivar Logging por Consola

```bash
APD_LOG_CONSOLE_OUTPUT=false
```

### Timeout Personalizado por Entorno

**Development:**
```yaml
api:
  timeout: 30  # Respuesta rápida durante desarrollo
```

**Production:**
```bash
APD_API_TIMEOUT=120  # Timeout más largo en producción
```

---

## 📈 Beneficios Logrados

| Aspecto | Mejora |
|---------|--------|
| **Flexibilidad** | Múltiples fuentes de configuración |
| **Seguridad** | Secretos en variables de entorno |
| **Mantenibilidad** | Configuración separada del código |
| **Portabilidad** | Fácil cambiar entre entornos |
| **Validación** | Detección de configuraciones inválidas |
| **Compatibilidad** | 100% compatible con código existente |
| **Prioridad clara** | ENV > YAML > Default |

---

## 🔄 Progreso Fase 1

| Mejora | Estado |
|--------|--------|
| 1. Separar responsabilidades en módulos | ✅ Completado |
| 2. Sistema de logging estructurado | ✅ Completado |
| 3. Configuración externa | ✅ Completado |
| 4. Tests unitarios | ⏳ Siguiente |

---

## 📝 Archivos Creados/Modificados

### Nuevos archivos:
- `config.yaml` - Configuración YAML principal
- `.env.example` - Plantilla de variables de entorno
- `test_config.py` - Suite de pruebas de configuración
- `docs/IMPLEMENTACION_CONFIGURACION.md` - Esta documentación

### Modificados:
- `apd_scrap/config.py` - Sistema de configuración completo
- `requirements.txt` - Agregadas pyyaml y python-dotenv
- `.gitignore` - .env ignorado, config.yaml opcional

---

## 🚀 Siguiente mejora: Tests Unitarios

¿Deseas que continúe con la **Tests unitarios** (mejora #4 de Fase 1)? Esta mejora incluirá:

- Tests para todos los módulos
- Mocking de dependencias externas
- Tests de integración
- Cobertura de código >80%
- Ejecución automática en CI/CD

---

## ✨ Conclusión

La implementación del sistema de configuración externa ha sido **exitosa**. El sistema ahora cuenta con:

- **Configuración flexible** desde YAML y variables de entorno
- **Prioridad clara** de fuentes de configuración
- **Validación automática** de valores
- **Seguridad mejorada** con secretos fuera del código
- **Compatibilidad total** con código existente
- **Soporte multi-entorno** para development, staging, production

Todas las pruebas pasaron exitosamente y la funcionalidad es 100% compatible.

**Estado:** ✅ **LISTO PARA LA SIGUIENTE MEJORA**

---

**Generado:** 2025-05-31  
**Versión:** 2.2.0