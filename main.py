# main.py
import argparse
import logging
import os
import sys
import traceback
from pathlib import Path

from config import Config
from pdf_processor import PDFProcessor
from query_engine import QueryEngine
import sys
import traceback

# Logging konfigurieren
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler('pdf_tokenizer.log')
    ]
)
logger = logging.getLogger(__name__)


def setup_argparse():
    """
    Richtet die Kommandozeilenargumente ein.

    Returns:
        ArgumentParser-Objekt
    """
    parser = argparse.ArgumentParser(description="PDF Tokenizer und Abfrage-Tool")
    subparsers = parser.add_subparsers(dest="command", help="Befehle")

    # Indexierungs-Befehl
    index_parser = subparsers.add_parser("index", help="PDFs indizieren")
    index_parser.add_argument(
        "--pdf_dir",
        help="Verzeichnis mit den PDF-Dateien (überschreibt Konfiguration)"
    )
    index_parser.add_argument(
        "--index_dir",
        help="Verzeichnis zum Speichern des Index (überschreibt Konfiguration)"
    )
    index_parser.add_argument(
        "--files",
        nargs="+",
        help="Spezifische PDF-Dateien, die indiziert werden sollen"
    )

    # Abfrage-Befehl
    query_parser = subparsers.add_parser("query", help="Indizierten PDFs abfragen")
    query_parser.add_argument(
        "question",
        help="Frage an die Dokumente"
    )
    query_parser.add_argument(
        "--index_dir",
        help="Verzeichnis mit dem Index (überschreibt Konfiguration)"
    )
    query_parser.add_argument(
        "--max_results",
        type=int,
        default=5,
        help="Maximale Anzahl an Quellen in der Antwort"
    )

    # Interaktiver Modus
    subparsers.add_parser("interactive", help="Interaktiver Abfragemodus")

    return parser


def main():
    """
    Hauptfunktion des Programms.
    """
    try:
        # Konfiguration initialisieren
        config = Config.initialize()

        # Kommandozeilenargumente verarbeiten
        parser = setup_argparse()
        args = parser.parse_args()

        # Wenn kein Befehl angegeben wurde, Hilfe anzeigen
        if not args.command:
            parser.print_help()
            return

        # Indexierungsbefehl
        if args.command == "index":
            logger.info("Starte Indexierungsprozess...")

            # PDF-Verzeichnis überschreiben, falls angegeben
            if args.pdf_dir:
                config.PDF_DIR = args.pdf_dir

            # Index-Verzeichnis überschreiben, falls angegeben
            if args.index_dir:
                config.INDEX_DIR = args.index_dir

            processor = PDFProcessor(config)

            # Spezifische Dateien oder ganzes Verzeichnis verarbeiten
            if args.files:
                # Prüfen, ob alle angegebenen Dateien existieren
                pdf_files = [f for f in args.files if os.path.exists(f) and f.lower().endswith('.pdf')]
                if not pdf_files:
                    logger.error("Keine der angegebenen PDF-Dateien gefunden!")
                    return

                logger.info(f"Verarbeite {len(pdf_files)} spezifische PDF-Dateien...")
                processor.process_pdfs(pdf_files)
            else:
                processor.process_pdfs()

            processor.save_index()
            logger.info("Indexierung abgeschlossen.")

        # Abfragebefehl
        elif args.command == "query":
            # Index-Verzeichnis überschreiben, falls angegeben
            if args.index_dir:
                config.INDEX_DIR = args.index_dir

            engine = QueryEngine(config=config)
            result = engine.query(args.question, max_results=args.max_results)

            if "error" in result:
                logger.error(result["error"])
                return

            print("\n" + "=" * 80)
            print(f"FRAGE: {args.question}")
            print("=" * 80)
            print(f"ANTWORT: {result['answer']}")
            print("=" * 80)

            if result["sources"]:
                print("QUELLEN:")
                for i, source in enumerate(result["sources"], 1):
                    print(f"\n[{i}] Dokument: {source['document']}, Seite: {source['page']}")
                    print(f"    Score: {source['score']:.4f}" if source['score'] else "")
                    print(f"    Text: {source['text'][:500]}...")

        # Interaktiver Modus
        elif args.command == "interactive":
            engine = QueryEngine(config=config)

            print("\n" + "=" * 80)
            print("INTERAKTIVER MODUS - Geben Sie 'exit' oder 'quit' ein, um zu beenden")
            print("=" * 80 + "\n")

            while True:
                question = input("\nFrage: ")

                if question.lower() in ["exit", "quit", "q"]:
                    break

                result = engine.query(question)

                if "error" in result:
                    print(f"Fehler: {result['error']}")
                    continue

                print("\n" + "-" * 80)
                print(f"ANTWORT: {result['answer']}")
                print("-" * 80)

                if result["sources"]:
                    print("QUELLEN:")
                    for i, source in enumerate(result["sources"], 1):
                        print(f"\n[{i}] Dokument: {source['document']}, Seite: {source['page']}")
                        if source['score']:
                            print(f"    Score: {source['score']:.4f}")
                        print(f"    Text: {source['text'][:150]}...")
    except Exception as e:
        logger.error(f"Ein Fehler ist aufgetreten: {str(e)}")
        traceback.print_exc()
        print(f"\nFEHLER: {str(e)}")
        print("Für weitere Details prüfen Sie bitte die Protokolldatei: pdf_tokenizer.log")


if __name__ == "__main__":
    main()
