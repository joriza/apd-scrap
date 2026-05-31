"""
Gestión de conexión y operaciones con la base de datos SQLite.

Este módulo proporciona una clase para manejar todas las operaciones
de base de datos, incluyendo inicialización e inserción de ofertas.
"""

import sqlite3
from typing import Any, Optional

from apd_scrap.database.schema import (
    COLUMNAS,
    CREATE_TABLE_SQL,
    CREATE_TABLE_ESTADOS_SQL,
    CREATE_TABLE_POSTULANTES_SQL,
    COLUMNAS_POSTULANTES,
    ALTER_TABLE_ADD_CUIL_PUNTERO,
    ALTER_TABLE_ADD_CUIL_GANADOR,
    ALTER_TABLE_ADD_PUNTAJE_PUNTERO,
    ALTER_TABLE_ADD_NOMBRE_PUNTERO,
    ALTER_TABLE_ADD_PUNTAJE_GANADOR,
    ALTER_TABLE_ADD_NOMBRE_GANADOR,
    get_insert_sql,
    get_insert_estados_sql,
    get_insert_postulantes_sql,
    get_estados_values,
)
from apd_scrap.utils.logging import LoggerMixin


class DatabaseConnection(LoggerMixin):
    """
    Maneja la conexión y operaciones con la base de datos SQLite.

    Esta clase proporciona una interfaz orientada a objetos para interactuar
    con la base de datos de APD-Scrap. Implementa el protocolo de context
    manager para manejo automático de conexiones y soporta transacciones
    implícitas a través de commits.

    Attributes:
        db_path (str): Ruta al archivo de base de datos SQLite
        connection (Optional[sqlite3.Connection]): Conexión activa o None

    Example:
        >>> # Uso simple
        >>> db = DatabaseConnection("my_database.db")
        >>> db.initialize_schema()
        >>> ofertas = [{'ige': 1, 'estado': 'Publicada'}]
        >>> db.save_ofertas(ofertas)
        >>> db.close()

        >>> # Uso con context manager (recomendado)
        >>> with DatabaseConnection() as db:
        ...     db.initialize_schema()
        ...     ofertas = [{'ige': 1, 'estado': 'Publicada'}]
        ...     registros = db.save_ofertas(ofertas, distrito='MERLO')

        >>> # Consultar datos
        >>> with DatabaseConnection() as db:
        ...     total = db.get_count()
        ...     merlo_count = db.get_distrito_count('MERLO')
    """

    def __init__(self, db_path: str = "apd.db") -> None:
        """
        Inicializa una nueva conexión a la base de datos.

        Args:
            db_path: Ruta al archivo de base de datos SQLite. Si no existe,
                se creará al ejecutar initialize_schema()
                (default: "apd.db")

        Example:
            >>> # Usar path por defecto
            >>> db = DatabaseConnection()

            >>> # Usar path personalizado
            >>> db = DatabaseConnection("/path/to/database.db")

            >>> # Base de datos en memoria (útil para tests)
            >>> db = DatabaseConnection(":memory:")
        """
        self.db_path: str = db_path
        self.connection: Optional[sqlite3.Connection] = None

    def connect(self) -> sqlite3.Connection:
        """
        Establece una conexión con la base de datos.

        Este método abre una conexión SQLite y la guarda en el atributo
        `connection`. Si ya existe una conexión, la cierra antes de crear
        una nueva.

        Returns:
            sqlite3.Connection: Conexión SQLite activa y abierta

        Raises:
            sqlite3.Error: Si hay un error al abrir la base de datos

        Note:
            Es recomendable usar el context manager (`with statement`) en
            lugar de llamar a connect() y close() manualmente.

        Example:
            >>> db = DatabaseConnection()
            >>> conn = db.connect()
            >>> # Usar conn para operaciones SQL
            >>> db.close()
        """
        self.connection = sqlite3.connect(self.db_path)
        return self.connection

    def close(self) -> None:
        """
        Cierra la conexión con la base de datos.

        Este método cierra la conexión activa si existe y establece
        `self.connection` a None. Es seguro llamarlo múltiples veces
        o cuando no hay conexión activa.

        Example:
            >>> db = DatabaseConnection()
            >>> db.connect()
            >>> db.close()
            >>> db.close()  # Llamada adicional, no hay error
        """
        if self.connection:
            self.connection.close()
            self.connection = None

    def __enter__(self) -> "DatabaseConnection":
        """
        Context manager entry - establece conexión.

        Returns:
            DatabaseConnection: La instancia misma para usar en with block

        Example:
            >>> with DatabaseConnection() as db:
            ...     # db.connection ya está establecida
            ...     db.initialize_schema()
        """
        self.connect()
        return self

    def __exit__(
        self, exc_type: Optional[type], exc_val: Optional[BaseException], exc_tb: Optional[Any]
    ) -> None:
        """
        Context manager exit - cierra conexión.

        Args:
            exc_type: Tipo de excepción si ocurrió
            exc_val: Valor de excepción si ocurrió
            exc_tb: Traceback de excepción si ocurrió

        Note:
            Las excepciones no se suprimen, se propagan normalmente.
        """
        self.close()

    def initialize_schema(self) -> bool:
        """
        Inicializa el esquema de la base de datos si no existe.

        Este método ejecuta la sentencia SQL CREATE TABLE IF NOT EXISTS
        para crear la tabla 'estados' y la tabla 'ofertas' con todas las
        columnas necesarias.

        Returns:
            bool: True si el esquema se inicializó correctamente,
                False si hubo un error

        Example:
            >>> db = DatabaseConnection(":memory:")
            >>> success = db.initialize_schema()
            >>> print(f"Esquema inicializado: {success}")
            Esquema inicializado: True
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(CREATE_TABLE_ESTADOS_SQL)
            cursor.execute(CREATE_TABLE_SQL)
            cursor.execute(CREATE_TABLE_POSTULANTES_SQL)
            
            # Migración: agregar nuevos campos si no existen
            cursor.execute("PRAGMA table_info(ofertas)")
            columnas_existentes = [row[1] for row in cursor.fetchall()]
            
            migraciones = [
                ("cuil_puntero", ALTER_TABLE_ADD_CUIL_PUNTERO),
                ("cuil_ganador", ALTER_TABLE_ADD_CUIL_GANADOR),
                ("puntaje_puntero", ALTER_TABLE_ADD_PUNTAJE_PUNTERO),
                ("nombre_puntero", ALTER_TABLE_ADD_NOMBRE_PUNTERO),
                ("puntaje_ganador", ALTER_TABLE_ADD_PUNTAJE_GANADOR),
                ("nombre_ganador", ALTER_TABLE_ADD_NOMBRE_GANADOR),
            ]
            
            for nombre_columna, sql_migracion in migraciones:
                if nombre_columna not in columnas_existentes:
                    try:
                        cursor.execute(sql_migracion)
                        self.logger.info(f"Columna {nombre_columna} agregada a la tabla ofertas")
                    except sqlite3.OperationalError as e:
                        self.logger.warning(f"No se pudo agregar {nombre_columna}: {e}")
            
            conn.commit()
            self.logger.debug("Esquema de base de datos inicializado correctamente")
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error al inicializar el esquema: {e}")
            return False
        finally:
            self.close()

    def populate_estados(self) -> bool:
        """
        Puebla la tabla de estados con los valores válidos.

        Este método inserta todos los estados válidos definidos en
        ESTADOS_VALIDOS en la tabla 'estados'.

        Returns:
            bool: True si los estados se insertaron correctamente,
                False si hubo un error

        Example:
            >>> db = DatabaseConnection(":memory:")
            >>> db.initialize_schema()
            >>> success = db.populate_estados()
            >>> print(f"Estados insertados: {success}")
            Estados insertados: True
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            sql = get_insert_estados_sql()
            estados_values = get_estados_values()
            cursor.execute(sql, estados_values)
            conn.commit()
            self.logger.debug(
                f"Tabla de estados poblada con {len(estados_values)} estados válidos"
            )
            return True
        except sqlite3.Error as e:
            self.logger.error(f"Error al poblar la tabla de estados: {e}")
            return False
        finally:
            self.close()

    def save_ofertas(self, ofertas: list[dict[str, Any]], distrito: Optional[str] = None) -> int:
        """
        Guarda o actualiza una lista de ofertas en la base de datos.

        Este método inserta o actualiza ofertas en la tabla 'ofertas'
        usando INSERT OR REPLACE, lo que significa que si un registro
        con el mismo valor de 'ige' ya existe, será actualizado.

        Args:
            ofertas: Lista de diccionarios donde cada diccionario
                representa una oferta con sus campos como claves
            distrito: Nombre del distrito (opcional, solo para logging)

        Returns:
            int: Número de registros guardados/actualizados. Retorna 0
                si la lista está vacía o hubo un error

        Example:
            >>> ofertas = [
            ...     {'ige': 1, 'estado': 'Publicada', 'cargo': 'Profesor'},
            ...     {'ige': 2, 'estado': 'Desierta', 'cargo': 'Ayudante'}
            ... ]
            >>> with DatabaseConnection() as db:
            ...     db.initialize_schema()
            ...     registros = db.save_ofertas(ofertas, distrito='MERLO')
            ...     print(f"Guardados: {registros}")
            Guardados: 2
        """
        if not ofertas:
            self.logger.warning("No hay ofertas para guardar en la base de datos.")
            return 0

        try:
            conn = self.connect()
            cursor = conn.cursor()
            sql = get_insert_sql()

            for oferta in ofertas:
                valores = tuple(oferta.get(col) for col in COLUMNAS)
                cursor.execute(sql, valores)

            conn.commit()

            if distrito:
                self.logger.info(
                    f"Distrito {distrito}: {len(ofertas)} registros "
                    f"guardados/actualizados en BD."
                )
            else:
                self.logger.info(
                    f"Guardados/actualizados {len(ofertas)} registros " f"en la base de datos."
                )

            return len(ofertas)

        except sqlite3.Error as e:
            self.logger.error(f"Error al interactuar con la base de datos: {e}")
            return 0
        finally:
            self.close()

    def save_postulantes(
        self,
        postulantes: list[dict[str, Any]],
        ige: Optional[int] = None,
    ) -> int:
        """
        Guarda o actualiza una lista de postulantes en la base de datos.

        Este método inserta o actualiza postulantes en la tabla 'postulantes'
        usando INSERT OR REPLACE, lo que significa que si un registro
        con la misma combinación de ige y idpostulacion ya existe, será actualizado.

        Args:
            postulantes: Lista de diccionarios donde cada diccionario
                representa un postulante con sus campos como claves
            ige: IGE de la oferta asociada (opcional, solo para logging)

        Returns:
            int: Número de registros guardados/actualizados. Retorna 0
                si la lista está vacía o hubo un error

        Example:
            >>> postulantes = [
            ...     {'ige': 4067362, 'cuil': '20217355827', 'nombres': 'Juan Pérez'},
            ...     {'ige': 4067362, 'cuil': '20217355828', 'nombres': 'María López'}
            ... ]
            >>> with DatabaseConnection() as db:
            ...     db.initialize_schema()
            ...     registros = db.save_postulantes(postulantes, ige=4067362)
            ...     print(f"Guardados: {registros}")
            Guardados: 2
        """
        if not postulantes:
            self.logger.debug("No hay postulantes para guardar en la base de datos.")
            return 0

        try:
            conn = self.connect()
            cursor = conn.cursor()
            sql = get_insert_postulantes_sql()

            for postulante in postulantes:
                valores = tuple(postulante.get(col) for col in COLUMNAS_POSTULANTES)
                cursor.execute(sql, valores)

            conn.commit()

            if ige:
                self.logger.info(
                    f"IGE {ige}: {len(postulantes)} postulantes guardados/actualizados en BD."
                )
            else:
                self.logger.info(
                    f"Guardados/actualizados {len(postulantes)} postulantes "
                    f"en la base de datos."
                )

            return len(postulantes)

        except sqlite3.Error as e:
            self.logger.error(f"Error al guardar postulantes en la base de datos: {e}")
            return 0
        finally:
            self.close()

    def get_count(self) -> int:
        """
        Obtiene el número total de registros en la base de datos.

        Returns:
            int: Número total de registros en la tabla 'ofertas'.
                Retorna 0 si hay un error o no hay registros.

        Example:
            >>> with DatabaseConnection() as db:
            ...     db.initialize_schema()
            ...     total = db.get_count()
            ...     print(f"Total de registros: {total}")
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute("SELECT COUNT(*) FROM ofertas")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error:
            self.logger.error("Error al obtener conteo total de registros")
            return 0
        finally:
            self.close()

    def get_distrito_count(self, distrito: str) -> int:
        """
        Obtiene el número de registros por distrito.

        Args:
            distrito: Nombre del distrito (se convierte a mayúsculas)

        Returns:
            int: Número de registros para el distrito especificado.
                Retorna 0 si hay un error o no hay registros.

        Example:
            >>> with DatabaseConnection() as db:
            ...     merlo_count = db.get_distrito_count('merlo')
            ...     print(f"Registros de Merlo: {merlo_count}")
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(
                "SELECT COUNT(*) FROM ofertas WHERE descdistrito = ?", (distrito.upper(),)
            )
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error:
            self.logger.error(f"Error al obtener conteo de registros para distrito {distrito}")
            return 0
        finally:
            self.close()

    def update_cuil_puntero(self) -> int:
        """
        Actualiza los campos de puntero en la tabla ofertas.

        Este método actualiza los campos cuil_puntero, puntaje_puntero y nombre_puntero
        de la tabla ofertas con los datos del postulante designado (designado='S').
        Si no hay postulante designado, usa los datos del postulante con mayor puntaje.

        Returns:
            int: Número de ofertas actualizadas. Retorna 0 si hay error.

        Example:
            >>> db = DatabaseConnection()
            >>> db.initialize_schema()
            >>> # Supongamos que hay postulantes para algunas ofertas
            >>> actualizados = db.update_cuil_puntero()
            >>> print(f"Ofertas actualizadas: {actualizados}")
            Ofertas actualizadas: 15

        Note:
            Este método busca en la tabla postulantes y actualiza:
            1. Ofertas con postulante designado (designado='S')
            2. Ofertas sin designado pero con postulante de mayor puntaje
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            actualizados = 0

            # Primero: actualizar ofertas con postulante designado
            update_designado = """
            UPDATE ofertas
            SET cuil_puntero = (
                SELECT p.cuil
                FROM postulantes p
                WHERE p.ige = ofertas.ige AND p.designado = 'S'
                LIMIT 1
            ),
            puntaje_puntero = (
                SELECT p.puntaje
                FROM postulantes p
                WHERE p.ige = ofertas.ige AND p.designado = 'S'
                LIMIT 1
            ),
            nombre_puntero = (
                SELECT p.nombres
                FROM postulantes p
                WHERE p.ige = ofertas.ige AND p.designado = 'S'
                LIMIT 1
            )
            WHERE ige IN (
                SELECT DISTINCT ige FROM postulantes WHERE designado = 'S'
            ) AND (cuil_puntero IS NULL OR puntaje_puntero IS NULL OR nombre_puntero IS NULL);
            """
            cursor.execute(update_designado)
            designados = cursor.rowcount
            actualizados += designados

            # Segundo: actualizar ofertas sin designado (usar mayor puntaje)
            update_max_puntaje = """
            UPDATE ofertas
            SET cuil_puntero = (
                SELECT p.cuil
                FROM postulantes p
                WHERE p.ige = ofertas.ige
                ORDER BY p.puntaje DESC
                LIMIT 1
            ),
            puntaje_puntero = (
                SELECT p.puntaje
                FROM postulantes p
                WHERE p.ige = ofertas.ige
                ORDER BY p.puntaje DESC
                LIMIT 1
            ),
            nombre_puntero = (
                SELECT p.nombres
                FROM postulantes p
                WHERE p.ige = ofertas.ige
                ORDER BY p.puntaje DESC
                LIMIT 1
            )
            WHERE ige IN (
                SELECT DISTINCT ige FROM postulantes WHERE ige NOT IN (
                    SELECT DISTINCT ige FROM postulantes WHERE designado = 'S'
                )
            ) AND (cuil_puntero IS NULL OR puntaje_puntero IS NULL OR nombre_puntero IS NULL);
            """
            cursor.execute(update_max_puntaje)
            max_puntaje = cursor.rowcount
            actualizados += max_puntaje

            conn.commit()

            if actualizados > 0:
                self.logger.info(
                    f"Punteros actualizados: {designados} designados, "
                    f"{max_puntaje} por puntaje (total: {actualizados})"
                )
            else:
                self.logger.debug("No se actualizaron punteros (no hay postulantes nuevos)")

            return actualizados

        except sqlite3.Error as e:
            self.logger.error(f"Error al actualizar punteros: {e}")
            return 0
        finally:
            self.close()
