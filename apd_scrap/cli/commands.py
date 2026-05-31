"""
Interfaz de línea de comandos para APD-Scrap.

Este módulo proporciona la funcionalidad de CLI para el scraper.
"""

import argparse


def create_parser() -> argparse.ArgumentParser:
    """
    Crea el parser de argumentos de línea de comandos.
    
    Returns:
        Parser configurado
    """
    parser = argparse.ArgumentParser(
        description="Descarga de ofertas de APD para un distrito.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python main.py --distrito merlo
  python -m apd_scrap.main --distrito moreno
        """
    )
    
    parser.add_argument(
        '--distrito', '-d',
        type=str,
        default='merlo',
        help='Distrito para descargar ofertas (default: merlo)'
    )
    
    return parser