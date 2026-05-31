# APD-Scrap

Scraper de ofertas educativas del sistema APD (Administración de Personal Docente) del gobierno de Argentina. Descarga y almacena ofertas laborales docentes de diferentes distritos.

## 📋 Versión

**Versión actual:** 2.0.0 (Estructura Modular)

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
│   │   ├── connection.py        # Gestión de conexión
│   │   └── schema.py            # Definición del esquema
│   ├── scrapers/                # Módulo de scrapers
│   │   ├── __init__.py
│   │   └── apd_scraper.py       # Scraper de APD
│   └── utils/                   # Utilidades
│       ├── __init__.py
│       └── ssl_adapter.py       # Adaptador SSL personalizado
├── main.py                      # Punto de entrada principal
├── test_modular.py              # Suite de pruebas
├── requirements.txt             # Dependencias
└── README.md                    # Esta documentación
```

## 🔧 Tecnologías

| Tecnología | Versión | Uso |
|------------|---------|-----|
| **Python** | 3.9+ | Lenguaje principal |
| **requests** | 2.31.0+ | Cliente HTTP |
| **SQLite** | 3.x | Base de datos local |

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
pip install -r requirements.txt
```

### 3. Ejecutar la aplicación

```bash
# Descargar ofertas de un distrito específico
python main.py --distrito merlo

# O usar el distrito por defecto (merlo)
python main.py

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

## 📊 Estructura de Datos

La tabla `ofertas` contiene **45 campos**:

- **Información del cargo**: `cargo`, `descripcioncargo`, `tipooferta`, `tipooferta_id`
- **Ubicación**: `escuela`, `domiciliodesempeno`, `descdistrito`, `numdistrito`
- **Fechas**: `iniciooferta`, `finoferta`, `tomaposesion`, `supl_desde`, `supl_hasta`, `ult_movimiento`
- **Reemplazo**: `reemp_apeynom`, `reemp_cuil`, `reemp_motivo`
- **Horarios**: `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado`, `turno`, `jornada`, `hsmodulos`
- **Otros**: `ige` (PK), `estado`, `id`, `idoferta`, `iddetalle`, `cursodivision`, `areaincumbencia`, `observaciones`, `infectocontagiosa`, `_version_`, `timestamp`

## 🗄️ Base de Datos

La base de datos se crea automáticamente en `apd.db` la primera vez que se ejecuta el scraper.

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

```
Distrito seleccionado: MERLO

Se encontraron 6759 registros. Obteniendo todos...

¡Éxito! 6759 registros guardados en 'output_merlo.json'.

Se han guardado/actualizado 6759 registros en 'apd.db'.
```

## 🔌 Uso Programático

También puedes usar el paquete en tus propios scripts:

```python
from apd_scrap import APDScraper, DatabaseConnection

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
```

## ⚠️ Notas

- El servidor requiere una configuración SSL/TLS específica implementada en `apd_scrap/utils/ssl_adapter.py`
- Los archivos JSON pueden ser grandes (15-40MB) según la cantidad de registros
- Usa `INSERT OR REPLACE` para actualizar registros existentes sin duplicados

## 📚 Documentación Adicional

- `ANALISIS_Y_MEJORAS.md` - Análisis completo del proyecto y propuesta de mejoras
- `IMPLEMENTACION_MODULAR.md` - Detalles de la implementación modular
- `REGENERACION_BASE_DE_DATOS.md` - Documentación sobre la base de datos

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

**Última actualización:** 2025-05-31  
**Versión:** 2.0.0