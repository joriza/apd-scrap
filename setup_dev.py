#!/usr/bin/env python3
"""
Script de configuración del entorno de desarrollo para APD-Scrap.

Este script instala todas las herramientas necesarias para desarrollo,
testing y linting del proyecto.
"""

import subprocess
import sys
from pathlib import Path


def run_command(cmd: list[str], description: str) -> bool:
    """
    Ejecuta un comando y muestra el resultado.
    
    Args:
        cmd: Comando a ejecutar como lista de strings
        description: Descripción del comando
        
    Returns:
        True si el comando fue exitoso, False en caso contrario
    """
    print(f"\n{'='*60}")
    print(f"{description}")
    print(f"{'='*60}")
    print(f"Comando: {' '.join(cmd)}")
    print()
    
    try:
        result = subprocess.run(
            cmd,
            check=True,
            capture_output=False,
            text=True
        )
        print(f"\n✓ {description} completado exitosamente")
        return True
    except subprocess.CalledProcessError as e:
        print(f"\n✗ Error en {description}")
        print(f"Código de salida: {e.returncode}")
        return False


def main() -> int:
    """
    Función principal del script de configuración.
    
    Returns:
        0 si todas las instalaciones fueron exitosas, 1 si hubo errores
    """
    print("="*60)
    print("Configuración del Entorno de Desarrollo - APD-Scrap")
    print("="*60)
    
    # Verificar Python
    python_version = f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
    print(f"\nPython versión: {python_version}")
    
    if sys.version_info < (3, 9):
        print("⚠ ADVERTENCIA: Se recomienda Python 3.9 o superior")
    
    # Instalar dependencias del proyecto
    success = run_command(
        [sys.executable, "-m", "pip", "install", "-r", "requirements.txt"],
        "Instalando dependencias del proyecto"
    )
    if not success:
        return 1
    
    # Instalar herramientas de testing
    success = run_command(
        [sys.executable, "-m", "pip", "install", "pytest>=7.4.3", "pytest-mock>=3.12.0", "pytest-cov>=4.1.0"],
        "Instalando herramientas de testing (pytest, pytest-mock, pytest-cov)"
    )
    if not success:
        return 1
    
    # Instalar herramientas de formateo y linting
    success = run_command(
        [sys.executable, "-m", "pip", "install", "black>=24.1.1", "ruff>=0.1.9", "mypy>=1.8.0"],
        "Instalando herramientas de formateo y linting (black, ruff, mypy)"
    )
    if not success:
        return 1
    
    # Instalar pre-commit
    success = run_command(
        [sys.executable, "-m", "pip", "install", "pre-commit>=3.6.0"],
        "Instalando pre-commit"
    )
    if not success:
        return 1
    
    # Instalar bandit (seguridad)
    success = run_command(
        [sys.executable, "-m", "pip", "install", "bandit>=1.7.6"],
        "Instalando bandit (security linter)"
    )
    if not success:
        return 1
    
    # Configurar pre-commit
    success = run_command(
        [sys.executable, "-m", "pre-commit", "install"],
        "Configurando pre-commit hooks"
    )
    if not success:
        return 1
    
    # Verificar herramientas instaladas
    print("\n" + "="*60)
    print("Verificando instalación de herramientas...")
    print("="*60)
    
    tools = [
        ("black", "--version"),
        ("ruff", "--version"),
        ("mypy", "--version"),
        ("pytest", "--version"),
        ("pre-commit", "--version"),
        ("bandit", "--version"),
    ]
    
    for tool, version_cmd in tools:
        try:
            result = subprocess.run(
                [sys.executable, "-m", tool, *version_cmd.split()[1:]],
                capture_output=True,
                text=True,
                check=True
            )
            version = result.stdout.strip()
            print(f"✓ {tool}: {version}")
        except (subprocess.CalledProcessError, ImportError):
            print(f"✗ {tool}: No instalado o error en verificación")
    
    # Ejecutar tests para verificar configuración
    print("\n" + "="*60)
    print("Ejecutando tests de verificación...")
    print("="*60)
    
    success = run_command(
        [sys.executable, "-m", "pytest", "tests/", "-v", "--tb=short", "-x"],
        "Ejecutando tests (para detenerse en el primer error usa -x)"
    )
    
    # Resumen
    print("\n" + "="*60)
    print("RESUMEN")
    print("="*60)
    
    if success:
        print("\n✓ Configuración completada exitosamente")
        print("\nHerramientas instaladas:")
        print("  - black: Formateador de código")
        print("  - ruff: Linter rápido")
        print("  - mypy: Type checking")
        print("  - pytest: Framework de tests")
        print("  - pre-commit: Hooks de pre-commit")
        print("  - bandit: Security linter")
        print("\nComandos útiles:")
        print("  - black .                    # Formatear código")
        print("  - ruff check .               # Verificar errores")
        print("  - ruff check . --fix         # Corregir errores automáticamente")
        print("  - mypy apd_scrap/            # Verificar tipos")
        print("  - pytest                     # Ejecutar tests")
        print("  - pytest --cov              # Ejecutar tests con cobertura")
        print("  - pre-commit run --all-files # Ejecutar hooks en todos los archivos")
        print("  - pre-commit install         # Instalar hooks de git")
        return 0
    else:
        print("\n⚠ ADVERTENCIA: Tests fallaron, revisa los errores arriba")
        return 1


if __name__ == "__main__":
    sys.exit(main())