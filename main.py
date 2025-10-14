import requests
import json

def fetch_and_print_data(url):
    """
    Realiza una petición GET a una URL, espera una respuesta JSON,
    y la imprime en la consola de forma legible.
    """
    try:
        # Realizar la petición GET a la URL
        response = requests.get(url)

        # Lanza un error si la petición no fue exitosa (ej. error 404, 500)
        response.raise_for_status()

        # La respuesta parece ser JSON, la convertimos a un objeto de Python
        data = response.json()

        # Imprimimos el resultado de forma ordenada y legible
        # El 'indent=4' crea el formato bonito
        # 'ensure_ascii=False' muestra correctamente acentos y caracteres especiales
        print(json.dumps(data, indent=4, ensure_ascii=False))

    except requests.exceptions.RequestException as e:
        print(f"Ocurrió un error al intentar acceder a la URL: {e}")

if __name__ == "__main__":
    target_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select?q=*%3A*&rows=2&fq=descdistrito%3Amerlo"
    fetch_and_print_data(target_url)