"""
Mecanismo de reintentos con backoff exponencial.

Este módulo proporciona un decorador para reintentar operaciones
automáticamente con reintentos con backoff exponencial entre intentos.
"""

import random
import time
import logging
from typing import Optional
from functools import wraps

# Obtener logger
logger = logging.getLogger(__name__)


class RetryError(Exception):
    """Excepción para fallos después de todos los reintentos."""

    def __init__(self, message: str, attempts: int, last_exception: Optional[Exception] = None):
        """
        Inicializa RetryError.

        Args:
            message: Mensaje de error
            attempts: Número de intentos realizados
            last_exception: Última excepción ocurrida
        """
        self.message = message
        self.attempts = attempts
        self.last_exception = last_exception
        super().__init__(self.message)


def retry_with_backoff(
    max_retries: int = 3,
    initial_delay: float = 1.0,
    max_delay: float = 60.0,
    backoff_factor: float = 2.0,
    jitter: bool = True,
    exceptions: tuple = (Exception,),
):
    """
    Decorador para reintentos con backoff exponencial.

    Este decorador permite reintentar automáticamente una función
    si falla con ciertas excepciones, utilizando un backoff
    exponencial entre intentos para evitar sobrecargar el servidor.

    Args:
        max_retries: Número máximo de reintentos (default: 3)
        initial_delay: Delay inicial en segundos (default: 1.0)
        max_delay: Delay máximo en segundos (default: 60.0)
        backoff_factor: Factor de multiplicación del delay (default: 2.0)
        jitter: Si True, añade aleatoriedad al delay (default: True)
        exceptions: Tupla de excepciones a capturar (default: Exception)

    Returns:
        Decorador que reintenta la función decorada

    Raises:
        RetryError: Si todos los intentos fallan

    Example:
        >>> @retry_with_backoff(max_retries=3, exceptions=(requests.Timeout,))
        ... def fetch_api_data(url):
        ...     return requests.get(url, timeout=10)
        >>>
        >>> data = fetch_api_data('https://api.example.com')
        # Reintentará automáticamente si hay timeout

    Note:
        - El delay se calcula como: min(initial_delay * (backoff_factor ** attempt), max_delay)
        - Jitter añade variación aleatoria para evitar sincronización
        - Se loggea cada intento para debug
    """

    def decorator(func):
        """
        Decorador interno que envuelve la función.

        Args:
            func: Función a decorar

        Returns:
            Función envuelta con lógica de reintentos
        """

        @wraps(func)
        def wrapper(*args, **kwargs):
            """
            Wrapper que implementa la lógica de reintentos.

            Args:
                *args: Argumentos posicionales de la función
                **kwargs: Argumentos nombrados de la función

            Returns:
                Resultado de la función si tiene éxito

            Raises:
                RetryError: Si todos los intentos fallan
            """
            last_exception: Optional[Exception] = None
            delay = initial_delay

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)

                except exceptions as e:
                    last_exception = e

                    # Si es el último intento, lanzar RetryError
                    if attempt == max_retries - 1:
                        raise RetryError(
                            f"Todos los {max_retries} intentos fallaron para {func.__name__}",
                            max_retries,
                            last_exception,
                        ) from e

                    # Loggear intento fallido
                    logger.warning(
                        f"Intento {attempt + 1}/{max_retries} falló para {func.__name__}: {e}. "
                        f"Reintentando en {delay:.1f}s..."
                    )

                    # Esperar antes de reintentar
                    time.sleep(delay)

                    # Calcular siguiente delay
                    delay = min(delay * backoff_factor, max_delay)

                    # Añadir jitter aleatorio
                    if jitter:
                        delay = delay * (0.8 + 0.4 * random.random())  # 80%-120%

        return wrapper

    return decorator


def retry_conditionally(condition, max_retries: int = 3, initial_delay: float = 1.0):
    """
    Decorador para reintentos condicionales.

    A diferencia de retry_with_backoff, este decorador permite especificar
    una condición personalizada para determinar si se debe reintentar.

    Args:
        condition: Función que recibe (intentos, excepción) y retorna True si reintentar
        max_retries: Número máximo de reintentos
        initial_delay: Delay inicial en segundos

    Returns:
        Decorador configurado

    Example:
        >>> def should_retry(attempt, exc):
        ...     # Reintentar solo si es timeout, no otros errores
        ...     return isinstance(exc, requests.Timeout)
        >>>
        >>> @retry_conditionally(should_retry)
        >>> def fetch_data():
        ...     return requests.get(url)
    """

    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            last_exception: Optional[Exception] = None

            for attempt in range(max_retries):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    last_exception = e

                    if not condition(attempt, e):
                        raise

                    if attempt < max_retries - 1:
                        delay = initial_delay * (2**attempt)
                        logger.warning(f"Reintentando en {delay:.1f}s...")
                        time.sleep(delay)

            raise RetryError(
                f"Máximo de {max_retries} intentos alcanzado", max_retries, last_exception
            )

        return wrapper

    return decorator


class RetryConfig:
    """
    Configuración centralizada para reintentos.

    Attributes:
        max_retries: Número máximo de reintentos
        initial_delay: Delay inicial en segundos
        max_delay: Delay máximo en segundos
        backoff_factor: Factor de backoff
        jitter: Si usar jitter
        exceptions: Excepciones a capturar
    """

    # Configuración para API HTTP
    API_HTTP: dict = {
        "max_retries": 3,
        "initial_delay": 2.0,
        "max_delay": 30.0,
        "backoff_factor": 2.0,
        "jitter": True,
    }

    # Configuración para base de datos
    DATABASE: dict = {
        "max_retries": 3,
        "initial_delay": 1.0,
        "max_delay": 10.0,
        "backoff_factor": 2.0,
        "jitter": True,
    }

    @classmethod
    def create_from_dict(cls, config):
        """
        Crea configuración desde un diccionario.

        Args:
            config: Diccionario con configuración

        Returns:
            RetryConfig: Configuración creada
        """
        return cls(
            max_retries=config.get("max_retries", 3),
            initial_delay=config.get("initial_delay", 1.0),
            max_delay=config.get("max_delay", 60.0),
            backoff_factor=config.get("backoff_factor", 2.0),
            jitter=config.get("jitter", True),
            exceptions=config.get("exceptions", (Exception,)),
        )

    def __init__(
        self,
        max_retries: int = 3,
        initial_delay: float = 1.0,
        max_delay: float = 60.0,
        backoff_factor: float = 2.0,
        jitter: bool = True,
        exceptions: tuple = (Exception,),
    ):
        """Inicializa RetryConfig."""
        self.max_retries = max_retries
        self.initial_delay = initial_delay
        self.max_delay = max_delay
        self.backoff_factor = backoff_factor
        self.jitter = jitter
        self.exceptions = exceptions
