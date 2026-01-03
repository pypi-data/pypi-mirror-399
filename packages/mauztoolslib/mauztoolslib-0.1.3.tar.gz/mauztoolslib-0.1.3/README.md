# mauztoolslib – Dokumentation

Dies ist die Dokumentation für die `mauztoolslib`-Bibliothek.
Aktuell enthält die Bibliothek **`disklib`** für Festplatten- und Speicherinformationen, die **Path-Klasse**, eine **Export-Funktion** sowie die **HTML-Bibliothek** zur Analyse und Manipulation von HTML-Inhalten.

---

## Installation

```bash
pip install mauztoolslib
```

> Hinweis: `mauztoolslib` enthält aktuell `disklib`, HTML-Tools (`HTMLReader`, `Paragraph`, `Script`, `Image`, `Heading`), `Path` und `export`.

---

## Verwendung

### DiskUsage

```python
from mauztoolslib.disklib import DiskUsage

disk = DiskUsage("C:/", "GB")
disk.free_on()
disk.usage_on()
disk.total_on()
print(disk)
```

### Export

Die Export-Funktion erlaubt das Speichern von `DiskUsage`-Instanzen in JSON, CSV oder Excel.

```python
from mauztoolslib.disklib import DiskUsage, export

disk = DiskUsage("C:/", "GB")
disk.free_on()
disk.usage_on()
disk.total_on()

# Export als JSON
export(disk, format="json", filename="disk.json")

# Export als CSV
export(disk, format="csv", filename="disk.csv")

# Export als Excel
export(disk, format="excel", filename="disk.xlsx")
```

**Wichtige Hinweise:**

* `obj` muss eine erlaubte Klasse sein (`DiskUsage`)
* `format` kann `json`, `csv` oder `excel` sein
* `filename` kann ein String oder `Path`-Objekt sein

### HTML-Bibliothek

```python
from mauztoolslib.html import HTMLReader, Script, Paragraph, Image, Heading

html_content = """<html>
<head>
    <script src="app.js"></script>
</head>
<body>
    <p>Hello World</p>
    <img src="logo.png" alt="Logo">
    <h1>Main Heading</h1>
</body>
</html>"""

reader = HTMLReader(html_content)

scripts = reader["script"]
paragraphs = reader["p"]
images = reader["img"]
headings = reader["h1"]
```

#### Script, Paragraph, Image, Heading

Siehe vorherige Beispiele (Methoden: `to_html()`, `write_to(target)`, `save(path)` für Image).

### Path

```python
from mauztoolslib.disklib import Path

p = Path("example.txt")
p.write_text("Hallo Welt")
print(p.read_text())

folder = Path("example_folder")
folder.mkdir(parents=True, exist_ok=True)
new_folder = Path("copy_folder")
folder.copy_to(new_folder)
```

---

## Fehlerbehandlung

* HTMLReader wirft **KeyError**, wenn ein angefragtes Tag nicht existiert.
* Image wirft **ValueError**, wenn `save()` ohne PIL-Image aufgerufen wird.
* Path-Methoden werfen **OSError**, **FileNotFoundError** oder **NotADirectoryError**.
* Export-Funktion wirft **TypeError**, wenn die Klasse nicht erlaubt ist, und **ValueError**, wenn das Format unbekannt ist.

---

## Lizenz

`mauztoolslib` ist unter der MIT-Lizenz lizenziert.
