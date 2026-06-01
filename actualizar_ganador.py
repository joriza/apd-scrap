"""
Script para actualizar campos ganador de ofertas DESIGNADA/RENUNCIADA.

Este script actualiza los campos cuil_ganador, puntaje_ganador y nombre_ganador
de las ofertas que cumplen:
- ige > 4097270
- estado IN ('DESIGNADA', 'RENUNCIADA')
- cuil_ganador IS NULL

Para cada oferta, consulta a la API de postulantes con designado=S y rellena
los campos con los datos del postulante designado.
"""

from apd_scrap.database.connection import DatabaseConnection


def main():
    """Función principal del script."""
    print("=" * 60)
    print("Actualizando campos ganador de ofertas DESIGNADA/RENUNCIADA")
    print("=" * 60)
    print()

    try:
        db = DatabaseConnection('apd.db')
        
        # Verificar esquema
        db.initialize_schema()
        
        # Ejecutar actualización
        print("Buscando ofertas con condiciones:")
        print("  - ige > 4097270")
        print("  - estado IN ('DESIGNADA', 'RENUNCIADA')")
        print("  - cuil_ganador IS NULL")
        print()
        
        actualizados = db.update_cuil_ganador()
        
        print()
        print("=" * 60)
        print(f"✅ Ofertas actualizadas: {actualizados}")
        print("=" * 60)
        
        db.close()
        
    except KeyboardInterrupt:
        print("\n⚠️ Ejecución interrumpida por el usuario")
    except Exception as e:
        print(f"\n❌ Error: {e}")


if __name__ == "__main__":
    main()