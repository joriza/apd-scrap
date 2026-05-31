"""
Script de prueba para la estructura modular de APD-Scrap.

Este script verifica que todos los componentes funcionen correctamente
después de la refactorización.
"""

import sys
from apd_scrap import Config, APDScraper, DatabaseConnection
from apd_scrap.database.schema import COLUMNAS, get_insert_sql
from apd_scrap.cli.commands import create_parser


def test_imports():
    """Verifica que todas las importaciones funcionen."""
    print("=" * 60)
    print("TEST 1: Importaciones")
    print("=" * 60)
    
    try:
        from apd_scrap.config import Config
        from apd_scrap.scrapers.apd_scraper import APDScraper
        from apd_scrap.database.connection import DatabaseConnection
        from apd_scrap.database.schema import COLUMNAS, CREATE_TABLE_SQL, get_insert_sql
        from apd_scrap.cli.commands import create_parser
        from apd_scrap.utils.ssl_adapter import CustomHttpAdapter, CIPHERS
        
        print("[OK] Todas las importaciones exitosas")
        return True
    except ImportError as e:
        print(f"[ERROR] Error de importación: {e}")
        return False


def test_config():
    """Verifica la configuración."""
    print("\n" + "=" * 60)
    print("TEST 2: Configuración")
    print("=" * 60)
    
    config = Config()
    
    print(f"[OK] API URL: {config.API_BASE_URL}")
    print(f"[OK] Timeout: {config.API_TIMEOUT}s")
    print(f"[OK] DB Path: {config.DB_PATH}")
    
    params = config.get_api_query_params('merlo', rows=10)
    print(f"[OK] Parámetros generados: {params}")
    
    filename = config.get_output_filename('merlo')
    print(f"[OK] Filename: {filename}")
    
    return True


def test_database_schema():
    """Verifica el esquema de base de datos."""
    print("\n" + "=" * 60)
    print("TEST 3: Esquema de Base de Datos")
    print("=" * 60)
    
    print(f"[OK] Total de columnas: {len(COLUMNAS)}")
    print(f"[OK] PK: {COLUMNAS[0]}")
    print(f"[OK] Últimas columnas: {', '.join(COLUMNAS[-3:])}")
    
    insert_sql = get_insert_sql()
    print(f"[OK] SQL INSERT generado correctamente")
    print(f"  Placeholders: {insert_sql.count('?')} (esperado: {len(COLUMNAS)})")
    
    return True


def test_database_operations():
    """Verifica operaciones de base de datos."""
    print("\n" + "=" * 60)
    print("TEST 4: Operaciones de Base de Datos")
    print("=" * 60)
    
    try:
        with DatabaseConnection() as db:
            # Inicializar esquema
            db.initialize_schema()
            print("[OK] Esquema inicializado")
            
            # Obtener conteo
            total = db.get_count()
            print(f"[OK] Total registros: {total}")
            
            # Obtener conteo por distrito
            merlo_count = db.get_distrito_count('merlo')
            print(f"[OK] Registros MERLO: {merlo_count}")
            
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_scraper():
    """Verifica el scraper (sin descargar datos reales)."""
    print("\n" + "=" * 60)
    print("TEST 5: Scraper")
    print("=" * 60)
    
    try:
        scraper = APDScraper()
        print("[OK] Scraper inicializado")
        
        # Obtener total (solicitud real pero pequeña)
        total = scraper.get_total_records('merlo')
        print(f"[OK] Total registros merlo: {total}")
        
        scraper.close()
        return True
    except Exception as e:
        print(f"[ERROR] Error: {e}")
        return False


def test_cli():
    """Verifica la línea de comandos."""
    print("\n" + "=" * 60)
    print("TEST 6: CLI")
    print("=" * 60)
    
    parser = create_parser()
    
    # Test default
    args = parser.parse_args([])
    print(f"[OK] Default distrito: {args.distrito}")
    
    # Test con argumento
    args = parser.parse_args(['--distrito', 'moreno'])
    print(f"[OK] Distrito especificado: {args.distrito}")
    
    return True


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("\n" + "[TEST] " * 15)
    print("APD-Scrap: Suite de Pruebas - Estructura Modular")
    print("[TEST] " * 15 + "\n")
    
    tests = [
        test_imports,
        test_config,
        test_database_schema,
        test_database_operations,
        test_scraper,
        test_cli
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test falló con excepción: {e}")
            results.append(False)
    
    # Resumen
    print("\n" + "=" * 60)
    print("RESUMEN")
    print("=" * 60)
    passed = sum(results)
    total = len(results)
    
    print(f"[OK] Pasados: {passed}/{total}")
    print(f"[ERROR] Fallidos: {total - passed}/{total}")
    
    if passed == total:
        print("\n[EXITO] Todas las pruebas pasaron exitosamente!")
        return 0
    else:
        print("\n[ERROR] Algunas pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())