"""Tests para el módulo de validaciones."""

import pytest

from apd_scrap.utils.validators import (
    Validators,
    ValidationError,
    validate_cuil,
    validate_ige,
    validate_distrito,
)


class TestValidationError:
    """Tests para ValidationError."""

    def test_create_with_message(self):
        """Puede crear error con mensaje."""
        error = ValidationError("Mensaje de error")
        assert str(error) == "Mensaje de error"
        assert error.message == "Mensaje de error"
        assert error.field is None

    def test_create_with_field(self):
        """Puede crear error con campo."""
        error = ValidationError("Mensaje de error", field="cuil")
        assert "cuil:" in str(error)
        assert error.field == "cuil"


class TestValidateCuil:
    """Tests para validación de CUIL."""

    def test_valid_cuil_with_hyphens(self):
        """Valida CUIL con guiones."""
        assert Validators.validate_cuil("20-17355827-6")

    def test_valid_cuil_without_hyphens(self):
        """Valida CUIL sin guiones."""
        assert Validators.validate_cuil("20173558276")

    def test_valid_cuil_checksum(self):
        """Valida dígito verificador correcto."""
        # 20-17355827-6 tiene dígito verificador correcto
        assert Validators._validate_cuil_checksum("20173558276")

    def test_invalid_cuil_checksum(self):
        """Rechaza dígito verificador incorrecto."""
        # 20-17355827-9 tiene dígito verificador incorrecto
        assert not Validators._validate_cuil_checksum("20173558279")

    def test_invalid_cuil_empty(self):
        """Rechaza CUIL vacío."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_cuil("")

    def test_invalid_cuil_none(self):
        """Rechaza CUIL None."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_cuil(None)

    def test_invalid_cuil_not_string(self):
        """Rechaza CUIL no string."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_cuil(12345678901)

    def test_invalid_cuil_too_short(self):
        """Rechaza CUIL muy corto."""
        with pytest.raises(ValidationError, match="debe tener 11 dígitos"):
            Validators.validate_cuil("123456789")

    def test_invalid_cuil_too_long(self):
        """Rechaza CUIL muy largo."""
        with pytest.raises(ValidationError, match="debe tener 11 dígitos"):
            Validators.validate_cuil("123456789012")

    def test_invalid_cuil_non_digits(self):
        """Rechaza CUIL con caracteres no numéricos."""
        with pytest.raises(ValidationError, match="solo puede contener dígitos"):
            Validators.validate_cuil("20-17355827-A")

    def test_invalid_cuil_wrong_checksum(self):
        """Rechaza CUIL con checksum incorrecto."""
        with pytest.raises(ValidationError, match="Dígito verificador inválido"):
            Validators.validate_cuil("20-17355827-9")


class TestValidateIge:
    """Tests para validación de IGE."""

    def test_valid_ige_int(self):
        """Valida IGE como entero."""
        assert Validators.validate_ige(4067362)

    def test_valid_ige_string(self):
        """Valida IGE como string de dígitos."""
        assert Validators.validate_ige("4067362")

    def test_valid_ige_small(self):
        """Valida IGE pequeño."""
        assert Validators.validate_ige(1)

    def test_valid_ige_large(self):
        """Valida IGE grande."""
        assert Validators.validate_ige(99999999)

    def test_invalid_ige_zero(self):
        """Rechaza IGE cero."""
        with pytest.raises(ValidationError, match="debe ser positivo"):
            Validators.validate_ige(0)

    def test_invalid_ige_negative(self):
        """Rechaza IGE negativo."""
        with pytest.raises(ValidationError, match="debe ser positivo"):
            Validators.validate_ige(-1)

    def test_invalid_ige_not_int(self):
        """Rechaza IGE no entero."""
        with pytest.raises(ValidationError, match="debe ser un número entero"):
            Validators.validate_ige(1.5)

    def test_invalid_ge_string_non_digits(self):
        """Rechaza IGE string con no dígitos."""
        with pytest.raises(ValidationError, match="debe contener solo dígitos"):
            Validators.validate_ige("12a456")

    def test_invalid_ige_too_large(self):
        """Rechaza IGE mayor al máximo permitido."""
        with pytest.raises(ValidationError, match="excede el máximo permitido"):
            Validators.validate_ige(100000000)

    def test_invalid_ige_none(self):
        """Rechaza IGE None."""
        with pytest.raises(ValidationError, match="debe ser un número entero"):
            Validators.validate_ige(None)


class TestValidateDistrito:
    """Tests para validación de distrito."""

    def test_valid_distrito_uppercase(self):
        """Valida distrito en mayúsculas."""
        assert Validators.validate_distrito("MERLO")

    def test_valid_distrito_lowercase(self):
        """Valida distrito en minúsculas (case insensitive)."""
        assert Validators.validate_distrito("merlo")

    def test_valid_distrito_mixed_case(self):
        """Valida distrito en case mixto."""
        assert Validators.validate_distrito("MeRlO")

    def test_valid_distrito_with_spaces(self):
        """Valida distrito con espacios (se hace strip)."""
        assert Validators.validate_distrito(" MERLO ")

    def test_valid_distrito_multi_word(self):
        """Valida distrito con múltiples palabras."""
        assert Validators.validate_distrito("LA MATANZA")

    def test_invalid_distrito_empty(self):
        """Rechaza distrito vacío."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_distrito("")

    def test_invalid_distrito_none(self):
        """Rechaza distrito None."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_distrito(None)

    def test_invalid_distrito_not_string(self):
        """Rechaza distrito no string."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_distrito(123)

    def test_invalid_distrito_only_spaces(self):
        """Rechaza distrito solo espacios."""
        with pytest.raises(ValidationError, match="no puede estar vacío"):
            Validators.validate_distrito("   ")

    def test_invalid_distrito_unknown(self):
        """Rechaza distrito no reconocido."""
        with pytest.raises(ValidationError, match="no reconocido"):
            Validators.validate_distrito("INVALIDO")


class TestValidateEstado:
    """Tests para validación de estado."""

    def test_valid_estado_publicada(self):
        """Valida estado Publicada."""
        assert Validators.validate_estado("Publicada")

    def test_valid_estado_designada(self):
        """Valida estado DESIGNADA (case sensitive)."""
        assert Validators.validate_estado("DESIGNADA")

    def test_valid_estado_anulada(self):
        """Valida estado Anulada."""
        assert Validators.validate_estado("Anulada")

    def test_invalid_estado_empty(self):
        """Rechaza estado vacío."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_estado("")

    def test_invalid_estado_none(self):
        """Rechaza estado None."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_estado(None)

    def test_invalid_estado_lowercase_publicada(self):
        """Rechaza estado en minúsculas (case sensitive)."""
        with pytest.raises(ValidationError, match="no válido"):
            Validators.validate_estado("publicada")

    def test_invalid_estado_unknown(self):
        """Rechaza estado no válido."""
        with pytest.raises(ValidationError, match="no válido"):
            Validators.validate_estado("INVALIDO")


class TestValidateDesignado:
    """Tests para validación de designado."""

    def test_valid_designado_s(self):
        """Valida designado S."""
        assert Validators.validate_designado("S")

    def test_valid_designado_s_lowercase(self):
        """Valida designado s (case insensitive)."""
        assert Validators.validate_designado("s")

    def test_valid_designado_n(self):
        """Valida designado N."""
        assert Validators.validate_designado("N")

    def test_valid_designado_n_lowercase(self):
        """Valida designado n (case insensitive)."""
        assert Validators.validate_designado("n")

    def test_invalid_designado_empty(self):
        """Rechaza designado vacío."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_designado("")

    def test_invalid_designado_none(self):
        """Rechaza designado None."""
        with pytest.raises(ValidationError, match="debe ser una cadena"):
            Validators.validate_designado(None)

    def test_invalid_designado_x(self):
        """Rechaza designado X."""
        with pytest.raises(ValidationError, match="debe ser 'S' o 'N'"):
            Validators.validate_designado("X")

    def test_invalid_designado_yes(self):
        """Rechaza designado YES."""
        with pytest.raises(ValidationError, match="debe ser 'S' o 'N'"):
            Validators.validate_designado("YES")


class TestValidateBatch:
    """Tests para validación en lote."""

    def test_validate_batch_all_valid(self):
        """Valida lote donde todos son válidos."""
        data = ["20-17355827-6", "20-01735582-7"]
        errors = Validators.validate_batch(data, Validators.validate_cuil)
        assert len(errors) == 0

    def test_validate_batch_some_invalid(self):
        """Valida lote donde algunos son inválidos."""
        data = ["20-17355827-6", "123"]
        errors = Validators.validate_batch(data, Validators.validate_cuil)
        assert len(errors) == 1
        assert "cuil" in str(errors[0]).lower()

    def test_validate_batch_all_invalid(self):
        """Valida lote donde todos son inválidos."""
        data = ["123", "456"]
        errors = Validators.validate_batch(data, Validators.validate_cuil)
        assert len(errors) == 2

    def test_validate_batch_empty(self):
        """Valida lote vacío."""
        data = []
        errors = Validators.validate_batch(data, Validators.validate_cuil)
        assert len(errors) == 0

    def test_validate_batch_with_ige(self):
        """Valida lote de IGEs."""
        data = [123, 456, 789]
        errors = Validators.validate_batch(data, Validators.validate_ige)
        assert len(errors) == 0


class TestConvenienceFunctions:
    """Tests para funciones de conveniencia."""

    def test_validate_cuil_convenience(self):
        """Función validate_cuil funciona."""
        assert validate_cuil("20-17355827-6") is True

    def test_validate_ige_convenience(self):
        """Función validate_ige funciona."""
        assert validate_ige(4067362)

    def test_validate_distrito_convenience(self):
        """Función validate_distrito funciona."""
        assert validate_distrito("MERLO")


class TestValidatorsClass:
    """Tests para la clase Validators."""

    def test_cuil_pattern_exists(self):
        """El patrón de CUIL existe."""
        assert hasattr(Validators, "CUIL_PATTERN")
        assert Validators.CUIL_PATTERN is not None

    def test_distritos_validos_exists(self):
        """La lista de distritos válidos existe."""
        assert hasattr(Validators, "DISTRITOS_VALIDOS")
        assert isinstance(Validators.DISTRITOS_VALIDOS, set)
        assert "MERLO" in Validators.DISTRITOS_VALIDOS
        assert "MORON" in Validators.DISTRITOS_VALIDOS

    def test_distritos_validos_count(self):
        """Verifica que haya una cantidad razonable de distritos."""
        assert len(Validators.DISTRITOS_VALIDOS) > 20
