# query_engine.py
import logging
from typing import List, Dict, Any, Optional

from llama_index.core import VectorStoreIndex
# Entfernte den problematischen Import
# from llama_index.core.response.schema import Response

from pdf_processor import PDFProcessor
from config import Config

# Logging konfigurieren
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class QueryEngine:
    """
    Klasse zum Abfragen von indizierten PDF-Dokumenten.
    """

    def __init__(self, index_dir: Optional[str] = None, config: Config = None):
        """
        Initialisiert die Abfrage-Engine.

        Args:
            index_dir: Verzeichnis, aus dem der Index geladen werden soll (optional)
            config: Konfigurationsobjekt (optional)
        """
        self.config = config or Config.initialize()
        self.pdf_processor = PDFProcessor(self.config)

        # Index laden
        index_directory = index_dir or self.config.INDEX_DIR
        self.index = self.pdf_processor.load_index(index_directory)

        if self.index is None:
            logger.warning("Kein Index geladen. Bitte erstellen Sie zuerst einen Index mit dem PDF-Processor.")
        else:
            self.query_engine = self.pdf_processor.create_query_engine()
            logger.info("Abfrage-Engine bereit für Anfragen.")

    def query(self, question: str, max_results: int = 5) -> Dict[str, Any]:
        """
        Stellt eine Frage an die indizierten Dokumente.

        Args:
            question: Die Frage, die beantwortet werden soll
            max_results: Maximale Anzahl an Quellen, die zurückgegeben werden sollen

        Returns:
            Dictionary mit Antwort und Quellen
        """
        if self.index is None or self.query_engine is None:
            logger.error("Keine Abfrage-Engine verfügbar. Bitte laden oder erstellen Sie zuerst einen Index.")
            return {"error": "Keine Abfrage-Engine verfügbar"}

        try:
            # Abfrage durchführen
            response = self.query_engine.query(question)

            # Ergebnis formatieren
            result = {
                "answer": str(response),
                "sources": []
            }

            # Quellen extrahieren (falls vorhanden)
            if hasattr(response, "source_nodes"):
                source_nodes = response.source_nodes[:max_results]

                for node in source_nodes:
                    source = {
                        "text": node.node.text,
                        "score": float(node.score) if hasattr(node, "score") else None,
                        "document": node.node.metadata.get("filename", "Unbekannt"),
                        "page": node.node.metadata.get("page_label", "Unbekannt")
                    }
                    result["sources"].append(source)

            return result

        except Exception as e:
            logger.error(f"Fehler bei der Abfrage: {str(e)}")
            return {"error": f"Fehler bei der Abfrage: {str(e)}"}

    def get_similarity_search(self, query: str, top_k: int = 5) -> List[Dict[str, Any]]:
        """
        Führt eine einfache Ähnlichkeitssuche durch, ohne eine vollständige Antwort zu generieren.

        Args:
            query: Suchanfrage
            top_k: Anzahl der zurückzugebenden Dokumente

        Returns:
            Liste der ähnlichsten Textabschnitte mit Metadaten
        """
        if self.index is None:
            logger.error("Kein Index für die Ähnlichkeitssuche verfügbar.")
            return []

        try:
            # Retriever für Ähnlichkeitssuche erstellen
            retriever = self.index.as_retriever(similarity_top_k=top_k)
            nodes = retriever.retrieve(query)

            results = []
            for node in nodes:
                result = {
                    "text": node.node.text,
                    "score": float(node.score) if hasattr(node, "score") else None,
                    "document": node.node.metadata.get("filename", "Unbekannt"),
                    "page": node.node.metadata.get("page_label", "Unbekannt")
                }
                results.append(result)

            return results

        except Exception as e:
            logger.error(f"Fehler bei der Ähnlichkeitssuche: {str(e)}")
            return []


if __name__ == "__main__":
    # Beispielverwendung
    engine = QueryEngine()
    result = engine.query("Was sind die Hauptthemen in den Dokumenten?")
    print(result["answer"])
    print("\nQuellen:")
    for source in result["sources"]:
        print(f"- Dokument: {source['document']}, Seite: {source['page']}")