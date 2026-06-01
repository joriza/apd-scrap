"""
Tests unitarios para el módulo apd_scrap.utils.ssl_adapter
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from apd_scrap.utils.ssl_adapter import CustomHttpAdapter, LegacyHttpAdapter, CIPHERS


class TestCiphersConstant:
    """Tests para la constante CIPHERS."""

    def test_cipher_string_exists(self):
        """Verifica que la cadena de ciphers exista."""
        assert isinstance(CIPHERS, str)
        assert len(CIPHERS) > 0

    def test_cipher_contains_required_components(self):
        """Verifica que la cadena de ciphers contenga componentes esenciales."""
        assert "AESGCM" in CIPHERS
        assert "!aNULL" in CIPHERS
        assert "!eNULL" in CIPHERS
        assert "!MD5" in CIPHERS

    def test_cipher_contains_aes_variants(self):
        """Verifica que la cadena de ciphers contenga variantes AES."""
        assert "ECDH+AESGCM" in CIPHERS
        assert "DH+AESGCM" in CIPHERS
        assert "RSA+AESGCM" in CIPHERS

    def test_cipher_contains_3des(self):
        """Verifica que la cadena de ciphers contenga 3DES."""
        assert "3DES" in CIPHERS

    def test_cipher_format(self):
        """Verifica el formato de la cadena de ciphers."""
        assert ":" in CIPHERS  # Debe ser una lista separada por :
        assert not CIPHERS.endswith(":")  # No debe terminar en :


class TestCustomHttpAdapter:
    """Tests para CustomHttpAdapter."""

    def test_instantiation(self):
        """Puede instanciar CustomHttpAdapter."""
        adapter = CustomHttpAdapter()
        assert adapter is not None
        assert isinstance(adapter, CustomHttpAdapter)

    @patch("apd_scrap.utils.ssl_adapter.create_urllib3_context")
    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    def test_init_poolmanager_creates_ssl_context(
        self, mock_super_init_poolmanager, mock_create_context
    ):
        """Verifica que init_poolmanager cree un contexto SSL con ciphers específicos."""
        # Setup
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        adapter = CustomHttpAdapter()
        mock_create_context.reset_mock()  # Resetear después de inicialización
        adapter.init_poolmanager(connections=10, maxsize=100)

        # Verify
        assert mock_create_context.called
        # Verificar que el último llamado fue con CIPHERS
        last_call = mock_create_context.call_args_list[-1]
        assert last_call[1]["ciphers"] == CIPHERS
        mock_super_init_poolmanager.assert_called()
        call_kwargs = mock_super_init_poolmanager.call_args.kwargs
        assert "ssl_context" in call_kwargs
        assert call_kwargs["ssl_context"] == mock_context

    @patch("apd_scrap.utils.ssl_adapter.create_urllib3_context")
    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    def test_init_poolmanager_passes_all_args(
        self, mock_super_init_poolmanager, mock_create_context
    ):
        """Verifica que init_poolmanager pase todos los argumentos correctamente."""
        # Setup
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        adapter = CustomHttpAdapter()
        adapter.init_poolmanager(connections=5, maxsize=50, block=True, extra_param="test")

        # Verify
        call_args = mock_super_init_poolmanager.call_args.args
        assert call_args[0] == 5  # connections
        assert call_args[1] == 50  # maxsize
        assert call_args[2] is True  # block
        assert mock_super_init_poolmanager.call_args.kwargs["extra_param"] == "test"

    @patch("apd_scrap.utils.ssl_adapter.create_urllib3_context")
    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    def test_init_poolmanager_returns_poolmanager(
        self, mock_super_init_poolmanager, mock_create_context
    ):
        """Verifica que init_poolmanager retorne el PoolManager."""
        # Setup
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_poolmanager = Mock()
        mock_super_init_poolmanager.return_value = mock_poolmanager

        # Execute
        adapter = CustomHttpAdapter()
        result = adapter.init_poolmanager(connections=10, maxsize=100)

        # Verify
        assert result == mock_poolmanager


class TestLegacyHttpAdapter:
    """Tests para LegacyHttpAdapter."""

    def test_instantiation(self):
        """Puede instanciar LegacyHttpAdapter."""
        adapter = LegacyHttpAdapter()
        assert adapter is not None
        assert isinstance(adapter, LegacyHttpAdapter)

    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    @patch("apd_scrap.utils.ssl_adapter.ssl.SSLContext")
    @patch("apd_scrap.utils.ssl_adapter.ssl.TLSVersion")
    def test_init_poolmanager_creates_ssl_context(
        self, mock_tls_version, mock_ssl_context, mock_super_init_poolmanager
    ):
        """Verifica que init_poolmanager cree un contexto SSL legacy."""
        # Setup
        mock_context_instance = Mock()
        mock_context_instance.minimum_version = Mock()
        mock_context_instance.set_ciphers = Mock()
        mock_context_instance.check_hostname = False
        mock_context_instance.verify_mode = Mock()
        mock_ssl_context.return_value = mock_context_instance
        mock_tls_version.TLSv1_2 = Mock()

        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        adapter = LegacyHttpAdapter()
        mock_ssl_context.reset_mock()  # Resetear después de inicialización
        adapter.init_poolmanager(connections=10, maxsize=100)

        # Verify
        assert mock_ssl_context.called
        mock_context_instance.set_ciphers.assert_called()

        # Verificar que se pasó el contexto SSL al super
        call_kwargs = mock_super_init_poolmanager.call_args.kwargs
        assert "ssl_context" in call_kwargs
        assert call_kwargs["ssl_context"] == mock_context_instance

    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    @patch("apd_scrap.utils.ssl_adapter.ssl.SSLContext")
    @patch("apd_scrap.utils.ssl_adapter.ssl.TLSVersion")
    @patch("apd_scrap.utils.ssl_adapter.ssl.PROTOCOL_TLS_CLIENT")
    @patch("apd_scrap.utils.ssl_adapter.ssl.CERT_NONE")
    def test_init_poolmanager_configures_legacy_ssl(
        self,
        mock_cert_none,
        mock_protocol_tls_client,
        mock_tls_version,
        mock_ssl_context,
        mock_super_init_poolmanager,
    ):
        """Verifica que init_poolmanager configure SSL legacy correctamente."""
        # Setup
        mock_context_instance = Mock()
        mock_ssl_context.return_value = mock_context_instance
        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        adapter = LegacyHttpAdapter()
        adapter.init_poolmanager(connections=10, maxsize=100)

        # Verify configuraciones legacy
        assert mock_context_instance.check_hostname is False
        mock_context_instance.verify_mode = mock_cert_none

    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    @patch("apd_scrap.utils.ssl_adapter.ssl.SSLContext")
    @patch("apd_scrap.utils.ssl_adapter.ssl.TLSVersion")
    def test_init_poolmanager_passes_all_args(
        self, mock_tls_version, mock_ssl_context, mock_super_init_poolmanager
    ):
        """Verifica que init_poolmanager pase todos los argumentos correctamente."""
        # Setup
        mock_context_instance = Mock()
        mock_ssl_context.return_value = mock_context_instance
        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        adapter = LegacyHttpAdapter()
        adapter.init_poolmanager(connections=5, maxsize=50, block=True, extra_param="test")

        # Verify
        call_args = mock_super_init_poolmanager.call_args.args
        assert call_args[0] == 5  # connections
        assert call_args[1] == 50  # maxsize
        assert call_args[2] is True  # block
        assert mock_super_init_poolmanager.call_args.kwargs["extra_param"] == "test"

    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    @patch("apd_scrap.utils.ssl_adapter.ssl.SSLContext")
    @patch("apd_scrap.utils.ssl_adapter.ssl.TLSVersion")
    def test_init_poolmanager_returns_poolmanager(
        self, mock_tls_version, mock_ssl_context, mock_super_init_poolmanager
    ):
        """Verifica que init_poolmanager retorne el PoolManager."""
        # Setup
        mock_context_instance = Mock()
        mock_ssl_context.return_value = mock_context_instance
        mock_poolmanager = Mock()
        mock_super_init_poolmanager.return_value = mock_poolmanager

        # Execute
        adapter = LegacyHttpAdapter()
        result = adapter.init_poolmanager(connections=10, maxsize=100)

        # Verify
        assert result == mock_poolmanager


class TestAdaptersIntegration:
    """Tests de integración de los adaptadores."""

    @patch("apd_scrap.utils.ssl_adapter.create_urllib3_context")
    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    def test_custom_adapter_different_from_legacy(
        self, mock_super_init_poolmanager, mock_create_context
    ):
        """Verifica que CustomHttpAdapter y LegacyHttpAdapter sean diferentes."""
        # Setup
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        custom = CustomHttpAdapter()
        legacy = LegacyHttpAdapter()

        # Verify que son instancias diferentes
        assert isinstance(custom, CustomHttpAdapter)
        assert isinstance(legacy, LegacyHttpAdapter)
        assert custom != legacy

    @patch("apd_scrap.utils.ssl_adapter.create_urllib3_context")
    @patch("apd_scrap.utils.ssl_adapter.HTTPAdapter.init_poolmanager")
    def test_custom_adapter_uses_cipher_string(
        self, mock_super_init_poolmanager, mock_create_context
    ):
        """Verifica que CustomHttpAdapter use la constante CIPHERS."""
        # Setup
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_super_init_poolmanager.return_value = Mock()

        # Execute
        adapter = CustomHttpAdapter()
        mock_create_context.reset_mock()  # Resetear después de inicialización
        adapter.init_poolmanager(connections=10, maxsize=100)

        # Verify
        assert mock_create_context.called
        last_call = mock_create_context.call_args_list[-1]
        assert last_call[1]["ciphers"] == CIPHERS
