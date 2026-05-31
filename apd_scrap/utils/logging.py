"""
Sistema de logging estructurado para APD-Scrap.

Este módulo proporciona una configuración centralizada de logging
con niveles, rotación de archivos y formato consistente.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path
from typing import Literal, Optional


LogFormat = Literal['%(asctime)s - %(name)s - %(levelname)s - %(message)s']
LogLevel = Literal['DEBUG', 'INFO', 'WARNING', 'ERROR', 'CRITICAL']


def setup_logging(
    name: str = "apd_scrap",
    log_level: int = logging.INFO,
    log_file: Optional[str] = "apd_scrap.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    console_output: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging para APD-Scrap.
    
    Esta función crea un logger con handlers para consola y archivo,
    configurados con rotación automática cuando el archivo alcanza
    el tamaño máximo especificado.
    
    Args:
        name: Nombre del logger (default: "apd_scrap")
        log_level: Nivel mínimo de logging (default: logging.INFO)
            Valores válidos: logging.DEBUG, logging.INFO, logging.WARNING,
            logging.ERROR, logging.CRITICAL
        log_file: Ruta al archivo de log. Si None, solo se usa consola
            (default: "apd_scrap.log")
        max_bytes: Tamaño máximo del archivo de log en bytes antes de rotar
            (default: 5 * 1024 * 1024 = 5MB)
        backup_count: Número máximo de archivos de respaldo a mantener.
            Los archivos se nombran como log_file.1, log_file.2, etc.
            (default: 3)
        console_output: Si True, muestra logs también en stdout.
            Si False, solo guarda en archivo (default: True)
        
    Returns:
        logging.Logger: Logger configurado con handlers apropiados
        
    Raises:
        OSError: Si no se puede crear el directorio del archivo de log
        
    Example:
        >>> # Configuración básica
        >>> logger = setup_logging()
        >>> logger.info("Aplicación iniciada")
        
        >>> # Configuración con nivel DEBUG y solo consola
        >>> logger = setup_logging(
        ...     log_level=logging.DEBUG,
        ...     log_file=None,
        ...     console_output=True
        ... )
        >>> logger.debug("Información detallada de debug")
        
        >>> # Configuración para producción (sin consola)
        >>> logger = setup_logging(
        ...     log_level=logging.WARNING,
        ...     log_file="/var/log/apd_scrap.log",
        ...     console_output=False
        ... )
        >>> logger.warning("Advertencia en producción")
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Evitar agregar handlers duplicados
    if logger.handlers:
        logger.handlers.clear()
    
    # Formateador con timestamp
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Handler de consola
    if console_output:
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(log_level)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)
    
    # Handler de archivo con rotación
    if log_file:
        log_path = Path(log_file)
        log_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_handler = RotatingFileHandler(
            log_file,
            maxBytes=max_bytes,
            backupCount=backup_count,
            encoding='utf-8'
        )
        file_handler.setLevel(log_level)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    return logger


def get_logger(name: str = "apd_scrap") -> logging.Logger:
    """
    Obtiene un logger existente o crea uno nuevo.
    
    Esta función es un wrapper simple alrededor de logging.getLogger
    que proporciona un logger ya configurado si setup_logging fue
    llamado anteriormente.
    
    Args:
        name: Nombre del logger. Usar nombres con notación de puntos
            para jerarquía (ej: "apd_scrap.database")
            (default: "apd_scrap")
        
    Returns:
        logging.Logger: Logger con el nombre especificado
        
    Example:
        >>> # Obtener logger raíz
        >>> logger = get_logger()
        >>> logger.info("Mensaje informativo")
        
        >>> # Obtener logger específico de módulo
        >>> db_logger = get_logger("apd_scrap.database")
        >>> db_logger.debug("Información de base de datos")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin para añadir logging automático a cualquier clase.
    
    Esta clase proporciona una propiedad `logger` que crea automáticamente
    un logger con el nombre del módulo y la clase. Esto elimina la
    necesidad de configurar loggers manualmente en cada clase.
    
    Attributes:
        logger: logging.Logger - Logger configurado para la clase
        
    Example:
        >>> class MiClase(LoggerMixin):
        ...     def __init__(self):
        ...         self.valor = 42
        ...     
        ...     def metodo(self):
        ...         self.logger.info(f"Método ejecutado con valor={self.valor}")
        ...     
        ...     def otro_metodo(self):
        ...         self.logger.debug("Información detallada")
        ...         self.logger.warning("Advertencia")
        ...         self.logger.error("Error ocurrido")
        
        >>> obj = MiClase()
        >>> obj.metodo()
        # Salida: apd_scrap.module_name.MiClase - INFO - Método ejecutado con valor=42
    """
    
    @property
    def logger(self) -> logging.Logger:
        """
        Obtiene un logger configurado para esta clase.
        
        El logger se crea automáticamente con el nombre completo
        incluyendo el módulo y el nombre de la clase.
        
        Returns:
            logging.Logger: Logger configurado para la instancia
            
        Example:
            >>> class MiClase(LoggerMixin):
            ...     pass
            >>> obj = MiClase()
            >>> logger_name = obj.logger.name
            >>> # logger_name será algo como "apd_scrap.module_name.MiClase"
        """
        name: str = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)