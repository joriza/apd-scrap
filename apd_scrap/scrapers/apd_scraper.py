"""
Scraper de la API de APD del gobierno argentino.

Este módulo contiene la lógica principal para obtener datos de
la API de ofertas educativas del sistema APD.
"""

import json
from typing import Any, Optional

import requests

from apd_scrap.config import Config
from apd_scrap.utils.logging import LoggerMixin
from apd_scrap.utils.ssl_adapter import CustomHttpAdapter
from apd_scrap.utils.retry import retry_with_backoff, RetryError
from apd_scrap.utils.retry import retry_with_backoff, RetryConfig, RetryError


class APIResponse:
    """
    Estructura de respuesta esperada de la API.

    La API del gobierno argentino devuelve datos en formato JSON
    con la siguiente estructura:

    {
        "response": {
            "numFound": 12345,
            "start": 0,
            "docs": [
                {
                    "ige": 123,
                    "estado": "Publicada",
                    ...
                }
            ]
        }
    }
    """

    pass


class APDScraper(LoggerMixin):
    """
    Scraper para obtener ofertas educativas del sistema APD.

    Esta clase proporciona una interfaz para interactuar con la API
    del gobierno argentino que contiene ofertas laborales docentes.
    Maneja automáticamente la configuración SSL específica requerida
    por el servidor y proporciona métodos para obtener y guardar datos.

    Attributes:
        config (Config): Configuración del scraper
        session (requests.Session): Sesión HTTP con configuración SSL

    Example:
        >>> # Obtener todos los registros de un distrito
        >>> with APDScraper() as scraper:
        ...     data = scraper.fetch_all_records('MERLO')
        ...     scraper.save_to_json(data, 'MERLO')

        >>> # Obtener solo el conteo
        >>> scraper = APDScraper()
        >>> total = scraper.get_total_records('MORENO')
        >>> print(f"Total: {total}")
    """

    def __init__(self, config: Optional[Config] = None) -> None:
        """
        Inicializa el scraper con configuración.

        Args:
            config: Configuración personalizada. Si None, usa
                Config() con valores por defecto.

        Raises:
            requests.exceptions.RequestException: Si hay error
                al configurar la sesión

        Example:
            >>> # Configuración por defecto
            >>> scraper = APDScraper()

            >>> # Configuración personalizada
            >>> from apd_scrap.config import Config
            >>> config = Config()
            >>> config.API_TIMEOUT = 120
            >>> scraper = APDScraper(config=config)
        """
        self.config: Config = config or Config()
        self.session: requests.Session = self._create_session()

    def _create_session(self) -> requests.Session:
        """
        Crea una sesión HTTP con configuración SSL personalizada.

        La sesión se configura con un adaptador SSL personalizado
        para cumplir con los requisitos del servidor del gobierno
        argentino.

        Returns:
            requests.Session: Sesión HTTP configurada con SSL

        Note:
            Este método es privado y se llama automáticamente en __init__.
        """
        session = requests.Session()
        session.mount(self.config.API_BASE_URL, CustomHttpAdapter())
        self.logger.debug("Sesión HTTP configurada con SSL adapter personalizado")
        return session

    def get_total_records(self, distrito: str) -> int:
        """
        Obtiene el número total de registros para un distrito.

        Este método hace una solicitud inicial a la API con rows=1
        para obtener el conteo total sin descargar todos los datos.

        Args:
            distrito: Nombre del distrito (no sensible a mayúsculas)

        Returns:
            int: Número total de registros disponibles. Retorna 0 si
                hay error o no se encontraron registros.

        Example:
            >>> scraper = APDScraper()
            >>> total = scraper.get_total_records('merlo')
            >>> print(f"Hay {total} ofertas en Merlo")
            Hay 6759 ofertas en Merlo
        """
        self.logger.debug(f"Obteniendo conteo total de registros para distrito: {distrito}")
        params = self.config.get_api_query_params(distrito, rows=1)
        data = self._fetch_data(params)

        if not data or "response" not in data:
            self.logger.warning(f"No se pudo obtener response para distrito {distrito}")
            return 0

        total = data["response"].get("numFound", 0)
        self.logger.debug(f"Total de registros encontrados: {total}")
        return total

    def fetch_all_records(self, distrito: str) -> Optional[dict[str, Any]]:
        """
        Obtiene todos los registros de un distrito.

        Este método primero obtiene el conteo total de registros y
        luego descarga todos los datos en una sola solicitud.

        Args:
            distrito: Nombre del distrito a consultar

        Returns:
            Optional[Dict[str, Any]]: Datos completos de la API o
                None si hay error o no hay registros. La estructura
                del diccionario sigue el formato de APIResponse.

        Example:
            >>> scraper = APDScraper()
            >>> data = scraper.fetch_all_records('MERLO')
            >>> if data:
            ...     num_docs = len(data.get('response', {}).get('docs', []))
            ...     print(f"Descargados {num_docs} documentos")
            Descargados 6759 documentos
        """
        # Primero obtener el total
        total = self.get_total_records(distrito)

        if total == 0:
            self.logger.warning(f"No se encontraron registros para el distrito {distrito}.")
            return None

        self.logger.debug(
            f"Distrito {distrito}: se encontraron {total} registros. Obteniendo todos..."
        )

        # Obtener todos los registros
        params = self.config.get_api_query_params(distrito, rows=total)
        data = self._fetch_data(params)

        if data:
            num_docs = len(data.get("response", {}).get("docs", []))
            self.logger.debug(f"Se obtuvieron {num_docs} documentos de {total} esperados")

        return data

    @retry_with_backoff(
        max_retries=3,
        initial_delay=2.0,
        max_delay=30.0,
        exceptions=(
            requests.Timeout,
            requests.ConnectionError,
            requests.exceptions.RequestException
        )
    )
    def _fetch_data(self, params: dict[str, Any]) -> Optional[dict[str, Any]]:
        """
        Realiza la solicitud a la API con reintentos automáticos.

        Este método privado maneja la solicitud HTTP, validación de
        respuestas y fallback para problemas de codificación. Implementa
        reintentos automáticos con backoff exponencial para fallos temporales.

        Args:
            params: Parámetros de consulta para la API

        Returns:
            Optional[Dict[str, Any]]: Datos JSON decodificados o None
                si hay error. Se aplica fallback de decodificación si
                response.json() falla.

        Note:
            - Usa response.json() como método principal de decodificación
            - Aplica fallback decodificando response.content con apparent_encoding
            - Maneja RequestException y JSONDecodeError silenciosamente
            - Reintenta automáticamente con backoff exponencial
            - Máximo 3 reintentos con delays de 2s, 4s, 8s
        """
        try:
            response = self.session.get(
                self.config.API_BASE_URL, params=params, timeout=self.config.API_TIMEOUT
            )
            response.raise_for_status()

            try:
                data = response.json()
                self.logger.debug("Respuesta JSON decodificada correctamente")
                return data
            except json.JSONDecodeError:
                # Fallback para problemas de codificación
                self.logger.warning("JSON decode error, usando fallback")
                try:
                    data = json.loads(response.content.decode(response.apparent_encoding))
                    return data
                except (UnicodeDecodeError, json.JSONDecodeError) as e:
                    self.logger.error(f"Fallback de decodificación falló: {e}")
                    return None

        except requests.exceptions.RequestException as e:
            self.logger.error(f"Ocurrió un error en la solicitud HTTP: {e}")
            return None
        except json.JSONDecodeError as e:
            self.logger.error(
                f"Error de decodificación: La respuesta no es un JSON válido. Error: {e}"
            )
            return None

    def save_to_json(self, data: dict[str, Any], distrito: str) -> Optional[str]:
        """
        Guarda los datos en un archivo JSON.

        Este método guarda los datos de la API en un archivo JSON
        con formato legible (indent=4, ensure_ascii=False) y
        encoding UTF-8.

        Args:
            data: Datos a guardar. Se espera que siga el formato
                de APIResponse.
            distrito: Nombre del distrito para generar el nombre
                del archivo

        Returns:
            Optional[str]: Ruta del archivo guardado o None si hay error.
                El nombre del archivo sigue el formato:
                "output_{distrito.lower()}.json"

        Raises:
            IOError: Si hay error al escribir el archivo

        Example:
            >>> scraper = APDScraper()
            >>> data = {'response': {'docs': [{'ige': 1}]}}
            >>> path = scraper.save_to_json(data, 'MERLO')
            >>> print(f"Guardado en: {path}")
            Guardado en: output_merlo.json
        """
        if not data:
            self.logger.warning("No hay datos para guardar en archivo JSON")
            return None

        filename = self.config.get_output_filename(distrito)

        try:
            with open(filename, "w", encoding="utf-8") as f:
                json.dump(data, f, ensure_ascii=False, indent=4)

            num_docs = len(data.get("response", {}).get("docs", []))
            self.logger.info(f"Archivos JSON: {num_docs} registros guardados en '{filename}'.")

            return filename
        except OSError as e:
            self.logger.error(f"Error al guardar archivo JSON: {e}")
            return None

    def close(self) -> None:
        """
        Cierra la sesión HTTP.

        Este método debe llamarse cuando ya no se necesite el scraper
        para liberar recursos. Si se usa el context manager,
        este método se llama automáticamente.

        Example:
            >>> scraper = APDScraper()
            >>> # Usar scraper
            >>> scraper.close()

            >>> # Mejor: usar context manager
            >>> with APDScraper() as scraper:
            ...     # Usar scraper
            ...     pass  # close() se llama automáticamente
        """
        if self.session:
            self.session.close()
            self.logger.debug("Sesión HTTP cerrada")

    def __enter__(self) -> "APDScraper":
        """
        Context manager entry - inicializa scraper.

        Returns:
            APDScraper: La instancia misma para usar en with block

        Example:
            >>> with APDScraper() as scraper:
            ...     data = scraper.fetch_all_records('MERLO')
        """
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]
    ) -> None:
        """
        Context manager exit - cierra sesión.

        Args:
            exc_type: Tipo de excepción si ocurrió
            exc_val: Valor de excepción si ocurrió
            exc_tb: Traceback de excepción si ocurrió

        Note:
            Las excepciones no se suprimen, se propagan normalmente.
        """
        self.close()
