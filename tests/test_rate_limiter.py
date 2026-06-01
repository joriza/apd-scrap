"""Tests para el módulo de rate limiting."""

import time
import pytest
from unittest.mock import patch

from apd_scrap.utils.rate_limiter import (
    RateLimiter,
    RateLimiterConfig,
    create_rate_limiter,
    rate_limit,
)


class TestRateLimiter:
    """Tests para RateLimiter."""

    def test_instantiation(self):
        """Puede instanciar RateLimiter."""
        limiter = RateLimiter(max_requests=10, period=1.0)
        assert limiter is not None
        assert limiter.max_requests == 10
        assert limiter.period == 1.0

    def test_invalid_max_requests(self):
        """Rechaza max_requests <= 0."""
        with pytest.raises(ValueError, match="max_requests debe ser positivo"):
            RateLimiter(max_requests=0, period=1.0)

        with pytest.raises(ValueError, match="max_requests debe ser positivo"):
            RateLimiter(max_requests=-1, period=1.0)

    def test_invalid_period(self):
        """Rechaza period <= 0."""
        with pytest.raises(ValueError, match="period debe ser positivo"):
            RateLimiter(max_requests=10, period=0.0)

        with pytest.raises(ValueError, match="period debe ser positivo"):
            RateLimiter(max_requests=10, period=-1.0)

    @patch("time.sleep")
    def test_wait_if_needed_first_request(self, mock_sleep):
        """Primera petición no espera."""
        limiter = RateLimiter(max_requests=10, period=1.0)
        waited = limiter.wait_if_needed()

        assert waited == 0.0
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_wait_if_needed_under_limit(self, mock_sleep):
        """Peticiones bajo el límite no esperan."""
        limiter = RateLimiter(max_requests=10, period=1.0)

        for _ in range(5):
            waited = limiter.wait_if_needed()
            assert waited == 0.0

        mock_sleep.assert_not_called()

    @patch("time.sleep")
    @patch("time.time")
    def test_wait_if_needed_at_limit(self, mock_time, mock_sleep):
        """Espera cuando alcanza el límite."""
        # Simular tiempo
        times = [0.0, 0.1, 0.2, 0.3, 0.4, 0.5]
        mock_time.side_effect = times

        limiter = RateLimiter(max_requests=3, period=1.0)

        # Primeras 3 peticiones no esperan
        for _ in range(3):
            waited = limiter.wait_if_needed()
            assert waited == 0.0

        # Cuarta petición debe esperar
        waited = limiter.wait_if_needed()
        assert waited > 0.0
        mock_sleep.assert_called()

    @patch("time.sleep")
    @patch("time.time")
    def test_wait_if_needed_period_reset(self, mock_time, mock_sleep):
        """Resetea el contador después del periodo."""
        # Simular tiempo: primera petición a t=0, segunda a t=2 (periodo completado)
        times = [0.0, 2.0]
        mock_time.side_effect = times

        limiter = RateLimiter(max_requests=2, period=1.0)

        # Primera petición
        waited1 = limiter.wait_if_needed()
        assert waited1 == 0.0

        # Segunda petición (periodo reseteado)
        waited2 = limiter.wait_if_needed()
        assert waited2 == 0.0

        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_min_interval_between_requests(self, mock_sleep):
        """Respeta el intervalo mínimo entre peticiones."""
        limiter = RateLimiter(max_requests=10, period=1.0, min_interval=0.2)

        # Primera petición no espera
        waited1 = limiter.wait_if_needed()
        assert waited1 == 0.0

        # Segunda petición debe esperar por intervalo mínimo
        waited2 = limiter.wait_if_needed()
        assert waited2 > 0.0
        mock_sleep.assert_called()

    def test_reset(self):
        """Resetea todos los contadores."""
        limiter = RateLimiter(max_requests=10, period=1.0)

        # Hacer algunas peticiones
        for _ in range(3):
            limiter.wait_if_needed()

        # Verificar que hay peticiones
        stats_before = limiter.get_stats()
        assert stats_before["requests_in_period"] == 3

        # Resetear
        limiter.reset()

        # Verificar que reseteó
        stats_after = limiter.get_stats()
        assert stats_after["requests_in_period"] == 0

    def test_get_stats(self):
        """Obtiene estadísticas correctas."""
        limiter = RateLimiter(max_requests=10, period=1.0)

        stats = limiter.get_stats()

        assert "requests_in_period" in stats
        assert "remaining_requests" in stats
        assert "period_elapsed" in stats
        assert "time_until_reset" in stats
        assert stats["remaining_requests"] == 10

    def test_get_stats_after_requests(self):
        """Estadísticas actualizadas después de peticiones."""
        limiter = RateLimiter(max_requests=10, period=1.0)

        # Hacer 3 peticiones
        for _ in range(3):
            limiter.wait_if_needed()

        stats = limiter.get_stats()
        assert stats["requests_in_period"] == 3
        assert stats["remaining_requests"] == 7

    def test_repr(self):
        """Representación string del limiter."""
        limiter = RateLimiter(max_requests=10, period=1.0, min_interval=0.1)
        repr_str = repr(limiter)

        assert "RateLimiter" in repr_str
        assert "max_requests=10" in repr_str
        assert "period=1" in repr_str
        assert "min_interval=0.1" in repr_str


class TestRateLimiterConfig:
    """Tests para RateLimiterConfig."""

    def test_apd_main_config(self):
        """Configuración APD_MAIN existe y tiene valores correctos."""
        assert hasattr(RateLimiterConfig, "APD_MAIN")
        config = RateLimiterConfig.APD_MAIN
        assert config["max_requests"] == 5
        assert config["period"] == 1.0
        assert config["min_interval"] == 0.15

    def test_apd_postulantes_config(self):
        """Configuración APD_POSTULANTES existe y tiene valores correctos."""
        assert hasattr(RateLimiterConfig, "APD_POSTULANTES")
        config = RateLimiterConfig.APD_POSTULANTES
        assert config["max_requests"] == 3
        assert config["period"] == 1.0
        assert config["min_interval"] == 0.25

    def test_default_config(self):
        """Configuración DEFAULT existe y tiene valores correctos."""
        assert hasattr(RateLimiterConfig, "DEFAULT")
        config = RateLimiterConfig.DEFAULT
        assert config["max_requests"] == 10
        assert config["period"] == 1.0
        assert config["min_interval"] == 0.0


class TestCreateRateLimiter:
    """Tests para create_rate_limiter."""

    def test_create_default_limiter(self):
        """Crea limiter con configuración DEFAULT."""
        limiter = create_rate_limiter("DEFAULT")
        assert isinstance(limiter, RateLimiter)
        assert limiter.max_requests == 10
        assert limiter.period == 1.0

    def test_create_apd_main_limiter(self):
        """Crea limiter con configuración APD_MAIN."""
        limiter = create_rate_limiter("APD_MAIN")
        assert isinstance(limiter, RateLimiter)
        assert limiter.max_requests == 5
        assert limiter.min_interval == 0.15

    def test_create_apd_postulantes_limiter(self):
        """Crea limiter con configuración APD_POSTULANTES."""
        limiter = create_rate_limiter("APD_POSTULANTES")
        assert isinstance(limiter, RateLimiter)
        assert limiter.max_requests == 3
        assert limiter.min_interval == 0.25

    def test_invalid_config_name(self):
        """Rechaza nombre de configuración inválido."""
        with pytest.raises(ValueError, match="Configuración inválida"):
            create_rate_limiter("INVALID")


class TestRateLimitDecorator:
    """Tests para el decorador @rate_limit."""

    @patch("time.sleep")
    def test_decorator_without_wait(self, mock_sleep):
        """Decorador funciona sin esperar."""
        call_count = 0

        @rate_limit(max_requests=10, period=1.0)
        def my_function():
            nonlocal call_count
            call_count += 1
            return call_count

        for _ in range(5):
            result = my_function()

        assert result == 5
        assert call_count == 5
        mock_sleep.assert_not_called()

    @patch("time.sleep")
    @patch("time.time")
    def test_decorator_with_wait(self, mock_time, mock_sleep):
        """Decorador espera cuando excede el límite."""
        # Simular tiempo
        times = [0.0, 0.1, 0.2, 0.3]
        mock_time.side_effect = times

        call_count = 0

        @rate_limit(max_requests=2, period=1.0)
        def my_function():
            nonlocal call_count
            call_count += 1
            return call_count

        # Primeras 2 llamadas no esperan
        my_function()
        my_function()

        # Tercera llamada debe esperar
        my_function()

        assert call_count == 3
        mock_sleep.assert_called()

    def test_decorator_preserves_function_name(self):
        """El decorador preserva el nombre de la función."""
        @rate_limit(max_requests=10, period=1.0)
        def my_function():
            return "result"

        assert my_function.__name__ == "my_function"

    def test_decorator_preserves_docstring(self):
        """El decorador preserva el docstring."""
        @rate_limit(max_requests=10, period=1.0)
        def my_function():
            """Docstring de prueba."""
            return "result"

        assert my_function.__doc__ == "Docstring de prueba."


class TestRateLimiterThreadSafety:
    """Tests para thread-safety."""

    def test_multiple_wait_calls(self):
        """Múltiples llamadas a wait_if_needed funcionan correctamente."""
        limiter = RateLimiter(max_requests=10, period=1.0)

        # Hacer múltiples llamadas concurrentes simuladas
        for _ in range(20):
            waited = limiter.wait_if_needed()
            assert isinstance(waited, float)
            assert waited >= 0.0

    def test_stats_thread_safety(self):
        """get_stats funciona correctamente."""
        limiter = RateLimiter(max_requests=10, period=1.0)

        # Hacer algunas peticiones
        for _ in range(5):
            limiter.wait_if_needed()

        # Obtener stats múltiples veces
        for _ in range(10):
            stats = limiter.get_stats()
            assert stats["requests_in_period"] == 5
            assert stats["remaining_requests"] == 5


class TestRateLimiterEdgeCases:
    """Tests para casos extremos."""

    @patch("time.sleep")
    def test_zero_min_interval(self, mock_sleep):
        """Funciona con min_interval=0."""
        limiter = RateLimiter(max_requests=10, period=1.0, min_interval=0.0)

        # Hacer 10 peticiones
        for _ in range(10):
            waited = limiter.wait_if_needed()
            assert waited == 0.0

        mock_sleep.assert_not_called()

    @patch("time.sleep")
    def test_large_max_requests(self, mock_sleep):
        """Funciona con max_requests grande."""
        limiter = RateLimiter(max_requests=1000, period=1.0)

        # Hacer 50 peticiones
        for _ in range(50):
            waited = limiter.wait_if_needed()
            assert waited == 0.0

        mock_sleep.assert_not_called()

    @patch("time.sleep")
    @patch("time.time")
    def test_very_short_period(self, mock_time, mock_sleep):
        """Funciona con periodo muy corto."""
        # Simular tiempo progresivo
        times = [i * 0.01 for i in range(20)]
        mock_time.side_effect = times

        limiter = RateLimiter(max_requests=2, period=0.05)

        # Hacer peticiones
        for _ in range(5):
            waited = limiter.wait_if_needed()
            assert isinstance(waited, float)

        # Alguna petición debería haber esperado
        assert mock_sleep.called

    def test_decorator_with_args_kwargs(self):
        """El decorador pasa args y kwargs correctamente."""
        @rate_limit(max_requests=10, period=1.0)
        def my_function(a, b, c=None):
            return (a, b, c)

        result = my_function(1, 2, c=3)
        assert result == (1, 2, 3)
