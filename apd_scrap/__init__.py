"""
APD-Scrap: Scraper de ofertas educativas del sistema APD.

Este paquete permite descargar y almacenar ofertas laborales docentes
de diferentes distritos del sistema APD del gobierno de Argentina.
"""

__version__ = "2.0.0"
__author__ = "APD-Scrap Team"

from apd_scrap.config import Config
from apd_scrap.database.connection import DatabaseConnection
from apd_scrap.scrapers.apd_scraper import APDScraper

__all__ = [
    "Config",
    "APDScraper",
    "DatabaseConnection",
]
