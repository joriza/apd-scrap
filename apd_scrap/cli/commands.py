"""
Interfaz de línea de comandos para APD-Scrap.

Este módulo proporciona la funcionalidad de CLI para el scraper,
incluyendo el parser de argumentos y la validación de entrada.
"""

import argparse
from typing import NamedTuple, Optional


class CLIArgs(NamedTuple):
    """
    Tupla nombrada para los argumentos de línea de comandos.

    Attributes:
        distrito: Nombre del distrito a consultar
        export_excel: Si se debe exportar a formato Excel
        export_format: Formato de exportación (ofertas, postulantes, both)
        output_file: Ruta personalizada para archivo de salida
    """

    distrito: str
    export_excel: bool = False
    export_format: str = "ofertas"
    output_file: Optional[str] = None


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
        prog="APD-Scrap",
        description="Scraper de ofertas educativas del sistema APD del gobierno argentino.",
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
        """,
    )

    parser.add_argument(
        "--distrito",
        "-d",
        type=str,
        default="merlo",
        metavar="DISTRITO",
        help=(
            "Nombre del distrito para descargar ofertas educativas. "
            "El distrito se convertirá a mayúsculas internamente. "
            "(default: %(default)s)"
        ),
    )

    # Argumentos para exportación a Excel
    parser.add_argument(
        "--export-excel",
        action="store_true",
        help="Exportar datos a formato Excel después de descargar"
    )

    parser.add_argument(
        "--export-format",
        choices=["ofertas", "postulantes", "both"],
        default="ofertas",
        help=(
            "Qué datos exportar a Excel. "
            "ofertas: solo tabla de ofertas, "
            "postulantes: solo tabla de postulantes, "
            "both: ambas tablas en un archivo Excel "
            "(default: %(default)s)"
        ),
    )

    parser.add_argument(
        "--output-file",
        type=str,
        metavar="RUTA",
        help=(
            "Ruta personalizada para archivo Excel de salida. "
            "Si no se especifica, se genera un nombre automático "
            "con timestamp en el directorio actual"
        ),
    )

    return parser


def parse_args(args: Optional[list[str]] = None) -> CLIArgs:
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

    # Validar parámetros de exportación
    if parsed_args.export_excel:
        if parsed_args.export_format not in ["ofertas", "postulantes", "both"]:
            parser.error("Formato de exportación inválido. Debe ser 'ofertas', 'postulantes' o 'both'")
        
        if parsed_args.output_file and not parsed_args.output_file.lower().endswith('.xlsx'):
            parser.error("El archivo de salida debe tener extensión .xlsx")

    return CLIArgs(
        distrito=parsed_args.distrito.strip(),
        export_excel=parsed_args.export_excel,
        export_format=parsed_args.export_format,
        output_file=parsed_args.output_file
    )
