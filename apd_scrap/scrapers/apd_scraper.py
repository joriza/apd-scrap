"""
Scraper de la API de APD del gobierno argentino.

Este módulo contiene la lógica principal para obtener datos de
la API de ofertas educativas.
"""

import json
import requests
from typing import Optional, Dict, Any

from apd_scrap.config import Config
from apd_scrap.utils.ssl_adapter import CustomHttpAdapter


class APDScraper:
    """
    Scraper para obtener ofertas educativas del sistema APD.
    """
    
    def __init__(self, config: Optional[Config] = None):
        """
        Inicializa el scraper.
        
        Args:
            config: Configuración personalizada (opcional)
        """
        self.config = config or Config()
        self.session = self._create_session()
    
    def _create_session(self) -> requests.Session:
        """
        Crea una sesión HTTP con configuración SSL personalizada.
        
        Returns:
            Sesión HTTP configurada
        """
        session = requests.Session()
        session.mount(self.config.API_BASE_URL, CustomHttpAdapter())
        return session
    
    def get_total_records(self, distrito: str) -> int:
        """
        Obtiene el número total de registros para un distrito.
        
        Args:
            distrito: Nombre del distrito
            
        Returns:
            Número total de registros, 0 si hay error
        """
        params = self.config.get_api_query_params(distrito, rows=1)
        data = self._fetch_data(params)
        
        if not data or 'response' not in data:
            return 0
        
        return data['response'].get('numFound', 0)
    
    def fetch_all_records(self, distrito: str) -> Optional[Dict[str, Any]]:
        """
        Obtiene todos los registros de un distrito.
        
        Args:
            distrito: Nombre del distrito
            
        Returns:
            Datos completos de la API o None si hay error
        """
        # Primero obtener el total
        total = self.get_total_records(distrito)
        
        if total == 0:
            print(f"No se encontraron registros para el distrito {distrito}.")
            return None
        
        print(f"Se encontraron {total} registros. Obteniendo todos...")
        
        # Obtener todos los registros
        params = self.config.get_api_query_params(distrito, rows=total)
        data = self._fetch_data(params)
        
        return data
    
    def _fetch_data(self, params: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Realiza la solicitud a la API y maneja errores de decodificación.
        
        Args:
            params: Parámetros de consulta
            
        Returns:
            Datos JSON decodificados o None si hay error
        """
        try:
            response = self.session.get(
                self.config.API_BASE_URL,
                params=params,
                timeout=self.config.API_TIMEOUT
            )
            response.raise_for_status()
            
            try:
                return response.json()
            except json.JSONDecodeError:
                # Fallback para problemas de codificación
                return json.loads(response.content.decode(response.apparent_encoding))
                
        except requests.exceptions.RequestException as e:
            print(f"Ocurrió un error en la solicitud HTTP: {e}")
        except json.JSONDecodeError as e:
            print(f"Error de decodificación: La respuesta no es un JSON válido. Error: {e}")
        
        return None
    
    def save_to_json(self, data: Dict[str, Any], distrito: str) -> Optional[str]:
        """
        Guarda los datos en un archivo JSON.
        
        Args:
            data: Datos a guardar
            distrito: Nombre del distrito
            
        Returns:
            Ruta del archivo guardado o None si hay error
        """
        if not data:
            return None
        
        filename = self.config.get_output_filename(distrito)
        
        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)
            
            num_docs = len(data.get("response", {}).get("docs", []))
            print(f"\n¡Éxito! {num_docs} registros guardados en '{filename}'.")
            
            return filename
        except IOError as e:
            print(f"Error al guardar archivo JSON: {e}")
            return None
    
    def close(self) -> None:
        """Cierra la sesión HTTP."""
        self.session.close()
    
    def __enter__(self):
        """Context manager entry."""
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()