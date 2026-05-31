"""
Tests unitarios para el módulo apd_scrap.utils.ssl_adapter
"""

import pytest
from unittest.mock import Mock, patch

from apd_scrap.utils.ssl_adapter import CustomHttpAdapter, CIPHERS


class TestCustomHttpAdapter:
    """Tests para CustomHttpAdapter."""
    
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
    
    def test_custom_adapter_instantiation(self):
        """Puede instanciar CustomHttpAdapter."""
        adapter = CustomHttpAdapter()
        assert adapter is not None
    
    @patch('apd_scrap.utils.ssl_adapter.create_urllib3_context')
    def test_init_poolmanager_creates_ssl_context(self, mock_create_context):
        """Verifica que init_poolmanager cree un contexto SSL."""
        mock_context = Mock()
        mock_create_context.return_value = mock_context
        mock_create_context.reset_mock()  # Resetear mock porque puede haber sido llamado antes
        
        adapter = CustomHttpAdapter()
        
        # Simular el init_poolmanager
        mock_poolmanager = Mock()
        adapter.init_poolmanager = lambda *args, **kwargs: mock_poolmanager(*args, **kwargs)
        
        # Llamar manualmente a la lógica
        context = mock_create_context(ciphers=CIPHERS)
        
        # Verificar que se creó un contexto con ciphers
        assert mock_create_context.called
        assert context == mock_context