"""
Módulo de rate limiting para controlar la frecuencia de peticiones API.

Este módulo proporciona clases para limitar la frecuencia de peticiones
a las APIs externas, evitando bloqueos por exceso de requests y
siendo un buen ciudadano de la API.
"""

import time
from typing import Callable
from threading import Lock
from functools import wraps

from apd_scrap.utils.logging import LoggerMixin


class RateLimiter(LoggerMixin):
    """
    Rate limiter basado en tiempo para controlar frecuencia de peticiones.

    Este limiter asegura que no se hagan más de X peticiones en Y segundos,
    implementando un algoritmo de token bucket simplificado.

    Attributes:
        max_requests: Número máximo de peticiones permitidas en el periodo
        period: Periodo de tiempo en segundos
        min_interval: Intervalo mínimo entre peticiones en segundos
        _last_request_time: Timestamp de la última petición
        _requests_in_period: Contador de peticiones en el periodo actual
        _period_start_time: Timestamp de inicio del periodo actual
        _lock: Lock para thread-safety

    Example:
        >>> limiter = RateLimiter(max_requests=10, period=1)
        >>> for i in range(15):
        ...     limiter.wait_if_needed()
        ...     make_request()
        # Hará 10 peticiones en el primer segundo, luego esperará
    """

    def __init__(self, max_requests: int = 10, period: float = 1.0, min_interval: float = 0.0):
        """
        Inicializa el rate limiter.

        Args:
            max_requests: Número máximo de peticiones permitidas en el periodo
            period: Periodo de tiempo en segundos
            min_interval: Intervalo mínimo entre peticiones en segundos

        Raises:
            ValueError: Si max_requests <= 0 o period <= 0
        """
        if max_requests <= 0:
            raise ValueError("max_requests debe ser positivo")
        if period <= 0:
            raise ValueError("period debe ser positivo")

        self.max_requests = max_requests
        self.period = period
        self.min_interval = min_interval

        self._last_request_time: float = 0.0
        self._requests_in_period: int = 0
        self._period_start_time: float = 0.0
        self._lock = Lock()

        self.logger.debug(
            f"RateLimiter inicializado: max_requests={max_requests}, "
            f"period={period}s, min_interval={min_interval}s"
        )

    def wait_if_needed(self) -> float:
        """
        Espera si es necesario para respetar el rate limit.

        Este método calcula si hay que esperar antes de hacer la siguiente
        petición, considerando tanto el límite máximo por periodo como el
        intervalo mínimo entre peticiones.

        Returns:
            float: Tiempo esperado en segundos (0 si no hubo espera)

        Example:
            >>> limiter = RateLimiter(max_requests=10, period=1)
            >>> waited = limiter.wait_if_needed()
            >>> print(f"Esperó {waited:.2f} segundos")
            Esperó 0.00 segundos
        """
        with self._lock:
            current_time = time.time()

            # Calcular tiempo de espera
            wait_time = self._calculate_wait_time(current_time)

            if wait_time > 0:
                self.logger.debug(f"Rate limit: esperando {wait_time:.2f} segundos")
                time.sleep(wait_time)
                # Actualizar tiempo después de esperar
                current_time = time.time()

            # Actualizar contadores
            self._update_counters(current_time)

            return wait_time

    def _calculate_wait_time(self, current_time: float) -> float:
        """
        Calcula el tiempo de espera necesario.

        Args:
            current_time: Timestamp actual

        Returns:
            float: Tiempo de espera en segundos
        """
        # Espera por intervalo mínimo entre peticiones
        time_since_last_request = current_time - self._last_request_time
        wait_time = max(0.0, self.min_interval - time_since_last_request)

        # Espera si excedemos el límite de peticiones por periodo
        if self._requests_in_period >= self.max_requests:
            time_in_period = current_time - self._period_start_time
            if time_in_period < self.period:
                # Esperar hasta que termine el periodo
                wait_time = max(wait_time, self.period - time_in_period)
            else:
                # Periodo completado, resetear contadores
                self._requests_in_period = 0
                self._period_start_time = current_time

        return wait_time

    def _update_counters(self, current_time: float) -> None:
        """
        Actualiza los contadores después de una petición.

        Args:
            current_time: Timestamp actual
        """
        # Resetear contadores si pasó el periodo
        if current_time - self._period_start_time >= self.period:
            self._requests_in_period = 0
            self._period_start_time = current_time

        self._requests_in_period += 1
        self._last_request_time = current_time

    def reset(self) -> None:
        """
        Resetea todos los contadores del rate limiter.

        Example:
            >>> limiter = RateLimiter(max_requests=10, period=1)
            >>> limiter.reset()
        """
        with self._lock:
            self._last_request_time = 0.0
            self._requests_in_period = 0
            self._period_start_time = 0.0
            self.logger.debug("RateLimiter reseteado")

    def get_stats(self) -> dict[str, int | float]:
        """
        Obtiene estadísticas del rate limiter.

        Returns:
            dict[str, int | float]: Diccionario con estadísticas:
                - requests_in_period: Peticiones en el periodo actual
                - remaining_requests: Peticiones restantes en el periodo
                - period_elapsed: Tiempo transcurrido del periodo actual
                - time_until_reset: Tiempo hasta reset de contadores

        Example:
            >>> limiter = RateLimiter(max_requests=10, period=1)
            >>> stats = limiter.get_stats()
            >>> print(f"Peticiones restantes: {stats['remaining_requests']}")
            Peticiones restantes: 10
        """
        with self._lock:
            current_time = time.time()
            period_elapsed = current_time - self._period_start_time

            return {
                "requests_in_period": self._requests_in_period,
                "remaining_requests": max(0, self.max_requests - self._requests_in_period),
                "period_elapsed": period_elapsed,
                "time_until_reset": max(0.0, self.period - period_elapsed),
            }

    def __repr__(self) -> str:
        """Representación del rate limiter."""
        return (
            f"RateLimiter(max_requests={self.max_requests}, "
            f"period={self.period}, min_interval={self.min_interval})"
        )


class RateLimiterConfig:
    """
    Configuración predefinida de rate limiters para diferentes APIs.

    Attributes:
        APD_MAIN: Configuración para API principal de APD
        APD_POSTULANTES: Configuración para API de postulantes
        DEFAULT: Configuración por defecto
    """

    # API principal: máx 5 peticiones/segundo
    APD_MAIN: dict = {"max_requests": 5, "period": 1.0, "min_interval": 0.15}

    # API de postulantes: más conservador, máx 3 peticiones/segundo
    APD_POSTULANTES: dict = {"max_requests": 3, "period": 1.0, "min_interval": 0.25}

    # Configuración por defecto: máx 10 peticiones/segundo
    DEFAULT: dict = {"max_requests": 10, "period": 1.0, "min_interval": 0.0}


def create_rate_limiter(config_name: str = "DEFAULT") -> RateLimiter:
    """
    Crea un rate limiter desde configuración predefinida.

    Args:
        config_name: Nombre de la configuración (APD_MAIN, APD_POSTULANTES, DEFAULT)

    Returns:
        RateLimiter: Rate limiter configurado

    Raises:
        ValueError: Si config_name no es válido

    Example:
        >>> limiter = create_rate_limiter("APD_MAIN")
        >>> limiter.wait_if_needed()
    """
    if not hasattr(RateLimiterConfig, config_name):
        raise ValueError(
            f"Configuración inválida: {config_name}. Usar: APD_MAIN, APD_POSTULANTES, DEFAULT"
        )

    config = getattr(RateLimiterConfig, config_name)
    return RateLimiter(**config)


def rate_limit(max_requests: int = 10, period: float = 1.0, min_interval: float = 0.0):
    """
    Decorador para aplicar rate limiting a una función.

    Este decorador crea un rate limiter compartido para todas las llamadas
    a la función decorada, asegurando que el rate limit se respete
    independientemente de cuántas veces se llame la función.

    Args:
        max_requests: Número máximo de peticiones permitidas en el periodo
        period: Periodo de tiempo en segundos
        min_interval: Intervalo mínimo entre peticiones en segundos

    Returns:
        Decorador que aplica rate limiting a la función

    Example:
        >>> @rate_limit(max_requests=5, period=1.0)
        ... def fetch_data(url):
        ...     return requests.get(url)
        >>>
        >>> for i in range(10):
        ...     fetch_data(url)
        # Hará 5 peticiones en el primer segundo, luego esperará
    """
    limiter = RateLimiter(max_requests=max_requests, period=period, min_interval=min_interval)

    def decorator(func: Callable) -> Callable:
        @wraps(func)
        def wrapper(*args, **kwargs):
            limiter.wait_if_needed()
            return func(*args, **kwargs)

        return wrapper

    return decorator
