# Onshape API Automation - Anleitung

Dieses Python-Skript automatisiert die Änderung von Variablen in Onshape und den Export von CAD-Dateien.

## Features

- ✅ Ändern von Variablen in Onshape Part Studios
- ✅ Export als STEP-Datei
- ✅ Export als Parasolid (.x_t)
- ✅ Automatische Schleife über Wertebereiche
- ✅ Einfach konfigurierbar

## Voraussetzungen

1. **Python 3.6+** installiert
2. **requests** Bibliothek:
   ```bash
   pip install requests
   ```

## Setup

### 1. API Keys erstellen

1. Gehe zu https://cad.onshape.com/appstore/dev-portal
2. Klicke auf "Create new API key"
3. Kopiere **Access Key** und **Secret Key**

### 2. Document-Informationen finden

Öffne dein Onshape-Dokument und schau dir die URL an:

```
https://cad.onshape.com/documents/AAAAAAAAAAAAAAAAAAAAAAAA/w/BBBBBBBBBBBBBBBBBBBBBBBB/e/CCCCCCCCCCCCCCCCCCCCCCCC
```

- `AAAAAAAAAAAAAAAAAAAAAAAA` = **DOCUMENT_ID** (24 Zeichen)
- `BBBBBBBBBBBBBBBBBBBBBBBB` = **WORKSPACE_ID** (24 Zeichen)
- `CCCCCCCCCCCCCCCCCCCCCCCC` = **ELEMENT_ID** (24 Zeichen)

### 3. Variablennamen finden

In deinem Onshape Part Studio:
1. Öffne die Variablentabelle (Tabellensymbol in der Toolbar)
2. Notiere den exakten Namen der Variable, die du ändern möchtest

## Konfiguration

Öffne `onshape_api_automation.py` und passe die Werte in der `main()` Funktion an:

```python
# API Zugangsdaten
ACCESS_KEY = "dein_access_key"
SECRET_KEY = "dein_secret_key"

# Document-Informationen
DOCUMENT_ID = "deine_document_id"
WORKSPACE_ID = "deine_workspace_id"
ELEMENT_ID = "deine_element_id"

# Variable die geändert werden soll
VARIABLE_NAME = "length"  # Name der Variable

# Bereich für die Schleife
START_VALUE = 10.0    # Startwert
END_VALUE = 50.0      # Endwert
STEP_SIZE = 5.0       # Schrittweite

# Export-Einstellungen
OUTPUT_FOLDER = "output"
EXPORT_STEP = True          # STEP exportieren?
EXPORT_PARASOLID = False    # Parasolid exportieren?

# Wartezeit zwischen Iterationen (Sekunden)
DELAY_BETWEEN_ITERATIONS = 2
```

## Verwendung

Führe das Skript aus:

```bash
python onshape_api_automation.py
```

Das Skript wird:
1. Die Variable auf den ersten Wert setzen
2. Die CAD-Datei exportieren
3. Die Variable auf den nächsten Wert setzen
4. Den Prozess wiederholen bis zum Endwert

## Ausgabe

Die exportierten Dateien werden im `output/` Ordner gespeichert mit folgenden Namen:

```
output/
  ├── length_10.step
  ├── length_15.step
  ├── length_20.step
  ├── ...
```

Der Dateiname enthält den Variablennamen und den aktuellen Wert.

## Beispiel-Output

```
============================================================
Starte Onshape API Automation
============================================================
Variable: length
Werte: 10.0 bis 50.0 (Schritt: 5.0)
Anzahl Iterationen: 9
============================================================

--- Iteration 1/9: length = 10.0 ---
✓ Variable 'length' auf 10.0 gesetzt
✓ STEP-Datei exportiert: output/length_10.step

--- Iteration 2/9: length = 15.0 ---
✓ Variable 'length' auf 15.0 gesetzt
✓ STEP-Datei exportiert: output/length_15.step

...
```

## Erweiterte Optionen

### Mehrere Variablen ändern

Du kannst das Skript erweitern, um mehrere Variablen gleichzeitig zu ändern:

```python
# In der Schleife:
api.update_variable(..., "length", value1)
api.update_variable(..., "width", value2)
api.update_variable(..., "height", value3)
```

### Spezifische Teile exportieren

Wenn du nur bestimmte Teile exportieren möchtest:

```python
# Finde Part IDs im API Explorer
part_ids = ["part_id_1", "part_id_2"]
api.export_step(..., part_ids=part_ids)
```

### Andere Formate exportieren

Das Skript kann einfach erweitert werden für:
- STL Export
- IGES Export
- DXF/DWG Export (für Zeichnungen)

## Troubleshooting

### "Fehler beim Abrufen der Variablen: 401"
→ Überprüfe deine API Keys

### "Variable 'xyz' nicht gefunden"
→ Überprüfe den exakten Variablennamen in Onshape

### "Fehler beim STEP-Export: 404"
→ Überprüfe Document ID, Workspace ID und Element ID

### Rate Limiting
Falls du viele Requests machst, erhöhe `DELAY_BETWEEN_ITERATIONS`

## Nützliche Links

- [Onshape API Dokumentation](https://onshape-public.github.io/docs/)
- [API Explorer](https://cad.onshape.com/glassworks/explorer/)
- [API Keys erstellen](https://cad.onshape.com/appstore/dev-portal)

## Lizenz

Dieses Skript ist frei verwendbar. Nutze es für deine eigenen Projekte!
