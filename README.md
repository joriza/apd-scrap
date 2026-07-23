# APD-Scrap

Scraper de ofertas educativas del sistema APD (Administración de Personal Docente) del gobierno de Argentina. Descarga y almacena ofertas laborales docentes de diferentes distritos.

## 📋 Versión

**Versión actual:** 2.3.0 (Exportación a Excel)

## 🏗️ Estructura del Proyecto

```
apd-scrap/
├── apd_scrap/                    # Paquete principal
│   ├── __init__.py              # Exportaciones públicas
│   ├── config.py                # Configuración centralizada
│   ├── cli/                     # Módulo de CLI
│   │   ├── __init__.py
│   │   └── commands.py          # Parser de argumentos
│   ├── database/                # Módulo de base de datos
│   │   ├── __init__.py
│   │   ├── connection.py        # Gestión de conexión y exportación
│   │   └── schema.py            # Definición del esquema
│   ├── scrapers/                # Módulo de scrapers
│   │   ├── __init__.py
│   │   └── apd_scraper.py       # Scraper de APD
│   ├── exporters/               # Módulo de exportación
│   │   ├── __init__.py
│   │   ├── excel_exporter.py    # Exportador a Excel
│   │   └── formatters.py       # Formateo de Excel
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       ├── ssl_adapter.py       # Adaptador SSL personalizado
│       ├── logging.py           # Configuración de logging
│       ├── rate_limiter.py      # Limitación de tasa
│       └── retry.py             # Mecanismos de reintento
├── main.py                      # Punto de entrada principal
├── requirements.txt             # Dependencias de desarrollo
├── requirements-prod.txt        # Dependencias de producción
├── test_modular.py              # Suite de pruebas
└── README.md                    # Esta documentación
```

## 🔧 Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.9+ | Lenguaje principal |
| **requests** | 2.31.0+ | Cliente HTTP |
| **SQLite** | 3.x | Base de datos local |
| **pandas** | 2.0.0+ | Manipulación de datos |
| **openpyxl** | 3.1.2+ | Exportación a Excel |

## 🚀 Instalación y Ejecución

### 1. Crear y activar el entorno virtual

```bash
# Crear el entorno virtual (si no existe)
python -m venv venv

# Activar entorno virtual en Windows
.\venv\Scripts\activate

# Activar entorno virtual en Linux/Mac
source venv/bin/activate
```

### 2. Instalar dependencias

```bash
# Instalar dependencias de producción
pip install -r requirements-prod.txt

# O instalar dependencias de desarrollo (incluye pruebas y herramientas)
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
# Descargar ofertas de un distrito específico
python main.py --distrito merlo

# O usar el distrito por defecto (merlo)
python main.py

# Exportar a Excel después de descargar
python main.py --export-excel --export-format both --output export_apd.xlsx

# Exportar solo ofertas a Excel
python main.py --export-excel --export-format ofertas --output ofertas.xlsx

# Exportar solo postulantes a Excel
python main.py --export-excel --export-format postulantes --output postulantes.xlsx

# Ver ayuda
python main.py --help
```

Distritos disponibles: `merlo`, `moreno`, `moron`, `ituzaingo`, `matanza`, etc.

## ⚙️ Funcionamiento

1. **Configuración SSL**: Implementa un `CustomHttpAdapter` para forzar un cipher suite específico requerido por el servidor.

2. **Proceso de scraping**:
   - Obtiene datos de la API del gobierno de Argentina
   - Filtra por distrito
   - Primero obtiene el conteo total de registros
   - Luego descarga todos los registros

3. **Almacenamiento**:
   - Guarda JSON en `output_{distrito}.json`
   - Inserta/actualiza registros en SQLite (`apd.db`)
   - Usa `INSERT OR REPLACE` para manejar duplicados

4. **Exportación a Excel** (versión 2.3.0+):
   - Exporta datos a formato Excel profesional
   - Soporta exportación de ofertas, postulantes o ambos
   - Incluye múltiples hojas con formateo automático
   - Maneja grandes volúmenes con paginación
   - Incluye resumen y metadatos en el archivo Excel

## 📊 Estructura de Datos

### Tabla `ofertas` (55 campos)
- **Información del cargo**: `cargo`, `descripcioncargo`, `tipooferta`, `tipooferta_id`
- **Ubicación**: `escuela`, `domiciliodesempeno`, `descdistrito`, `numdistrito`
- **Fechas**: `iniciooferta`, `finoferta`, `tomaposesion`, `supl_desde`, `supl_hasta`, `ult_movimiento`
- **Reemplazo**: `reemp_apeynom`, `reemp_cuil`, `reemp_motivo`
- **Horarios**: `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado`, `turno`, `jornada`, `hsmodulos`
- **Otros**: `ige` (PK), `estado`, `id`, `idoferta`, `iddetalle`, `cursodivision`, `areaincumbencia`, `observaciones`, `infectocontagiosa`, `_version_`, `timestamp`

### Tabla `postulantes` (21 campos)
- **Información personal**: `nombres`, `cuil`, `fechanacimiento`, `telefono`, `email`
- **Información de postulación**: `puntaje`, `designado`, `estadopostulacion`, `prioridad`
- **Información laboral**: `cargo`, `areaincumbencia`, `TieneCargoTitular`, `tienehojaruta`
- **Otros**: `ige` (FK), `idpostulacion`, `listadoorigen`, `recalificadoart`, `pun_titu`, `pun_res`, `cuilautor`

### Tabla `estados` (catálogo)
- Contiene los estados válidos: `Anulada`, `Desierta`, `DESIGNADA`, `RENUNCIADA`, `Finalizada`, `Publicada`, `Cerrada`

## 🗄️ Base de Datos

La base de datos se crea automáticamente en `apd.db` la primera vez que se ejecuta el scraper.

### Esquema completo

```sql
-- Tabla principal de ofertas
CREATE TABLE ofertas (
    ige INTEGER PRIMARY KEY,
    estado TEXT,
    -- ... 52 campos adicionales ...
    timestamp TEXT
);

-- Tabla de postulantes
CREATE TABLE postulantes (
    ige INTEGER NOT NULL,
    cuil TEXT,
    -- ... 19 campos adicionales ...
    PRIMARY KEY (ige, cuil),
    FOREIGN KEY (ige) REFERENCES ofertas(ige) ON DELETE CASCADE
);

-- Tabla de estados (catálogo)
CREATE TABLE estados (
    estado TEXT PRIMARY KEY
);
```

### Consultas útiles

```sql
-- Ver todas las ofertas publicadas de un distrito
SELECT * FROM ofertas WHERE estado = "Publicada" AND descdistrito = "MERLO";

-- Contar ofertas por estado
SELECT estado, COUNT(*) FROM ofertas GROUP BY estado;

-- Ver ofertas recientes
SELECT * FROM ofertas ORDER BY iniciooferta DESC LIMIT 10;

-- Contar por distrito
SELECT descdistrito, COUNT(*) as total FROM ofertas GROUP BY descdistrito;

-- Ver postulantes de una oferta específica
SELECT * FROM postulantes WHERE ige = 4067362;

-- Ver ganador de una oferta
SELECT * FROM postulantes WHERE ige = 4067362 AND designado = 'S';
```

## 🧪 Pruebas

El proyecto incluye una suite de pruebas para validar la estructura modular:

```bash
python test_modular.py
```

Esto ejecuta 6 pruebas:
1. Importaciones
2. Configuración
3. Esquema de Base de Datos
4. Operaciones de Base de Datos
5. Scraper
6. CLI

## 📝 Ejemplo de Salida

### Descarga normal
```
Distrito seleccionado: MERLO

Se encontraron 8477 registros. Obteniendo todos...

¡Éxito! 8477 registros guardados en 'output_merlo.json'.

Se han guardado/actualizados 8477 registros en 'apd.db'.
```

### Con exportación a Excel
```
Distrito seleccionado: MERLO

Se encontraron 8477 registros. Obteniendo todos...

¡Éxito! 8477 registros guardados en 'output_merlo.json'.

Se han guardado/actualizados 8477 registros en 'apd.db'.

Iniciando exportación a Excel...
Exportación completada: export_both_20240723_131741.xlsx
```

### Estructura del archivo Excel exportado
```
export_both_20240723_131741.xlsx
├── Hoja1: Resumen [Estadísticas totales]
├── Hoja2: Ofertas [55 columnas completas]
├── Hoja3: Postulantes [21 columnas completas] 
└── Hoja4: Metadatos [Información de exportación]
```

## 🔌 Uso Programático

También puedes usar el paquete en tus propios scripts:

```python
from apd_scrap import APDScraper, DatabaseConnection
from apd_scrap.exporters import ExcelExporter

# Obtener datos del scraper
with APDScraper() as scraper:
    total = scraper.get_total_records('merlo')
    print(f"Total registros: {total}")
    
    data = scraper.fetch_all_records('merlo')
    scraper.save_to_json(data, 'merlo')

# Guardar en base de datos
with DatabaseConnection() as db:
    db.initialize_schema()
    ofertas = data['response']['docs']
    db.save_ofertas(ofertas)

# Exportar a Excel
with DatabaseConnection() as db:
    excel_exporter = ExcelExporter(db)
    excel_path = excel_exporter.export_data(
        export_type="both",
        output_path="custom_export.xlsx"
    )
    print(f"Exportado a: {excel_path}")
```

## ⚠️ Notas

- El servidor requiere una configuración SSL/TLS específica implementada en `apd_scrap/utils/ssl_adapter.py`
- Los archivos JSON pueden ser grandes (15-40MB) según la cantidad de registros
- Usa `INSERT OR REPLACE` para actualizar registros existentes sin duplicados
- La exportación a Excel requiere las dependencias pandas y openpyxl
- Para exportaciones grandes, se usa paginación para evitar problemas de memoria
- Los archivos Excel incluyen formateo profesional con tablas, filtros y estilos

## 🆕 Novedades en versión 2.3.0

- **Exportación a Excel**: Nueva funcionalidad para exportar datos a formato Excel
- **Módulo de exportación**: Nuevo paquete `exporters` con clases especializadas
- **Paginación inteligente**: Manejo eficiente de grandes volúmenes de datos
- **Formateo profesional**: Excel con múltiples hojas, tablas y estilos
- **Argumentos CLI nuevos**: `--export-excel`, `--export-format`, `--output-file`
- **Manejo de errores mejorado**: Validación de seguridad y manejo de errores robusto

## 📚 Documentación Adicional

- `ANALISIS_Y_MEJORAS.md` - Análisis completo del proyecto y propuesta de mejoras
- `IMPLEMENTACION_MODULAR.md` - Detalles de la implementación modular
- `REGENERACION_BASE_DE_DATOS.md` - Documentación sobre la base de datos
- `docs/` - Documentación detallada de cada módulo

## 📊 Características de Exportación a Excel

### Formato del archivo Excel
- **Múltiples hojas**: Ofertas, Postulantes, Resumen, Metadatos
- **Tablas estructuradas**: Con formato y filtros automáticos
- **Encabezados con estilo**: Formato profesional y legible
- **Ajuste automático de columnas**: Optimización del espacio

### Opciones de exportación
- **`ofertas`**: Exporta solo la tabla de ofertas (55 columnas)
- **`postulantes`**: Exporta solo la tabla de postulantes (21 columnas)
- **`both`**: Exporta ambas tablas en un archivo Excel

### Seguridad y rendimiento
- **Validación de espacio en disco**: Evita errores por falta de espacio
- **Paginación por lotes**: Maneja eficientemente grandes volúmenes
- **Protección de datos**: Manejo adecuado de información sensible
- **Logging detallado**: Monitoreo completo del proceso

## 📄 Licencia

Este proyecto es de uso educativo y para consulta de información pública del sistema educativo argentino.

## 🤝 Contribuir

Las contribuciones son bienvenidas. Por favor, asegúrate de:
1. Seguir la estructura modular del proyecto
2. Agregar docstrings a nuevas funciones
3. Ejecutar las pruebas antes de hacer commit
4. Mantener la compatibilidad con versiones anteriores

## 📞 Soporte

Para preguntas o problemas:
- Revisar la documentación en los archivos `.md`
- Ejecutar `python test_modular.py` para diagnosticar problemas
- Crear un issue en el repositorio

---

**Última actualización:** 2026-07-23  
**Versión:** 2.3.0