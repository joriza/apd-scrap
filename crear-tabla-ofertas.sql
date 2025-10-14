CREATE TABLE IF NOT EXISTS ofertas (
    ige INTEGER PRIMARY KEY, -- Campo clave e índice
    estado TEXT,
    tipooferta TEXT,
    jornada TEXT,
    miercoles TEXT,
    martes TEXT,
    acargodireccion TEXT,
    cuilautor TEXT,
    supl_hasta TEXT, -- Se usa TEXT para almacenar el formato de fecha/hora ISO
    turno TEXT,
    idoferta INTEGER,
    sabado TEXT,
    id TEXT,
    iddetalle INTEGER,
    cargo TEXT,
    tomaposesion TEXT, -- Se usa TEXT para almacenar el formato de fecha/hora ISO
    supl_revista TEXT,
    domiciliodesempeno TEXT,
    reemp_apeynom TEXT,
    numdistrito INTEGER,
    areaincumbencia TEXT,
    finoferta TEXT, -- Se usa TEXT para almacenar el formato de fecha/hora ISO
    observaciones TEXT,
    cupof INTEGER,
    tipooferta_id INTEGER,
    supl_desde TEXT, -- Se usa TEXT para almacenar el formato de fecha/hora ISO
    reemp_cuil TEXT,
    escuela TEXT,
    iniciooferta TEXT, -- Se usa TEXT para almacenar el formato de fecha/hora ISO
    hsmodulos INTEGER,
    cursodivision TEXT,
    idsuna INTEGER,
    descnivelmodalidad TEXT,
    lunes TEXT,
    infectocontagiosa BOOLEAN, -- Se almacena como 0 o 1 en SQLite
    reemp_motivo TEXT,
    descdistrito TEXT,
    jueves TEXT,
    nivelmodalidad TEXT,
    viernes TEXT,
    descripcionarea TEXT,
    descripcioncargo TEXT,
    ult_movimiento TEXT, -- Se usa TEXT para almacenar el formato de fecha/hora ISO
    _version_ INTEGER,
    timestamp TEXT -- Se usa TEXT para almacenar el formato de fecha/hora ISO
);