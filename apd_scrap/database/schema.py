"""
Definición del esquema de base de datos.

Este módulo contiene todas las definiciones relacionadas con el esquema
de la base de datos de APD-Scrap.
"""


# Lista de columnas de la tabla ofertas
COLUMNAS: list[str] = [
    "ige",
    "estado",
    "tipooferta",
    "jornada",
    "miercoles",
    "martes",
    "acargodireccion",
    "cuilautor",
    "supl_hasta",
    "turno",
    "idoferta",
    "sabado",
    "id",
    "iddetalle",
    "cargo",
    "tomaposesion",
    "supl_revista",
    "domiciliodesempeno",
    "reemp_apeynom",
    "numdistrito",
    "areaincumbencia",
    "finoferta",
    "observaciones",
    "cupof",
    "tipooferta_id",
    "supl_desde",
    "reemp_cuil",
    "escuela",
    "iniciooferta",
    "hsmodulos",
    "cursodivision",
    "idsuna",
    "descnivelmodalidad",
    "lunes",
    "infectocontagiosa",
    "reemp_motivo",
    "descdistrito",
    "jueves",
    "nivelmodalidad",
    "viernes",
    "descripcionarea",
    "descripcioncargo",
    "ult_movimiento",
    "_version_",
    "timestamp",
]

# Estados válidos para las ofertas
ESTADOS_VALIDOS: list[str] = [
    "Anulada",
    "Desierta",
    "DESIGNADA",
    "RENUNCIADA",
    "Finalizada",
    "Publicada",
    "Cerrada",
]

# SQL para crear la tabla de estados
CREATE_TABLE_ESTADOS_SQL: str = """
CREATE TABLE IF NOT EXISTS estados (
    estado TEXT PRIMARY KEY
);
"""

# SQL para crear la tabla de ofertas
CREATE_TABLE_SQL: str = """
CREATE TABLE IF NOT EXISTS ofertas (
    ige INTEGER PRIMARY KEY,
    estado TEXT,
    tipooferta TEXT,
    jornada TEXT,
    miercoles TEXT,
    martes TEXT,
    acargodireccion TEXT,
    cuilautor TEXT,
    supl_hasta TEXT,
    turno TEXT,
    idoferta INTEGER,
    sabado TEXT,
    id TEXT,
    iddetalle INTEGER,
    cargo TEXT,
    tomaposesion TEXT,
    supl_revista TEXT,
    domiciliodesempeno TEXT,
    reemp_apeynom TEXT,
    numdistrito INTEGER,
    areaincumbencia TEXT,
    finoferta TEXT,
    observaciones TEXT,
    cupof INTEGER,
    tipooferta_id INTEGER,
    supl_desde TEXT,
    reemp_cuil TEXT,
    escuela TEXT,
    iniciooferta TEXT,
    hsmodulos INTEGER,
    cursodivision TEXT,
    idsuna INTEGER,
    descnivelmodalidad TEXT,
    lunes TEXT,
    infectocontagiosa BOOLEAN,
    reemp_motivo TEXT,
    descdistrito TEXT,
    jueves TEXT,
    nivelmodalidad TEXT,
    viernes TEXT,
    descripcionarea TEXT,
    descripcioncargo TEXT,
    ult_movimiento TEXT,
    _version_ INTEGER,
    timestamp TEXT,
    FOREIGN KEY (estado) REFERENCES estados(estado)
);
"""


def get_insert_sql() -> str:
    """
    Genera la sentencia SQL para insertar/actualizar ofertas.

    Esta función genera dinámicamente la sentencia INSERT OR REPLACE
    utilizando todas las columnas definidas en COLUMNAS con el
    número apropiado de placeholders '?'.

    Returns:
        str: Sentencia SQL preparada con placeholders

    Example:
        >>> sql = get_insert_sql()
        >>> print(sql)
        INSERT OR REPLACE INTO ofertas (ige, estado, ...) VALUES (?, ?, ...)
    """
    placeholders: str = ", ".join(["?"] * len(COLUMNAS))
    columns: str = ", ".join(COLUMNAS)
    return f"INSERT OR REPLACE INTO ofertas ({columns}) VALUES ({placeholders})"


def get_insert_estados_sql() -> str:
    """
    Genera la sentencia SQL para insertar estados válidos.

    Returns:
        str: Sentencia SQL para insertar estados válidos

    Example:
        >>> sql = get_insert_estados_sql()
        >>> print(sql)
        INSERT OR REPLACE INTO estados (estado) VALUES (?), (?), ...
    """
    placeholders: str = ", ".join(["(?)"] * len(ESTADOS_VALIDOS))
    return f"INSERT OR REPLACE INTO estados (estado) VALUES {placeholders}"


def get_estados_values() -> list[str]:
    """
    Obtiene la lista de valores de estados válidos.

    Returns:
        list[str]: Lista de estados válidos

    Example:
        >>> estados = get_estados_values()
        >>> print(estados)
        ['Anulada', 'Desierta', 'DESIGNADA', ...]
    """
    return ESTADOS_VALIDOS[:]
