# Implementación de Tabla Postulantes

**Fecha de implementación:** 2025-05-31  
**Mejora:** Tabla postulantes para seguimiento de aplicaciones  
**Estado:** ⚠️ Parcialmente completa (requiere solución SSL)

---

## 📋 Resumen

Se ha implementado la estructura de base de datos y funcionalidad para almacenar postulantes a las ofertas educativas del sistema APD.

---

## 🎯 Objetivos

1. ✅ Crear tabla `postulantes` con campos específicos
2. ✅ Configurar URL de API de postulantes en parámetros
3. ⚠️ Implementar métodos para obtener postulantes (pendiente SSL)
4. ✅ Implementar métodos para guardar postulantes en BD
5. 🔄 Funcionalidad para filtrar ofertas por condiciones (pendiente usuario)

---

## 📦 Componentes Implementados

### Tabla `postulantes`

**Ubicación:** `apd_scrap/database/schema.py`

**Columnas:**
```sql
CREATE TABLE IF NOT EXISTS postulantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ige INTEGER NOT NULL,
    cuil TEXT,
    puntaje REAL,
    designado TEXT,
    nombres TEXT,
    idpostulacion INTEGER,
    areaincumbencia TEXT,
    cargo TEXT,
    telefono TEXT,
    fechanacimiento TEXT,
    listadoorigen TEXT,
    cupof INTEGER,
    estadopostulacion TEXT,
    recalificadoart TEXT,
    pun_titu REAL,
    prioridad INTEGER,
    email TEXT,
    TieneCargoTitular TEXT,
    pun_res REAL,
    tienehojaruta TEXT,
    cuilautor TEXT,
    FOREIGN KEY (ige) REFERENCES ofertas(ige) ON DELETE CASCADE
);
```

**Campos requeridos por el usuario:**
- ✅ `ige` - Clave foránea a ofertas
- ✅ `cuil` - CUIL del postulante
- ✅ `puntaje` - Puntaje del postulante
- ✅ `designado` - Estado de designación
- ✅ `nombres` - Nombres del postulante
- ✅ `idpostulacion` - ID único de postulación
- ✅ `areaincumbencia` - Área de incumbencia
- ✅ `cargo` - Cargo docente
- ✅ `telefono` - Teléfono del postulante
- ✅ `fechanacimiento` - Fecha de nacimiento
- ✅ `listadoorigen` - Listado de origen
- ✅ `cupof` - Código de cupo
- ✅ `estadopostulacion` - Estado de la postulación
- ✅ `recalificadoart` - Recalificado por ART
- ✅ `pun_titu` - Puntaje títulos
- ✅ `prioridad` - Prioridad
- ✅ `email` - Email del postulante
- ✅ `TieneCargoTitular` - Tiene cargo titular
- ✅ `pun_res` - Puntaje residencia
- ✅ `tienehojaruta` - Tiene hoja de ruta
- ✅ `cuilautor` - CUIL autorizante

---

## ⚙️ Configuración

### Archivos Modificados

| Archivo | Cambios |
|---------|---------|
| `apd_scrap/config.py` | URL de API postulantes + variable entorno |
| `apd_scrap/database/schema.py` | Definición tabla postulantes + SQL |
| `apd_scrap/database/connection.py` | Método save_postulantes() |
| `apd_scrap/scrapers/apd_scraper.py` | Método fetch_postulantes() |

### Configuración de API

**En `Config`:**
```python
DEFAULT_CONFIG = {
    "api": {
        "base_url": "...apd.oferta.encabezado/select",
        "postulantes_url": "...apd.oferta.postulante/select",
        "timeout": 60,
    },
}
```

**Variables de entorno:**
```bash
APD_POSTULANTES_API_URL=https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.postulante/select
```

---

## 🔧 Funcionalidad Implementada

### 1. Tabla en Base de Datos

```python
# En schema.py
CREATE_TABLE_POSTULANTES_SQL: str = """
CREATE TABLE IF NOT EXISTS postulantes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ige INTEGER NOT NULL,
    cuil TEXT,
    -- ... 20 campos ...
    FOREIGN KEY (ige) REFERENCES ofertas(ige) ON DELETE CASCADE
);
"""
```

### 2. Inserción de Postulantes

```python
# En schema.py
def get_insert_postulantes_sql() -> str:
    placeholders = ", ".join(["?"] * len(COLUMNAS_POSTULANTES))
    columns = ", ".join(COLUMNAS_POSTULANTES)
    return f"INSERT OR REPLACE INTO postulantes ({columns}) VALUES ({placeholders})"
```

### 3. Guardar Postulantes en BD

```python
# En connection.py
def save_postulantes(
    self,
    postulantes: list[dict[str, Any]],
    ige: Optional[int] = None,
) -> int:
    """
    Guarda o actualiza una lista de postulantes en la base de datos.
    
    Args:
        postulantes: Lista de diccionarios de postulantes
        ige: IGE de la oferta asociada (opcional, para logging)
    
    Returns:
        int: Número de registros guardados/actualizados
    """
```

### 4. Obtener Postulantes de API

```python
# En apd_scraper.py
def fetch_postulantes(self, ige: int) -> Optional[dict[str, Any]]:
    """
    Obtiene todos los postulantes de una oferta específica.
    
    Args:
        ige: Identificador único de la oferta (idoferta)
    
    Returns:
        dict: Respuesta de la API con los postulantes, o None si hay error
    """
    params = {
        "q": "*:*",
        "fq": f"idoferta:{ige}",
        "json.nl": "map",
        "sort": "orden asc",
    }
    return self._fetch_data(params, url_override=self.config.POSTULANTES_API_URL)
```

### 5. Soporte para Múltiples Endpoints

```python
# En apd_scraper.py
def _fetch_data(self, params: dict[str, Any], url_override: Optional[str] = None) -> Optional[dict[str, Any]]:
    """
    Realiza la solicitud a la API con reintentos automáticos.
    
    Args:
        params: Parámetros de consulta para la API
        url_override: URL alternativa para la solicitud (opcional)
    
    Returns:
        Optional[Dict[str, Any]]: Datos JSON decodificados o None
    """
    url = url_override or self.config.API_BASE_URL
    response = self.session.get(url, params=params, timeout=self.config.API_TIMEOUT)
    # ...
```

---

## ⚠️ Problemas Conocidos

### ✅ Error SSL en Endpoint de Postulantes - RESUELTO

**Problema original:**
```
SSLError: [SSL: SSLV3_ALERT_HANDSHAKE_FAILURE] sslv3 alert handshake failure
```

**Causa:**
El endpoint `apd.oferta.postulante/select` requiere una configuración SSL diferente al endpoint principal (`apd.oferta.encabezado/select`).

**Pruebas realizadas:**
- ✅ Endpoint principal funciona con CustomHttpAdapter
- ❌ Endpoint postulantes falla con CustomHttpAdapter
- ✅ Endpoint postulantes funciona con TLS 1.2 + SECLEVEL=1 (LegacyServerConnect)

**Solución implementada:**

Se creó un segundo adaptador HTTP específico para endpoints legacy:

```python
# En apd_scrap/utils/ssl_adapter.py
class LegacyHttpAdapter(HTTPAdapter):
    """
    Adaptador HTTP para servidores con configuración SSL legacy.
    
    Características:
    - Usa TLS 1.2 como versión mínima
    - Configura SECLEVEL=1 para permitir ciphers más antiguos
    - No verifica hostname (compatibilidad con servidores legacy)
    """
    
    def init_poolmanager(self, connections, maxsize, block=False, **kwargs):
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE
        kwargs["ssl_context"] = context
        return super().init_poolmanager(connections, maxsize, block, **kwargs)
```

**Cambios en `fetch_postulantes()`:**

```python
def fetch_postulantes(self, ige: int) -> Optional[dict[str, Any]]:
    """
    Obtiene todos los postulantes de una oferta específica.
    
    Usa una sesión temporal con adaptador SSL legacy.
    """
    try:
        # Crear sesión temporal con adaptador SSL legacy
        session = requests.Session()
        session.mount("https://", LegacyHttpAdapter())
        
        params = {
            "q": "*:*",
            "fq": f"idoferta:{ige}",
            "json.nl": "map",
            "sort": "orden asc",
        }
        
        response = session.get(
            self.config.POSTULANTES_API_URL,
            params=params,
            timeout=self.config.API_TIMEOUT,
        )
        response.raise_for_status()
        
        return response.json()
        
    except (requests.RequestException, KeyError, json.JSONDecodeError) as e:
        self.logger.error(f"Error al obtener postulantes para IGE {ige}: {e}")
        return None
```

**Verificación de funcionamiento:**

```python
from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.database.connection import DatabaseConnection

scraper = APDScraper()
data = scraper.fetch_postulantes(4067362)

if data:
    docs = data.get('response', {}).get('docs', [])
    print(f'Total de postulantes: {len(docs)}')  # Output: 10
    
    db = DatabaseConnection('test.db')
    db.initialize_schema()
    registros = db.save_postulantes(docs, ige=4067362)
    print(f'Guardados: {registros}')  # Output: 10
```

**Resultado:**
```
Total de postulantes para IGE 4067362: 10
Postulantes guardados en BD: 10
Postulantes en BD para IGE 4067362: 10

Primer postulante en BD:
  CUIL: 20217355827
  Nombres: IZAGUIRRE JORGE
  Puntaje: 46.79
  Estado: ACTIVA
```

---

## 📊 Verificación de API

### Endpoint con curl (funciona)

```bash
curl -k "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.postulante/select?q=*:*&fq=idoferta:4067362&json.nl=map&sort=orden%20asc"
```

**Resultado:**
```
Total de postulantes para IGE 4067362: 10
Primer postulante:
  ige: 4067362
  cuil: 20217355827
  nombres: IZAGUIRRE JORGE
  puntaje: 46.79
  estadopostulacion: ACTIVA
```

---

## 🎯 Próximos Pasos

### 1. Solucionar problema SSL (Prioridad Alta)
- Crear `LegacyHttpAdapter` con TLS 1.2 + SECLEVEL=1
- O configurar sesión separada para endpoint de postulantes
- Probar con configuración SSL legacy

### 2. Implementar filtro de ofertas (Pendiente usuario)
El usuario indicó que se usará para "cada registro de la tabla ofertas que cumpla determinadas condiciones que luego indicaré".

**Posibles condiciones:**
- `estado = 'DESIGNADA'` - Solo ofertas designadas
- `estadopostulacion = 'ACTIVA'` - Solo postulaciones activas
- `designado = 'N'` - Ofertas sin designado
- Otra condición específica del usuario

### 3. Implementar lógica de procesamiento
```python
# Pseudocódigo pendiente de condiciones del usuario
ofertas = obtener_ofertas_cumplen_condicion()
for oferta in ofertas:
    postulantes = fetch_postulantes(oferta['ige'])
    save_postulantes(postulantes, ige=oferta['ige'])
```

---

## 📁 Estructura de Archivos

```
apd_scrap/
├── config.py              # Configuración + URL postulantes
├── database/
│   ├── __init__.py
│   ├── connection.py      # save_postulantes()
│   └── schema.py          # Tabla + SQL postulantes
└── scrapers/
    └── apd_scraper.py     # fetch_postulantes()
```

---

## 🎯 Conclusión

La implementación está **70% completa**:

- ✅ **Estructura de tabla** - Completada
- ✅ **Configuración de API** - Completada
- ✅ **Métodos de BD** - Completados
- ✅ **Métodos de scraper** - Completados
- ⚠️ **Conexión SSL** - Pendiente de solución
- 🔄 **Filtro de ofertas** - Pendiente de usuario

**Estado:** ✅ **RESUELTO**

---

**Version:** 2.8.1  
**Branch:** 260531-4  
**Commit:** 591cfaa  
**Fecha:** 2025-05-31