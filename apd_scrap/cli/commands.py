"""
Interfaz de línea de comandos para APD-Scrap.

Este módulo proporciona la funcionalidad de CLI para el scraper,
incluyendo el parser de argumentos y la validación de entrada.
"""

import argparse
from typing import NamedTuple, Optional, List


class CLIArgs(NamedTuple):
    """
    Tupla nombrada para los argumentos de línea de comandos.
    
    Attributes:
        distrito: Nombre del distrito a consultar
    """
    distrito: str


def create_parser() -> argparse.ArgumentParser:
    """
    Crea el parser de argumentos de línea de comandos para APD-Scrap.
    
    Esta función configura y devuelve un ArgumentParser que permite
    especificar el distrito desde la línea de comandos. El distrito
    puede especificarse usando --distrito o -d.
    
    Returns:
        argparse.ArgumentParser: Parser configurado con argumentos
        de APD-Scrap
            
    Example:
        >>> parser = create_parser()
        >>> args = parser.parse_args(['--distrito', 'merlo'])
        >>> args.distrito
        'merlo'
        
        >>> # Usando el alias corto
        >>> args = parser.parse_args(['-d', 'moreno'])
        >>> args.distrito
        'moreno'
        
        >>> # Sin argumentos (usa default)
        >>> args = parser.parse_args([])
        >>> args.distrito
        'merlo'
    """
    parser = argparse.ArgumentParser(
        prog='APD-Scrap',
        description='Scraper de ofertas educativas del sistema APD del gobierno argentino.',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  # Descargar ofertas de Merlo (distrito por defecto)
  python main.py
  
  # Descargar ofertas de un distrito específico
  python main.py --distrito moreno
  
  # Usar el alias corto
  python main.py -d moron
  
  # Ver ayuda
  python main.py --help

Distritos disponibles:
  merlo, moreno, moron, ituzaingo, matanza, etc.

Para más información, visite: https://github.com/joriza/apd-scrap
        """
    )
    
    parser.add_argument(
        '--distrito', '-d',
        type=str,
        default='merlo',
        metavar='DISTRITO',
        help=(
            'Nombre del distrito para descargar ofertas educativas. '
            'El distrito se convertirá a mayúsculas internamente. '
            '(default: %(default)s)'
        )
    )
    
    return parser


def parse_args(args: Optional[List[str]] = None) -> CLIArgs:
    """
    Parsea los argumentos de línea de comandos y los valida.
    
    Esta función crea el parser, parsea los argumentos y valida
    que el distrito no esté vacío.
    
    Args:
        args: Lista de argumentos a parsear. Si None, usa sys.argv[1:].
            Útil para testing.
            
    Returns:
        CLIArgs: Tupla nombrada con los argumentos parseados
        
    Raises:
        ValueError: Si el distrito está vacío después de parsear
            
    Example:
        >>> # Parsear argumentos reales
        >>> args = parse_args(['--distrito', 'merlo'])
        >>> args.distrito
        'merlo'
        
        >>> # Parsear sin argumentos
        >>> args = parse_args([])
        >>> args.distrito
        'merlo'
        
        >>> # Para testing (evita sys.argv)
        >>> args = parse_args(['-d', 'moreno'])
        >>> args.distrito
        'moreno'
    """
    parser = create_parser()
    parsed_args = parser.parse_args(args)
    
    # Validar que el distrito no esté vacío
    if not parsed_args.distrito or not parsed_args.distrito.strip():
        parser.error("El distrito no puede estar vacío")
    
    return CLIArgs(distrito=parsed_args.distrito.strip())