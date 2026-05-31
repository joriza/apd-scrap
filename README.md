# APD-Scrap

Scraper de ofertas educativas del sistema APD (Administración de Personal Docente) del gobierno de Argentina. Descarga y almacena ofertas laborales docentes de diferentes distritos.

## 📋 Propósito

Este proyecto permite descargar y almacenar en una base de datos SQLite las ofertas de trabajo docente publicadas en el sistema APD, filtradas por distrito.

## 🏗️ Estructura del Proyecto

```
apd-scrap/
├── main.py                      # Script principal del scraper
├── crear-tabla-ofertas.sql      # Script SQL para crear la tabla de la BD
├── apd.db                       # Base de datos SQLite
├── README.md                    # Esta documentación
├── .gitignore                   # Archivos a ignorar en Git
├── output_*.json                # Datos descargados por distrito
└── venv/                        # Entorno virtual Python
```

## 🔧 Tecnologías

| Tecnología | Uso |
|------------|-----|
| **Python** | Lenguaje principal |
| **requests** | Cliente HTTP |
| **SQLite** | Base de datos local |
| **argparse** | Argumentos de línea de comandos |
| **urllib3** | Manejo SSL/TLS |

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
pip install requests
```

### 3. Ejecutar la aplicación

```bash
# Descargar ofertas de un distrito específico
python main.py --distrito merlo

# O usar el distrito por defecto (merlo)
python main.py
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

La tabla `ofertas` contiene **41 campos**:

- **Información del cargo**: `cargo`, `descripcioncargo`, `tipooferta`, `tipooferta_id`
- **Ubicación**: `escuela`, `domiciliodesempeno`, `descdistrito`, `numdistrito`
- **Fechas**: `iniciooferta`, `finoferta`, `tomaposesion`, `supl_desde`, `supl_hasta`, `ult_movimiento`
- **Reemplazo**: `reemp_apeynom`, `reemp_cuil`, `reemp_motivo`
- **Horarios**: `lunes`, `martes`, `miercoles`, `jueves`, `viernes`, `sabado`, `turno`, `jornada`, `hsmodulos`
- **Otros**: `ige` (PK), `estado`, `id`, `idoferta`, `iddetalle`, `cursodivision`, `areaincumbencia`, `observaciones`, `infectocontagiosa`

## 🗄️ Base de Datos

Para crear la tabla de la base de datos:

```bash
sqlite3 apd.db < crear-tabla-ofertas.sql
```

### Consultas útiles

```sql
-- Ver todas las ofertas publicadas de un distrito
SELECT * FROM ofertas WHERE estado = "Publicada" AND descdistrito = "MERLO";

-- Contar ofertas por estado
SELECT estado, COUNT(*) FROM ofertas GROUP BY estado;

-- Ver ofertas recientes
SELECT * FROM ofertas ORDER BY iniciooferta DESC LIMIT 10;
```

## 📝 Ejemplo de Salida

```
Distrito seleccionado: MERLO

Se encontraron 15423 registros. Obteniendo todos...

¡Éxito! 15423 registros guardados en 'output_merlo.json'.

Se han guardado/actualizado 15423 registros en 'apd.db'.
```

## ⚠️ Notas

- El servidor requiere una configuración SSL/TLS específica implementada en el script
- Los archivos JSON pueden ser grandes (15-37MB) según la cantidad de registros
- Usa `INSERT OR REPLACE` para actualizar registros existentes sin duplicados

## 📄 Licencia

Este proyecto es de uso educativo y para consulta de información pública del sistema educativo argentino.