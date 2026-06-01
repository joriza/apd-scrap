"""
Script para actualizar tabla postulantes de ofertas.

Este script consulta a la API de postulantes para cada oferta con ige >= IGE_MINIMO
y guarda/reemplaza los datos en la tabla postulantes.

La PK es (ige, cuil), por lo que si se repite la consulta con el mismo IGE y CUIL,
se pisan los registros (INSERT OR REPLACE).
"""

import argparse
from typing import Any

from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.database.connection import DatabaseConnection

# IGE mínimo desde el cual comenzar (puede cambiarse con argumento)
IGE_MINIMO = 4097270


def actualizar_postulantes(ige_minimo: int) -> dict[str, Any]:
    """
    Actualiza tabla postulantes para ofertas con ige >= IGE_MINIMO.
    
    Args:
        ige_minimo: IGE mínimo desde el cual comenzar
    
    Returns:
        dict: Estadísticas de la actualización
    """
    stats = {
        "ofertas_procesadas": 0,
        "postulantes_guardados": 0,
        "errores": 0
    }
    
    try:
        # Obtener ofertas con ige >= IGE_MINIMO
        db = DatabaseConnection('apd.db')
        db.initialize_schema()
        
        conn = db.connect()
        cursor = conn.cursor()
        
        cursor.execute("""
            SELECT ige, descdistrito, estado 
            FROM ofertas 
            WHERE ige >= ?
            ORDER BY ige
        """, (ige_minimo,))
        
        ofertas = cursor.fetchall()
        total_ofertas = len(ofertas)
        
        conn.close()
        
        if not ofertas:
            print(f"No hay ofertas con ige >= {ige_minimo}")
            return stats
        
        print(f"Ofertas a procesar: {total_ofertas} (ige >= {ige_minimo})")
        print()
        
        scraper = APDScraper()
        
        for i, (ige, distrito, estado) in enumerate(ofertas, 1):
            try:
                print(f"[{i}/{total_ofertas}] IGE {ige} ({distrito} - {estado})", end=" ... ")
                
                # Consultar API de postulantes
                data = scraper.fetch_postulantes(ige)
                
                if data:
                    docs = data.get('response', {}).get('docs', [])
                    
                    if docs:
                        # Guardar/reemplazar postulantes
                        registros = db.save_postulantes(docs, ige=ige)
                        stats["ofertas_procesadas"] += 1
                        stats["postulantes_guardados"] += registros
                        print(f"{registros} postulantes")
                    else:
                        print("sin postulantes")
                else:
                    print("error en API")
                    stats["errores"] += 1
                    
            except Exception as e:
                print(f"ERROR: {e}")
                stats["errores"] += 1
                continue
        
        scraper.close()
        db.close()
        
    except KeyboardInterrupt:
        print("\nEjecucion interrumpida por el usuario")
    except Exception as e:
        print(f"\nERROR: {e}")
        stats["errores"] += 1
    
    return stats


def main():
    """Función principal del script."""
    parser = argparse.ArgumentParser(
        description="Actualizar tabla postulantes de ofertas"
    )
    parser.add_argument(
        "--ige-minimo",
        type=int,
        default=IGE_MINIMO,
        help=f"IGE minimo desde el cual comenzar (defecto: {IGE_MINIMO})"
    )
    
    args = parser.parse_args()
    
    print("=" * 60)
    print("Actualizando tabla postulantes")
    print("=" * 60)
    print(f"IGE minimo: {args.ige_minimo}")
    print()
    
    stats = actualizar_postulantes(args.ige_minimo)
    
    print()
    print("=" * 60)
    print("Estadisticas:")
    print(f"  Ofertas procesadas: {stats['ofertas_procesadas']}")
    print(f"  Postulantes guardados: {stats['postulantes_guardados']}")
    print(f"  Errores: {stats['errores']}")
    print("=" * 60)


if __name__ == "__main__":
    main()