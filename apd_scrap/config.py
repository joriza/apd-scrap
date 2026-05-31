"""
Configuración centralizada de APD-Scrap.

Este módulo proporciona un sistema de configuración flexible que soporta:
- Valores por defecto hardcoded
- Archivos YAML
- Variables de entorno
- Configuración por entorno (development, staging, production)

Prioridad de configuración (mayor a menor):
1. Variables de entorno (.env)
2. Archivo YAML (config.yaml)
3. Valores por defecto
"""

import logging
import os
from pathlib import Path
from typing import Any, Optional

try:
    import yaml

    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from dotenv import load_dotenv

    DOTENV_AVAILABLE = True
except ImportError:
    DOTENV_AVAILABLE = False


class ConfigError(Exception):
    """Excepción para errores de configuración."""

    pass


class Config:
    """
    Gestiona la configuración del sistema.

    Prioridad de carga:
    1. Variables de entorno (.env)
    2. Archivo YAML (config.yaml)
    3. Valores por defecto
    """

    # Valores por defecto
    DEFAULT_CONFIG = {
        # API Configuration
        "api": {
            "base_url": "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select",
            "postulantes_url": "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.postulante/select",
            "timeout": 60,
        },
        # Database Configuration
        "database": {
            "path": "apd.db",
            "batch_size": 1000,
        },
        # Logging Configuration
        "logging": {
            "name": "apd_scrap",
            "level": "INFO",
            "file": "apd_scrap.log",
            "max_bytes": 5 * 1024 * 1024,
            "backup_count": 3,
            "console_output": True,
        },
        # Output Configuration
        "output": {
            "directory": ".",
            "format": "json",
            "pretty_print": True,
        },
        # SSL Configuration
        "ssl": {
            "ciphers": (
                "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:"
                "ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:"
                "RSA+3DES:!aNULL:!eNULL:!MD5"
            )
        },
        # Environment
        "environment": "development",
    }

    def __init__(self, config_path: Optional[str] = None, env_path: Optional[str] = None):
        """
        Inicializa la configuración.

        Args:
            config_path: Ruta al archivo YAML de configuración (opcional)
            env_path: Ruta al archivo .env (opcional)
        """
        self._config: dict[str, Any] = self.DEFAULT_CONFIG.copy()
        self._load_config(config_path, env_path)

        # Exponer configuración como atributos para compatibilidad
        self._expose_attributes()

    def _load_config(self, config_path: Optional[str], env_path: Optional[str]) -> None:
        """
        Carga configuración desde YAML y variables de entorno.

        Args:
            config_path: Ruta al archivo YAML
            env_path: Ruta al archivo .env
        """
        # Cargar variables de entorno
        self._load_env(env_path)

        # Cargar configuración YAML
        if config_path is None:
            config_path = "config.yaml"

        if Path(config_path).exists() and YAML_AVAILABLE:
            self._load_yaml(config_path)

        # Sobrescribir con variables de entorno (mayor prioridad)
        self._override_with_env()

    def _load_env(self, env_path: Optional[str]) -> None:
        """
        Carga variables de entorno desde archivo .env.

        Args:
            env_path: Ruta al archivo .env
        """
        if env_path is None:
            env_path = ".env"

        if Path(env_path).exists() and DOTENV_AVAILABLE:
            load_dotenv(env_path)

    def _load_yaml(self, config_path: str) -> None:
        """
        Carga configuración desde archivo YAML.

        Args:
            config_path: Ruta al archivo YAML

        Raises:
            ConfigError: Si el YAML es inválido
        """
        try:
            with open(config_path, encoding="utf-8") as f:
                yaml_config = yaml.safe_load(f)

            if yaml_config:
                self._deep_merge(self._config, yaml_config)
                # Reexponer atributos después de cargar YAML
                self._expose_attributes()

        except Exception as e:
            raise ConfigError(f"Error al cargar configuración desde {config_path}: {e}")

    def _override_with_env(self) -> None:
        """Sobrescribe configuración con variables de entorno."""
        # API Configuration
        if os.getenv("APD_API_URL"):
            self._config["api"]["base_url"] = os.getenv("APD_API_URL")
        if os.getenv("APD_POSTULANTES_API_URL"):
            self._config["api"]["postulantes_url"] = os.getenv("APD_POSTULANTES_API_URL")
        if os.getenv("APD_API_TIMEOUT"):
            self._config["api"]["timeout"] = int(os.getenv("APD_API_TIMEOUT"))

        # Forzar reexposición de atributos después de cambios
        self._expose_attributes()

        # Database Configuration
        if os.getenv("APD_DB_PATH"):
            self._config["database"]["path"] = os.getenv("APD_DB_PATH")

        # Logging Configuration
        if os.getenv("APD_LOG_NAME"):
            self._config["logging"]["name"] = os.getenv("APD_LOG_NAME")
        if os.getenv("APD_LOG_LEVEL"):
            self._config["logging"]["level"] = os.getenv("APD_LOG_LEVEL")
        if os.getenv("APD_LOG_FILE"):
            self._config["logging"]["file"] = os.getenv("APD_LOG_FILE")
        if os.getenv("APD_LOG_MAX_BYTES"):
            self._config["logging"]["max_bytes"] = int(os.getenv("APD_LOG_MAX_BYTES"))
        if os.getenv("APD_LOG_BACKUP_COUNT"):
            self._config["logging"]["backup_count"] = int(os.getenv("APD_LOG_BACKUP_COUNT"))
        if os.getenv("APD_LOG_CONSOLE_OUTPUT"):
            self._config["logging"]["console_output"] = os.getenv(
                "APD_LOG_CONSOLE_OUTPUT"
            ).lower() in ("true", "1", "yes")

        # Output Configuration
        if os.getenv("APD_OUTPUT_DIR"):
            self._config["output"]["directory"] = os.getenv("APD_OUTPUT_DIR")

        # Environment
        if os.getenv("APD_ENVIRONMENT"):
            self._config["environment"] = os.getenv("APD_ENVIRONMENT")

    def _deep_merge(self, base: dict, override: dict) -> None:
        """
        Fusiona recursivamente dos diccionarios.

        Args:
            base: Diccionario base (se modifica)
            override: Diccionario con valores que sobrescriben
        """
        for key, value in override.items():
            if key in base and isinstance(base[key], dict) and isinstance(value, dict):
                self._deep_merge(base[key], value)
            else:
                base[key] = value

    def _expose_attributes(self) -> None:
        """Expone configuración como atributos para compatibilidad con código existente."""
        # API Configuration
        self.API_BASE_URL = self._config["api"]["base_url"]
        self.POSTULANTES_API_URL = self._config["api"]["postulantes_url"]
        self.API_TIMEOUT = self._config["api"]["timeout"]

        # Database Configuration
        self.DB_PATH = self._config["database"]["path"]

        # Logging Configuration

        self.LOG_NAME = self._config["logging"]["name"]
        self.LOG_LEVEL = getattr(logging, self._config["logging"]["level"].upper(), logging.INFO)
        self.LOG_FILE = self._config["logging"]["file"]
        self.LOG_MAX_BYTES = self._config["logging"]["max_bytes"]
        self.LOG_BACKUP_COUNT = self._config["logging"]["backup_count"]
        self.LOG_CONSOLE_OUTPUT = self._config["logging"]["console_output"]

        # Output Configuration
        self.OUTPUT_DIR = self._config["output"]["directory"]

        # SSL Configuration
        self.CIPHERS = self._config["ssl"]["ciphers"]

        # Environment
        self.ENVIRONMENT = self._config["environment"]

    def get(self, key: str, default: Any = None) -> Any:
        """
        Obtiene un valor de configuración usando notación de puntos.

        Args:
            key: Clave con notación de puntos (ej: 'api.base_url')
            default: Valor por defecto si no existe

        Returns:
            Valor de configuración

        Example:
            >>> config = Config()
            >>> config.get('api.timeout')
            60
        """
        keys = key.split(".")
        value = self._config

        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default

        return value

    def get_api_query_params(self, distrito: str, rows: int = 0) -> dict[str, Any]:
        """
        Genera los parámetros de consulta para la API.

        Args:
            distrito: Nombre del distrito a consultar
            rows: Número de filas a obtener (0 = todas)

        Returns:
            Diccionario con parámetros de consulta
        """
        params = {"q": "*:*", "fq": f"descdistrito:{distrito.upper()}", "wt": "json"}

        if rows > 0:
            params["rows"] = rows

        return params

    def get_output_filename(self, distrito: str) -> str:
        """
        Genera el nombre del archivo de salida.

        Args:
            distrito: Nombre del distrito

        Returns:
            Nombre del archivo JSON de salida
        """
        return f"output_{distrito.lower()}.json"

    def validate(self) -> bool:
        """
        Valida la configuración actual.

        Returns:
            True si la configuración es válida

        Raises:
            ConfigError: Si hay errores de configuración
        """
        errors = []

        # Validar API timeout
        if self.API_TIMEOUT <= 0:
            errors.append("API_TIMEOUT debe ser positivo")

        # Validar logging max_bytes
        if self.LOG_MAX_BYTES <= 0:
            errors.append("LOG_MAX_BYTES debe ser positivo")

        # Validar logging backup_count
        if self.LOG_BACKUP_COUNT < 0:
            errors.append("LOG_BACKUP_COUNT debe ser no negativo")

        # Validar logging level
        valid_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        if self.get("logging.level", "").upper() not in valid_levels:
            errors.append(f"LOG_LEVEL debe ser uno de: {', '.join(valid_levels)}")

        if errors:
            raise ConfigError(f"Errores de configuración: {', '.join(errors)}")

        return True

    def __repr__(self) -> str:
        """Representación de la configuración."""
        return f"Config(environment={self.ENVIRONMENT}, api_timeout={self.API_TIMEOUT})"
