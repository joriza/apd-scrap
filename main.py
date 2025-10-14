import json
import requests
import argparse
import sqlite3
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter

try:
    from requests.packages.urllib3.util.ssl_ import create_urllib3_context
except ImportError:
    from urllib3.util.ssl_ import create_urllib3_context

# --- Start of SSL/TLS Handshake Fix ---
# Required to connect to the server, which uses a specific cipher suite.
CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

class CustomHttpAdapter(HTTPAdapter):
    """Custom HTTP adapter to force a specific cipher suite."""
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(CustomHttpAdapter, self).init_poolmanager(*args, **kwargs)

# --- Database Section ---
COLUMNAS = [
    'ige', 'estado', 'tipooferta', 'jornada', 'miercoles', 'martes',
    'acargodireccion', 'cuilautor', 'supl_hasta', 'turno', 'idoferta',
    'sabado', 'id', 'iddetalle', 'cargo', 'tomaposesion', 'supl_revista',
    'domiciliodesempeno', 'reemp_apeynom', 'numdistrito', 'areaincumbencia',
    'finoferta', 'observaciones', 'cupof', 'tipooferta_id', 'supl_desde',
    'reemp_cuil', 'escuela', 'iniciooferta', 'hsmodulos', 'cursodivision',
    'idsuna', 'descnivelmodalidad', 'lunes', 'infectocontagiosa',
    'reemp_motivo', 'descdistrito', 'jueves', 'nivelmodalidad', 'viernes',
    'descripcionarea', 'descripcioncargo', 'ult_movimiento', '_version_',
    'timestamp'
]

def guardar_ofertas_en_db(ofertas):
    """Guarda o actualiza una lista de ofertas en la base de datos."""
    if not ofertas:
        print("No hay ofertas para guardar en la base de datos.")
        return
    try:
        with sqlite3.connect('apd.db') as conn:
            cursor = conn.cursor()
            placeholders = ', '.join(['?'] * len(COLUMNAS))
            sql = f"INSERT OR REPLACE INTO ofertas ({', '.join(COLUMNAS)}) VALUES ({placeholders})"
            
            for oferta in ofertas:
                valores = tuple(oferta.get(col) for col in COLUMNAS)
                cursor.execute(sql, valores)
            
            conn.commit()
            print(f"\nSe han guardado/actualizado {len(ofertas)} registros en 'apd.db'.")
    except sqlite3.Error as e:
        print(f"\nError al interactuar con la base de datos: {e}")

def get_api_data(session, base_url, params):
    """Obtiene datos de la API y maneja errores y decodificación."""
    try:
        response = session.get(base_url, params=params, timeout=60)
        response.raise_for_status()
        try:
            return response.json()
        except json.JSONDecodeError:
            # Fallback para problemas de codificación
            return json.loads(response.content.decode(response.apparent_encoding))
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error en la solicitud HTTP: {e}")
    except json.JSONDecodeError as e:
        print(f"Error de decodificación: La respuesta no es un JSON válido. Error: {e}")
    return None

def main():
    parser = argparse.ArgumentParser(description="Descarga de ofertas de APD para un distrito.")
    parser.add_argument('--distrito', type=str, default='merlo', help='Distrito para descargar ofertas.')
    args = parser.parse_args()
    distrito = args.distrito.upper()
    print(f"Distrito seleccionado: {distrito}\n")

    base_api_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
    query_params = {'q': '*:*', 'fq': f'descdistrito:{distrito}', 'wt': 'json'}

    session = requests.Session()
    session.mount(base_api_url, CustomHttpAdapter())

    # Paso 1: Obtener el número total de registros
    initial_data = get_api_data(session, base_api_url, {**query_params, 'rows': 1})
    if not initial_data or 'response' not in initial_data:
        print("No se pudo obtener el número total de registros. Abortando.")
        return

    total_records = initial_data['response'].get('numFound', 0)
    if total_records == 0:
        print("No se encontraron registros para el distrito.")
        return
        
    print(f"Se encontraron {total_records} registros. Obteniendo todos...")

    # Paso 2: Obtener todos los registros
    api_data = get_api_data(session, base_api_url, {**query_params, 'rows': total_records})
    if not api_data:
        print("\nNo se pudieron obtener los datos finales de la API.")
        return

    # Paso 3: Guardar los datos
    output_filename = f"output_{distrito.lower()}.json"
    with open(output_filename, "w", encoding="utf-8") as f:
        json.dump(api_data, f, ensure_ascii=False, indent=4)
    
    num_docs = len(api_data.get("response", {}).get("docs", []))
    print(f"\n¡Éxito! {num_docs} registros guardados en '{output_filename}'.")

    ofertas_docs = api_data.get('response', {}).get('docs', [])
    guardar_ofertas_en_db(ofertas_docs)

if __name__ == "__main__":
    main()
