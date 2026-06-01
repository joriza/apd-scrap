"""
Adaptador HTTP personalizado con soporte SSL/TLS.

Este módulo proporciona un adaptador HTTP personalizado que fuerza
un cipher suite específico requerido por el servidor de la API del
gobierno argentino.

El servidor de la API del gobierno argentino requiere una configuración
SSL/TLS específica con ciphers heredados que no son compatibles con
las configuraciones predeterminadas de Python 3.x.
"""

from typing import Any

from requests.adapters import HTTPAdapter
from urllib3.poolmanager import PoolManager

import ssl

try:
    from requests.packages.urllib3.util.ssl_ import create_urllib3_context
except ImportError:
    from urllib3.util.ssl_ import create_urllib3_context


# Cipher suite específico requerido por el servidor
CIPHERS: str = (
    "ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:"
    "ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:"
    "RSA+3DES:!aNULL:!eNULL:!MD5"
)


class CustomHttpAdapter(HTTPAdapter):
    """
    Adaptador HTTP personalizado para forzar un cipher suite específico.

    Este adaptador es necesario porque el servidor de la API del gobierno
    argentino requiere una configuración SSL/TLS específica con ciphers
    heredados que no son compatibles con las configuraciones predeterminadas
    de Python 3.x. Sin este adaptador, las conexiones HTTPS fallarían
    con errores de handshake SSL.

    Attributes:
        CIPHERS (str): Cipher suite SSL/TLS específico para el servidor

    Example:
        >>> import requests
        >>> from apd_scrap.utils.ssl_adapter import CustomHttpAdapter
        >>>
        >>> session = requests.Session()
        >>> session.mount("https://servicios3.abc.gob.ar/", CustomHttpAdapter())
        >>>
        >>> # Ahora las solicitudes usarán el cipher suite correcto
        >>> response = session.get("https://servicios3.abc.gob.ar/...")

    Note:
        Este adaptador solo es necesario para conectarse a servidores que
        requieren ciphers heredados. Para conexiones HTTPS estándar, el
        adaptador predeterminado de requests es suficiente.
    """

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **kwargs: Any
    ) -> PoolManager:
        """
        Inicializa el pool manager con contexto SSL personalizado.

        Este método sobrescribe el método de HTTPAdapter para crear
        un contexto SSL con el cipher suite específico requerido por
        el servidor de la API del gobierno argentino.

        Args:
            connections: Número de conexiones a mantener en el pool
            maxsize: Número máximo de conexiones en el pool
            block: Si True, bloquea cuando el pool está lleno
            **kwargs: Argumentos adicionales pasados al pool manager

        Returns:
            PoolManager: Pool manager configurado con contexto SSL personalizado

        Note:
            El contexto SSL se crea con el cipher suite definido en CIPHERS
            y se pasa al pool manager a través del parámetro 'ssl_context'.
        """
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs["ssl_context"] = context
        return super().init_poolmanager(connections, maxsize, block, **kwargs)


class LegacyHttpAdapter(HTTPAdapter):
    """
    Adaptador HTTP para servidores con configuración SSL legacy.

    Este adaptador es necesario para conectarse a endpoints que requieren
    configuraciones SSL más antiguas o inseguras, como el endpoint de
    postulantes del sistema APD.

    Características:
    - Usa TLS 1.2 como versión mínima
    - Configura SECLEVEL=1 para permitir ciphers más antiguos
    - No verifica hostname (compatibilidad con servidores legacy)

    Example:
        >>> import requests
        >>> from apd_scrap.utils.ssl_adapter import LegacyHttpAdapter
        >>>
        >>> session = requests.Session()
        >>> session.mount("https://servicios3.abc.gob.ar/", LegacyHttpAdapter())
        >>>
        >>> response = session.get("https://servicios3.abc.gob.ar/...")

    Note:
        Este adaptador es menos seguro que CustomHttpAdapter y solo debe
        usarse cuando el servidor no soporta configuraciones SSL modernas.
    """

    def init_poolmanager(
        self, connections: int, maxsize: int, block: bool = False, **kwargs: Any
    ) -> PoolManager:
        """
        Inicializa el pool manager con contexto SSL legacy.

        Este método crea un contexto SSL con configuración legacy:
        - TLS 1.2 como versión mínima
        - SECLEVEL=1 para permitir ciphers antiguos
        - Verificación de hostname desactivada

        Args:
            connections: Número de conexiones a mantener en el pool
            maxsize: Número máximo de conexiones en el pool
            block: Si True, bloquea cuando el pool está lleno
            **kwargs: Argumentos adicionales pasados al pool manager

        Returns:
            PoolManager: Pool manager configurado con contexto SSL legacy
        """
        context = ssl.SSLContext(ssl.PROTOCOL_TLS_CLIENT)
        context.minimum_version = ssl.TLSVersion.TLSv1_2
        context.set_ciphers("DEFAULT@SECLEVEL=1")
        context.check_hostname = False
        context.verify_mode = ssl.CERT_NONE

        kwargs["ssl_context"] = context
        return super().init_poolmanager(connections, maxsize, block, **kwargs)
