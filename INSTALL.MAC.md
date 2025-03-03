# Installationsanleitung für das PDF-Abfrage-Tool (Mac)

Diese Anleitung führt Sie durch die vollständige Installation und Einrichtung des PDF-Abfrage-Tools für Mac-Benutzer, die noch kein Python installiert haben.

## 1. Python installieren

1. **Python herunterladen**:
    - Besuchen Sie [python.org](https://www.python.org/downloads/)
    - Klicken Sie auf den gelben Button "Download Python x.x.x" (neueste Version)

2. **Python installieren**:
    - Öffnen Sie die heruntergeladene .pkg-Datei
    - Folgen Sie den Anweisungen des Installationsassistenten
    - Geben Sie bei Aufforderung Ihr Administratorpasswort ein
    - Warten Sie, bis die Installation abgeschlossen ist
    - Klicken Sie auf "Close"

3. **Installation überprüfen**:
    - Öffnen Sie das Terminal (über Spotlight: `Cmd + Leertaste`, dann "Terminal" eingeben)
    - Geben Sie folgenden Befehl ein:
      ```
      python3 --version
      ```
    - Sie sollten die installierte Python-Version sehen (z.B. "Python 3.11.4")

## 2. Das PDF-Abfrage-Tool einrichten

1. **Projektordner entpacken**:
    - Entpacken Sie die ZIP-Datei des Projekts in einen Ordner Ihrer Wahl, z.B. in Ihren Dokumente-Ordner

2. **Terminal öffnen**:
    - Öffnen Sie das Terminal
    - Navigieren Sie zum Projektordner:
      ```
      cd ~/Dokumente/PDF-Tool
      ```
   (Ersetzen Sie `~/Dokumente/PDF-Tool` durch den tatsächlichen Pfad zu Ihrem entpackten Projektordner)

3. **Virtuelle Umgebung erstellen**:
   ```
   python3 -m venv .venv
   ```

4. **Virtuelle Umgebung aktivieren**:
   ```
   source .venv/bin/activate
   ```
   Sie sollten nun `(.venv)` am Anfang der Eingabezeile sehen

5. **Erforderliche Pakete installieren**:
   ```
   pip install -r requirements.txt
   ```
   Dies kann je nach Internetgeschwindigkeit einige Minuten dauern.

## 3. Konfiguration einrichten

1. **Konfigurationsdatei erstellen**:
    - Kopieren Sie die Beispiel-Konfigurationsdatei:
      ```
      cp .env.example .env
      ```

2. **Konfigurationsdatei bearbeiten**:
    - Öffnen Sie die `.env`-Datei mit einem Texteditor:
      ```
      open -e .env
      ```
    - Fügen Sie Ihre API-Schlüssel ein:
        - Für OpenAI: Tragen Sie Ihren OpenAI API-Schlüssel neben `OPENAI_API_KEY=` ein
        - Für Anthropic: Tragen Sie Ihren Anthropic API-Schlüssel neben `ANTHROPIC_API_KEY=` ein
    - Wählen Sie Ihren bevorzugten LLM-Provider durch Ändern von `LLM_PROVIDER=`
    - Speichern Sie die Datei (Cmd + S) und schließen Sie den Editor

## 4. PDF-Dateien hinzufügen

1. **PDF-Dateien platzieren**:
    - Platzieren Sie Ihre PDF-Dateien im Ordner `pdfs` im Projektverzeichnis
    - Sie können dies im Terminal tun:
      ```
      mkdir -p pdfs
      ```
    - Oder über den Finder, indem Sie zum Projektordner navigieren und einen Ordner namens "pdfs" erstellen

## 5. Verwendung des Tools

1. **PDFs indizieren**:
   ```
   python main.py index
   ```
   Dieser Vorgang kann je nach Anzahl und Größe Ihrer PDFs einige Zeit in Anspruch nehmen.

2. **Fragen stellen**:
   ```
   python main.py query "Ihre Frage hier"
   ```
   Zum Beispiel:
   ```
   python main.py query "Was sind die Hauptthemen in diesen Dokumenten?"
   ```

3. **Interaktiven Modus verwenden**:
   ```
   python main.py interactive
   ```
   In diesem Modus können Sie mehrere Fragen nacheinander stellen, ohne den Befehl jedes Mal neu eingeben zu müssen.

## Häufige Probleme und Lösungen

### "Python wurde nicht gefunden"
- Versuchen Sie `python3` statt `python` zu verwenden
- Überprüfen Sie, ob Python korrekt installiert wurde mit `which python3`
- Installieren Sie Python erneut, falls nötig

### "ModuleNotFoundError"
- Stellen Sie sicher, dass die virtuelle Umgebung aktiviert ist (Sie sollten `(.venv)` am Anfang der Eingabezeile sehen)
- Führen Sie `pip install -r requirements.txt` erneut aus

### API-Fehler
- Überprüfen Sie, ob Ihre API-Schlüssel korrekt in der `.env`-Datei eingegeben wurden
- Stellen Sie sicher, dass Ihr API-Konto aktiv ist und über ausreichendes Guthaben verfügt

### "Keine PDFs gefunden"
- Überprüfen Sie, ob Sie PDFs im Ordner `pdfs` platziert haben mit `ls -la pdfs/`
- Stellen Sie sicher, dass die Dateien die Endung `.pdf` haben

### Berechtigungsprobleme
- Wenn Sie Berechtigungsfehler erhalten, führen Sie `chmod +x main.py` aus
- Bei Problemen mit dem Zugriff auf den pdfs-Ordner: `chmod -R 755 pdfs/`

## Tipps zur Optimierung

- Passen Sie die Chunk-Größe in der `.env`-Datei an (`CHUNK_SIZE=`) für bessere Ergebnisse
- Bei großen PDF-Sammlungen beschränken Sie die Anzahl der zu verarbeitenden PDFs mit `MAX_PDFS=` in der `.env`-Datei
- Probieren Sie verschiedene Modelle und Provider aus, um das beste Ergebnis zu erzielen

## Deaktivieren der virtuellen Umgebung

Wenn Sie die Arbeit mit dem Tool beendet haben, können Sie die virtuelle Umgebung deaktivieren:
```
deactivate
```
