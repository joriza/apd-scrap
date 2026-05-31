# Implementación: Sistema de Logging Estructurado

**Fecha de implementación:** 2025-05-31  
**Mejora:** Fase 1 - Sistema de logging estructurado  
**Estado:** ✅ Completada y probada

---

## 📋 Resumen

Se ha implementado un sistema de logging estructurado que reemplaza los `print()` statements por un sistema de logging profesional con niveles, rotación de archivos y formato consistente.

---

## 🎯 Objetivos

1. ✅ Reemplazar `print()` por logging estructurado
2. ✅ Implementar niveles de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
3. ✅ Configurar rotación de archivos (5MB, 3 backups)
4. ✅ Formato consistente con timestamps
5. ✅ Logging tanto a consola como a archivo
6. ✅ LoggerMixin para fácil integración en clases

---

## 📦 Componentes Implementados

### 1. `apd_scrap/utils/logging.py` - Módulo de Logging

**Funciones principales:**

#### `setup_logging()`
Configura el sistema de logging completo.

```python
def setup_logging(
    name: str = "apd_scrap",
    log_level: int = logging.INFO,
    log_file: str = "apd_scrap.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    console_output: bool = True
) -> logging.Logger
```

**Características:**
- Formato: `YYYY-MM-DD HH:MM:SS - nombre - nivel - mensaje`
- Rotación automática cuando el archivo alcanza 5MB
- Máximo 3 archivos de respaldo (apd_scrap.log.1, .2, .3)
- Output a consola y/o archivo
- UTF-8 encoding para caracteres especiales

#### `get_logger()`
Obtiene un logger existente o crea uno nuevo.

```python
logger = get_logger("mi_modulo")
```

#### `LoggerMixin`
Mixin para añadir logging a cualquier clase automáticamente.

```python
class MiClase(LoggerMixin):
    def metodo(self):
        self.logger.info("Método ejecutado")
```

---

### 2. Configuración en `apd_scrap/config.py`

**Nuevos parámetros:**

```python
# Logging Configuration
LOG_NAME: str = "apd_scrap"
LOG_LEVEL: int = logging.INFO
LOG_FILE: str = "apd_scrap.log"
LOG_MAX_BYTES: int = 5 * 1024 * 1024  # 5MB
LOG_BACKUP_COUNT: int = 3
LOG_CONSOLE_OUTPUT: bool = True
```

---

### 3. Actualización de Módulos

#### `apd_scrap/database/connection.py`
- Hereda de `LoggerMixin`
- Usa `self.logger.error()` para errores
- Usa `self.logger.warning()` para advertencias
- Usa `self.logger.info()` para información
- Mensajes con contexto de distrito

**Antes:**
```python
print("No hay ofertas para guardar en la base de datos.")
print(f"Error al inicializar el esquema: {e}")
```

**Después:**
```python
self.logger.warning("No hay ofertas para guardar en la base de datos.")
self.logger.error(f"Error al inicializar el esquema: {e}")
```

#### `apd_scrap/scrapers/apd_scraper.py`
- Hereda de `LoggerMixin`
- Logging de progreso de scraping
- Logging de errores HTTP y JSON
- Logging de guardado de archivos

**Antes:**
```python
print(f"No se encontraron registros para el distrito {distrito}.")
print(f"Ocurrió un error en la solicitud HTTP: {e}")
print(f"\n¡Éxito! {num_docs} registros guardados en '{filename}'.")
```

**Después:**
```python
self.logger.warning(f"No se encontraron registros para el distrito {distrito}.")
self.logger.error(f"Ocurrió un error en la solicitud HTTP: {e}")
self.logger.info(f"Archivos JSON: {num_docs} registros guardados en '{filename}'.")
```

#### `main.py`
- Configura logging al inicio
- Logging de inicio y fin de ejecución
- Manejo de excepciones críticas

```python
# Configurar logging
config = Config()
logger = setup_logging(
    name=config.LOG_NAME,
    log_level=config.LOG_LEVEL,
    log_file=config.LOG_FILE,
    max_bytes=config.LOG_MAX_BYTES,
    backup_count=config.LOG_BACKUP_COUNT,
    console_output=config.LOG_CONSOLE_OUTPUT
)

logger.info(f"APD-Scrap iniciado - Distrito: {distrito}")
# ...
logger.info("APD-Scrap finalizado exitosamente")
```

---

## 🧪 Pruebas Implementadas

### `test_logging.py` - Suite de Pruebas de Logging

| Test | Estado | Descripción |
|------|--------|-------------|
| Logging Básico | ✅ | Verifica niveles INFO, WARNING, ERROR, CRITICAL |
| Niveles de Logging | ✅ | Filtrado por nivel (DEBUG no muestra si nivel=INFO) |
| Obtener Logger Existente | ✅ | Reutilización de loggers |
| LoggerMixin | ✅ | Integración en clases |
| Logging a Archivo | ✅ | Verifica que los logs se guarden |
| Logging por Consola | ✅ | Output a stdout |

**Resultado:** 6/6 pruebas pasadas exitosamente.

---

## 📊 Comparación Antes/Después

### Antes

```python
# En main.py
print(f"Distrito seleccionado: {distrito}\n")

# En scraper
print(f"Se encontraron {total} registros. Obteniendo todos...")
print(f"Ocurrió un error en la solicitud HTTP: {e}")

# En database
print("No hay ofertas para guardar en la base de datos.")
print(f"Se han guardado/actualizados {registros_guardados} registros en 'apd.db'.")
```

### Después

```python
# En main.py
logger.info(f"APD-Scrap iniciado - Distrito: {distrito}")

# En scraper
self.logger.info(f"Distrito {distrito}: se encontraron {total} registros. Obteniendo todos...")
self.logger.error(f"Ocurrió un error en la solicitud HTTP: {e}")

# En database
self.logger.warning("No hay ofertas para guardar en la base de datos.")
self.logger.info(f"Distrito {distrito}: {len(ofertas)} registros guardados/actualizados en BD.")
```

---

## 📄 Archivo de Log

### Formato de Output

```
2026-05-31 12:14:24 - apd_scrap - INFO - APD-Scrap iniciado - Distrito: MORENO
2026-05-31 12:14:25 - apd_scrap.scrapers.apd_scraper.APDScraper - INFO - Distrito MORENO: se encontraron 9190 registros. Obteniendo todos...
2026-05-31 12:14:28 - apd_scrap.scrapers.apd_scraper.APDScraper - INFO - Archivos JSON: 9190 registros guardados en 'output_moreno.json'.
2026-05-31 12:14:28 - apd_scrap.database.connection.DatabaseConnection - INFO - Distrito MORENO: 9190 registros guardados/actualizados en BD.
2026-05-31 12:14:28 - apd_scrap - INFO - APD-Scrap finalizado exitosamente
```

### Rotación de Archivos

```
apd_scrap.log        (archivo actual, max 5MB)
apd_scrap.log.1      (primer backup)
apd_scrap.log.2      (segundo backup)
apd_scrap.log.3      (tercer backup)
```

Cuando `apd_scrap.log` alcanza 5MB:
- `apd_scrap.log.3` → eliminado
- `apd_scrap.log.2` → renombrado a `.3`
- `apd_scrap.log.1` → renombrado a `.2`
- `apd_scrap.log` → renombrado a `.1`
- Nuevo `apd_scrap.log` creado

---

## 🎯 Uso del Sistema de Logging

### Básico

```python
from apd_scrap.utils.logging import setup_logging

logger = setup_logging()
logger.info("Mensaje informativo")
logger.warning("Mensaje de advertencia")
logger.error("Mensaje de error")
```

### Con Nivel Específico

```python
import logging
from apd_scrap.utils.logging import setup_logging

logger = setup_logging(log_level=logging.DEBUG)
logger.debug("Este mensaje aparecerá")  # Solo si nivel <= DEBUG
```

### Solo Archivo o Solo Consola

```python
# Solo archivo
logger = setup_logging(log_file="mi_log.log", console_output=False)

# Solo consola
logger = setup_logging(log_file=None, console_output=True)
```

### En Clases (con LoggerMixin)

```python
from apd_scrap.utils.logging import LoggerMixin

class MiClase(LoggerMixin):
    def procesar(self):
        self.logger.info("Procesando...")
        self.logger.debug("Información de debug")
```

---

## 🔧 Configuración

### Cambiar Nivel de Logging

En `apd_scrap/config.py`:

```python
# Para ver todos los mensajes
LOG_LEVEL: int = logging.DEBUG

# Para ver solo errores y críticos
LOG_LEVEL: int = logging.ERROR
```

### Cambiar Ubicación del Archivo de Log

```python
LOG_FILE: str = "logs/apd_scrap.log"
```

### Desactivar Logging por Consola

```python
LOG_CONSOLE_OUTPUT: bool = False
```

---

## ✅ Pruebas Funcionales

| Comando | Estado | Resultado |
|---------|--------|-----------|
| `python main.py --distrito merlo` | ✅ | Logs generados correctamente |
| `python test_logging.py` | ✅ | 6/6 pruebas pasadas |
| `python test_modular.py` | ✅ | 6/6 pruebas pasadas |
| Verificar `apd_scrap.log` | ✅ | Archivo creado con formato correcto |

---

## 📈 Beneficios Logrados

| Aspecto | Mejora |
|---------|--------|
| **Trazabilidad** | Todos los eventos están registrados con timestamps |
| **Debugging** | Información contextual por módulo y clase |
| **Auditoría** | Registro histórico de operaciones |
| **Monitoreo** | Facilidad para monitorear en producción |
| **Mantenimiento** | Diferenciación clara entre INFO, WARNING, ERROR |
| **Gestión de archivos** | Rotación automática sin crecimiento infinito |
| **Contexto** | Mensajes con contexto de distrito, operación, etc. |

---

## 🔄 Compatibilidad

### Backward Compatibility
- ✅ La funcionalidad es idéntica a la versión anterior
- ✅ Los mensajes por consola se mantienen para UX
- ✅ La API pública no cambió

### Nuevos Archivos Generados
- `apd_scrap.log` - Archivo de log principal
- `apd_scrap.log.1, .2, .3` - Backups rotativos

---

## 📝 Archivos Creados/Modificados

### Nuevos archivos:
- `apd_scrap/utils/logging.py` - Sistema de logging
- `test_logging.py` - Suite de pruebas de logging

### Modificados:
- `apd_scrap/__init__.py` - Exportaciones de logging
- `apd_scrap/utils/__init__.py` - Exportaciones de logging
- `apd_scrap/config.py` - Configuración de logging
- `apd_scrap/database/connection.py` - Uso de logging
- `apd_scrap/scrapers/apd_scraper.py` - Uso de logging
- `main.py` - Configuración de logging
- `test_modular.py` - Actualizado para logging

---

## 📚 Niveles de Logging

| Nivel | Uso | Ejemplo |
|-------|-----|---------|
| **DEBUG** | Información detallada para debugging | "Conexión establecida", "SQL ejecutado" |
| **INFO** | Información general del flujo | "Scraper iniciado", "Registros guardados" |
| **WARNING** | Situaciones inesperadas pero no fatales | "No se encontraron registros", "JSON decode fallback" |
| **ERROR** | Errores que no interrumpen la ejecución | "Error en solicitud HTTP", "Error de BD" |
| **CRITICAL** | Errores graves que interrumpen la ejecución | "Error crítico en la ejecución" |

---

## 🚀 Próximos Pasos (Fase 1)

Esta mejora está **completada**. Las siguientes mejoras de la Fase 1 son:

1. ✅ Separar responsabilidades en módulos - **HECHO**
2. ✅ Sistema de logging estructurado - **HECHO**
3. ⏳ Configuración externa - **PRÓXIMO**
4. ⏳ Tests unitarios - **PENDIENTE**

---

## 🐛 Problemas Encontrados y Solucionados

### Problema 1: Archivos de Log en Uso
**Descripción:** Error al eliminar archivos de log durante pruebas porque estaban abiertos por los handlers.  
**Solución:** Cerrar todos los handlers antes de eliminar archivos.

### Problema 2: Múltiples Loggers
**Descripción:** Se creaban múltiples handlers duplicados.  
**Solución:** Limpiar handlers existentes antes de agregar nuevos en `setup_logging()`.

---

## ✨ Conclusión

La implementación del sistema de logging estructurado ha sido **exitosa**. El sistema ahora cuenta con:

- **Logging profesional** con niveles y rotación
- **Trazabilidad completa** de todas las operaciones
- **Fácil mantenimiento** con mensajes contextualizados
- **Flexibilidad** de configuración
- **Compatibilidad total** con la versión anterior

Todas las pruebas pasaron exitosamente y la funcionalidad es idéntica a la anterior, con el beneficio adicional de un sistema de logging robusto.

**Estado:** ✅ **LISTO PARA LA SIGUIENTE MEJORA**

---

**Generado:** 2025-05-31  
**Versión:** 2.1.0