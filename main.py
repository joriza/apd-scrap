import json
import requests
from urllib.parse import urlencode
from requests.adapters import HTTPAdapter

# urllib3 moved create_urllib3_context in recent versions.
# This try/except block handles the import for different versions.
try:
    from requests.packages.urllib3.util.ssl_ import create_urllib3_context
except ImportError:
    from urllib3.util.ssl_ import create_urllib3_context

# --- Start of SSL/TLS Handshake Fix ---
# The error 'SSLV3_ALERT_HANDSHAKE_FAILURE' indicates that the client (requests)
# and the server could not agree on a secure connection protocol (cipher suite).
# This happens because the server likely requires a specific configuration that
# Python's default security settings don't provide out of the box.
#
# The custom adapter below tells 'requests' to offer a broader, more compatible
# set of ciphers, allowing the handshake to succeed. This explains why the
# original script used Playwright, as a full browser engine has a much more
# advanced and flexible networking stack for handling such server-side quirks.

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


def get_api_data(base_url, params):
    """
    Obtiene los datos de la API usando una solicitud HTTP directa con la librería requests.
    Usa un adaptador custom para solucionar problemas de negociación SSL/TLS.
    Retorna los datos como un diccionario de Python o None si falla.
    """
    request_params = params.copy()
    request_params['wt'] = 'json'
    
    full_url = f"{base_url}?{urlencode(request_params)}"

    # Se crea una sesión y se le monta el adaptador custom para la URL base.
    session = requests.Session()
    session.mount(base_url, CustomHttpAdapter())

    try:
        print(f"Obteniendo datos desde: {full_url}")
        
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        
        response = session.get(base_url, params=request_params, timeout=30, headers=headers)
        response.raise_for_status()
        
        return response.json()

    except requests.exceptions.SSLError as e:
        print(f"Ocurrió un error de SSL irrecuperable: {e}")
        return None
    except requests.exceptions.Timeout:
        print("Error: La solicitud tardó demasiado en responder (timeout).")
        return None
    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error en la solicitud HTTP: {e}")
        return None
    except json.JSONDecodeError:
        print("Error: La respuesta recibida no es un JSON válido.")
        return None
    except Exception as e:
        print(f"Ocurrió un error inesperado: {e}")
        return None

if __name__ == "__main__":
    base_api_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
    query_params = {
        'q': '*:*',
        'fq': 'descdistrito:merlo'
    }

    # --- Paso 1: Obtener el número total de registros ---
    print("--- Paso 1: Obteniendo el número total de registros ---")
    initial_params = query_params.copy()
    initial_params['rows'] = 1  # Solo necesitamos 1 registro para obtener el total

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
        # Si no se encontraron registros, el resultado final es la respuesta inicial (que puede estar vacía)
        api_data = initial_data

    # --- Paso 3: Guardar los datos finales ---
    if api_data:
        output_filename = "output.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            json.dump(api_data, f, ensure_ascii=False, indent=4)
        
        num_docs = len(api_data.get("response", {}).get("docs", []))
        print(f"\n¡Éxito! Los datos se han guardado en '{output_filename}'")
        print(f"Se procesaron y guardaron {num_docs} de {total_records} registros.")
    else:
        print("\nNo se pudieron obtener los datos finales de la API.")
