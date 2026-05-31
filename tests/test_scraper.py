"""
Tests unitarios para el módulo apd_scrap.scrapers.apd_scraper
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import json
import requests

from apd_scrap.scrapers.apd_scraper import APDScraper
from apd_scrap.config import Config


@pytest.fixture
def mock_response():
    """Fixture que crea un mock de respuesta HTTP."""
    response = Mock(spec=requests.Response)
    response.raise_for_status = Mock()
    response.json.return_value = {
        "response": {
            "numFound": 100,
            "docs": [
                {"ige": 1, "estado": "Publicada", "cargo": "Profesor", "descdistrito": "MERLO"}
            ],
        }
    }
    response.content = b'{"response":{"numFound":100,"docs":[]}}'
    response.apparent_encoding = "utf-8"
    return response


@pytest.fixture
def scraper():
    """Fixture que crea una instancia de APDScraper."""
    return APDScraper()


class TestAPDScraper:
    """Tests para APDScraper."""

    def test_inicializacion_con_config_default(self):
        """Verifica inicialización con config por defecto."""
        scraper = APDScraper()
        assert scraper.config is not None
        assert isinstance(scraper.config, Config)

    def test_inicializacion_con_config_personalizada(self):
        """Verifica inicialización con config personalizada."""
        config = Config()
        scraper = APDScraper(config=config)
        assert scraper.config == config

    def test_crea_session(self):
        """Verifica que _create_session retorne una Session."""
        scraper = APDScraper()
        session = scraper._create_session()
        assert isinstance(session, requests.Session)

    @patch("apd_scrap.scrapers.apd_scraper.APDScraper._fetch_data")
    def test_get_total_records(self, mock_fetch, scraper):
        """Verifica que get_total_records retorne el conteo."""
        mock_fetch.return_value = {"response": {"numFound": 100}}

        result = scraper.get_total_records("MERLO")

        assert result == 100

    @patch("apd_scrap.scrapers.apd_scraper.APDScraper._fetch_data")
    def test_get_total_records_sin_datos(self, mock_fetch, scraper):
        """Verifica get_total_records sin datos."""
        mock_fetch.return_value = None

        result = scraper.get_total_records("MERLO")

        assert result == 0

    @patch("apd_scrap.scrapers.apd_scraper.APDScraper._fetch_data")
    def test_get_total_records_sin_response(self, mock_fetch, scraper):
        """Verifica get_total_records sin campo response."""
        mock_fetch.return_value = {}

        result = scraper.get_total_records("MERLO")

        assert result == 0

    @patch("apd_scrap.scrapers.apd_scraper.APDScraper.get_total_records")
    @patch("apd_scrap.scrapers.apd_scraper.APDScraper._fetch_data")
    def test_fetch_all_records(self, mock_fetch, mock_get_total, scraper):
        """Verifica fetch_all_records."""
        mock_get_total.return_value = 100
        mock_fetch.return_value = {"response": {"docs": []}}

        result = scraper.fetch_all_records("MERLO")

        assert result is not None
        assert "response" in result

    @patch("apd_scrap.scrapers.apd_scraper.APDScraper.get_total_records")
    def test_fetch_all_records_sin_registros(self, mock_get_total, scraper):
        """Verifica fetch_all_records sin registros."""
        mock_get_total.return_value = 0

        result = scraper.fetch_all_records("MERLO")

        assert result is None

    @patch.object(requests.Session, "get")
    def test_fetch_data_exitoso(self, mock_get, scraper, mock_response):
        """Verifica _fetch_data exitoso."""
        mock_get.return_value = mock_response

        result = scraper._fetch_data({})

        assert result is not None
        assert "response" in result

    @patch.object(requests.Session, "get")
    def test_fetch_data_con_request_exception(self, mock_get, scraper):
        """Verifica _fetch_data con RequestException."""
        mock_get.side_effect = requests.exceptions.RequestException("Error simulado")

        result = scraper._fetch_data({})

        assert result is None

    @patch.object(requests.Session, "get")
    def test_fetch_data_con_json_decode_error(self, mock_get, scraper, mock_response):
        """Verifica _fetch_data con JSONDecodeError y fallback."""
        mock_response.json.side_effect = json.JSONDecodeError("Error", "", 0)
        mock_get.return_value = mock_response

        result = scraper._fetch_data({})

        # Debería usar el fallback
        assert result is not None

    def test_save_to_json_con_datos(self, scraper, tmp_path):
        """Verifica save_to_json con datos válidos."""
        data = {"response": {"docs": [{"ige": 1}]}}

        filename = scraper.save_to_json(data, "merlo")

        assert filename == "output_merlo.json"
        assert filename is not None

    def test_save_to_json_sin_datos(self, scraper):
        """Verifica save_to_json sin datos."""
        result = scraper.save_to_json(None, "merlo")

        assert result is None

    def test_save_to_json_con_datos_vacios(self, scraper):
        """Verifica save_to_json con datos vacíos."""
        # Datos vacíos pero con estructura válida
        data = {"response": {"docs": []}}
        result = scraper.save_to_json(data, "merlo")

        assert result is not None

    def test_close_cierra_session(self, scraper):
        """Verifica que close cierre la sesión."""
        scraper.close()
        # Si no lanza excepción, pasó el test

    def test_context_manager(self):
        """Verifica que APDScraper funcione como context manager."""
        with APDScraper() as scraper:
            assert scraper is not None
            assert scraper.session is not None

    @patch("apd_scrap.scrapers.apd_scraper.APDScraper._fetch_data")
    def test_obtiene_parametros_correctos(self, mock_fetch, scraper):
        """Verifica que se usen los parámetros correctos."""
        mock_fetch.return_value = {"response": {"numFound": 10}}

        scraper.get_total_records("MORENO")

        # Verificar que _fetch_data fue llamado
        assert mock_fetch.called

    def test_save_to_json_crea_archivo(self, scraper, tmp_path):
        """Verifica que save_to_json cree un archivo."""
        import os
        import tempfile

        with tempfile.TemporaryDirectory() as tmp_dir:
            old_cwd = os.getcwd()
            os.chdir(tmp_dir)

            try:
                data = {"response": {"docs": [{"ige": 1, "estado": "Publicada"}]}}

                filename = scraper.save_to_json(data, "test")

                assert os.path.exists(filename)

                with open(filename, "r", encoding="utf-8") as f:
                    content = json.load(f)
                    assert "response" in content
            finally:
                os.chdir(old_cwd)
