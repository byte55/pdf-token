# config.py
import os
from dotenv import load_dotenv
from pathlib import Path

# .env Datei laden (falls vorhanden)
load_dotenv()


# Konfigurationsklasse
class Config:
    # Pfade
    BASE_DIR = Path(__file__).parent.absolute()
    PDF_DIR = os.getenv("PDF_DIR", str(BASE_DIR / "pdfs"))
    INDEX_DIR = os.getenv("INDEX_DIR", str(BASE_DIR / "index_storage"))

    # API Keys
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY", "")

    # LLM Konfiguration
    LLM_PROVIDER = os.getenv("LLM_PROVIDER", "openai")  # Optionen: "openai", "anthropic"
    ANTHROPIC_MODEL = os.getenv("ANTHROPIC_MODEL", "claude-3-5-sonnet")

    # LlamaIndex Einstellungen
    CHUNK_SIZE = int(os.getenv("CHUNK_SIZE", "512"))
    CHUNK_OVERLAP = int(os.getenv("CHUNK_OVERLAP", "50"))
    EMBEDDING_MODEL = os.getenv("EMBEDDING_MODEL", "intfloat/multilingual-e5-large")

    # Einstellungen für PDF-Verarbeitung
    MAX_PDFS = int(os.getenv("MAX_PDFS", "0"))  # 0 = Alle PDFs verarbeiten

    # Überprüfen, ob Pfade existieren, sonst erstellen
    @classmethod
    def initialize(cls):
        os.makedirs(cls.PDF_DIR, exist_ok=True)
        os.makedirs(cls.INDEX_DIR, exist_ok=True)

        # API Keys setzen, falls vorhanden
        if cls.OPENAI_API_KEY:
            os.environ["OPENAI_API_KEY"] = cls.OPENAI_API_KEY

        if cls.ANTHROPIC_API_KEY:
            os.environ["ANTHROPIC_API_KEY"] = cls.ANTHROPIC_API_KEY

        return cls