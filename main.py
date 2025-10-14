import json
from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
from urllib.parse import urlencode

def get_api_data(base_url, params):
    """
    Usa Playwright en modo oculto para obtener los datos de la API,
    evitando las restricciones del servidor y problemas de la consola.
    Retorna los datos como un diccionario de Python o None si falla.
    """
    full_url = f"{base_url}?{urlencode(params)}"
    with sync_playwright() as p:
        # Volvemos a modo headless (oculto) para que no se abra ninguna ventana.
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        try:
            print(f"Obteniendo datos desde: {full_url}")
            page.goto(full_url, timeout=60000, wait_until="networkidle")
            json_text = page.locator('pre').inner_text()
            browser.close()
            return json.loads(json_text)
        except PlaywrightTimeoutError:
            print("Error: La página tardó demasiado en cargar (timeout).")
            browser.close()
            return None
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")
            browser.close()
            return None

if __name__ == "__main__":
    base_api_url = "https://servicios3.abc.gob.ar/valoracion.docente/api/apd.oferta.encabezado/select"
    query_params = {
        'q': '*:*',
        'rows': 50,  # Puedes ajustar la cantidad de registros aquí
        'fq': 'descdistrito:merlo'
    }

    api_data = get_api_data(base_api_url, query_params)

    if api_data:
        output_filename = "output.json"
        with open(output_filename, "w", encoding="utf-8") as f:
            # Usamos json.dump para guardar el diccionario directamente con formato
            json.dump(api_data, f, ensure_ascii=False, indent=4)
        print(f"¡Éxito! Los datos se han guardado en '{output_filename}'")
        num_docs = len(api_data.get("response", {}).get("docs", []))
        print(f"Se procesaron {num_docs} registros.")
    else:
        print("No se pudieron obtener los datos de la API.")