"""
Gestión de conexión y operaciones con la base de datos SQLite.

Este módulo proporciona una clase para manejar todas las operaciones
de base de datos, incluyendo inicialización e inserción de ofertas.
"""

import sqlite3
from typing import List, Dict, Any

from apd_scrap.database.schema import COLUMNAS, CREATE_TABLE_SQL, get_insert_sql


class DatabaseConnection:
    """
    Maneja la conexión y operaciones con la base de datos SQLite.
    """
    
    def __init__(self, db_path: str = "apd.db"):
        """
        Inicializa la conexión a la base de datos.
        
        Args:
            db_path: Ruta al archivo de base de datos
        """
        self.db_path = db_path
        self.connection = None
    
    def connect(self) -> sqlite3.Connection:
        """
        Establece conexión con la base de datos.
        
        Returns:
            Conexión SQLite activa
        """
        self.connection = sqlite3.connect(self.db_path)
        return self.connection
    
    def close(self) -> None:
        """Cierra la conexión con la base de datos."""
        if self.connection:
            self.connection.close()
            self.connection = None
    
    def __enter__(self):
        """Context manager entry."""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit."""
        self.close()
    
    def initialize_schema(self) -> bool:
        """
        Inicializa el esquema de la base de datos si no existe.
        
        Returns:
            True si se inicializó correctamente
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(CREATE_TABLE_SQL)
                conn.commit()
            return True
        except sqlite3.Error as e:
            print(f"Error al inicializar el esquema: {e}")
            return False
    
    def save_ofertas(self, ofertas: List[Dict[str, Any]]) -> int:
        """
        Guarda o actualiza una lista de ofertas en la base de datos.
        
        Args:
            ofertas: Lista de diccionarios con datos de ofertas
            
        Returns:
            Número de registros guardados/actualizados
        """
        if not ofertas:
            print("No hay ofertas para guardar en la base de datos.")
            return 0
        
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                sql = get_insert_sql()
                
                for oferta in ofertas:
                    valores = tuple(oferta.get(col) for col in COLUMNAS)
                    cursor.execute(sql, valores)
                
                conn.commit()
                return len(ofertas)
                
        except sqlite3.Error as e:
            print(f"Error al interactuar con la base de datos: {e}")
            return 0
    
    def get_count(self) -> int:
        """
        Obtiene el número total de registros en la base de datos.
        
        Returns:
            Número de registros
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT COUNT(*) FROM ofertas")
                return cursor.fetchone()[0]
        except sqlite3.Error:
            return 0
    
    def get_distrito_count(self, distrito: str) -> int:
        """
        Obtiene el número de registros por distrito.
        
        Args:
            distrito: Nombre del distrito
            
        Returns:
            Número de registros para el distrito
        """
        try:
            with self.connect() as conn:
                cursor = conn.cursor()
                cursor.execute(
                    "SELECT COUNT(*) FROM ofertas WHERE descdistrito = ?",
                    (distrito.upper(),)
                )
                return cursor.fetchone()[0]
        except sqlite3.Error:
            return 0