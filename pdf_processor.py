# pdf_processor.py
import os
import glob
from typing import List, Optional, Dict, Any
from pathlib import Path
import logging

from llama_index.core import VectorStoreIndex, SimpleDirectoryReader, StorageContext, Settings
from llama_index.core.indices.base import BaseIndex
from llama_index.readers.file import PDFReader
from llama_index.core.node_parser import SimpleNodeParser
from llama_index.embeddings.huggingface import HuggingFaceEmbedding
from llama_index.llms.openai import OpenAI
from llama_index.llms.anthropic import Anthropic

from config import Config

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class PDFProcessor:
    """
    Klasse zum Verarbeiten von PDF-Dokumenten mit LlamaIndex.
    """

    def __init__(self, config: Config = None):
        """
        Initialisiert den PDF-Processor mit der angegebenen Konfiguration.

        Args:
            config: Konfigurationsobjekt mit Einstellungen
        """
        self.config = config or Config.initialize()
        self.index = None
        self._setup_llama_index()

    def _setup_llama_index(self):
        """Konfiguriert LlamaIndex mit den Einstellungen aus der Konfiguration."""
        # Mehrsprachiges Embedding-Modell verwenden
        embed_model = HuggingFaceEmbedding(model_name=self.config.EMBEDDING_MODEL)
        Settings.embed_model = embed_model

        # Anpassen der Chunk-Größe für bessere Verarbeitung
        node_parser = SimpleNodeParser.from_defaults(
            chunk_size=self.config.CHUNK_SIZE,
            chunk_overlap=self.config.CHUNK_OVERLAP
        )
        Settings.node_parser = node_parser

        # LLM Provider konfigurieren
        if self.config.LLM_PROVIDER.lower() == "anthropic":
            if not self.config.ANTHROPIC_API_KEY:
                logger.warning("Anthropic API-Key fehlt, aber Anthropic als Provider ausgewählt!")
            else:
                llm = Anthropic(
                    model=self.config.ANTHROPIC_MODEL,
                    api_key=self.config.ANTHROPIC_API_KEY
                )
                Settings.llm = llm
                logger.info(f"Anthropic LLM konfiguriert mit Modell: {self.config.ANTHROPIC_MODEL}")
        else:
            # Default: OpenAI
            if self.config.OPENAI_API_KEY:
                llm = OpenAI()
                Settings.llm = llm
                logger.info("OpenAI LLM konfiguriert")

        logger.info(f"LlamaIndex konfiguriert mit: Embedding-Modell={self.config.EMBEDDING_MODEL}, "
                    f"Chunk-Größe={self.config.CHUNK_SIZE}, Chunk-Überlappung={self.config.CHUNK_OVERLAP}")

    def get_pdf_files(self) -> List[str]:
        """
        Findet alle PDF-Dateien im konfigurierten PDF-Verzeichnis.

        Returns:
            Liste der PDF-Dateipfade
        """
        # Prüfen ob das Verzeichnis existiert
        if not os.path.exists(self.config.PDF_DIR):
            logger.warning(f"PDF-Verzeichnis existiert nicht: {self.config.PDF_DIR}")
            os.makedirs(self.config.PDF_DIR, exist_ok=True)
            logger.info(f"PDF-Verzeichnis wurde erstellt: {self.config.PDF_DIR}")
            return []

        pdf_pattern = os.path.join(self.config.PDF_DIR, "**/*.pdf")
        pdf_files = glob.glob(pdf_pattern, recursive=True)

        # Optional: Begrenze die Anzahl der PDFs
        if self.config.MAX_PDFS > 0:
            pdf_files = pdf_files[:self.config.MAX_PDFS]

        logger.info(f"{len(pdf_files)} PDF-Dateien gefunden in {self.config.PDF_DIR}")
        return pdf_files

    def process_pdfs(self, pdf_files: Optional[List[str]] = None) -> VectorStoreIndex | None:
        """
        Verarbeitet die angegebenen PDF-Dateien und erstellt einen Index.

        Args:
            pdf_files: Liste der zu verarbeitenden PDF-Dateien (optional)

        Returns:
            Der erstellte VectorStoreIndex
        """
        if pdf_files is None:
            pdf_files = self.get_pdf_files()

        if not pdf_files:
            logger.warning("Keine PDF-Dateien zum Verarbeiten gefunden!")
            return None

        logger.info(f"Verarbeite {len(pdf_files)} PDF-Dateien...")

        # PDF-Reader initialisieren
        pdf_reader = PDFReader()

        # PDFs laden (angepasst für neuere Versionen)
        documents = []
        try:
            # Für neuere Versionen von llama-index
            for pdf_file in pdf_files:
                try:
                    # Path-Objekt erstellen, da die Methode path und nicht string erwartet
                    pdf_path = Path(pdf_file)
                    doc = pdf_reader.load_data(file=pdf_path)
                    documents.extend(doc)
                    logger.info(f"PDF geladen: {pdf_file}")
                except Exception as e:
                    logger.error(f"Fehler beim Laden von {pdf_file}: {str(e)}")
        except Exception as e:
            logger.error(f"Fehler beim Laden der PDFs: {str(e)}")
            if not documents:
                return None

        # Erstelle eine Zuordnung zwischen Dokumenten und ihren Quell-PDFs
        pdf_docs = {}
        pdf_files_mapping = {}

        # Ermittle zuerst alle gültigen PDF-Quellen
        for pdf_file in pdf_files:
            basename = os.path.basename(pdf_file)
            pdf_files_mapping[basename] = {
                "filename": basename,
                "filepath": pdf_file,
                "filesize": os.path.getsize(pdf_file) if os.path.exists(pdf_file) else 0
            }

        # Sammle auch Informationen aus Dokumenten mit vollständigen Pfaden
        for doc in documents:
            file_path = doc.metadata.get("file_path", "")
            if file_path and file_path not in pdf_docs and os.path.exists(file_path):
                basename = os.path.basename(file_path)
                pdf_docs[file_path] = {
                    "filename": basename,
                    "filesize": os.path.getsize(file_path)
                }
                # Füge es auch zur Mapping-Liste hinzu falls noch nicht vorhanden
                if basename not in pdf_files_mapping:
                    pdf_files_mapping[basename] = {
                        "filename": basename,
                        "filepath": file_path,
                        "filesize": os.path.getsize(file_path)
                    }

        # Füge Metadaten zu allen Dokumenten hinzu
        missing_path_warned = False
        for doc in documents:
            file_path = doc.metadata.get("file_path", "")

            # Versuche verschiedene Methoden, um die Quelldatei zu identifizieren
            if file_path and os.path.exists(file_path):
                # Direkter Pfad verfügbar
                basename = os.path.basename(file_path)
                doc.metadata["filename"] = basename
                doc.metadata["filesize"] = os.path.getsize(file_path)

            else:
                # Suche nach alternativen Quell-Identifikatoren
                source_identified = False

                # Prüfe verschiedene Metadatenfelder
                source_candidates = [
                    doc.metadata.get("source", ""),
                    doc.metadata.get("source_filename", ""),
                    doc.metadata.get("file_name", ""),
                    doc.metadata.get("document_id", "")
                ]

                # Manchmal ist die Quellpfad-Information in anderen Feldern enthalten
                for candidate in source_candidates:
                    if candidate:
                        # Extrahiere den Dateinamen, falls ein Pfad enthalten ist
                        basename = os.path.basename(candidate) if os.path.sep in candidate else candidate

                        # Prüfe, ob dieser Dateiname einem unserer bekannten PDFs entspricht
                        for pdf_name in pdf_files_mapping:
                            if pdf_name in basename or basename in pdf_name:
                                doc.metadata["filename"] = pdf_name
                                doc.metadata["filesize"] = pdf_files_mapping[pdf_name]["filesize"]
                                source_identified = True
                                break

                        if source_identified:
                            break

                # Wenn keine Quelle identifiziert wurde, aber wir nur eine PDF haben
                if not source_identified and len(pdf_files) == 1:
                    # Bei nur einer PDF-Datei können wir annehmen, dass alle Dokumente daraus stammen
                    basename = os.path.basename(pdf_files[0])
                    doc.metadata["filename"] = basename
                    doc.metadata["filesize"] = os.path.getsize(pdf_files[0]) if os.path.exists(pdf_files[0]) else 0
                    source_identified = True

                # Falls immer noch keine Quelle identifiziert wurde
                if not source_identified:
                    # Prüfe auf "page_label" oder ähnliche Indikatoren, die auf PDF-Seiten hinweisen
                    if "page_label" in doc.metadata or "page" in doc.metadata:
                        # Wenn wir wenige PDFs haben, können wir die Warnung mit den verfügbaren Dateinamen anzeigen
                        if len(pdf_files_mapping) <= 5:
                            doc.metadata["filename"] = f"Ein PDF aus: {', '.join(pdf_files_mapping.keys())}"
                        else:
                            doc.metadata["filename"] = "Ein PDF aus der Sammlung"
                    else:
                        doc.metadata["filename"] = "unbekannt"

                    doc.metadata["filesize"] = 0

                # Nur eine Warnung für alle fehlenden Pfade ausgeben
                if not source_identified and not missing_path_warned:
                    logger.info("Einige Dokumentfragmente konnten nicht eindeutig einer Quelldatei zugeordnet werden.")
                    missing_path_warned = True

        logger.info(f"{len(documents)} Dokumente geladen")

        # Index erstellen
        self.index = VectorStoreIndex.from_documents(documents)
        logger.info("Index erfolgreich erstellt")

        return self.index

    def save_index(self, directory: Optional[str] = None) -> str | None | Any:
        """
        Speichert den Index in dem angegebenen Verzeichnis.

        Args:
            directory: Verzeichnis zum Speichern (optional, verwendet sonst das konfigurierte Verzeichnis)

        Returns:
            Pfad zum gespeicherten Index
        """
        if self.index is None:
            logger.error("Kein Index zum Speichern vorhanden!")
            return None

        save_dir = directory or self.config.INDEX_DIR
        self.index.storage_context.persist(save_dir)
        logger.info(f"Index gespeichert in: {save_dir}")
        return save_dir

    def load_index(self, directory: Optional[str] = None) -> BaseIndex | None:
        """
        Lädt einen gespeicherten Index.

        Args:
            directory: Verzeichnis, aus dem der Index geladen werden soll

        Returns:
            Der geladene VectorStoreIndex
        """
        from llama_index.core import StorageContext, load_index_from_storage

        load_dir = directory or self.config.INDEX_DIR

        if not os.path.exists(load_dir):
            logger.error(f"Index-Verzeichnis existiert nicht: {load_dir}")
            return None

        try:
            storage_context = StorageContext.from_defaults(persist_dir=load_dir)
            self.index = load_index_from_storage(storage_context)
            logger.info(f"Index erfolgreich geladen aus: {load_dir}")
            return self.index
        except Exception as e:
            logger.error(f"Fehler beim Laden des Index: {str(e)}")
            return None

    def create_query_engine(self):
        """
        Erstellt eine Abfrage-Engine für den aktuellen Index.

        Returns:
            QueryEngine für Abfragen
        """
        if self.index is None:
            logger.error("Kein Index für Abfragen vorhanden!")
            return None

        return self.index.as_query_engine()


if __name__ == "__main__":
    # Beispielverwendung
    processor = PDFProcessor()
    processor.process_pdfs()
    processor.save_index()