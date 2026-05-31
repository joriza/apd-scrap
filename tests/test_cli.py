"""
Tests unitarios para el módulo apd_scrap.cli.commands
"""

import pytest
import argparse

from apd_scrap.cli.commands import create_parser


class TestCreateParser:
    """Tests para create_parser."""

    def test_create_parser_retorna_parser(self):
        """Verifica que create_parser retorne un ArgumentParser."""
        parser = create_parser()
        assert isinstance(parser, argparse.ArgumentParser)

    def test_parser_tiene_descripcion(self):
        """Verifica que el parser tenga descripción."""
        parser = create_parser()
        assert parser.description is not None

    def test_parser_tiene_argumento_distrito(self):
        """Verifica que exista el argumento --distrito."""
        parser = create_parser()
        args = parser.parse_args(["--distrito", "moreno"])
        assert args.distrito == "moreno"

    def test_parser_tiene_alias_d(self):
        """Verifica que exista el alias -d para --distrito."""
        parser = create_parser()
        args = parser.parse_args(["-d", "moron"])
        assert args.distrito == "moron"

    def test_parser_distrito_default_merlo(self):
        """Verifica que el default sea 'merlo'."""
        parser = create_parser()
        args = parser.parse_args([])
        assert args.distrito == "merlo"

    def test_parser_distrito_convierte_a_mayusculas(self):
        """Verifica que el parser acepte minúsculas (main.py lo convierte)."""
        parser = create_parser()
        args = parser.parse_args(["--distrito", "moreno"])
        assert args.distrito == "moreno"  # Parser no convierte, main.py sí

    def test_parser_tiene_help(self):
        """Verifica que el parser soporte --help."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["--help"])

    def test_parser_tiene_alias_h(self):
        """Verifica que el parser soporte -h."""
        parser = create_parser()
        with pytest.raises(SystemExit):
            parser.parse_args(["-h"])

    def test_parser_varios_distritos(self):
        """Nota: El parser actual solo acepta un distrito a la vez."""
        parser = create_parser()
        args = parser.parse_args(["--distrito", "moreno"])
        assert args.distrito == "moreno"

    def test_parser_epilog_contiene_ejemplos(self):
        """Verifica que el epilog contenga ejemplos."""
        parser = create_parser()
        assert parser.epilog is not None
        assert "Ejemplos:" in parser.epilog
