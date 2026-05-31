# Análisis y Propuesta de Mejoras - APD-Scrap

**Fecha:** 2025-05-31  
**Proyecto:** APD-Scrap - Scraper de ofertas educativas del sistema APD  
**Versión actual:** 1.0 (desarrollo activo)

---

## 📊 Resumen Ejecutivo

APD-Scrap es un scraper funcional que extrae ofertas laborales docentes de la API del gobierno argentino. El proyecto cumple su objetivo principal pero presenta oportunidades significativas de mejora en áreas como estructura, calidad del código, seguridad, mantenibilidad y robustez.

**Estado actual:**
- ✅ Funcionalidad básica operativa
- ✅ Conexión con API funcionando
- ✅ Almacenamiento en SQLite implementado
- ⚠️ Monolito en un solo archivo
- ⚠️ Sin tests
- ⚠️ Sin logging estructurado
- ⚠️ Configuración hardcoded

---

## 🎯 Matriz de Prioridad

| Mejora | Importancia | Impacto | Esfuerzo | Prioridad |
|--------|-------------|---------|----------|-----------|
| Separar responsabilidades en módulos | Alta | Alto | Medio | 🔴 Alta |
| Sistema de logging | Alta | Alto | Bajo | 🔴 Alta |
| Configuración externa | Alta | Alto | Bajo | 🔴 Alta |
| Tests unitarios | Alta | Alto | Medio | 🔴 Alta |
| Manejo robusto de errores | Alta | Alto | Medio | 🔴 Alta |
| Tipo hints y docstrings | Media | Alto | Bajo | 🟡 Media |
| Pre-commit hooks y linting | Media | Alto | Bajo | 🟡 Media |
| Reintentos automáticos | Media | Alto | Bajo | 🟡 Media |
| Variables de entorno | Media | Medio | Bajo | 🟡 Media |
| CLI mejorado | Media | Medio | Bajo | 🟡 Media |
| Indices en base de datos | Media | Medio | Bajo | 🟡 Media |
| CI/CD | Media | Medio | Medio | 🟡 Media |
| Documentación de API | Baja | Medio | Medio | 🟢 Baja |
| Dockerización | Baja | Medio | Medio | 🟢 Baja |
| Cache de respuestas | Baja | Medio | Alto | 🟢 Baja |
| Dashboard de estadísticas | Baja | Bajo | Alto | 🟢 Baja |

**Leyenda:**
- 🔴 **Alta prioridad:** Implementar en corto plazo (1-2 semanas)
- 🟡 **Media prioridad:** Implementar en mediano plazo (1 mes)
- 🟢 **Baja prioridad:** Implementar en largo plazo (3+ meses)

---

## 🔴 Mejoras de Alta Prioridad

### 1. Separar Responsabilidades en Módulos

**Problema actual:**
- Todo el código está en `main.py` (un solo archivo de ~150 líneas)
- Mezcla de lógica de scraping, base de datos, configuración y CLI
- Difícil de mantener y probar

**Solución propuesta:**
```
apd_scrap/
├── __init__.py
├── main.py                 # Punto de entrada
├── config.py               # Configuración
├── scrapers/
│   ├── __init__.py
│   └── apd_scraper.py      # Lógica de scraping
├── database/
│   ├── __init__.py
│   ├── connection.py       # Conexión a DB
│   ├── models.py           # Modelos/ORM
│   └── repositories.py     # Acceso a datos
├── cli/
│   ├── __init__.py
│   └── commands.py         # Comandos CLI
├── utils/
│   ├── __init__.py
│   ├── logging.py          # Configuración logging
│   └── ssl_adapter.py      # SSL adapter
└── tests/
```

**Impacto:**
- ✅ Mejor organización y legibilidad
- ✅ Facilita testing
- ✅ Reutilización de componentes
- ✅ Escalabilidad futura

**Esfuerzo:** Medio (~6-8 horas)

---

### 2. Sistema de Logging Estructurado

**Problema actual:**
- Solo usa `print()` statements
- Sin niveles de log (INFO, WARNING, ERROR)
- Sin rotación de archivos
- Sin timestamps estructurados

**Solución propuesta:**
```python
import logging
from logging.handlers import RotatingFileHandler
import sys

def setup_logging(log_level=logging.INFO, log_file='apd_scrap.log'):
    """Configura el sistema de logging."""
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    
    # Console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    
    # File handler con rotación
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5*1024*1024,  # 5MB
        backupCount=3
    )
    file_handler.setFormatter(formatter)
    
    # Root logger
    logger = logging.getLogger('apd_scrap')
    logger.setLevel(log_level)
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    
    return logger
```

**Uso:**
```python
logger = logging.getLogger('apd_scrap')
logger.info(f"Descargando {total_records} registros para {distrito}")
logger.warning(f"JSON decode error, usando fallback para distrito {distrito}")
logger.error(f"Error al conectar con API: {e}")
```

**Impacto:**
- ✅ Trazabilidad de errores
- ✅ Debugging más fácil
- ✅ Auditoría de operaciones
- ✅ Monitoreo en producción

**Esfuerzo:** Bajo (~2-3 horas)

---

### 3. Configuración Externa

**Problema actual:**
- URLs hardcoded en el código
- Límites de tiempo hardcoded
- Sin archivos de configuración
- Difícil cambiar entre entornos

**Solución propuesta:**

**`config.yaml`:**
```yaml
api:
  base_url: "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
  timeout: 60
  max_retries: 3
  retry_delay: 5

database:
  path: "apd.db"
  batch_size: 1000

logging:
  level: "INFO"
  file: "apd_scrap.log"
  max_bytes: 5242880
  backup_count: 3

output:
  directory: "output"
  format: "json"
  pretty_print: true
```

**`config.py`:**
```python
import yaml
from pathlib import Path
from typing import Dict, Any

class Config:
    """Gestiona la configuración del sistema."""
    
    def __init__(self, config_path: str = "config.yaml"):
        self.config = self._load_config(config_path)
    
    def _load_config(self, path: str) -> Dict[str, Any]:
        """Carga configuración desde archivo YAML."""
        config_file = Path(path)
        if config_file.exists():
            with open(config_file, 'r', encoding='utf-8') as f:
                return yaml.safe_load(f)
        return self._get_default_config()
    
    def get(self, key: str, default=None):
        """Obtiene valor de configuración con notación de puntos."""
        keys = key.split('.')
        value = self.config
        for k in keys:
            value = value.get(k, {})
        return value if value != {} else default
```

**Impacto:**
- ✅ Flexibilidad de configuración
- ✅ Fácil cambio entre entornos
- ✅ Valores sensibles fuera del código
- ✅ Personalización por usuario

**Esfuerzo:** Bajo (~3-4 horas)

---

### 4. Tests Unitarios

**Problema actual:**
- Sin tests
- Sin validación de correcciones
- Miedo a refactorizar
- Regresiones no detectadas

**Solución propuesta:**

**`tests/test_scraper.py`:**
```python
import pytest
from unittest.mock import Mock, patch
from apd_scrap.scrapers.apd_scraper import APDScraper

class TestAPDScraper:
    """Tests para APDScraper."""
    
    @patch('requests.Session.get')
    def test_get_total_records(self, mock_get):
        """Prueba obtención de total de registros."""
        mock_response = Mock()
        mock_response.json.return_value = {
            'response': {'numFound': 100}
        }
        mock_response.raise_for_status.return_value = None
        mock_get.return_value = mock_response
        
        scraper = APDScraper()
        total = scraper.get_total_records('MERLO')
        assert total == 100
```

**`tests/test_database.py`:**
```python
import pytest
import sqlite3
import tempfile
from pathlib import Path
from apd_scrap.database.connection import DatabaseConnection

@pytest.fixture
def temp_db():
    """Crea base de datos temporal para tests."""
    fd, path = tempfile.mkstemp(suffix='.db')
    yield path
    Path(path).unlink()

class TestDatabaseConnection:
    """Tests para DatabaseConnection."""
    
    def test_insert_oferta(self, temp_db):
        """Prueba inserción de oferta."""
        db = DatabaseConnection(temp_db)
        db.initialize_schema()
        
        oferta = {
            'ige': 123,
            'estado': 'Publicada',
            'cargo': 'Profesor de Matemática'
        }
        result = db.insert_oferta(oferta)
        assert result is True
```

**`pytest.ini`:**
```ini
[pytest]
testpaths = tests
python_files = test_*.py
python_classes = Test*
python_functions = test_*
addopts = -v --cov=apd_scrap --cov-report=html --cov-report=term-missing
```

**Impacto:**
- ✅ Confianza en el código
- ✅ Refactoring seguro
- ✅ Documentación viva
- ✅ Detección temprana de bugs

**Esfuerzo:** Medio (~8-10 horas)

---

### 5. Manejo Robusto de Errores

**Problema actual:**
- Manejo básico de excepciones
- Sin recuperación automática
- Sin validación de datos
- Errores crípticos para usuarios

**Solución propuesta:**

**`utils/exceptions.py`:**
```python
class APDScrapError(Exception):
    """Base exception for APD-Scrap."""
    pass

class APIConnectionError(APDScrapError):
    """Error al conectar con la API."""
    pass

class InvalidDataError(APDScrapError):
    """Datos inválidos recibidos."""
    pass

class DatabaseError(APDScrapError):
    """Error en operación de base de datos."""
    pass

class DistrictNotFoundError(APDScrapError):
    """Distrito no encontrado."""
    pass
```

**`scrapers/apd_scraper.py` con manejo mejorado:**
```python
import time
from typing import Optional, Dict, Any
from utils.exceptions import APIConnectionError, InvalidDataError

class APDScraper:
    MAX_RETRIES = 3
    RETRY_DELAY = 5
    
    def fetch_data(self, params: Dict[str, Any]) -> Optional[Dict]:
        """Obtiene datos de la API con reintentos."""
        last_error = None
        
        for attempt in range(self.MAX_RETRIES):
            try:
                response = self.session.get(
                    self.base_url,
                    params=params,
                    timeout=self.timeout
                )
                response.raise_for_status()
                
                data = self._parse_response(response)
                self._validate_data(data)
                return data
                
            except requests.Timeout as e:
                last_error = e
                logger.warning(f"Timeout en intento {attempt + 1}/{self.MAX_RETRIES}")
                
            except requests.HTTPError as e:
                if e.response.status_code == 404:
                    raise DistrictNotFoundError(f"Distrito no encontrado")
                last_error = e
                
            except (json.JSONDecodeError, KeyError) as e:
                raise InvalidDataError(f"Datos inválidos: {e}")
            
            if attempt < self.MAX_RETRIES - 1:
                time.sleep(self.RETRY_DELAY)
        
        raise APIConnectionError(f"No se pudo conectar tras {self.MAX_RETRIES} intentos: {last_error}")
    
    def _validate_data(self, data: Dict) -> None:
        """Valida estructura de datos recibida."""
        if not isinstance(data, dict):
            raise InvalidDataError("La respuesta no es un diccionario")
        
        if 'response' not in data:
            raise InvalidDataError("Falta campo 'response'")
        
        if 'docs' not in data['response']:
            raise InvalidDataError("Falta campo 'response.docs'")
```

**Impacto:**
- ✅ Recuperación automática
- ✅ Mensajes de error claros
- ✅ Validación de datos
- ✅ Mejor UX

**Esfuerzo:** Medio (~4-6 horas)

---

## 🟡 Mejoras de Media Prioridad

### 6. Type Hints y Docstrings

**Problema actual:**
- Sin type hints
- Sin docstrings
- Autocompletado limitado
- Difícil entender funciones

**Solución propuesta:**

```python
from typing import List, Dict, Any, Optional
from dataclasses import dataclass

@dataclass
class Oferta:
    """Modelo de datos para una oferta educativa."""
    ige: int
    estado: str
    cargo: str
    escuela: str
    descdistrito: str
    iniciooferta: str
    finoferta: str
    # ... otros campos
    
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Oferta':
        """Crea una Oferta desde un diccionario."""
        return cls(**{k: data.get(k) for k in cls.__dataclass_fields__})

def guardar_ofertas_en_db(ofertas: List[Oferta], db_path: str = 'apd.db') -> int:
    """
    Guarda o actualiza una lista de ofertas en la base de datos.
    
    Args:
        ofertas: Lista de ofertas a guardar
        db_path: Ruta al archivo de base de datos
        
    Returns:
        Número de registros guardados/actualizados
        
    Raises:
        DatabaseError: Si hay un error en la base de datos
        
    Example:
        >>> ofertas = [Oferta(ige=1, estado='Publicada', ...)]
        >>> guardar_ofertas_en_db(ofertas)
        1
    """
    if not ofertas:
        logger.warning("Lista de ofertas vacía")
        return 0
    
    try:
        with sqlite3.connect(db_path) as conn:
            # ... implementación
            return len(ofertas)
    except sqlite3.Error as e:
        raise DatabaseError(f"Error guardando ofertas: {e}")
```

**Impacto:**
- ✅ Mejor autocompletado
- ✅ Documentación integrada
- ✅ Detección temprana de errores
- ✅ IDEs más útiles

**Esfuerzo:** Bajo (~3-4 horas)

---

### 7. Pre-commit Hooks y Linting

**Problema actual:**
- Sin validación de código antes de commit
- Sin formateo automático
- Inconsistencias de estilo
- Bugs simples no detectados

**Solución propuesta:**

**`.pre-commit-config.yaml`:**
```yaml
repos:
  - repo: https://github.com/psf/black
    rev: 23.12.1
    hooks:
      - id: black
        language_version: python3.9
        
  - repo: https://github.com/astral-sh/ruff-pre-commit
    rev: v0.1.9
    hooks:
      - id: ruff
        args: [--fix, --exit-non-zero-on-fix]
        
  - repo: https://github.com/pre-commit/mirrors-mypy
    rev: v1.8.0
    hooks:
      - id: mypy
        additional_dependencies: [types-requests]
        
  - repo: https://github.com/pre-commit/pre-commit-hooks
    rev: v4.5.0
    hooks:
      - id: check-yaml
      - id: check-json
      - id: check-toml
      - id: check-added-large-files
      - id: check-merge-conflict
      - id: end-of-file-fixer
      - id: trailing-whitespace
```

**`pyproject.toml`:**
```toml
[tool.black]
line-length = 100
target-version = ['py39']
include = '\.pyi?$'

[tool.ruff]
line-length = 100
select = ["E", "F", "W", "I", "N", "UP", "B", "C4"]
ignore = ["E501"]

[tool.mypy]
python_version = "3.9"
warn_return_any = true
warn_unused_configs = true
ignore_missing_imports = true
```

**Instalación:**
```bash
pip install black ruff mypy pre-commit
pre-commit install
```

**Impacto:**
- ✅ Código consistente
- ✅ Detección automática de issues
- ✅ Mejor legibilidad
- ✅ Less time in code reviews

**Esfuerzo:** Bajo (~2-3 horas)

---

### 8. Reintentos Automáticos con Backoff

**Problema actual:**
- Sin reintentos automáticos
- Sin backoff exponencial
- Fallos únicos causan error total

**Solución propuesta:**

```python
import time
from typing import Callable, TypeVar, Optional
from functools import wraps

T = TypeVar('T')

def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    exceptions: tuple = (Exception,)
) -> Callable:
    """
    Decorador para reintentos con backoff exponencial.
    
    Args:
        max_retries: Número máximo de reintentos
        initial_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        backoff_factor: Factor de multiplicación del delay
        exceptions: Tupla de excepciones a capturar
    """
    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            last_exception = None
            delay = initial_delay
            
            for attempt in range(max_retries + 1):
                try:
                    return func(*args, **kwargs)
                except exceptions as e:
                    last_exception = e
                    
                    if attempt == max_retries:
                        break
                    
                    logger.warning(
                        f"Intento {attempt + 1}/{max_retries} falló. "
                        f"Reintentando en {delay:.1f}s... Error: {e}"
                    )
                    time.sleep(delay)
                    delay = min(delay * backoff_factor, max_delay)
            
            raise last_exception
        
        return wrapper
    return decorator

# Uso:
@retry_with_backoff(
    max_retries=3,
    initial_delay=2.0,
    exceptions=(requests.Timeout, requests.ConnectionError)
)
def fetch_api_data(url: str, params: dict) -> dict:
    """Obtiene datos de la API con reintentos."""
    response = requests.get(url, params=params, timeout=60)
    response.raise_for_status()
    return response.json()
```

**Impacto:**
- ✅ Mayor robustez
- ✅ Recuperación de fallos temporales
- ✅ Menos errores en producción
- ✅ UX mejorada

**Esfuerzo:** Bajo (~2-3 horas)

---

### 9. Variables de Entorno

**Problema actual:**
- Configuración mezclada con código
- Difícil cambiar entre entornos
- Riesgo de commits con valores locales

**Solución propuesta:**

**`.env.example`:**
```bash
# API Configuration
APD_API_URL=https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select
APD_API_TIMEOUT=60
APD_MAX_RETRIES=3

# Database Configuration
APD_DB_PATH=apd.db

# Logging Configuration
APD_LOG_LEVEL=INFO
APD_LOG_FILE=apd_scrap.log

# Output Configuration
APD_OUTPUT_DIR=output
```

**`config.py`:**
```python
import os
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()

class Config:
    """Configuración desde variables de entorno."""
    
    # API
    API_URL: str = os.getenv('APD_API_URL', 'https://servicios3.abc.gob.ar/...')
    API_TIMEOUT: int = int(os.getenv('APD_API_TIMEOUT', '60'))
    MAX_RETRIES: int = int(os.getenv('APD_MAX_RETRIES', '3'))
    
    # Database
    DB_PATH: str = os.getenv('APD_DB_PATH', 'apd.db')
    
    # Logging
    LOG_LEVEL: str = os.getenv('APD_LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('APD_LOG_FILE', 'apd_scrap.log')
    
    # Output
    OUTPUT_DIR: str = os.getenv('APD_OUTPUT_DIR', 'output')
    
    @classmethod
    def validate(cls) -> None:
        """Valida configuración."""
        if cls.API_TIMEOUT <= 0:
            raise ValueError("API_TIMEOUT debe ser positivo")
        if cls.MAX_RETRIES < 0:
            raise ValueError("MAX_RETRIES debe ser no negativo")
```

**Impacto:**
- ✅ Configuración por entorno
- ✅ Sin secretos en código
- ✅ Fácil despliegue
- ✅ Seguridad mejorada

**Esfuerzo:** Bajo (~2-3 horas)

---

### 10. CLI Mejorado

**Problema actual:**
- CLI básico
- Sin subcomandos
- Sin ayuda detallada
- Sin opciones avanzadas

**Solución propuesta:**

```python
import argparse
from typing import List

def create_parser() -> argparse.ArgumentParser:
    """Crea el parser de argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(
        description='Scraper de ofertas educativas del sistema APD',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Descargar ofertas de Merlo
  python main.py --distrito merlo
  
  # Descargar múltiples distritos
  python main.py --distrito merlo moreno moron
  
  # Descargar todos los distritos disponibles
  python main.py --all
  
  # Usar archivo de configuración personalizado
  python main.py --config custom_config.yaml --distrito matanza
  
  # Ver estadísticas de distrito
  python main.py stats --distrito merlo
  
  # Listar distritos disponibles
  python main.py list-districts
        """
    )
    
    # Subcomandos
    subparsers = parser.add_subparsers(dest='command', help='Comandos disponibles')
    
    # Comando: download (default)
    download_parser = subparsers.add_parser('download', help='Descargar ofertas')
    download_parser.add_argument(
        '--distrito', '-d',
        nargs='+',
        help='Distrito(s) a descargar (merlo, moreno, moron, etc.)'
    )
    download_parser.add_argument(
        '--all', '-a',
        action='store_true',
        help='Descargar todos los distritos disponibles'
    )
    download_parser.add_argument(
        '--output-dir', '-o',
        default='output',
        help='Directorio de salida (default: output)'
    )
    download_parser.add_argument(
        '--no-db',
        action='store_true',
        help='No guardar en base de datos'
    )
    
    # Comando: stats
    stats_parser = subparsers.add_parser('stats', help='Ver estadísticas')
    stats_parser.add_argument(
        '--distrito', '-d',
        required=True,
        help='Distrito para ver estadísticas'
    )
    
    # Comando: list-districts
    subparsers.add_parser('list-districts', help='Listar distritos disponibles')
    
    # Comando: export
    export_parser = subparsers.add_parser('export', help='Exportar datos')
    export_parser.add_argument(
        '--format', '-f',
        choices=['csv', 'json', 'xlsx'],
        default='json',
        help='Formato de exportación'
    )
    export_parser.add_argument(
        '--distrito', '-d',
        required=True,
        help='Distrito a exportar'
    )
    
    return parser

def main():
    """Punto de entrada principal."""
    parser = create_parser()
    args = parser.parse_args()
    
    if not args.command:
        args.command = 'download'
    
    if args.command == 'download':
        handle_download(args)
    elif args.command == 'stats':
        handle_stats(args)
    elif args.command == 'list-districts':
        handle_list_districts()
    elif args.command == 'export':
        handle_export(args)
```

**Impacto:**
- ✅ CLI más amigable
- ✅ Más funcionalidades
- ✅ Mejor documentación
- ✅ UX mejorada

**Esfuerzo:** Bajo (~3-4 horas)

---

### 11. Índices en Base de Datos

**Problema actual:**
- Solo PK en ige
- Consultas lentas en campos frecuentes
- Sin índices para filtros comunes

**Solución propuesta:**

**`migrations/002_add_indexes.sql`:**
```sql
-- Índices para consultas frecuentes

-- Por estado y distrito (consulta más común)
CREATE INDEX IF NOT EXISTS idx_ofertas_estado_distrito 
ON ofertas(estado, descdistrito);

-- Por distrito
CREATE INDEX IF NOT EXISTS idx_ofertas_distrito 
ON ofertas(descdistrito);

-- Por fechas (para consultas de rango)
CREATE INDEX IF NOT EXISTS idx_ofertas_inicio 
ON ofertas(iniciooferta);

CREATE INDEX IF NOT EXISTS idx_ofertas_fin 
ON ofertas(finoferta);

-- Por tipo de oferta
CREATE INDEX IF NOT EXISTS idx_ofertas_tipo 
ON ofertas(tipooferta, tipooferta_id);

-- Por escuela
CREATE INDEX IF NOT EXISTS idx_ofertas_escuela 
ON ofertas(escuela);

-- Para búsqueda por cargo
CREATE INDEX IF NOT EXISTS idx_ofertas_cargo 
ON ofertas(cargo);

-- Índice compuesto para estadísticas
CREATE INDEX IF NOT EXISTS idx_ofertas_stats 
ON ofertas(descdistrito, estado, iniciooferta);
```

**Validación de mejora:**
```sql
-- Plan de ejecución antes/después
EXPLAIN QUERY PLAN 
SELECT * FROM ofertas 
WHERE estado = 'Publicada' AND descdistrito = 'MERLO';
```

**Impacto:**
- ✅ Consultas 10-100x más rápidas
- ✅ Mejor rendimiento
- ✅ Dashboard más responsivo

**Esfuerzo:** Bajo (~1-2 horas)

---

### 12. CI/CD con GitHub Actions

**Problema actual:**
- Sin validación automática
- Sin tests en PRs
- Sin despliegue automático
- Sin calidad de código asegurada

**Solución propuesta:**

**`.github/workflows/ci.yml`:**
```yaml
name: CI/CD

on:
  push:
    branches: [ main, develop ]
  pull_request:
    branches: [ main ]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: [3.9, 3.10, 3.11]
    
    steps:
    - uses: actions/checkout@v4
    
    - name: Set up Python ${{ matrix.python-version }}
      uses: actions/setup-python@v4
      with:
        python-version: ${{ matrix.python-version }}
    
    - name: Cache pip
      uses: actions/cache@v3
      with:
        path: ~/.cache/pip
        key: ${{ runner.os }}-pip-${{ hashFiles('**/requirements.txt') }}
        restore-keys: |
          ${{ runner.os }}-pip-
    
    - name: Install dependencies
      run: |
        python -m pip install --upgrade pip
        pip install -r requirements.txt
        pip install pytest pytest-cov black ruff mypy
    
    - name: Lint with ruff
      run: |
        ruff check .
    
    - name: Format check with black
      run: |
        black --check .
    
    - name: Type check with mypy
      run: |
        mypy apd_scrap --ignore-missing-imports
    
    - name: Run tests
      run: |
        pytest --cov=apd_scrap --cov-report=xml
    
    - name: Upload coverage
      uses: codecov/codecov-action@v3
      with:
        file: ./coverage.xml
        flags: unittests
        name: codecov-umbrella

  security:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v4
    
    - name: Run safety check
      run: |
        pip install safety
        safety check
```

**Impacto:**
- ✅ Calidad asegurada
- ✅ Detección temprana de bugs
- ✅ Documentación de cobertura
- ✅ Confianza en despliegues

**Esfuerzo:** Medio (~4-5 horas)

---

## 🟢 Mejoras de Baja Prioridad

### 13. Documentación de API con Sphinx

**Problema actual:**
- Sin documentación formal
- Difícil para nuevos contribuidores
- Sin ejemplos de uso detallados

**Solución propuesta:**

**`docs/index.rst`:**
```rst
APD-Scrap Documentation
========================

Bienvenido a la documentación de APD-Scrap.

.. toctree::
   :maxdepth: 2
   :caption: Contents:

   installation
   quickstart
   api
   cli
   contributing

Installation
------------

.. code-block:: bash

   git clone https://github.com/your-org/apd-scrap.git
   cd apd-scrap
   python -m venv venv
   source venv/bin/activate  # Windows: venv\Scripts\activate
   pip install -r requirements.txt

Quick Start
-----------

Basic usage:

.. code-block:: python

   from apd_scrap import APDScraper
   
   scraper = APDScraper()
   ofertas = scraper.fetch_district('merlo')
   scraper.save_to_database(ofertas)
```

**Impacto:**
- ✅ Mejor onboarding
- ✅ Ejemplos claros
- ✅ Documentación generada

**Esfuerzo:** Medio (~6-8 horas)

---

### 14. Dockerización

**Problema actual:**
- Difícil despliegue
- Dependencias manuales
- Sin aislamiento de entorno

**Solución propuesta:**

**`Dockerfile`:**
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar y instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar código
COPY apd_scrap/ ./apd_scrap/
COPY config.yaml .

# Crear directorio de salida
RUN mkdir -p /app/output

# Montar volume para datos
VOLUME ["/app/data"]

# Entry point
ENTRYPOINT ["python", "-m", "apd_scrap.main"]
```

**`docker-compose.yml`:**
```yaml
version: '3.8'

services:
  apd-scrap:
    build: .
    volumes:
      - ./output:/app/output
      - ./data:/app/data
      - ./config.yaml:/app/config.yaml
    environment:
      - APD_LOG_LEVEL=INFO
      - APD_OUTPUT_DIR=/app/output
    command: ["--distrito", "merlo"]
```

**Impacto:**
- ✅ Despliegue consistente
- ✅ Aislamiento de entorno
- ✅ Fácil distribución

**Esfuerzo:** Medio (~4-5 horas)

---

### 15. Cache de Respuestas con TTL

**Problema actual:**
- Sin cache de respuestas
- Solicitudes redundantes
- Mayor carga en API externa

**Solución propuesta:**

```python
import json
import hashlib
from pathlib import Path
from datetime import datetime, timedelta

class ResponseCache:
    """Cache de respuestas de API con TTL."""
    
    def __init__(self, cache_dir: str = 'cache', ttl_hours: int = 24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.ttl = timedelta(hours=ttl_hours)
    
    def _get_cache_key(self, url: str, params: dict) -> str:
        """Genera clave única para la solicitud."""
        content = f"{url}{json.dumps(params, sort_keys=True)}"
        return hashlib.md5(content.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key: str) -> Path:
        """Obtiene ruta del archivo de cache."""
        return self.cache_dir / f"{cache_key}.json"
    
    def _is_valid(self, cache_file: Path) -> bool:
        """Verifica si el cache aún es válido."""
        if not cache_file.exists():
            return False
        
        mtime = datetime.fromtimestamp(cache_file.stat().st_mtime)
        return datetime.now() - mtime < self.ttl
    
    def get(self, url: str, params: dict) -> Optional[dict]:
        """Obtiene respuesta del cache si existe y es válida."""
        cache_key = self._get_cache_key(url, params)
        cache_file = self._get_cache_file(cache_key)
        
        if self._is_valid(cache_file):
            with open(cache_file, 'r', encoding='utf-8') as f:
                logger.info(f"Cache HIT para {url}")
                return json.load(f)
        
        return None
    
    def set(self, url: str, params: dict, data: dict) -> None:
        """Guarda respuesta en cache."""
        cache_key = self._get_cache_key(url, params)
        cache_file = self._get_cache_file(cache_key)
        
        with open(cache_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Guardado en cache: {cache_key}")
    
    def clear(self) -> None:
        """Limpia todo el cache."""
        for file in self.cache_dir.glob('*.json'):
            file.unlink()
        logger.info("Cache limpiado")

# Uso en scraper:
cache = ResponseCache(ttl_hours=24)

def fetch_with_cache(url: str, params: dict) -> dict:
    """Obtiene datos usando cache."""
    cached = cache.get(url, params)
    if cached:
        return cached
    
    data = fetch_api_data(url, params)
    cache.set(url, params, data)
    return data
```

**Impacto:**
- ✅ Menor carga en API
- ✅ Respuestas más rápidas
- ✅ Ahorro de ancho de banda

**Esfuerzo:** Alto (~6-8 horas)

---

### 16. Dashboard de Estadísticas

**Problema actual:**
- Sin visualización de datos
- Difícil analizar tendencias
- Sin reportes automáticos

**Solución propuesta:**

Usar Streamlit para un dashboard interactivo:

**`dashboard/app.py`:**
```python
import streamlit as st
import pandas as pd
import plotly.express as px
from apd_scrap.database.connection import DatabaseConnection

st.set_page_config(page_title="APD-Scrap Dashboard", layout="wide")

st.title("📊 Dashboard de Ofertas Educativas - APD")

# Conexión a DB
@st.cache_data(ttl=300)
def load_data():
    """Carga datos desde la base de datos."""
    db = DatabaseConnection('apd.db')
    query = """
        SELECT 
            descdistrito,
            estado,
            tipooferta,
            iniciooferta,
            finoferta,
            cargo
        FROM ofertas
    """
    return pd.read_sql_query(query, db.connection)

df = load_data()

# Métricas principales
col1, col2, col3, col4 = st.columns(4)
with col1:
    st.metric("Total Ofertas", len(df))
with col2:
    st.metric("Publicadas", len(df[df['estado'] == 'Publicada']))
with col3:
    st.metric("Distritos", df['descdistrito'].nunique())
with col4:
    st.metric("Tipos de Cargo", df['cargo'].nunique())

# Filtros
st.sidebar.header("Filtros")
distritos = st.sidebar.multiselect(
    "Distrito",
    options=df['descdistrito'].unique(),
    default=df['descdistrito'].unique()
)

estados = st.sidebar.multiselect(
    "Estado",
    options=df['estado'].unique(),
    default=df['estado'].unique()
)

df_filtered = df[
    df['descdistrito'].isin(distritos) & 
    df['estado'].isin(estados)
]

# Gráficos
tab1, tab2, tab3 = st.tabs(["Por Distrito", "Por Estado", "Timeline"])

with tab1:
    fig_distrito = px.bar(
        df_filtered.groupby('descdistrito').size().reset_index(name='count'),
        x='descdistrito',
        y='count',
        title="Ofertas por Distrito"
    )
    st.plotly_chart(fig_distrito, use_container_width=True)

with tab2:
    fig_estado = px.pie(
        df_filtered,
        names='estado',
        title="Distribución por Estado"
    )
    st.plotly_chart(fig_estado, use_container_width=True)

with tab3:
    df_filtered['iniciooferta'] = pd.to_datetime(df_filtered['iniciooferta'])
    timeline = df_filtered.groupby(
        df_filtered['iniciooferta'].dt.date
    ).size().reset_index(name='count')
    
    fig_timeline = px.line(
        timeline,
        x='iniciooferta',
        y='count',
        title="Ofertas en el Tiempo"
    )
    st.plotly_chart(fig_timeline, use_container_width=True)
```

**`requirements-dashboard.txt`:**
```txt
streamlit==1.29.0
plotly==5.18.0
pandas==2.1.4
```

**Ejecutar:**
```bash
streamlit run dashboard/app.py
```

**Impacto:**
- ✅ Visualización de datos
- ✅ Análisis interactivo
- ✅ Toma de decisiones informada

**Esfuerzo:** Alto (~8-10 horas)

---

## 📋 Roadmap de Implementación

### Fase 1: Fundamentos (Semanas 1-2)
- [x] Separar responsabilidades en módulos
- [ ] Sistema de logging estructurado
- [ ] Configuración externa
- [ ] Type hints y docstrings

### Fase 2: Calidad (Semanas 3-4)
- [ ] Tests unitarios
- [ ] Pre-commit hooks y linting
- [ ] Manejo robusto de errores
- [ ] Reintentos automáticos

### Fase 3: Robustez (Semanas 5-6)
- [ ] Variables de entorno
- [ ] CLI mejorado
- [ ] Índices en base de datos
- [ ] CI/CD

### Fase 4: Extras (Semanas 7-10)
- [ ] Documentación con Sphinx
- [ ] Dockerización
- [ ] Cache de respuestas
- [ ] Dashboard de estadísticas

---

## 🛠️ Herramientas Sugeridas

```txt
# requirements.txt
requests==2.31.0
pyyaml==6.0.1
python-dotenv==1.0.0
tenacity==8.2.3

# Calidad de código
black==23.12.1
ruff==0.1.9
mypy==1.8.0
pre-commit==3.6.0

# Testing
pytest==7.4.3
pytest-cov==4.1.0
pytest-mock==3.12.0

# Dashboard (opcional)
streamlit==1.29.0
plotly==5.18.0
pandas==2.1.4

# Documentación (opcional)
sphinx==7.2.6
sphinx-rtd-theme==2.0.0
```

---

## 💡 Patrones de Diseño Sugeridos

1. **Repository Pattern**: Para acceso a datos
2. **Factory Pattern**: Para crear scrapers
3. **Strategy Pattern**: Para diferentes formatos de exportación
4. **Observer Pattern**: Para notificaciones de eventos
5. **Singleton Pattern**: Para conexión a base de datos

---

## 📊 Métricas de Éxito

- **Cobertura de tests**: > 80%
- **Tiempo de respuesta**: < 30s para 15k registros
- **Uptime de scraper**: > 99%
- **Reintentos exitosos**: > 95% de fallos recuperados
- **Tiempo de setup**: < 5 minutos para nuevo desarrollador

---

## 🔄 Mantenimiento Continuo

### Tareas Mensuales
- Actualizar dependencias
- Revisar logs de errores
- Validar endpoints de API
- Limpiar cache antiguo

### Tareas Trimestrales
- Revisar y mejorar tests
- Actualizar documentación
- Revisar métricas de rendimiento
- Planificar nuevas features

---

## 📞 Contacto y Soporte

Para preguntas o sugerencias sobre este análisis:
- Crear issue en el repositorio
- Contactar al equipo de desarrollo
- Revisar documentación actualizada

---

**Documento generado:** 2025-05-31  
**Última actualización:** 2025-05-31  
**Versión:** 1.0