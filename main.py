"""
APD-Scrap: Scraper de ofertas educativas del sistema APD.

Punto de entrada principal de la aplicación.
"""

import sys
import logging
from apd_scrap.config import Config
from apd_scrap.utils.logging import setup_logging
from apd_scrap.cli.commands import create_parser
from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.database.connection import DatabaseConnection


def main() -> int:
    """
    Función principal del scraper.
    
    Flujo de ejecución:
    1. Configurar logging
    2. Parsear argumentos de línea de comandos
    3. Inicializar scraper y base de datos
    4. Obtener datos de la API
    5. Guardar en JSON y base de datos
    
    Returns:
        0 si éxito, 1 si error
    """
    # Configurar logging
    config = Config()
    logger = setup_logging(
        name=config.LOG_NAME,
        log_level=config.LOG_LEVEL,
        log_file=config.LOG_FILE,
        max_bytes=config.LOG_MAX_BYTES,
        backup_count=config.LOG_BACKUP_COUNT,
        console_output=config.LOG_CONSOLE_OUTPUT
    )
    
    # Parsear argumentos
    parser = create_parser()
    args = parser.parse_args()
    
    distrito = args.distrito.upper()
    logger.info(f"APD-Scrap iniciado - Distrito: {distrito}")
    print(f"Distrito seleccionado: {distrito}\n")
    
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
            ofertas_docs = api_data.get('response', {}).get('docs', [])
            
            with DatabaseConnection() as db:
                # Inicializar esquema si no existe
                db.initialize_schema()
                
                # Guardar ofertas
                registros_guardados = db.save_ofertas(ofertas_docs, distrito)
                
                if registros_guardados > 0:
                    print(f"\nSe han guardado/actualizado {registros_guardados} registros en 'apd.db'.")
                else:
                    print("\nNo se guardaron registros en la base de datos.")
    
    except Exception as e:
        logger.critical(f"Error crítico en la ejecución: {e}")
        return 1
    
    logger.info("APD-Scrap finalizado exitosamente")
    return 0


if __name__ == "__main__":
    sys.exit(main())