"""
APD-Scrap: Scraper de ofertas educativas del sistema APD.

Punto de entrada principal de la aplicación.
"""

import sys
from apd_scrap.cli.commands import create_parser
from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.database.connection import DatabaseConnection


def main():
    """
    Función principal del scraper.
    
    Flujo de ejecución:
    1. Parsear argumentos de línea de comandos
    2. Inicializar scraper y base de datos
    3. Obtener datos de la API
    4. Guardar en JSON y base de datos
    """
    # Parsear argumentos
    parser = create_parser()
    args = parser.parse_args()
    
    distrito = args.distrito.upper()
    print(f"Distrito seleccionado: {distrito}\n")
    
    # Inicializar componentes
    with APDScraper() as scraper:
        # Obtener datos de la API
        api_data = scraper.fetch_all_records(distrito)
        
        if not api_data:
            print("No se pudieron obtener los datos de la API.")
            return 1
        
        # Guardar en JSON
        output_file = scraper.save_to_json(api_data, distrito)
        
        if not output_file:
            print("Error al guardar archivo JSON.")
            return 1
        
        # Guardar en base de datos
        ofertas_docs = api_data.get('response', {}).get('docs', [])
        
        with DatabaseConnection() as db:
            # Inicializar esquema si no existe
            db.initialize_schema()
            
            # Guardar ofertas
            registros_guardados = db.save_ofertas(ofertas_docs)
            
            if registros_guardados > 0:
                print(f"\nSe han guardado/actualizado {registros_guardados} registros en 'apd.db'.")
            else:
                print("\nNo se guardaron registros en la base de datos.")
    
    return 0


if __name__ == "__main__":
    sys.exit(main())