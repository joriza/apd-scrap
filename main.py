import requests
import json
# Importar InsecureRequestWarning para suprimir el aviso
from requests.packages.urllib3.exceptions import InsecureRequestWarning

# Suprimir el aviso de seguridad al usar verify=False
requests.packages.urllib3.disable_warnings(InsecureRequestWarning)

def fetch_and_print_data(url):
    """
    Realiza una petición GET a una URL, esperando una respuesta JSON.
    Deshabilita la verificación SSL para evitar el error de handshake.
    """
    try:
        # Realizar la petición GET a la URL, DESACTIVANDO la verificación SSL.
        # Esto ignora el error de handshake y permite la conexión.
        response = requests.get(url, verify=False) 

        # Lanza un error si la petición no fue exitosa (ej. error 404, 500)
        # NOTA: El error de SSL/Handshake ocurre ANTES de esta línea.
        response.raise_for_status()

        # La respuesta es JSON, la convertimos a un objeto de Python
        data = response.json()

        # Imprimimos el resultado de forma ordenada y legible
        print(json.dumps(data, indent=4, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error al intentar acceder a la URL: {e}")

if __name__ == "__main__":
    target_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select?q=*%3A*&rows=2&fq=descdistrito%3Amerlo"
    fetch_and_print_data(target_url)
    