"""
Tests unitarios para el módulo apd_scrap.database.connection
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sqlite3

from apd_scrap.database.connection import DatabaseConnection
from apd_scrap.database.schema import COLUMNAS


@pytest.fixture
def mock_db_connection():
    """Fixture que crea un mock de conexión a base de datos."""
    mock_conn = Mock(spec=sqlite3.Connection)
    mock_cursor = Mock()
    mock_conn.cursor.return_value = mock_cursor
    mock_conn.__enter__ = Mock(return_value=mock_conn)
    mock_conn.__exit__ = Mock(return_value=None)
    return mock_conn


@pytest.fixture
def db_connection():
    """Fixture que crea una instancia de DatabaseConnection."""
    return DatabaseConnection(":memory:")


class TestDatabaseConnection:
    """Tests para DatabaseConnection."""

    def test_inicializacion_con_path_default(self):
        """Verifica inicialización con path por defecto."""
        db = DatabaseConnection()
        assert db.db_path == "apd.db"

    def test_inicializacion_con_path_personalizado(self):
        """Verifica inicialización con path personalizado."""
        db = DatabaseConnection(":memory:")
        assert db.db_path == ":memory:"

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_connect_llama_sqlite3_connect(self, mock_connect):
        """Verifica que connect llame a sqlite3.connect."""
        mock_connect.return_value = Mock()
        db = DatabaseConnection(":memory:")
        db.connect()
        mock_connect.assert_called_once_with(":memory:")

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_connect_retorna_conexion(self, mock_connect):
        """Verifica que connect retorne una conexión."""
        mock_conn = Mock()
        mock_connect.return_value = mock_conn
        db = DatabaseConnection(":memory:")
        result = db.connect()
        assert result == mock_conn

    def test_close_cierra_conexion(self):
        """Verifica que close cierre la conexión."""
        db = DatabaseConnection()
        mock_conn = Mock()
        db.connection = mock_conn
        db.close()
        mock_conn.close.assert_called_once()

    def test_context_manager(self):
        """Verifica que DatabaseConnection funcione como context manager."""
        with DatabaseConnection(":memory:") as db:
            assert db is not None
            assert db.connection is not None

    def test_initialize_schema_ejecuta_create_table(self, db_connection):
        """Verifica que initialize_schema ejecute CREATE TABLE."""
        with patch.object(db_connection, "connect", return_value=Mock()) as mock_connect:
            mock_conn = mock_connect.return_value
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor

            result = db_connection.initialize_schema()

            assert result is True
            mock_cursor.execute.assert_called()

    def test_initialize_schema_con_error_sqlite(self, db_connection):
        """Verifica manejo de errores SQLite."""
        with patch.object(db_connection, "connect") as mock_connect:
            mock_conn = Mock()
            mock_conn.cursor.side_effect = sqlite3.Error("Error simulado")
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=None)
            mock_connect.return_value = mock_conn

            result = db_connection.initialize_schema()

            assert result is False

    def test_save_ofertas_con_lista_vacia(self, db_connection):
        """Verifica comportamiento con lista vacía."""
        result = db_connection.save_ofertas([])
        assert result == 0

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_ofertas_inserta_registros(self, mock_connect):
        """Verifica que save_ofertas inserte registros."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            ofertas = [{"ige": 1, "estado": "Publicada"}]
            result = db.save_ofertas(ofertas)
            assert result == 1

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_ofertas_con_distrito(self, mock_connect):
        """Verifica logging con distrito."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            ofertas = [{"ige": 1, "estado": "Publicada"}]
            result = db.save_ofertas(ofertas, distrito="MERLO")
            assert result == 1

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_ofertas_con_error_sqlite(self, mock_connect):
        """Verifica manejo de errores SQLite al guardar."""
        mock_conn = Mock()
        mock_conn.cursor.side_effect = sqlite3.Error("Error simulado")
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            ofertas = [{"ige": 1, "estado": "Publicada"}]
            result = db.save_ofertas(ofertas)
            assert result == 0

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_get_count(self, mock_connect):
        """Verifica que get_count retorne el total de registros."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [100]
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            result = db.get_count()
            assert result == 100

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_get_count_con_error(self, mock_connect):
        """Verifica get_count con error."""
        mock_conn = Mock()
        mock_conn.cursor.side_effect = sqlite3.Error("Error simulado")
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            result = db.get_count()
            assert result == 0

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_get_distrito_count(self, mock_connect):
        """Verifica que get_distrito_count retorne registros por distrito."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = [50]
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            result = db.get_distrito_count("MERLO")
            assert result == 50

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_get_distrito_count_con_error(self, mock_connect):
        """Verifica get_distrito_count con error."""
        mock_conn = Mock()
        mock_conn.cursor.side_effect = sqlite3.Error("Error simulado")
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            result = db.get_distrito_count("MERLO")
            assert result == 0

    def test_save_ofertas_con_columnas_completas(self):
        """Verifica que se usen todas las columnas definidas."""
        with patch("apd_scrap.database.connection.sqlite3.connect") as mock_connect:
            mock_conn = Mock()
            mock_cursor = Mock()
            mock_conn.cursor.return_value = mock_cursor
            mock_conn.__enter__ = Mock(return_value=mock_conn)
            mock_conn.__exit__ = Mock(return_value=None)
            mock_connect.return_value = mock_conn

            with DatabaseConnection() as db:
                # Crear oferta con todas las columnas (con valores None)
                oferta = {col: None for col in COLUMNAS}
                ofertas = [oferta]

                result = db.save_ofertas(ofertas)

                assert result == 1
                mock_cursor.execute.assert_called()

    def test_save_postulantes_con_lista_vacia(self, db_connection):
        """Verifica que save_postulantes retorne 0 con lista vacía."""
        result = db_connection.save_postulantes([])
        assert result == 0

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_postulantes_inserta_registros(self, mock_connect):
        """Verifica que save_postulantes inserte registros."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            postulantes = [
                {"ige": 4067362, "cuil": "20217355827", "designado": "N"}
            ]
            result = db.save_postulantes(postulantes, ige=4067362)
            assert result == 1

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_postulantes_con_ige(self, mock_connect):
        """Verifica logging con IGE."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            postulantes = [
                {"ige": 4067362, "cuil": "20217355827", "designado": "N"}
            ]
            result = db.save_postulantes(postulantes, ige=4067362)
            assert result == 1

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_postulantes_sin_ige(self, mock_connect):
        """Verifica logging sin IGE."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            postulantes = [
                {"ige": 4067362, "cuil": "20217355827", "designado": "N"}
            ]
            result = db.save_postulantes(postulantes)
            assert result == 1

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_postulantes_con_error_sqlite(self, mock_connect):
        """Verifica manejo de errores SQLite al guardar postulantes."""
        mock_conn = Mock()
        mock_conn.cursor.side_effect = sqlite3.Error("Error simulado")
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            postulantes = [
                {"ige": 4067362, "cuil": "20217355827", "designado": "N"}
            ]
            result = db.save_postulantes(postulantes)
            assert result == 0

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_ofertas_error_commit(self, mock_connect):
        """Verifica manejo de error en commit de save_ofertas."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit.side_effect = sqlite3.Error("Error commit")
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            ofertas = [{"ige": 1, "estado": "Publicada"}]
            result = db.save_ofertas(ofertas)
            assert result == 0

    @patch("apd_scrap.database.connection.sqlite3.connect")
    def test_save_postulantes_error_commit(self, mock_connect):
        """Verifica manejo de error en commit de save_postulantes."""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_conn.commit.side_effect = sqlite3.Error("Error commit")
        mock_conn.__enter__ = Mock(return_value=mock_conn)
        mock_conn.__exit__ = Mock(return_value=None)
        mock_connect.return_value = mock_conn

        with DatabaseConnection() as db:
            postulantes = [
                {"ige": 4067362, "cuil": "20217355827", "designado": "N"}
            ]
            result = db.save_postulantes(postulantes)
            assert result == 0
