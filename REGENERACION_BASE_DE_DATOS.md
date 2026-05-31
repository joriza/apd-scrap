# Análisis: Regeneración de la Base de Datos

**Fecha:** 2025-05-31  
**Proyecto:** APD-Scrap  
**Pregunta:** ¿Es posible regenerar la estructura de la base de datos sin tener acceso a la BD actual?

---

## ✅ Respuesta: SÍ, es posible regenerar completamente la estructura

La información disponible en el proyecto es **suficiente y consistente** para recrear la base de datos desde cero.

---

## 📋 Información Disponible

### 1. Archivo SQL de Creación (`crear-tabla-ofertas.sql`)
```sql
CREATE TABLE IF NOT EXISTS ofertas (
    ige INTEGER PRIMARY KEY,
    estado TEXT,
    tipooferta TEXT,
    jornada TEXT,
    miercoles TEXT,
    martes TEXT,
    acargodireccion TEXT,
    cuilautor TEXT,
    supl_hasta TEXT,
    turno TEXT,
    idoferta INTEGER,
    sabado TEXT,
    id TEXT,
    iddetalle INTEGER,
    cargo TEXT,
    tomaposesion TEXT,
    supl_revista TEXT,
    domiciliodesempeno TEXT,
    reemp_apeynom TEXT,
    numdistrito INTEGER,
    areaincumbencia TEXT,
    finoferta TEXT,
    observaciones TEXT,
    cupof INTEGER,
    tipooferta_id INTEGER,
    supl_desde TEXT,
    reemp_cuil TEXT,
    escuela TEXT,
    iniciooferta TEXT,
    hsmodulos INTEGER,
    cursodivision TEXT,
    idsuna INTEGER,
    descnivelmodalidad TEXT,
    lunes TEXT,
    infectocontagiosa BOOLEAN,
    reemp_motivo TEXT,
    descdistrito TEXT,
    jueves TEXT,
    nivelmodalidad TEXT,
    viernes TEXT,
    descripcionarea TEXT,
    descripcioncargo TEXT,
    ult_movimiento TEXT,
    _version_ INTEGER,
    timestamp TEXT
);
```

### 2. Definición de Columnas en Python (`main.py`)
```python
COLUMNAS = [
    'ige', 'estado', 'tipooferta', 'jornada', 'miercoles', 'martes',
    'acargodireccion', 'cuilautor', 'supl_hasta', 'turno', 'idoferta',
    'sabado', 'id', 'iddetalle', 'cargo', 'tomaposesion', 'supl_revista',
    'domiciliodesempeno', 'reemp_apeynom', 'numdistrito', 'areaincumbencia',
    'finoferta', 'observaciones', 'cupof', 'tipooferta_id', 'supl_desde',
    'reemp_cuil', 'escuela', 'iniciooferta', 'hsmodulos', 'cursodivision',
    'idsuna', 'descnivelmodalidad', 'lunes', 'infectocontagiosa',
    'reemp_motivo', 'descdistrito', 'jueves', 'nivelmodalidad', 'viernes',
    'descripcionarea', 'descripcioncargo', 'ult_movimiento', '_version_',
    'timestamp'
]
```

### 3. Ejemplos de Datos Reales (`output_*.json`)
Los archivos JSON contienen datos reales de la API que muestran:
- Nombres exactos de los campos
- Tipos de datos de cada campo
- Valores de ejemplo
- Estructura completa de los documentos

---

## 🔍 Validación de Consistencia

### Verificación de Columnas
```
✅ Columnas en Python:   45
✅ Columnas en SQL:      45
✅ Coincidencia:         100%
```

**Resultado:** Todas las columnas definidas en Python existen en el SQL y viceversa.

### Análisis de Tipos de Datos

| Campo | Tipo SQL | Tipo JSON | Observación |
|-------|----------|-----------|-------------|
| `ige` | INTEGER | int | ✅ PK, coincide |
| `estado` | TEXT | str | ✅ Coincide |
| `tipooferta` | TEXT | str | ✅ Coincide |
| `cupof` | INTEGER | int | ✅ Coincide |
| `infectocontagiosa` | BOOLEAN | bool | ✅ Coincide |
| `_version_` | INTEGER | int | ✅ Coincide |
| `iniciooferta` | TEXT | str | ✅ ISO 8601 string |
| `finoferta` | TEXT | str | ✅ ISO 8601 string |
| `hsmodulos` | INTEGER | int | ✅ Coincide |

**Nota:** SQLite no tiene tipos nativos para datetime, por eso se almacenan como TEXT en formato ISO 8601 (ej: `2025-03-27T10:30:00Z`).

---

## 🛠️ Procedimiento para Regenerar la BD

### Opción 1: Usar el SQL existente (Recomendado)
```bash
# Borrar base de datos anterior si existe
rm apd.db

# Crear nueva base de datos
sqlite3 apd.db < crear-tabla-ofertas.sql

# Verificar estructura
sqlite3 apd.db ".schema ofertas"
```

### Opción 2: Usar Python para crear la BD
```python
import sqlite3
from pathlib import Path

# Definición de columnas con tipos
COLUMNAS_DEFINICION = {
    'ige': 'INTEGER PRIMARY KEY',
    'estado': 'TEXT',
    'tipooferta': 'TEXT',
    'jornada': 'TEXT',
    'miercoles': 'TEXT',
    'martes': 'TEXT',
    'acargodireccion': 'TEXT',
    'cuilautor': 'TEXT',
    'supl_hasta': 'TEXT',
    'turno': 'TEXT',
    'idoferta': 'INTEGER',
    'sabado': 'TEXT',
    'id': 'TEXT',
    'iddetalle': 'INTEGER',
    'cargo': 'TEXT',
    'tomaposesion': 'TEXT',
    'supl_revista': 'TEXT',
    'domiciliodesempeno': 'TEXT',
    'reemp_apeynom': 'TEXT',
    'numdistrito': 'INTEGER',
    'areaincumbencia': 'TEXT',
    'finoferta': 'TEXT',
    'observaciones': 'TEXT',
    'cupof': 'INTEGER',
    'tipooferta_id': 'INTEGER',
    'supl_desde': 'TEXT',
    'reemp_cuil': 'TEXT',
    'escuela': 'TEXT',
    'iniciooferta': 'TEXT',
    'hsmodulos': 'INTEGER',
    'cursodivision': 'TEXT',
    'idsuna': 'INTEGER',
    'descnivelmodalidad': 'TEXT',
    'lunes': 'TEXT',
    'infectocontagiosa': 'BOOLEAN',
    'reemp_motivo': 'TEXT',
    'descdistrito': 'TEXT',
    'jueves': 'TEXT',
    'nivelmodalidad': 'TEXT',
    'viernes': 'TEXT',
    'descripcionarea': 'TEXT',
    'descripcioncargo': 'TEXT',
    'ult_movimiento': 'TEXT',
    '_version_': 'INTEGER',
    'timestamp': 'TEXT'
}

def crear_base_de_datos(db_path: str = 'apd.db'):
    """Crea la base de datos desde cero."""
    db_path = Path(db_path)
    
    # Eliminar si existe
    if db_path.exists():
        db_path.unlink()
        print(f"Base de datos eliminada: {db_path}")
    
    # Crear nueva
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    # Construir SQL
    columnas_sql = ',\n    '.join([
        f'{col} {tipo_def}' 
        for col, tipo_def in COLUMNAS_DEFINICION.items()
    ])
    
    sql = f"""
    CREATE TABLE IF NOT EXISTS ofertas (
        {columnas_sql}
    );
    """
    
    cursor.execute(sql)
    conn.commit()
    
    # Verificar
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='ofertas';")
    tabla_existe = cursor.fetchone()
    
    conn.close()
    
    if tabla_existe:
        print(f"Base de datos creada exitosamente: {db_path}")
        print(f"Total columnas: {len(COLUMNAS_DEFINICION)}")
        return True
    else:
        print("Error al crear la tabla")
        return False

if __name__ == '__main__':
    crear_base_de_datos()
```

### Opción 3: Script de migración mejorado
```python
"""
migrations/001_create_ofertas_table.py

Migración para crear la tabla de ofertas desde cero.
"""
import sqlite3
from typing import List, Tuple

MIGRATION_NAME = "001_create_ofertas_table"
MIGRATION_VERSION = 1

def up(connection: sqlite3.Connection) -> None:
    """Aplica la migración."""
    sql = """
    CREATE TABLE IF NOT EXISTS ofertas (
        ige INTEGER PRIMARY KEY,
        estado TEXT,
        tipooferta TEXT,
        jornada TEXT,
        miercoles TEXT,
        martes TEXT,
        acargodireccion TEXT,
        cuilautor TEXT,
        supl_hasta TEXT,
        turno TEXT,
        idoferta INTEGER,
        sabado TEXT,
        id TEXT,
        iddetalle INTEGER,
        cargo TEXT,
        tomaposesion TEXT,
        supl_revista TEXT,
        domiciliodesempeno TEXT,
        reemp_apeynom TEXT,
        numdistrito INTEGER,
        areaincumbencia TEXT,
        finoferta TEXT,
        observaciones TEXT,
        cupof INTEGER,
        tipooferta_id INTEGER,
        supl_desde TEXT,
        reemp_cuil TEXT,
        escuela TEXT,
        iniciooferta TEXT,
        hsmodulos INTEGER,
        cursodivision TEXT,
        idsuna INTEGER,
        descnivelmodalidad TEXT,
        lunes TEXT,
        infectocontagiosa BOOLEAN,
        reemp_motivo TEXT,
        descdistrito TEXT,
        jueves TEXT,
        nivelmodalidad TEXT,
        viernes TEXT,
        descripcionarea TEXT,
        descripcioncargo TEXT,
        ult_movimiento TEXT,
        _version_ INTEGER,
        timestamp TEXT
    );
    """
    
    cursor = connection.cursor()
    cursor.execute(sql)
    connection.commit()

def down(connection: sqlite3.Connection) -> None:
    """Revierte la migración."""
    cursor = connection.cursor()
    cursor.execute("DROP TABLE IF EXISTS ofertas;")
    connection.commit()
```

---

## 📊 Resumen de Estructura

### Campos por Tipo de Dato

| Tipo SQL | Cantidad | Campos |
|----------|----------|--------|
| **INTEGER** | 10 | ige, idoferta, iddetalle, numdistrito, cupof, tipooferta_id, hsmodulos, idsuna, _version_ |
| **TEXT** | 34 | estado, tipooferta, jornada, miercoles, martes, acargodireccion, cuilautor, supl_hasta, turno, sabado, id, cargo, tomaposesion, supl_revista, domiciliodesempeno, reemp_apeynom, areaincumbencia, finoferta, observaciones, supl_desde, reemp_cuil, escuela, iniciooferta, cursodivision, descnivelmodalidad, lunes, reemp_motivo, descdistrito, jueves, nivelmodalidad, viernes, descripcionarea, descripcioncargo, ult_movimiento, timestamp |
| **BOOLEAN** | 1 | infectocontagiosa |

**Total:** 45 campos

### Campos Clave

| Campo | Descripción | Tipo |
|-------|-------------|------|
| `ige` | Identificador único (Primary Key) | INTEGER |
| `estado` | Estado de la oferta (Publicada, Desierta, etc.) | TEXT |
| `descdistrito` | Nombre del distrito | TEXT |
| `iniciooferta` / `finoferta` | Fechas de vigencia | TEXT (ISO 8601) |
| `cargo` / `descripcioncargo` | Tipo de cargo docente | TEXT |

---

## ⚠️ Consideraciones Importantes

### 1. Fechas como TEXT
SQLite no tiene tipo nativo DATE/DATETIME. Las fechas se almacenan como:
- **Formato:** ISO 8601 (`2025-03-27T10:30:00Z`)
- **Razón:** Facilita parsing y ordenamiento
- **Recomendación:** Usar `datetime.fromisoformat()` en Python

### 2. Campos Vacíos
Los campos pueden venir vacíos desde la API:
```python
# En JSON: "lunes": ""
# En SQLite: Se almacena como string vacío

value = oferta.get('lunes') or None  # Convertir a NULL si está vacío
```

### 3. Boolean en SQLite
SQLite no tiene tipo BOOLEAN nativo:
```python
# Se almacena como 0 (False) o 1 (True)
# En Python: se puede convertir automáticamente
```

### 4. Primary Key
`ige` es la PRIMARY KEY. Se usa `INSERT OR REPLACE` para evitar duplicados.

---

## 🚀 Procedimiento Completo de Regeneración

### Paso 1: Eliminar BD anterior
```bash
# Windows
del apd.db

# Linux/Mac
rm apd.db
```

### Paso 2: Crear nueva estructura
```bash
sqlite3 apd.db < crear-tabla-ofertas.sql
```

### Paso 3: Verificar estructura
```bash
sqlite3 apd.db ".schema ofertas"
```

### Paso 4: (Opcional) Poblar desde JSON existente
```bash
python main.py --distrito merlo
```

### Paso 5: Verificar datos
```bash
sqlite3 apd.db "SELECT COUNT(*) FROM ofertas;"
sqlite3 apd.db "SELECT descdistrito, estado, COUNT(*) FROM ofertas GROUP BY descdistrito, estado;"
```

---

## ✅ Conclusiones

| Aspecto | Estado |
|---------|--------|
| Información disponible | ✅ Completa |
| Consistencia Python-SQL | ✅ 100% |
| Tipos de datos documentados | ✅ Todos definidos |
| Ejemplos reales disponibles | ✅ JSON con datos |
| Script de creación | ✅ Existe (crear-tabla-ofertas.sql) |
| Posibilidad de regeneración | ✅ **TOTAL** |

**Respuesta final:**
> **SÍ, es completamente posible regenerar la estructura de la base de datos sin tener acceso a la BD actual.** La información en el proyecto es consistente, completa y autocontenida.

**Documentos necesarios:**
1. ✅ `crear-tabla-ofertas.sql` - Estructura SQL completa
2. ✅ `main.py` - Lista de columnas y lógica de inserción
3. ✅ `output_*.json` - Datos reales de referencia

---

## 📝 Recomendaciones Adicionales

### 1. Crear script de inicialización
```bash
# scripts/init_db.sh
#!/bin/bash
echo "Inicializando base de datos..."
rm -f apd.db
sqlite3 apd.db < crear-tabla-ofertas.sql
echo "Base de datos creada exitosamente"
```

### 2. Agregar validación al inicio del scraper
```python
def verificar_estructura_db(db_path: str = 'apd.db') -> bool:
    """Verifica que la tabla tenga la estructura correcta."""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    cursor.execute("PRAGMA table_info(ofertas);")
    columnas_db = {row[1]: row[2] for row in cursor.fetchall()}
    
    conn.close()
    
    return set(columnas_db.keys()) == set(COLUMNAS)
```

### 3. Documentar tipos de datos para referencia futura
```python
# database/schema.py - Documentación de tipos

SCHEMA_TYPES = {
    'ige': int,                    # PRIMARY KEY
    'estado': str,                 # 'Publicada', 'Desierta', 'Concluida'
    'numdistrito': int,            # Código de distrito
    'hsmodulos': int,              # Horas/módulos
    'infectocontagiosa': bool,     # Requiere certificado
    'iniciooferta': datetime,      # ISO 8601 string
    'finoferta': datetime,         # ISO 8601 string
    # ... resto de campos
}
```

---

**Documento generado:** 2025-05-31
**Versión:** 1.0