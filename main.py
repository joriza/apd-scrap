"""
APD-Scrap: Scraper de ofertas educativas del sistema APD.

Punto de entrada principal de la aplicación.
Este módulo orquesta el flujo completo de scraping: configuración,
obtención de datos, guardado en JSON y base de datos.
"""

import json
import sys

import requests

from apd_scrap.cli.commands import parse_args
from apd_scrap.config import Config
from apd_scrap.database.connection import DatabaseConnection
from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.utils.logging import setup_logging


def main() -> int:
    """
    Función principal del scraper de APD.

    Flujo de ejecución:
    1. Configurar logging
    2. Parsear argumentos de línea de comandos
    3. Inicializar scraper y base de datos
    4. Obtener datos de la API
    5. Guardar en JSON y base de datos
    6. Manejar errores y retornar código de salida apropiado

    Returns:
        int: 0 si éxito, 1 si error. El código de salida es
            útil para integración con scripts y CI/CD.

    Raises:
        SystemExit: Se propaga excepciones críticas no manejadas

    Example:
        >>> # Ejecución normal
        >>> exit_code = main()
        >>> print(f"Estado: {'OK' if exit_code == 0 else 'ERROR'}")

        >>> # Para uso en scripts
        >>> if __name__ == "__main__":
        ...     sys.exit(main())
    """
    # Configurar logging
    config = Config()
    logger = setup_logging(
        name=config.LOG_NAME,
        log_level=config.LOG_LEVEL,
        log_file=config.LOG_FILE,
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        console_output=config.LOG_CONSOLE_OUTPUT,
    )

    # Parsear argumentos
    args = parse_args()
    distrito = args.distrito.upper()

    logger.info("APD-Scrap iniciado - Versión 2.3.0")
    logger.info(f"Distrito seleccionado: {distrito}")

    # Inicializar componentes
    try:
        with APDScraper() as scraper:
            # Obtener datos de la API
            api_data = scraper.fetch_all_records(distrito)

            if not api_data:
                logger.error("No se pudieron obtener los datos de la API.")
                return 1

            # Guardar en JSON
            output_file = scraper.save_to_json(api_data, distrito)

            if not output_file:
                logger.error("Error al guardar archivo JSON.")
                return 1

            # Guardar en base de datos
            ofertas_docs = api_data.get("response", {}).get("docs", [])

            with DatabaseConnection() as db:
                # Inicializar esquema si no existe
                db.initialize_schema()

                # Guardar ofertas
                registros_guardados = db.save_ofertas(ofertas_docs, distrito)

                if registros_guardados > 0:
                    pass
                else:
                    pass

    except requests.exceptions.RequestException as e:
        logger.critical(f"Error de red: {e}")
        return 1
    except json.JSONDecodeError as e:
        logger.critical(f"Error al decodificar JSON: {e}")
        return 1
    except Exception as e:
        logger.critical(f"Error crítico en la ejecución: {e}")
        return 1

    logger.info("APD-Scrap finalizado exitosamente")
    return 0


if __name__ == "__main__":
    """Punto de entrada cuando se ejecuta como script."""
    sys.exit(main())
