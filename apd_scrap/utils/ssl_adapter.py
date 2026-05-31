"""
Adaptador HTTP personalizado con soporte SSL/TLS.

Este módulo proporciona un adaptador HTTP personalizado que fuerza
un cipher suite específico requerido por el servidor de la API del
gobierno argentino.
"""

from requests.adapters import HTTPAdapter

try:
    from requests.packages.urllib3.util.ssl_ import create_urllib3_context
except ImportError:
    from urllib3.util.ssl_ import create_urllib3_context


# Cipher suite específico requerido por el servidor
CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:'
    'ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:'
    'RSA+3DES:!aNULL:!eNULL:!MD5'
)


class CustomHttpAdapter(HTTPAdapter):
    """
    Adaptador HTTP personalizado para forzar un cipher suite específico.
    
    Este adaptador es necesario porque el servidor de la API del gobierno
    argentino requiere una configuración SSL/TLS específica.
    """
    
    def init_poolmanager(self, *args, **kwargs):
        """
        Inicializa el pool manager con contexto SSL personalizado.
        
        Args:
            *args: Argumentos posicionales
            **kwargs: Argumentos nombrados
            
        Returns:
            Pool manager configurado
        """
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(CustomHttpAdapter, self).init_poolmanager(*args, **kwargs)