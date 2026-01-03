# mauztoolslib – Dokumentation

Dies ist die Dokumentation für die `mauztoolslib`-Bibliothek, die derzeit **nur `disklib`** enthält, um Festplatten- und Speicherinformationen abzurufen.

---

## Installation

```bash
pip install mauztoolslib
```

> Hinweis: `mauztoolslib` enthält aktuell nur `disklib`.

---

## Verwendung

Hier ein Beispiel für die Nutzung von `disklib` innerhalb von `mauztoolslib`:

```python
from mauztoolslib.disklib import DiskUsage

# DiskUsage für Laufwerk C: in GB
disk = DiskUsage("C:/", "GB")

disk.free_on()
disk.usage_on()
disk.total_on()

print(disk)
```

---

## Klassen und Methoden

### DiskUsage

Die `DiskUsage`-Klasse ermöglicht das Abrufen von Festplattennutzungsinformationen.

#### Initialisierung

```python
disk = DiskUsage(pfad: str, einheit: str = "GB")
```

* `pfad`: Pfad des Laufwerks oder Verzeichnisses.
* `einheit`: Einheit für die Anzeige (B, KB, MB, GB, TB). Standard ist "GB".

#### Methoden

* `free_on()`: Ruft den freien Speicherplatz ab.
* `usage_on()`: Ruft den verwendeten Speicherplatz ab.
* `total_on()`: Ruft den gesamten Speicherplatz ab.
* `free_print(sprache: str = "DE") -> str`: Gibt freien Speicherplatz als String zurück.
* `usage_print(sprache: str = "DE") -> str`: Gibt verwendeten Speicherplatz als String zurück.
* `total_print(sprache: str = "DE") -> str`: Gibt gesamten Speicherplatz als String zurück.
* `get_einheit_auto(update: bool = False) -> str`: Bestimmt automatisch die passende Einheit.

---

## Fehlerbehandlung

* `NotValidPfadError`: Ausgelöst, wenn der angegebene Pfad ungültig ist.
* `NotValidEinheitError`: Ausgelöst, wenn die angegebene Einheit ungültig ist.

---

## Lizenz

`mauztoolslib` ist unter der MIT-Lizenz lizenziert.
