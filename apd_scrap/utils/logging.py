"""
Sistema de logging estructurado para APD-Scrap.

Este módulo proporciona una configuración centralizada de logging
con niveles, rotación de archivos y formato consistente.
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path


def setup_logging(
    name: str = "apd_scrap",
    log_level: int = logging.INFO,
    log_file: str = "apd_scrap.log",
    max_bytes: int = 5 * 1024 * 1024,
    backup_count: int = 3,
    console_output: bool = True
) -> logging.Logger:
    """
    Configura el sistema de logging.
    
    Args:
        name: Nombre del logger
        log_level: Nivel de logging (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Ruta al archivo de log
        max_bytes: Tamaño máximo del archivo de log en bytes (default: 5MB)
        backup_count: Número de archivos de respaldo a mantener
        console_output: Si True, también muestra logs en consola
        
    Returns:
        Logger configurado
        
    Example:
        >>> logger = setup_logging(log_level=logging.DEBUG)
        >>> logger.info("Aplicación iniciada")
        >>> logger.error("Error en la operación")
    """
    # Crear logger
    logger = logging.getLogger(name)
    logger.setLevel(log_level)
    
    # Evitar agregar handlers duplicados
    if logger.handlers:
        logger.handlers.clear()
    
    # Formateador
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
    Obtiene un logger configurado.
    
    Args:
        name: Nombre del logger (por defecto usa el logger raíz)
        
    Returns:
        Logger existente o nuevo si no existe
        
    Example:
        >>> logger = get_logger()
        >>> logger.info("Mensaje informativo")
    """
    return logging.getLogger(name)


class LoggerMixin:
    """
    Mixin para añadir logging a cualquier clase.
    
    Example:
        >>> class MiClase(LoggerMixin):
        ...     def metodo(self):
        ...         self.logger.info("Método ejecutado")
    """
    
    @property
    def logger(self) -> logging.Logger:
        """Obtiene el logger para la instancia."""
        name = f"{self.__class__.__module__}.{self.__class__.__name__}"
        return logging.getLogger(name)