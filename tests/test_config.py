"""
Script de prueba para el sistema de configuración externa.

Este script verifica que la configuración externa funcione correctamente
con YAML, variables de entorno y valores por defecto.
"""

import sys
import os
from pathlib import Path
import tempfile
import shutil

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from apd_scrap.config import Config, ConfigError


def test_default_config():
    """Prueba la configuración por defecto."""
    print("=" * 60)
    print("TEST 1: Configuración por Defecto")
    print("=" * 60)

    config = Config(config_path=None)

    print(f"[OK] API URL: {config.API_BASE_URL}")
    print(f"[OK] API Timeout: {config.API_TIMEOUT}")
    print(f"[OK] DB Path: {config.DB_PATH}")
    print(f"[OK] Log Level: {config.get('logging.level')}")
    print(f"[OK] Environment: {config.ENVIRONMENT}")

    assert config.API_TIMEOUT == 60
    assert config.DB_PATH == "apd.db"
    assert config.ENVIRONMENT == "development"

    return True


def test_yaml_config():
    """Prueba la configuración desde YAML."""
    print("\n" + "=" * 60)
    print("TEST 2: Configuración desde YAML")
    print("=" * 60)

    # Crear archivo YAML temporal
    yaml_content = """
api:
  base_url: "https://example.com/api"
  timeout: 120

database:
  path: "test.db"

logging:
  level: "DEBUG"
  console_output: false

environment: "testing"
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    try:
        config = Config(config_path=yaml_path)

        print(f"[OK] API URL (desde YAML): {config.API_BASE_URL}")
        print(f"[OK] API Timeout (desde YAML): {config.API_TIMEOUT}")
        print(f"[OK] DB Path (desde YAML): {config.DB_PATH}")
        print(f"[OK] Log Level (desde YAML): {config.get('logging.level')}")
        print(f"[OK] Environment (desde YAML): {config.ENVIRONMENT}")

        assert config.API_BASE_URL == "https://example.com/api"
        assert config.API_TIMEOUT == 120
        assert config.DB_PATH == "test.db"
        assert config.ENVIRONMENT == "testing"

        return True
    finally:
        os.unlink(yaml_path)


def test_env_override():
    """Prueba la sobrescritura con variables de entorno."""
    print("\n" + "=" * 60)
    print("TEST 3: Sobrescritura con Variables de Entorno")
    print("=" * 60)

    # Crear archivo .env temporal
    env_content = """
APD_API_TIMEOUT=30
APD_DB_PATH=custom.db
APD_LOG_LEVEL=ERROR
APD_ENVIRONMENT=production
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(env_content)
        env_path = f.name

    try:
        config = Config(env_path=env_path)

        print(f"[OK] API Timeout (desde ENV): {config.API_TIMEOUT}")
        print(f"[OK] DB Path (desde ENV): {config.DB_PATH}")
        print(f"[OK] Log Level (desde ENV): {config.get('logging.level')}")
        print(f"[OK] Environment (desde ENV): {config.ENVIRONMENT}")

        assert config.API_TIMEOUT == 30
        assert config.DB_PATH == "custom.db"
        assert config.ENVIRONMENT == "production"

        return True
    finally:
        os.unlink(env_path)


def test_get_method():
    """Prueba el método get con notación de puntos."""
    print("\n" + "=" * 60)
    print("TEST 4: Método get() con Notación de Puntos")
    print("=" * 60)

    # Limpiar variables de entorno para este test
    for key in list(os.environ.keys()):
        if key.startswith("APD_"):
            del os.environ[key]

    config = Config()

    assert config.get("api.timeout") == 60
    print(f"[OK] config.get('api.timeout'): {config.get('api.timeout')}")

    assert config.get("database.path") == "apd.db"
    print(f"[OK] config.get('database.path'): {config.get('database.path')}")

    assert config.get("logging.console_output") == True
    print(f"[OK] config.get('logging.console_output'): {config.get('logging.console_output')}")

    assert config.get("nonexistent.key", "default") == "default"
    print(
        f"[OK] config.get('nonexistent.key', 'default'): {config.get('nonexistent.key', 'default')}"
    )

    return True


def test_validation():
    """Prueba la validación de configuración."""
    print("\n" + "=" * 60)
    print("TEST 5: Validación de Configuración")
    print("=" * 60)

    # Configuración válida
    config = Config()
    try:
        is_valid = config.validate()
        print(f"[OK] Configuración válida: {is_valid}")
    except ConfigError as e:
        print(f"[ERROR] Error inesperado: {e}")
        return False

    # Configuración inválida (timeout negativo)
    yaml_invalid = """
api:
  timeout: -10
"""

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_invalid)
        yaml_path = f.name

    try:
        config_invalid = Config(config_path=yaml_path)
        try:
            config_invalid.validate()
            print("[ERROR] Debería haber fallado la validación")
            return False
        except ConfigError as e:
            print(f"[OK] Validación detectó error: {e}")
            return True
    finally:
        os.unlink(yaml_path)


def test_priority():
    """Prueba la prioridad: ENV > YAML > Default."""
    print("\n" + "=" * 60)
    print("TEST 6: Prioridad de Configuración")
    print("=" * 60)

    # Limpiar variables de entorno primero
    for key in list(os.environ.keys()):
        if key.startswith("APD_"):
            del os.environ[key]

    # YAML: timeout = 90
    yaml_content = """
api:
  timeout: 90
"""

    # ENV: timeout = 45 (debería ganar)
    env_content = "APD_API_TIMEOUT=45"

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        f.write(yaml_content)
        yaml_path = f.name

    with tempfile.NamedTemporaryFile(mode="w", suffix=".env", delete=False) as f:
        f.write(env_content)
        env_path = f.name

    try:
        config = Config(config_path=yaml_path, env_path=env_path)

        # ENV debería tener prioridad sobre YAML
        assert config.API_TIMEOUT == 45
        print(f"[OK] ENV (45) tiene prioridad sobre YAML (90): {config.API_TIMEOUT}")

        return True
    finally:
        os.unlink(yaml_path)
        os.unlink(env_path)


def test_backward_compatibility():
    """Prueba compatibilidad con código existente."""
    print("\n" + "=" * 60)
    print("TEST 7: Compatibilidad con Código Existente")
    print("=" * 60)

    config = Config()

    # Estos atributos deben existir para compatibilidad
    assert hasattr(config, "API_BASE_URL")
    assert hasattr(config, "API_TIMEOUT")
    assert hasattr(config, "DB_PATH")
    assert hasattr(config, "LOG_NAME")
    assert hasattr(config, "LOG_LEVEL")
    assert hasattr(config, "LOG_FILE")
    assert hasattr(config, "LOG_MAX_BYTES")
    assert hasattr(config, "LOG_BACKUP_COUNT")
    assert hasattr(config, "LOG_CONSOLE_OUTPUT")
    assert hasattr(config, "OUTPUT_DIR")
    assert hasattr(config, "CIPHERS")

    print("[OK] Todos los atributos de compatibilidad existen")

    # Probar métodos existentes
    params = config.get_api_query_params("merlo", rows=10)
    assert params["rows"] == 10
    assert params["fq"] == "descdistrito:MERLO"
    print(f"[OK] get_api_query_params() funciona: {params}")

    filename = config.get_output_filename("merlo")
    assert filename == "output_merlo.json"
    print(f"[OK] get_output_filename() funciona: {filename}")

    return True


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("\n" + "[TEST] " * 15)
    print("APD-Scrap: Suite de Pruebas - Configuración Externa")
    print("[TEST] " * 15 + "\n")

    tests = [
        test_default_config,
        test_yaml_config,
        test_env_override,
        test_get_method,
        test_validation,
        test_priority,
        test_backward_compatibility,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test falló con excepción: {e}")
            import traceback

            traceback.print_exc()
            results.append(False)

    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    passed = sum(results)
    total = len(results)

    print(f"[OK] Pasados: {passed}/{total}")
    print(f"[ERROR] Fallidos: {total - passed}/{total}")

    if passed == total:
        print("\n[EXITO] Todas las pruebas pasaron exitosamente!")
        return 0
    else:
        print("\n[ERROR] Algunas pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
