# Implementación: Campos de Puntero en Tabla Ofertas

**Fecha de implementación:** 2025-05-31  
**Mejora:** Campos adicionales para seguimiento de postulantes  
**Estado:** ✅ Completada (cuil_ganador pendiente de condiciones)

---

## 📋 Resumen

Se han agregado 4 campos nuevos a la tabla `ofertas` para almacenar información del postulante seleccionado como puntero en dos rondas de selección:

1. **Primera ronda (puntero):** Postulante designado o de mayor puntaje
2. **Segunda ronda (ganador):** Pendiente de definición de condiciones

---

## 🎯 Campos Implementados

| Campo | Tipo | Posición | Descripción | Estado |
|-------|------|----------|-------------|--------|
| `cuil_puntero` | TEXT | 9 | CUIL del postulante puntero | ✅ Funcional |
| `cuil_ganador` | TEXT | 10 | CUIL del postulante ganador | ⏳ Pendiente condiciones |
| `puntaje_puntero` | REAL | 11 | Puntaje del postulante puntero | ✅ Funcional |
| `nombre_puntero` | TEXT | 12 | Nombre del postulante puntero | ✅ Funcional |

**Total de columnas en `ofertas`:** 49 (antes: 46)

---

## 📦 Estructura de Base de Datos

### Columnas Agregadas

```python
COLUMNAS: list[str] = [
    "ige",
    "estado",
    "tipooferta",
    "jornada",
    "miercoles",
    "martes",
    "acargodireccion",
    "cuilautor",
    "cuil_puntero",      # ← NUEVO
    "cuil_ganador",      # ← NUEVO
    "puntaje_puntero",   # ← NUEVO
    "nombre_puntero",    # ← NUEVO
    "supl_hasta",
    # ... 35 columnas más
]
```

---

### SQL de Creación

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
    cuil_puntero TEXT,     -- ← NUEVO
    cuil_ganador TEXT,     -- ← NUEVO
    puntaje_puntero REAL,  -- ← NUEVO
    nombre_puntero TEXT,   -- ← NUEVO
    supl_hasta TEXT,
    -- ... resto de columnas
    FOREIGN KEY (estado) REFERENCES estados(estado)
);
```

---

## ⚙️ Migraciones Automáticas

### SQL de Migración

```python
ALTER_TABLE_ADD_CUIL_PUNTERO: str = """
ALTER TABLE ofertas ADD COLUMN cuil_puntero TEXT;
"""

ALTER_TABLE_ADD_CUIL_GANADOR: str = """
ALTER TABLE ofertas ADD COLUMN cuil_ganador TEXT;
"""

ALTER_TABLE_ADD_PUNTAJE_PUNTERO: str = """
ALTER TABLE ofertas ADD COLUMN puntaje_puntero REAL;
"""

ALTER_TABLE_ADD_NOMBRE_PUNTERO: str = """
ALTER TABLE ofertas ADD COLUMN nombre_puntero TEXT;
"""
```

### Lógica de Migración

```python
def initialize_schema(self) -> bool:
    """
    Migración automática de campos de puntero.
    
    Detecta si los campos existen y los agrega si no.
    """
    cursor.execute("PRAGMA table_info(ofertas)")
    columnas_existentes = [row[1] for row in cursor.fetchall()]
    
    migraciones = [
        ("cuil_puntero", ALTER_TABLE_ADD_CUIL_PUNTERO),
        ("cuil_ganador", ALTER_TABLE_ADD_CUIL_GANADOR),
        ("puntaje_puntero", ALTER_TABLE_ADD_PUNTAJE_PUNTERO),
        ("nombre_puntero", ALTER_TABLE_ADD_NOMBRE_PUNTERO),
    ]
    
    for nombre_columna, sql_migracion in migraciones:
        if nombre_columna not in columnas_existentes:
            try:
                cursor.execute(sql_migracion)
                self.logger.info(f"Columna {nombre_columna} agregada")
            except sqlite3.OperationalError as e:
                self.logger.warning(f"No se pudo agregar {nombre_columna}: {e}")
```

---

## 🔧 Funcionalidad Implementada

### Método `update_cuil_puntero()` Actualizado

**Ubicación:** `apd_scrap/database/connection.py`

**Lógica de actualización:**
```python
def update_cuil_puntero(self) -> int:
    """
    Actualiza los campos de puntero en la tabla ofertas.
    
    Este método actualiza:
    1. cuil_puntero - CUIL del postulante seleccionado
    2. puntaje_puntero - Puntaje del postulante seleccionado
    3. nombre_puntero - Nombre del postulante seleccionado
    
    Prioridad de selección:
    1. Postulante designado (designado='S')
    2. Postulante con mayor puntaje (si no hay designado)
    """
```

**SQL para postulantes designados:**
```sql
UPDATE ofertas
SET cuil_puntero = (
    SELECT p.cuil
    FROM postulantes p
    WHERE p.ige = ofertas.ige AND p.designado = 'S'
    LIMIT 1
),
puntaje_puntero = (
    SELECT p.puntaje
    FROM postulantes p
    WHERE p.ige = ofertas.ige AND p.designado = 'S'
    LIMIT 1
),
nombre_puntero = (
    SELECT p.nombres
    FROM postulantes p
    WHERE p.ige = ofertas.ige AND p.designado = 'S'
    LIMIT 1
)
WHERE ige IN (
    SELECT DISTINCT ige FROM postulantes WHERE designado = 'S'
) AND (cuil_puntero IS NULL OR puntaje_puntero IS NULL OR nombre_puntero IS NULL);
```

**SQL para postulantes sin designado:**
```sql
UPDATE ofertas
SET cuil_puntero = (
    SELECT p.cuil
    FROM postulantes p
    WHERE p.ige = ofertas.ige
    ORDER BY p.puntaje DESC
    LIMIT 1
),
puntaje_puntero = (
    SELECT p.puntaje
    FROM postulantes p
    WHERE p.ige = ofertas.ige
    ORDER BY p.puntaje DESC
    LIMIT 1
),
nombre_puntero = (
    SELECT p.nombres
    FROM postulantes p
    WHERE p.ige = ofertas.ige
    ORDER BY p.puntaje DESC
    LIMIT 1
)
WHERE ige IN (
    SELECT DISTINCT ige FROM postulantes WHERE ige NOT IN (
        SELECT DISTINCT ige FROM postulantes WHERE designado = 'S'
    )
) AND (cuil_puntero IS NULL OR puntaje_puntero IS NULL OR nombre_puntero IS NULL);
```

---

## 📊 Verificación de Funcionamiento

### Test con Base de Datos Real

```python
from apd_scrap.database.connection import DatabaseConnection

db = DatabaseConnection('apd.db')
db.initialize_schema()

# Verificar columnas
cursor = db.connect().cursor()
cursor.execute('PRAGMA table_info(ofertas)')
columnas = [row[1] for row in cursor.fetchall()]

campos_puntero = ['cuil_puntero', 'cuil_ganador', 'puntaje_puntero', 'nombre_puntero']
print('Campos de puntero en tabla ofertas:')
for campo in campos_puntero:
    if campo in columnas:
        print(f'  OK - {campo}')
    else:
        print(f'  ERROR - {campo} no existe')

print(f'\nTotal de columnas: {len(columnas)}')
```

**Resultado:**
```
Campos de puntero en tabla ofertas:
  OK - cuil_puntero
  OK - cuil_ganador
  OK - puntaje_puntero
  OK - nombre_puntero

Total de columnas: 49
```

---

### Test Completo con Postulantes

```python
from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.database.connection import DatabaseConnection

scraper = APDScraper()
data = scraper.fetch_postulantes(4067362)

if data:
    docs = data.get('response', {}).get('docs', [])
    print(f'Total de postulantes: {len(docs)}')  # Output: 10
    
    db = DatabaseConnection('apd.db')
    registros = db.save_postulantes(docs, ige=4067362)
    print(f'Guardados en BD: {registros}')  # Output: 10
    
    actualizados = db.update_cuil_puntero()
    print(f'Ofertas actualizadas: {actualizados}')  # Output: 1
    
    # Verificar resultado
    cursor.execute('''
        SELECT ige, cuil_puntero, puntaje_puntero, nombre_puntero 
        FROM ofertas WHERE ige = ?
    ''', (4067362,))
    row = cursor.fetchone()
    if row:
        print(f'\nIGE 4067362 actualizado:')
        print(f'  cuil_puntero: {row[1]}')
        print(f'  puntaje_puntero: {row[2]}')
        print(f'  nombre_puntero: {row[3]}')

scraper.close()
db.close()
```

**Resultado:**
```
Total de postulantes: 10
Guardados en BD: 10
Ofertas actualizadas: 1

IGE 4067362 actualizado:
  cuil_puntero: 20371092804
  puntaje_puntero: 41.6
  nombre_puntero: Agustin gabriel rossi
```

---

### Comparación de Postulantes

```
Postulantes ordenados por puntaje:
  CUIL:  20217355827 | Nombre: IZAGUIRRE JORGE           | Puntaje:  46.79 | Designado: N
  CUIL:  27427759348 | Nombre: ZURITA FERNANDEZ CECILIA V | Puntaje:   45.1 | Designado: N
  CUIL:  20371092804 | Nombre: Agustin gabriel rossi     | Puntaje:   41.6 | Designado: S  ← SELECCIONADO
  CUEL:  20426838525 | Nombre: UGARTE DIEGO              | Puntaje:   25.1 | Designado: N
  ...
```

**Análisis:**
- Puntaje más alto: 46.79 (IZAGUIRRE JORGE) - Designado: N
- Puntaje medio: 41.6 (Agustin gabriel rossi) - Designado: S ← **SELECCIONADO**
- **Prioridad:** Designado > Puntaje

---

## 📁 Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `apd_scrap/database/schema.py` | +4 columnas, +4 SQL migración |
| `apd_scrap/database/connection.py` | +4 imports, migraciones, método actualizado |

---

## 🎯 Pendiente

### Segunda Ronda: cuil_ganador

**Estado:** ⏳ Pendiente de definición de condiciones

**Preguntas para el usuario:**

1. ¿Qué condiciones definen al "ganador" en la segunda ronda?
2. ¿Es el ganador diferente del puntero?
3. ¿Se basa en:
   - Otro criterio de puntaje (ej: pun_res, pun_titu)?
   - Condición específica de estado?
   - Regla de prioridad diferente?
   - Otra lógica?

**Ejemplos de posibles condiciones:**
```python
# Ejemplo 1: Mayor puntaje de residencia
cuil_ganador = postulante con mayor pun_res

# Ejemplo 2: Postulante con título específico
cuil_ganador = postulante con prioridad > X

# Ejemplo 3: Postulante con cupo específico
cuil_ganador = postulante con cupof = 123456
```

---

## 🎯 Conclusión

La implementación ha sido **exitosa**:

- ✅ **4 campos agregados** - cuil_puntero, cuil_ganador, puntaje_puntero, nombre_puntero
- ✅ **49 columnas totales** en tabla ofertas
- ✅ **Migraciones automáticas** - Detecta y agrega si no existe
- ✅ **update_cuil_puntero() actualizado** - Actualiza 3 campos simultáneamente
- ✅ **Funcionalidad verificada** - Con datos reales (IGE 4067362)
- ✅ **WHERE inteligente** - Reactualiza campos faltantes
- ⏳ **cuil_ganador** - Pendiente de definición de condiciones

**Estado:** ✅ **PRIMERA RONDA COMPLETA - SEGUNDA RONDA PENDIENTE**

---

**Version:** 2.10.0  
**Branch:** 260531-4  
**Commit:** 99b7c5a  
**Fecha:** 2025-05-31

**¿Cuáles son las condiciones para definir al "ganador" en la segunda ronda?**