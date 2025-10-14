import json
import requests
import argparse
import sqlite3
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter

# urllib3 moved create_urllib3_context in recent versions.
# This try/except block handles the import for different versions.
try:
    from requests.packages.urllib3.util.ssl_ import create_urllib3_context
except ImportError:
    from urllib3.util.ssl_ import create_urllib3_context

# --- Start of SSL/TLS Handshake Fix ---
CIPHERS = (
    'ECDH+AESGCM:DH+AESGCM:ECDH+AES256:DH+AES256:ECDH+AES128:DH+AES:ECDH+HIGH:'
    'DH+HIGH:ECDH+3DES:DH+3DES:RSA+AESGCM:RSA+AES:RSA+HIGH:RSA+3DES:!aNULL:'
    '!eNULL:!MD5'
)

class CustomHttpAdapter(HTTPAdapter):
    """A custom HTTP adapter that forces a specific cipher suite."""
    def init_poolmanager(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(CustomHttpAdapter, self).init_poolmanager(*args, **kwargs)

    def proxy_manager_for(self, *args, **kwargs):
        context = create_urllib3_context(ciphers=CIPHERS)
        kwargs['ssl_context'] = context
        return super(CustomHttpAdapter, self).proxy_manager_for(*args, **kwargs)
# --- End of SSL/TLS Handshake Fix ---

# --- Database Section ---
# Definición de la lista de columnas para la tabla de ofertas
columnas = [
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
    """
    Guarda o actualiza una lista de ofertas en la base de datos.
    """
    conn = None
    try:
        conn = sqlite3.connect('apd.db')
        cursor = conn.cursor()

        for oferta in ofertas:
            # Usar INSERT OR REPLACE para insertar o actualizar basado en la clave primaria 'ige'
            placeholders = ', '.join(['?'] * len(columnas))
            sql = f"INSERT OR REPLACE INTO ofertas ({', '.join(columnas)}) VALUES ({placeholders})"
            
            # Se crea una tupla de valores en el orden correcto de las columnas
            valores = tuple(oferta.get(col) for col in columnas)
            
            cursor.execute(sql, valores)

        conn.commit()
        print(f"\nSe han guardado/actualizado {len(ofertas)} registros en la base de datos 'apd.db'.")

    except sqlite3.Error as e:
        print(f"\nError al interactuar con la base de datos: {e}")
    finally:
        if conn:
            conn.close()
# --- End of Database Section ---


def get_api_data(base_url, params):
    """
    Obtiene los datos de la API usando una solicitud HTTP directa con la librería requests.
    Usa un adaptador custom para solucionar problemas de negociación SSL/TLS y decodifica
    manualmente la respuesta para corregir errores de caracteres.
    Retorna los datos como un diccionario de Python o None si falla.
    """
    request_params = params.copy()
    request_params['wt'] = 'json'
    
    full_url = f"{base_url}?{urlencode(request_params)}"

    session = requests.Session()
    session.mount(base_url, CustomHttpAdapter())

    try:
        print(f"Obteniendo datos desde: {full_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = session.get(base_url, params=request_params, timeout=30, headers=headers)
        response.raise_for_status()
        
        # --- Inicio de la corrección de codificación ---
        try:
            # 1. Intenta con el método estándar .json(), que es el más rápido.
            return response.json()
        except json.JSONDecodeError:
            # 2. Si falla, es un problema de codificación. Confiamos en el análisis
            #    de la librería 'chardet' (usado en response.apparent_encoding)
            #    para obtener la codificación correcta y decodificar manualmente.
            encoding = response.apparent_encoding
            print(f"Advertencia: Falla en decodificación JSON. Reintentando con la codificación detectada: {encoding}")
            decoded_content = response.content.decode(encoding)
            return json.loads(decoded_content)
        # --- Fin de la corrección de codificación ---

    except requests.exceptions.SSLError as e:
        print(f"Ocurrió un error de SSL irrecuperable: {e}")
        return None
    except requests.exceptions.Timeout:
        print("Error: La solicitud tardó demasiado en responder (timeout).")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error en la solicitud HTTP: {e}")
        return None
    except (json.JSONDecodeError, UnicodeDecodeError) as e:
        print(f"Error final de decodificación: La respuesta del servidor no parece ser un JSON válido. Error: {e}")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Descarga de ofertas de APD para un distrito específico.")
    parser.add_argument(
        '--distrito',
        type=str,
        default='merlo',
        help='El distrito para el cual descargar las ofertas (ej: merlo, moron, laplata). Por defecto es "merlo".'
    )
    args = parser.parse_args()
    distrito = args.distrito
    print(f"Distrito seleccionado: {distrito.upper()}\n")

    base_api_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
    query_params = {
        'q': '*:*',
        'fq': f'descdistrito:{distrito}'
    }

    # --- Paso 1: Obtener el número total de registros ---
    print("--- Paso 1: Obteniendo el número total de registros ---")
    initial_params = query_params.copy()
    initial_params['rows'] = 1

    initial_data = get_api_data(base_api_url, initial_params)
    total_records = 0
    api_data = None

    if initial_data and 'response' in initial_data and 'numFound' in initial_data['response']:
        total_records = initial_data['response']['numFound']
        print(f"Se encontraron {total_records} registros en total.")
    else:
        print("No se pudo obtener el número total de registros. Abortando.")

    # --- Paso 2: Obtener todos los registros si se encontró el total ---
    if total_records > 0:
        print(f"\n--- Paso 2: Obteniendo los {total_records} registros ---")
        full_params = query_params.copy()
        full_params['rows'] = total_records
        api_data = get_api_data(base_api_url, full_params)
    else:
        api_data = initial_data

    # --- Paso 3: Guardar los datos finales ---
    if api_data:
        # Guardar en archivo JSON
        output_filename = f"output_{distrito}.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(api_data, f, ensure_ascii=False, indent=4)
        
        num_docs = len(api_data.get("response", {}).get("docs", []))
        print(f"\n¡Éxito! Los datos se han guardado en '{output_filename}'")
        print(f"Se procesaron y guardaron {num_docs} de {total_records} registros en el archivo.")

        # Guardar en Base de Datos
        ofertas_docs = api_data.get('response', {}).get('docs', [])
        if ofertas_docs:
            guardar_ofertas_en_db(ofertas_docs)
        else:
            print(f"No se encontraron ofertas en la respuesta para guardar en la base de datos.")

    else:
        print("\nNo se pudieron obtener los datos finales de la API.")
