"""
Configuración centralizada de APD-Scrap.

Este módulo contiene toda la configuración del sistema,
incluyendo URLs de API, parámetros de base de datos y
opciones de logging.
"""

from typing import Dict, Any


class Config:
    """Gestiona la configuración del sistema."""
    
    # API Configuration
    API_BASE_URL: str = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
    API_TIMEOUT: int = 60
    
    # Database Configuration
    DB_PATH: str = "apd.db"
    
    # Output Configuration
    OUTPUT_DIR: str = "."
    
    # SSL Configuration
    CIPHERS: str = (
        'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:'
        'ECDH+HIGH:DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:'
        'RSA+3DES:!aNULL:!eNULL:!MD5'
    )
    
    @classmethod
    def get_api_query_params(cls, distrito: str, rows: int = 0) -> Dict[str, Any]:
        """
        Genera los parámetros de consulta para la API.
        
        Args:
            distrito: Nombre del distrito a consultar
            rows: Número de filas a obtener (0 = todas)
            
        Returns:
            Diccionario con parámetros de consulta
        """
        params = {
            'q': '*:*',
            'fq': f'descdistrito:{distrito.upper()}',
            'wt': 'json'
        }
        
        if rows > 0:
            params['rows'] = rows
            
        return params
    
    @classmethod
    def get_output_filename(cls, distrito: str) -> str:
        """
        Genera el nombre del archivo de salida.
        
        Args:
            distrito: Nombre del distrito
            
        Returns:
            Nombre del archivo JSON de salida
        """
        return f"output_{distrito.lower()}.json"