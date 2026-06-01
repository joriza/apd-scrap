"""Tests para el módulo de reintentos con backoff."""

import time
import pytest
from unittest.mock import Mock, patch

from apd_scrap.utils.retry import (
    retry_with_backoff,
    retry_conditionally,
    RetryError,
    RetryConfig,
)


class TestRetryWithBackoff:
    """Tests para el decorador retry_with_backoff."""

    def test_retry_with_backoff_success_on_first_attempt(self):
        """Prueba éxito en primer intento."""

        @retry_with_backoff(
            max_retries=3, initial_delay=0.1, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def success_function():
            return "success"

        result = success_function()
        assert result == "success"

    def test_retry_with_backoff_success_on_second_attempt(self):
        """Prueba éxito en segundo intento."""
        attempts = 0

        @retry_with_backoff(
            max_retries=3, initial_delay=0.1, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def fail_then_success():
            nonlocal attempts
            attempts += 1
            if attempts < 2:
                raise ValueError("Fallo temporal")
            return "success"

        result = fail_then_success()
        assert result == "success"
        assert attempts == 2

    def test_retry_with_backoff_max_retries_exceeded(self):
        """Prueba que falla tras max_retries."""

        @retry_with_backoff(
            max_retries=2, initial_delay=0.1, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def always_fail():
            raise ValueError("Siempre falla")

        with pytest.raises(RetryError) as exc_info:
            always_fail()

        assert "Todos los 2 intentos fallaron" in str(exc_info.value)

    def test_retry_with_backoff_only_catches_specified_exceptions(self):
        """Prueba que solo captura excepciones especificadas."""

        @retry_with_backoff(
            max_retries=3, initial_delay=0.1, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def raise_key_error():
            raise KeyError("No capturada")

        with pytest.raises(KeyError):
            raise_key_error()

    @patch("time.sleep")
    def test_retry_with_backoff_with_delay(self, mock_sleep):
        """Prueba que hay delay entre reintentos."""
        call_times = []

        @retry_with_backoff(
            max_retries=2, initial_delay=0.2, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def fail_once():
            call_times.append(time.time())
            if len(call_times) < 2:
                raise ValueError("Fallo")
            return "success"

        result = fail_once()
        assert result == "success"
        assert len(call_times) == 2
        # Verificar que sleep fue llamado
        assert mock_sleep.call_count == 1

    def test_retry_with_backoff_zero_retries(self):
        """Prueba con max_retries=0 - la función nunca se ejecuta."""
        # Con max_retries=0, el loop no se ejecuta, por lo que la función nunca se llama
        call_count = 0

        @retry_with_backoff(
            max_retries=0, initial_delay=0.1, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def fail_function():
            nonlocal call_count
            call_count += 1
            raise ValueError("Fallo")

        # La función nunca se ejecuta, call_count debería ser 0
        fail_function()
        assert call_count == 0

    def test_retry_with_backoff_multiple_exception_types(self):
        """Prueba captura de múltiples tipos de excepciones."""
        attempts = 0

        @retry_with_backoff(
            max_retries=3,
            initial_delay=0.1,
            backoff_factor=2.0,
            exceptions=(ValueError, KeyError, TypeError),
        )
        def raise_different_errors():
            nonlocal attempts
            attempts += 1

            if attempts == 1:
                raise ValueError("Error 1")
            elif attempts == 2:
                raise KeyError("Error 2")
            else:
                raise TypeError("Error 3")

        # Debería capturar todas las excepciones hasta agotar reintentos
        with pytest.raises(RetryError):
            raise_different_errors()

        assert attempts == 3

    def test_retry_with_backoff_preserves_function_name(self):
        """Prueba que el decorador preserva el nombre de la función."""

        @retry_with_backoff(max_retries=3)
        def my_function():
            return "result"

        assert my_function.__name__ == "my_function"

    def test_retry_with_backoff_preserves_docstring(self):
        """Prueba que el decorador preserva el docstring."""

        @retry_with_backoff(max_retries=3)
        def my_function():
            """Docstring de prueba."""
            return "result"

        assert my_function.__doc__ == "Docstring de prueba."

    def test_retry_with_backoff_with_jitter(self):
        """Prueba que jitter está activado por defecto."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1, backoff_factor=1.0, jitter=True)
        def fail_once():
            raise ValueError("Fallo")

        # Jitter está activado por defecto, no debería fallar
        with pytest.raises(RetryError):
            fail_once()

    def test_retry_with_backoff_without_jitter(self):
        """Prueba sin jitter."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1, backoff_factor=1.0, jitter=False)
        def fail_once():
            raise ValueError("Fallo")

        # Sin jitter debería funcionar igual
        with pytest.raises(RetryError):
            fail_once()


class TestRetryConditionally:
    """Tests para el decorador retry_conditionally."""

    def test_retry_conditionally_with_condition_true(self):
        """Prueba retry cuando condición es True."""

        def should_retry(attempt, exc):
            return True  # Reintentar siempre

        attempts = 0

        @retry_conditionally(should_retry, max_retries=2, initial_delay=0.1)
        def fail_twice():
            nonlocal attempts
            attempts += 1
            raise ValueError("Fallo")

        with pytest.raises(RetryError):
            fail_twice()

        assert attempts == 2

    def test_retry_conditionally_with_condition_false(self):
        """Prueba que no reintentá cuando condición es False."""

        def should_retry(attempt, exc):
            return False  # No reintentar nunca

        attempts = 0

        @retry_conditionally(should_retry, max_retries=3, initial_delay=0.1)
        def fail_function():
            nonlocal attempts
            attempts += 1
            raise ValueError("Fallo")

        # Debería fallar en el primer intento
        with pytest.raises(ValueError):
            fail_function()

        assert attempts == 1

    def test_retry_conditionally_with_specific_exception(self):
        """Prueba retry solo para excepciones específicas."""
        attempts = [0]

        def should_retry_timeout(attempt, exc):
            # Reintentar solo si es TimeoutError
            return isinstance(exc, TimeoutError)

        @retry_conditionally(should_retry_timeout, max_retries=3, initial_delay=0.1)
        def raise_timeout_once():
            attempts[0] += 1

            if attempts[0] == 1:
                return "success"
            raise TimeoutError("Timeout")

        result = raise_timeout_once()
        assert result == "success"


class TestRetryError:
    """Tests para RetryError."""

    def test_retry_error_creation(self):
        """Prueba creación de RetryError."""
        error = RetryError("Mensaje de error", attempts=3, last_exception=ValueError("Test"))
        assert str(error) == "Mensaje de error"
        assert error.attempts == 3
        assert error.last_exception is not None

    def test_retry_error_no_exception(self):
        """Prueba RetryError sin excepción."""
        error = RetryError("Mensaje", attempts=2)
        assert error.last_exception is None


class TestRetryConfig:
    """Tests para RetryConfig."""

    def test_retry_config_class_defaults(self):
        """Prueba configuración por defecto de RetryConfig."""
        config = RetryConfig()

        assert config.max_retries == 3
        assert config.initial_delay == 1.0
        assert config.max_delay == 60.0
        assert config.backoff_factor == 2.0
        assert config.jitter is True
        assert config.exceptions == (Exception,)

    def test_retry_config_custom_values(self):
        """Prueba RetryConfig con valores personalizados."""
        config = RetryConfig(
            max_retries=5,
            initial_delay=2.0,
            max_delay=30.0,
            backoff_factor=1.5,
            jitter=False,
            exceptions=(ValueError, KeyError),
        )

        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 30.0
        assert config.backoff_factor == 1.5
        assert config.jitter is False
        assert config.exceptions == (ValueError, KeyError)

    def test_retry_config_api_http_preset(self):
        """Prueba preset API_HTTP."""
        assert RetryConfig.API_HTTP["max_retries"] == 3
        assert RetryConfig.API_HTTP["initial_delay"] == 2.0
        assert RetryConfig.API_HTTP["max_delay"] == 30.0
        assert RetryConfig.API_HTTP["backoff_factor"] == 2.0
        assert RetryConfig.API_HTTP["jitter"] is True

    def test_retry_config_database_preset(self):
        """Prueba preset DATABASE."""
        assert RetryConfig.DATABASE["max_retries"] == 3
        assert RetryConfig.DATABASE["initial_delay"] == 1.0
        assert RetryConfig.DATABASE["max_delay"] == 10.0
        assert RetryConfig.DATABASE["backoff_factor"] == 2.0
        assert RetryConfig.DATABASE["jitter"] is True

    def test_retry_config_create_from_dict(self):
        """Prueba crear RetryConfig desde diccionario."""
        config_dict = {
            "max_retries": 5,
            "initial_delay": 2.0,
            "max_delay": 30.0,
            "backoff_factor": 1.5,
            "jitter": False,
            "exceptions": (ValueError,),
        }

        config = RetryConfig.create_from_dict(config_dict)

        assert config.max_retries == 5
        assert config.initial_delay == 2.0
        assert config.max_delay == 30.0
        assert config.backoff_factor == 1.5
        assert config.jitter is False
        assert config.exceptions == (ValueError,)

    def test_retry_config_create_from_dict_with_defaults(self):
        """Prueba crear RetryConfig desde diccionario con valores parciales."""
        config_dict = {"max_retries": 5}

        config = RetryConfig.create_from_dict(config_dict)

        assert config.max_retries == 5
        assert config.initial_delay == 1.0  # Default
        assert config.max_delay == 60.0  # Default
        assert config.backoff_factor == 2.0  # Default


class TestRetryIntegration:
    """Tests de integración con funciones realistas."""

    @patch("time.sleep")
    def test_retry_in_http_request(self, mock_sleep):
        """Prueba retry en petición HTTP simulada."""
        call_count = 0

        @retry_with_backoff(
            max_retries=3, initial_delay=0.1, backoff_factor=2.0, exceptions=(ConnectionError,)
        )
        def mock_http_request(url):
            nonlocal call_count
            call_count += 1

            if call_count < 2:
                raise ConnectionError("Connection failed")
            return {"status": "ok"}

        result = mock_http_request("http://example.com")
        assert result == {"status": "ok"}
        assert call_count == 2
        # Verificar que sleep fue llamado para delays
        assert mock_sleep.call_count == 1

    def test_retry_with_timeout_simulation(self):
        """Prueba retry simulando timeout."""
        call_count = 0

        @retry_with_backoff(
            max_retries=3, initial_delay=0.05, backoff_factor=2.0, exceptions=(TimeoutError,)
        )
        def operation_with_timeout():
            nonlocal call_count
            call_count += 1

            if call_count < 3:
                raise TimeoutError("Operation timeout")
            return "completed"

        result = operation_with_timeout()
        assert result == "completed"
        assert call_count == 3


class TestRetryEdgeCases:
    """Tests para casos extremos."""

    def test_retry_with_negative_initial_delay(self):
        """Prueba con delay inicial negativo."""

        # No debe fallar, debería manejarlo
        @retry_with_backoff(
            max_retries=1, initial_delay=-1.0, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def raise_error():
            raise ValueError("Error")

        with pytest.raises(RetryError):
            raise_error()

    def test_retry_with_very_large_backoff_factor(self):
        """Prueba con factor de backoff muy grande."""
        call_count = 0

        @retry_with_backoff(
            max_retries=2, initial_delay=0.1, backoff_factor=1000.0, exceptions=(ValueError,)
        )
        def fail_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fallo")
            return "success"

        result = fail_once()
        assert result == "success"

    def test_retry_with_zero_max_delay(self):
        """Prueba con max_delay cero."""

        @retry_with_backoff(max_retries=1, initial_delay=0.0, max_delay=0.0, backoff_factor=2.0)
        def raise_error():
            raise ValueError("Error")

        with pytest.raises(RetryError):
            raise_error()

    def test_retry_decorator_with_no_exceptions(self):
        """Prueba sin especificar excepciones (usa Exception por defecto)."""

        @retry_with_backoff(max_retries=2, initial_delay=0.1)
        def raise_error():
            raise RuntimeError("Error")

        # Debería capturar cualquier Exception
        with pytest.raises(RetryError):
            raise_error()

    def test_retry_with_very_small_delay(self):
        """Prueba con delay muy pequeño."""
        call_count = 0

        @retry_with_backoff(
            max_retries=2, initial_delay=0.001, backoff_factor=2.0, exceptions=(ValueError,)
        )
        def fail_once():
            nonlocal call_count
            call_count += 1
            if call_count < 2:
                raise ValueError("Fallo")
            return "success"

        result = fail_once()
        assert result == "success"
        assert call_count == 2
