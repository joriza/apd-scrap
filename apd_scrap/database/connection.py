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
    get_insert_sql,
    get_insert_estados_sql,
    get_insert_postulantes_sql,
    get_estados_values,
    get_create_indexes_sql,
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
        columnas necesarias, y crea los indexes de rendimiento.

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

            # Crear indexes de rendimiento
            for index_sql in get_create_indexes_sql():
                cursor.execute(index_sql)

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
            self.logger.debug(f"Tabla de estados poblada con {len(estados_values)} estados válidos")
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
        usando INSERT OR REPLACE con batch insert para mejor rendimiento.

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

            # Usar executemany para batch insert (más eficiente)
            values_list = [tuple(oferta.get(col) for col in COLUMNAS) for oferta in ofertas]
            cursor.executemany(sql, values_list)

            conn.commit()

            if distrito:
                self.logger.info(
                    f"Distrito {distrito}: {len(ofertas)} registros guardados/actualizados en BD."
                )
            else:
                self.logger.info(
                    f"Guardados/actualizados {len(ofertas)} registros en la base de datos."
                )

            return len(ofertas)

        except sqlite3.Error as e:
            self.logger.error(f"Error al interactuar con la base de datos: {e}")
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

    def save_postulantes(
        self,
        postulantes: list[dict[str, Any]],
        ige: Optional[int] = None,
    ) -> int:
        """
        Guarda o reemplaza postulantes en la base de datos.

        Este metodo inserta o reemplaza postulantes en la tabla 'postulantes'
        usando INSERT OR REPLACE con batch insert para mejor rendimiento.
        La PK es (ige, cuil), por lo que si se repite la consulta con el
        mismo IGE y CUIL, se pisan los registros.

        Args:
            postulantes: Lista de diccionarios donde cada diccionario
                representa un postulante con sus campos como claves
            ige: IGE de la oferta asociada (opcional, solo para logging)

        Returns:
            int: Numero de registros guardados/reemplazados. Retorna 0
                si la lista esta vacia o hubo un error

        Example:
            >>> postulantes = [
            ...     {'ige': 4067362, 'cuil': '20217355827', 'designado': 'N', ...},
            ...     {'ige': 4067362, 'cuil': '20217355828', 'designado': 'S', ...}
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

            # Usar executemany para batch insert (más eficiente)
            values_list = [
                tuple(postulante.get(col) for col in COLUMNAS_POSTULANTES)
                for postulante in postulantes
            ]
            cursor.executemany(sql, values_list)

            conn.commit()

            if ige:
                self.logger.info(
                    f"IGE {ige}: {len(postulantes)} postulantes guardados/reemplazados en BD."
                )
            else:
                self.logger.info(
                    f"Guardados/reemplazados {len(postulantes)} postulantes en la base de datos."
                )

            return len(postulantes)

        except sqlite3.Error as e:
            self.logger.error(f"Error al guardar postulantes en la base de datos: {e}")
            return 0
        finally:
            self.close()

    def get_ofertas_paginated(
        self,
        offset: int = 0,
        limit: int = 1000,
        distrito: Optional[str] = None,
        estado: Optional[str] = None,
    ) -> list[dict[str, Any]]:
        """
        Obtiene ofertas de forma paginada.

        Este método permite obtener grandes cantidades de registros
        en lotes paginados, reduciendo el uso de memoria.

        Args:
            offset: Número de registros a saltar (default: 0)
            limit: Número máximo de registros a retornar (default: 1000)
            distrito: Filtrar por distrito (opcional)
            estado: Filtrar por estado (opcional)

        Returns:
            list[dict[str, Any]]: Lista de ofertas

        Example:
            >>> with DatabaseConnection() as db:
            ...     db.initialize_schema()
            ...     # Obtener primeros 1000 registros
            ...     batch1 = db.get_ofertas_paginated(0, 1000)
            ...     # Obtener siguientes 1000 registros
            ...     batch2 = db.get_ofertas_paginated(1000, 1000)
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            # Construir query base
            where_clauses = []
            params = []

            if distrito:
                where_clauses.append("descdistrito = ?")
                params.append(distrito.upper())

            if estado:
                where_clauses.append("estado = ?")
                params.append(estado)

            where_sql = "".join([f" WHERE {clause}" for clause in where_clauses])
            params.extend([limit, offset])

            sql = f"SELECT * FROM ofertas{where_sql} ORDER BY ige LIMIT ? OFFSET ?"

            cursor.execute(sql, params)
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            column_names = [description[0] for description in cursor.description]
            results = [dict(zip(column_names, row)) for row in rows]

            self.logger.debug(
                f"Obtenidos {len(results)} registros (offset={offset}, limit={limit})"
            )
            return results

        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener ofertas paginadas: {e}")
            return []
        finally:
            self.close()

    def get_postulantes_paginated(
        self,
        ige: int,
        offset: int = 0,
        limit: int = 100,
    ) -> list[dict[str, Any]]:
        """
        Obtiene postulantes de un IGE de forma paginada.

        Este método permite obtener grandes cantidades de postulantes
        en lotes paginados, reduciendo el uso de memoria.

        Args:
            ige: IGE de la oferta
            offset: Número de registros a saltar (default: 0)
            limit: Número máximo de registros a retornar (default: 100)

        Returns:
            list[dict[str, Any]]: Lista de postulantes

        Example:
            >>> with DatabaseConnection() as db:
            ...     db.initialize_schema()
            ...     # Obtener primeros 100 postulantes
            ...     batch1 = db.get_postulantes_paginated(4067362, 0, 100)
            ...     # Obtener siguientes 100 postulantes
            ...     batch2 = db.get_postulantes_paginated(4067362, 100, 100)
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM postulantes WHERE ige = ? ORDER BY ige LIMIT ? OFFSET ?"
            cursor.execute(sql, (ige, limit, offset))
            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            column_names = [description[0] for description in cursor.description]
            results = [dict(zip(column_names, row)) for row in rows]

            self.logger.debug(
                f"IGE {ige}: Obtenidos {len(results)} postulantes (offset={offset}, limit={limit})"
            )
            return results

        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener postulantes paginados para IGE {ige}: {e}")
            return []
        finally:
            self.close()

    def get_ofertas_by_estado_distrito(
        self, estado: str, distrito: Optional[str] = None
    ) -> list[dict[str, Any]]:
        """
        Obtiene ofertas filtradas por estado y opcionalmente por distrito.

        Usa el índice idx_ofertas_estado_distrito para mejor rendimiento.

        Args:
            estado: Estado a filtrar (ej: 'Publicada', 'DESIGNADA')
            distrito: Filtrar por distrito (opcional)

        Returns:
            list[dict[str, Any]]: Lista de ofertas

        Example:
            >>> with DatabaseConnection() as db:
            ...     db.initialize_schema()
            ...     publicadas = db.get_ofertas_by_estado_distrito('Publicada')
            ...     designadas_merlo = db.get_ofertas_by_estado_distrito('DESIGNADA', 'MERLO')
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            if distrito:
                sql = "SELECT * FROM ofertas WHERE estado = ? AND descdistrito = ?"
                cursor.execute(sql, (estado, distrito.upper()))
            else:
                sql = "SELECT * FROM ofertas WHERE estado = ?"
                cursor.execute(sql, (estado,))

            rows = cursor.fetchall()

            # Convertir a lista de diccionarios
            column_names = [description[0] for description in cursor.description]
            results = [dict(zip(column_names, row)) for row in rows]

            self.logger.debug(
                f"Obtenidos {len(results)} ofertas con estado '{estado}'"
                + (f" y distrito '{distrito}'" if distrito else "")
            )
            return results

        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener ofertas por estado/distrito: {e}")
            return []
        finally:
            self.close()

    def get_ganador_postulante(self, ige: int) -> Optional[dict[str, Any]]:
        """
        Obtiene el postulante designado de una oferta.

        Args:
            ige: IGE de la oferta

        Returns:
            Optional[dict[str, Any]]: Postulante designado o None si no existe

        Example:
            >>> with DatabaseConnection() as db:
            ...     ganador = db.get_ganador_postulante(4067362)
            ...     if ganador:
            ...         print(f"Ganador: {ganador['nombres']}")
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()

            sql = "SELECT * FROM postulantes WHERE ige = ? AND designado = 'S'"
            cursor.execute(sql, (ige,))
            row = cursor.fetchone()

            if row:
                column_names = [description[0] for description in cursor.description]
                result = dict(zip(column_names, row))
                self.logger.debug(f"Ganador encontrado para IGE {ige}")
                return result
            else:
                self.logger.debug(f"No hay ganador para IGE {ige}")
                return None

        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener ganador para IGE {ige}: {e}")
            return None
        finally:
            self.close()

    # Métodos para exportación a Excel
    
    def get_count(self, table_name: str = "ofertas") -> int:
        """
        Obtiene el número total de registros en una tabla específica.
        
        Args:
            table_name: Nombre de la tabla (default: "ofertas")
            
        Returns:
            int: Número total de registros en la tabla especificada
            
        Example:
            >>> with DatabaseConnection() as db:
            ...     total_ofertas = db.get_count("ofertas")
            ...     total_postulantes = db.get_count("postulantes")
        """
        try:
            conn = self.connect()
            cursor = conn.cursor()
            cursor.execute(f"SELECT COUNT(*) FROM {table_name}")
            result = cursor.fetchone()
            return result[0] if result else 0
        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener conteo de tabla {table_name}: {e}")
            return 0
        finally:
            self.close()
    
    def get_all_ofertas_paginated(self, offset: int = 0, limit: int = None) -> list[dict[str, Any]]:
        """
        Obtiene todas las ofertas con paginación para exportación.
        
        Args:
            offset: Número de registros a saltar (default: 0)
            limit: Límite de registros (None para todos)
            
        Returns:
            list[dict[str, Any]]: Lista de ofertas
            
        Example:
            >>> with DatabaseConnection() as db:
            ...     # Obtener primeros 10000 registros
            ...     batch = db.get_all_ofertas_paginated(0, 10000)
        """
        if limit is None:
            # Obtener todos los registros sin límite
            sql = "SELECT * FROM ofertas ORDER BY ige"
        else:
            sql = "SELECT * FROM ofertas ORDER BY ige LIMIT ? OFFSET ?"
            
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if limit is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, (limit, offset))
                
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            column_names = [description[0] for description in cursor.description]
            results = [dict(zip(column_names, row)) for row in rows]
            
            self.logger.debug(f"Obtenidos {len(results)} ofertas para exportación")
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener ofertas para exportación: {e}")
            return []
        finally:
            self.close()
    
    def get_all_postulantes_paginated(self, offset: int = 0, limit: int = None) -> list[dict[str, Any]]:
        """
        Obtiene todos los postulantes con paginación para exportación.
        
        Args:
            offset: Número de registros a saltar (default: 0)
            limit: Límite de registros (None para todos)
            
        Returns:
            list[dict[str, Any]]: Lista de postulantes
            
        Example:
            >>> with DatabaseConnection() as db:
            ...     # Obtener primeros 10000 registros
            ...     batch = db.get_all_postulantes_paginated(0, 10000)
        """
        if limit is None:
            # Obtener todos los registros sin límite
            sql = "SELECT * FROM postulantes ORDER BY ige, cuil"
        else:
            sql = "SELECT * FROM postulantes ORDER BY ige, cuil LIMIT ? OFFSET ?"
            
        try:
            conn = self.connect()
            cursor = conn.cursor()
            
            if limit is None:
                cursor.execute(sql)
            else:
                cursor.execute(sql, (limit, offset))
                
            rows = cursor.fetchall()
            
            # Convertir a lista de diccionarios
            column_names = [description[0] for description in cursor.description]
            results = [dict(zip(column_names, row)) for row in rows]
            
            self.logger.debug(f"Obtenidos {len(results)} postulantes para exportación")
            return results
            
        except sqlite3.Error as e:
            self.logger.error(f"Error al obtener postulantes para exportación: {e}")
            return []
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
