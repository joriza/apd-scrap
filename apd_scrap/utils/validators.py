"""
Módulo de validaciones para datos de APD-Scrap.

Este módulo proporciona funciones para validar datos de entrada
como CUIL, IGE, distritos y otros formatos específicos del sistema.
"""

import re
from typing import Any, Optional, Callable

from apd_scrap.utils.logging import LoggerMixin


class ValidationError(Exception):
    """Excepción para errores de validación."""

    def __init__(self, message: str, field: Optional[str] = None):
        """
        Inicializa ValidationError.

        Args:
            message: Mensaje de error
            field: Nombre del campo que falló la validación (opcional)
        """
        self.message = message
        self.field = field
        super().__init__(self.message)

    def __str__(self) -> str:
        """Representación string del error."""
        if self.field:
            return f"{self.field}: {self.message}"
        return self.message


class Validators(LoggerMixin):
    """
    Validadores para datos de APD-Scrap.

    Proporciona métodos estáticos para validar diferentes tipos de datos
    utilizados en el sistema.

    Example:
        >>> Validators.validate_cuil("20-17355827-6")  # True
        >>> Validators.validate_cuil("123")  # ValidationError
        >>> Validators.validate_ige(1234567)  # True
        >>> Validators.validate_distrito("MERLO")  # True
    """

    # Patrón regex para CUIL argentino (XX-XXXXXXXX-X o XXXXXXXXXXX)
    CUIL_PATTERN = re.compile(r"^(\d{2})[-]?(\d{8})[-]?(\d{1})$")

    # Lista de distritos válidos (ejemplo, puede extenderse)
    DISTRITOS_VALIDOS = {
        "MORENO",
        "MORON",
        "MERLO",
        "QUILMES",
        "PILAR",
        "TIGRE",
        "SAN MARTIN",
        "LA MATANZA",
        "TRES DE FEBRERO",
        "VICENTE LOPEZ",
        "SAN FERNANDO",
        "JOSE C. PAZ",
        "HURLINGHAM",
        "ITUZAINGO",
        "SAN MIGUEL",
        "ALMIRANTE BROWN",
        "BERAZATEGUI",
        "ESTEBAN ECHEVERRIA",
        "EZEIZA",
        "FLORENCIO VARELA",
        "LANUS",
        "LOMAS DE ZAMORA",
        "AVELLANEDA",
    }

    @staticmethod
    def validate_cuil(cuil: str) -> bool:
        """
        Valida un número de CUIL argentino.

        El CUIL (Código Único de Identificación Laboral) argentino
        sigue el formato XX-XXXXXXXX-X o XXXXXXXXXXX.

        Args:
            cuil: Número de CUIL a validar

        Returns:
            bool: True si el CUIL es válido

        Raises:
            ValidationError: Si el CUIL no es válido

        Example:
            >>> Validators.validate_cuil("20-17355827-6")
            True
            >>> Validators.validate_cuil("20173558276")
            True
            >>> Validators.validate_cuil("123")
            ValidationError: Formato de CUIL inválido: 123
        """
        if not cuil or not isinstance(cuil, str):
            raise ValidationError(f"El CUIL debe ser una cadena: {cuil}", "cuil")

        # Normalizar formato
        cuil_normalizado = cuil.replace("-", "")

        if len(cuil_normalizado) != 11:
            raise ValidationError(
                f"El CUIL debe tener 11 dígitos: {cuil}", "cuil"
            )

        if not cuil_normalizado.isdigit():
            raise ValidationError(f"El CUIL solo puede contener dígitos: {cuil}", "cuil")

        # Validar dígito verificador
        if not Validators._validate_cuil_checksum(cuil_normalizado):
            raise ValidationError(f"Dígito verificador inválido para CUIL: {cuil}", "cuil")

        return True

    @staticmethod
    def _validate_cuil_checksum(cuil: str) -> bool:
        """
        Valida el dígito verificador del CUIL.

        El algoritmo de validación es:
        - Multiplicar cada dígito por [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]
        - Sumar los resultados
        - Calcular módulo 11
        - Dígito verificador = 11 - (módulo % 11)
        - Si el resultado es 11, el dígito es 0
        - Si el resultado es 10, el dígito es inválido

        Args:
            cuil: CUIL de 11 dígitos (sin guiones)

        Returns:
            bool: True si el dígito verificador es correcto
        """
        if len(cuil) != 11:
            return False

        # Multiplicadores para validación
        multipliers = [5, 4, 3, 2, 7, 6, 5, 4, 3, 2]

        # Calcular suma ponderada
        total = 0
        for i in range(10):
            total += int(cuil[i]) * multipliers[i]

        # Calcular dígito verificador
        remainder = total % 11
        verifier = 11 - remainder

        # Ajustes especiales
        if verifier == 11:
            verifier = 0
        elif verifier == 10:
            return False  # Dígito inválido

        return int(cuil[10]) == verifier

    @staticmethod
    def validate_ige(ige: Any) -> bool:
        """
        Valida un número de IGE (Identificador General de Establecimiento).

        Args:
            ige: IGE a validar

        Returns:
            bool: True si el IGE es válido

        Raises:
            ValidationError: Si el IGE no es válido

        Example:
            >>> Validators.validate_ige(4067362)
            True
            >>> Validators.validate_ige("4067362")
            True
            >>> Validators.validate_ige(-1)
            ValidationError: El IGE debe ser positivo: -1
        """
        # Convertir a int si es string
        if isinstance(ige, str):
            if not ige.isdigit():
                raise ValidationError(f"El IGE debe contener solo dígitos: {ige}", "ige")
            ige = int(ige)

        if not isinstance(ige, int):
            raise ValidationError(f"El IGE debe ser un número entero: {ige}", "ige")

        if ige <= 0:
            raise ValidationError(f"El IGE debe ser positivo: {ige}", "ige")

        if ige > 99999999:
            raise ValidationError(f"El IGE excede el máximo permitido (99,999,999): {ige}", "ige")

        return True

    @staticmethod
    def validate_distrito(distrito: str) -> bool:
        """
        Valida el nombre de un distrito.

        Args:
            distrito: Nombre del distrito a validar

        Returns:
            bool: True si el distrito es válido

        Raises:
            ValidationError: Si el distrito no es válido

        Example:
            >>> Validators.validate_distrito("MERLO")
            True
            >>> Validators.validate_distrito("merlo")
            True  # Case insensitive
            >>> Validators.validate_distrito("INVALIDO")
            ValidationError: Distrito no reconocido: INVALIDO
        """
        if not distrito or not isinstance(distrito, str):
            raise ValidationError(f"El distrito debe ser una cadena: {distrito}", "distrito")

        distrito_normalizado = distrito.strip().upper()

        if not distrito_normalizado:
            raise ValidationError("El distrito no puede estar vacío", "distrito")

        if distrito_normalizado not in Validators.DISTRITOS_VALIDOS:
            raise ValidationError(
                f"Distrito no reconocido: {distrito}. "
                f"Distritos válidos: {', '.join(sorted(Validators.DISTRITOS_VALIDOS))}",
                "distrito",
            )

        return True

    @staticmethod
    def validate_estado(estado: str) -> bool:
        """
        Valida un estado de oferta.

        Args:
            estado: Estado a validar

        Returns:
            bool: True si el estado es válido

        Raises:
            ValidationError: Si el estado no es válido

        Example:
            >>> Validators.validate_estado("Publicada")
            True
            >>> Validators.validate_estado("DESIGNADA")
            True
            >>> Validators.validate_estado("INVALIDO")
            ValidationError: Estado no válido: INVALIDO
        """
        estados_validos = [
            "Anulada",
            "Desierta",
            "DESIGNADA",
            "RENUNCIADA",
            "Finalizada",
            "Publicada",
            "Cerrada",
        ]

        if not estado or not isinstance(estado, str):
            raise ValidationError(f"El estado debe ser una cadena: {estado}", "estado")

        if estado not in estados_validos:
            raise ValidationError(
                f"Estado no válido: {estado}. Estados válidos: {', '.join(estados_validos)}",
                "estado",
            )

        return True

    @staticmethod
    def validate_designado(designado: str) -> bool:
        """
        Valida el campo designado de postulantes.

        Args:
            designado: Valor del campo designado

        Returns:
            bool: True si es válido

        Raises:
            ValidationError: Si el valor no es válido

        Example:
            >>> Validators.validate_designado("S")
            True
            >>> Validators.validate_designado("N")
            True
            >>> Validators.validate_designado("X")
            ValidationError: El campo designado debe ser 'S' o 'N': X
        """
        if not designado or not isinstance(designado, str):
            raise ValidationError(
                f"El campo designado debe ser una cadena: {designado}", "designado"
            )

        if designado.upper() not in ["S", "N"]:
            raise ValidationError(
                f"El campo designado debe ser 'S' o 'N': {designado}", "designado"
            )

        return True

    @staticmethod
    def validate_batch(data: list[Any], validator: Callable) -> list[ValidationError]:
        """
        Valida una lista de elementos usando un validator.

        Args:
            data: Lista de elementos a validar
            validator: Función de validación a aplicar

        Returns:
            list[ValidationError]: Lista de errores de validación (vacía si no hay errores)

        Example:
            >>> errors = Validators.validate_batch(
            ...     ["20173558276", "123"],
            ...     Validators.validate_cuil
            ... )
            >>> len(errors)
            1
        """
        errors = []

        for i, item in enumerate(data):
            try:
                validator(item)
            except ValidationError as e:
                errors.append(ValidationError(f"Índice {i}: {e.message}", e.field))

        return errors


def validate_cuil(cuil: str) -> bool:
    """
    Función conveniente para validar CUIL.

    Args:
        cuil: Número de CUIL a validar

    Returns:
        bool: True si el CUIL es válido

    Example:
        >>> validate_cuil("20-17355827-6")
        True
    """
    return Validators.validate_cuil(cuil)


def validate_ige(ige: Any) -> bool:
    """
    Función conveniente para validar IGE.

    Args:
        ige: IGE a validar

    Returns:
        bool: True si el IGE es válido

    Example:
        >>> validate_ige(4067362)
        True
    """
    return Validators.validate_ige(ige)


def validate_distrito(distrito: str) -> bool:
    """
    Función conveniente para validar distrito.

    Args:
        distrito: Nombre del distrito a validar

    Returns:
        bool: True si el distrito es válido

    Example:
        >>> validate_distrito("MERLO")
        True
    """
    return Validators.validate_distrito(distrito)
