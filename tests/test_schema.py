"""
Tests unitarios para el módulo apd_scrap.database.schema
"""

import pytest

from apd_scrap.database.schema import COLUMNAS, CREATE_TABLE_SQL, get_insert_sql


class TestColumnas:
    """Tests para la lista de columnas."""
    
    def test_columnas_existe(self):
        """Verifica que la lista de columnas exista."""
        assert COLUMNAS is not None
        assert isinstance(COLUMNAS, list)
    
    def test_columnas_cantidad_correcta(self):
        """Verifica que haya 45 columnas."""
        assert len(COLUMNAS) == 45
    
    def test_columnas_ige_es_primera(self):
        """Verifica que ige sea la primera columna (PK)."""
        assert COLUMNAS[0] == 'ige'
    
    def test_columnas_ultimas_correctas(self):
        """Verifica las últimas columnas."""
        assert 'ult_movimiento' in COLUMNAS
        assert '_version_' in COLUMNAS
        assert 'timestamp' in COLUMNAS
    
    def test_columnas_no_duplicados(self):
        """Verifica que no haya columnas duplicadas."""
        assert len(COLUMNAS) == len(set(COLUMNAS))
    
    def test_columnas_contiene_esenciales(self):
        """Verifica columnas esenciales estén presentes."""
        esenciales = [
            'ige', 'estado', 'cargo', 'escuela', 'descdistrito',
            'iniciooferta', 'finoferta', 'id', 'idoferta'
        ]
        for col in esenciales:
            assert col in COLUMNAS


class TestCreateTableSQL:
    """Tests para la sentencia SQL CREATE TABLE."""
    
    def test_create_table_sql_existe(self):
        """Verifica que el SQL de creación exista."""
        assert CREATE_TABLE_SQL is not None
        assert isinstance(CREATE_TABLE_SQL, str)
    
    def test_create_table_sql_contiene_create(self):
        """Verifica que el SQL contenga CREATE TABLE."""
        assert "CREATE TABLE" in CREATE_TABLE_SQL.upper()
    
    def test_create_table_sql_contiene_ofertas(self):
        """Verifica que el SQL contenga el nombre de la tabla."""
        assert "ofertas" in CREATE_TABLE_SQL
    
    def test_create_table_sql_contiene_ige_pk(self):
        """Verifica que ige sea PRIMARY KEY."""
        assert "ige" in CREATE_TABLE_SQL
        assert "PRIMARY KEY" in CREATE_TABLE_SQL.upper()
    
    def test_create_table_sql_contiene_columnas(self):
        """Verifica que el SQL contenga columnas importantes."""
        assert "estado" in CREATE_TABLE_SQL
        assert "cargo" in CREATE_TABLE_SQL
        assert "descdistrito" in CREATE_TABLE_SQL


class TestGetInsertSQL:
    """Tests para la función get_insert_sql."""
    
    def test_get_insert_sql_existe(self):
        """Verifica que la función exista."""
        assert callable(get_insert_sql)
    
    def test_get_insert_sql_retorna_string(self):
        """Verifica que get_insert_sql retorne un string."""
        sql = get_insert_sql()
        assert isinstance(sql, str)
    
    def test_get_insert_sql_contiene_insert(self):
        """Verifica que el SQL contenga INSERT."""
        sql = get_insert_sql()
        assert "INSERT" in sql.upper()
    
    def test_get_insert_sql_contiene_replace(self):
        """Verifica que el SQL contenga OR REPLACE."""
        sql = get_insert_sql()
        assert "REPLACE" in sql.upper()
    
    def test_get_insert_sql_contiene_ofertas(self):
        """Verifica que el SQL contenga la tabla ofertas."""
        sql = get_insert_sql()
        assert "ofertas" in sql
    
    def test_get_insert_sql_placeholders_correctos(self):
        """Verifica que el número de placeholders sea correcto."""
        sql = get_insert_sql()
        placeholders = sql.count('?')
        assert placeholders == len(COLUMNAS)
    
    def test_get_insert_sql_contiene_todas_columnas(self):
        """Verifica que el SQL contenga todas las columnas."""
        sql = get_insert_sql()
        for col in COLUMNAS:
            assert col in sql