"""
Script de prueba para el sistema de logging.

Este script verifica que el logging funcione correctamente
en todos los niveles y componentes.
"""

import sys
import os
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.insert(0, str(Path(__file__).parent))

from apd_scrap.utils.logging import setup_logging, get_logger, LoggerMixin


def test_basic_logging():
    """Prueba el logging básico."""
    print("=" * 60)
    print("TEST 1: Logging Básico")
    print("=" * 60)

    logger = setup_logging(log_file="test_logging.log", console_output=True)

    logger.debug("Mensaje DEBUG")
    logger.info("Mensaje INFO")
    logger.warning("Mensaje WARNING")
    logger.error("Mensaje ERROR")
    logger.critical("Mensaje CRITICAL")

    print("[OK] Logging básico funcionando")
    return True


def test_logger_levels():
    """Prueba diferentes niveles de logging."""
    print("\n" + "=" * 60)
    print("TEST 2: Niveles de Logging")
    print("=" * 60)

    import logging

    # Logger con nivel INFO (DEBUG no debería aparecer)
    logger_info = setup_logging(
        name="test_info", log_level=logging.INFO, log_file="test_logging.log", console_output=False
    )
    logger_info.debug("Este mensaje DEBUG no debería aparecer")
    logger_info.info("Este mensaje INFO debería aparecer")

    # Logger con nivel DEBUG (todo debería aparecer)
    logger_debug = setup_logging(
        name="test_debug",
        log_level=logging.DEBUG,
        log_file="test_logging.log",
        console_output=False,
    )
    logger_debug.debug("Este mensaje DEBUG debería aparecer")
    logger_debug.info("Este mensaje INFO debería aparecer")

    print("[OK] Niveles de logging funcionando")
    return True


def test_get_logger():
    """Prueba obtener un logger existente."""
    print("\n" + "=" * 60)
    print("TEST 3: Obtener Logger Existente")
    print("=" * 60)

    logger1 = get_logger("test_module")
    logger2 = get_logger("test_module")

    if logger1 is logger2:
        print("[OK] Mismo logger devuelto")
    else:
        print("[ERROR] Loggers diferentes")
        return False

    return True


def test_logger_mixin():
    """Prueba el mixin de logging."""
    print("\n" + "=" * 60)
    print("TEST 4: LoggerMixin")
    print("=" * 60)

    class MiClase(LoggerMixin):
        """Clase de prueba con LoggerMixin."""

        def metodo(self):
            """Método que usa el logger."""
            self.logger.info("Método ejecutado")
            self.logger.debug("Información de debug")

    obj = MiClase()
    obj.metodo()

    print("[OK] LoggerMixin funcionando")
    return True


def test_file_logging():
    """Prueba que los logs se guarden en archivo."""
    print("\n" + "=" * 60)
    print("TEST 5: Logging a Archivo")
    print("=" * 60)

    log_file = "test_output.log"
    logger = setup_logging(name="test_file", log_file=log_file, console_output=False)

    test_message = "Mensaje de prueba para archivo"
    logger.info(test_message)

    # Verificar que el archivo se creó y contiene el mensaje
    if Path(log_file).exists():
        with open(log_file, "r", encoding="utf-8") as f:
            content = f.read()
            if test_message in content:
                print(f"[OK] Mensaje encontrado en {log_file}")
                return True
            else:
                print(f"[ERROR] Mensaje no encontrado en {log_file}")
                return False
    else:
        print(f"[ERROR] Archivo {log_file} no creado")
        return False


def test_console_logging():
    """Prueba el logging por consola."""
    print("\n" + "=" * 60)
    print("TEST 6: Logging por Consola")
    print("=" * 60)

    logger = setup_logging(name="test_console", log_file=None, console_output=True)  # Solo consola

    print("Mensaje de consola (debería aparecer arriba):")
    logger.info("Este es un mensaje de consola")

    print("[OK] Logging por consola funcionando")
    return True


def run_all_tests():
    """Ejecuta todas las pruebas."""
    print("\n" + "[TEST] " * 15)
    print("APD-Scrap: Suite de Pruebas - Sistema de Logging")
    print("[TEST] " * 15 + "\n")

    tests = [
        test_basic_logging,
        test_logger_levels,
        test_get_logger,
        test_logger_mixin,
        test_file_logging,
        test_console_logging,
    ]

    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n[ERROR] Test falló con excepción: {e}")
            import traceback

            traceback.print_exc()
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

        # Cerrar todos los handlers antes de limpiar
        import logging

        for logger_name in logging.root.manager.loggerDict:
            logger = logging.getLogger(logger_name)
            for handler in logger.handlers[:]:
                handler.close()
                logger.removeHandler(handler)

        # Limpiar archivos de prueba
        for file in ["test_logging.log", "test_output.log"]:
            try:
                if Path(file).exists():
                    Path(file).unlink()
                    print(f"Archivo de prueba eliminado: {file}")
            except PermissionError:
                print(f"[AVISO] No se pudo eliminar {file} (en uso)")

        return 0
    else:
        print("\n[ERROR] Algunas pruebas fallaron")
        return 1


if __name__ == "__main__":
    sys.exit(run_all_tests())
