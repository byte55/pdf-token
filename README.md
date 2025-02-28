# PDF Tokenizer und Abfrage-Tool

Dieses Tool ermöglicht es Ihnen, mehrere PDF-Dokumente zu tokenisieren, zu indizieren und mit natürlicher Sprache abzufragen. Das Tool unterstützt sowohl OpenAI als auch Anthropic (Claude) als LLM-Provider.

## Voraussetzungen

- Python 3.9 oder höher
- Pip (Python-Paketmanager)

## Installation

1. Klonen oder laden Sie die Skripte herunter
2. Installieren Sie die benötigten Abhängigkeiten:

```bash
pip install -r requirements.txt
```

3. Erstellen Sie eine `.env`-Datei basierend auf der `.env.example`-Datei:

```bash
cp .env.example .env
```

4. Bearbeiten Sie die `.env`-Datei und geben Sie bei Bedarf Ihren OpenAI API-Schlüssel an. Falls Sie ein anderes Modell verwenden möchten, konfigurieren Sie die entsprechenden Einstellungen.

## Verzeichnisstruktur

```
.
├── main.py                # Hauptskript
├── config.py              # Konfigurationsklasse
├── pdf_processor.py       # PDF-Verarbeitungsklasse
├── query_engine.py        # Abfrage-Engine-Klasse
├── .env                   # Konfigurationsdatei (erstellen Sie diese aus .env.example)
├── pdfs/                  # Legen Sie hier Ihre PDF-Dateien ab
└── index_storage/         # Hier wird der Index gespeichert
```

## Verwendung

### PDFs indizieren

Legen Sie Ihre PDF-Dateien im `pdfs`-Verzeichnis (oder dem in der Konfiguration angegebenen Verzeichnis) ab und führen Sie dann folgenden Befehl aus:

```bash
python main.py index
```

Sie können auch ein bestimmtes Verzeichnis angeben:

```bash
python main.py index --pdf_dir /pfad/zu/meinen/pdfs
```

Oder spezifische PDF-Dateien:

```bash
python main.py index --files /pfad/zu/dokument1.pdf /pfad/zu/dokument2.pdf
```

### Abfragen stellen

Nach der Indizierung können Sie Fragen zu Ihren PDF-Dokumenten stellen:

```bash
python main.py query "Was sind die Hauptthemen in diesen Dokumenten?"
```

Sie können auch einen anderen Index verwenden:

```bash
python main.py query "Meine Frage" --index_dir /pfad/zum/index
```

### Interaktiver Modus

Für mehrere Abfragen nacheinander können Sie den interaktiven Modus verwenden:

```bash
python main.py interactive
```

## Anpassung der Parameter

Sie können die Parameter in der `.env`-Datei anpassen:

- `CHUNK_SIZE`: Größe der Textabschnitte (in Zeichen)
- `CHUNK_OVERLAP`: Überlappung zwischen Abschnitten
- `EMBEDDING_MODEL`: Das verwendete Embedding-Modell
- `MAX_PDFS`: Maximale Anzahl an zu verarbeitenden PDFs (0 = alle)
- `LLM_PROVIDER`: Der zu verwendende LLM-Provider (`openai` oder `anthropic`)
- `ANTHROPIC_MODEL`: Das zu verwendende Claude-Modell (z.B. `claude-3-5-sonnet`, `claude-3-opus`)

## Verwendung in eigenen Skripten

Sie können die Klassen aus den Modulen auch in Ihren eigenen Skripten verwenden:

```python
from pdf_processor import PDFProcessor
from query_engine import QueryEngine

# PDFs verarbeiten
processor = PDFProcessor()
processor.process_pdfs()
processor.save_index()

# Abfragen stellen
engine = QueryEngine()
result = engine.query("Meine Frage")
print(result["answer"])
```

## Fehlerbehebung

- **Keine PDFs gefunden**: Stellen Sie sicher, dass die PDF-Dateien im richtigen Verzeichnis liegen und lesbar sind.
- **OpenAI API-Fehler**: Überprüfen Sie, ob Ihr API-Schlüssel korrekt ist und Sie über ausreichendes Guthaben verfügen.
- **Speicherprobleme**: Bei großen PDF-Sammlungen kann es zu Speicherproblemen kommen. Versuchen Sie, die Anzahl der PDFs mit `MAX_PDFS` zu begrenzen oder die Chunk-Größe zu verringern.

## Erweiterte Funktionen

### Embedding-Modell wechseln

Sie können in der `.env`-Datei ein anderes Embedding-Modell einstellen:

```
EMBEDDING_MODEL=sentence-transformers/paraphrase-multilingual-mpnet-base-v2
```

### LLM-Provider wechseln

Sie können zwischen OpenAI und Anthropic (Claude) einfach in der `.env`-Datei wechseln:

```
# Für OpenAI
LLM_PROVIDER=openai
OPENAI_API_KEY=sk-xxxxxxxxxxxxxxxxxxxx

# Für Anthropic Claude
LLM_PROVIDER=anthropic
ANTHROPIC_API_KEY=sk-ant-xxxxxxxxxxxxxxxxxxxx
ANTHROPIC_MODEL=claude-3-5-sonnet
```

Sie können auch ein Testskript ausführen, um die Verbindung zu Anthropic zu testen:

```bash
python anthropic_example.py
```

Falls Sie einen anderen LLM-Provider verwenden möchten (z.B. HuggingFace), müssen Sie den Code in `pdf_processor.py` anpassen:

```python
# Beispiel für HuggingFace
from llama_index.llms.huggingface import HuggingFaceLLM

llm = HuggingFaceLLM(model_name="mistralai/Mistral-7B-Instruct-v0.2")
Settings.llm = llm
```

## Lizenz

Dieses Projekt steht unter der MIT-Lizenz.