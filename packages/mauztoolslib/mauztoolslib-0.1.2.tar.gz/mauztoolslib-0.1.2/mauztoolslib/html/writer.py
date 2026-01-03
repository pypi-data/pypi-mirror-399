from __future__ import annotations
from pathlib import Path
from typing import Iterable, Union


class HTMLWriter:
    """
    HTMLWriter ist eine Hilfsklasse zum Erzeugen und Schreiben von HTML-Code
    aus einzelnen HTML-Objekten (z. B. Paragraph, Script, Image, Heading).

    Unterstützt:
    - Context Manager (`with`)
    - automatisches <!DOCTYPE html>
    - list-ähnliches Verhalten (getitem, setitem, remove, +=)
    """

    def __init__(
        self,
        file: str | Path | None = None,
        *,
        encoding: str = "utf-8",
        auto_doctype: bool = True
    ):
        """
        Initialisiert den HTMLWriter.

        Parameter:
            file: Optionaler Zielpfad für die HTML-Ausgabe.
            encoding: Textkodierung für die Ausgabedatei.
            auto_doctype: Fügt automatisch <!DOCTYPE html> hinzu.
        """
        self._elements: list[object] = []
        self._file = Path(file) if file else None
        self._encoding = encoding
        self._auto_doctype = auto_doctype

    # ==========================================================
    # Context Manager
    # ==========================================================

    def __enter__(self) -> HTMLWriter:
        return self

    def __exit__(self, exc_type, exc, tb) -> None:
        if exc_type is None and self._file:
            self.write_to(self._file)

    # ==========================================================
    # Element-Verwaltung
    # ==========================================================

    def add(self, element: object) -> None:
        """
        Fügt ein HTML-Objekt hinzu.

        Voraussetzung:
            Objekt besitzt eine Methode `to_html() -> str`.
        """
        if not hasattr(element, "to_html"):
            raise TypeError(
                f"{element.__class__.__name__} besitzt keine to_html()-Methode"
            )
        self._elements.append(element)

    def extend(self, elements: Iterable[object]) -> None:
        """
        Fügt mehrere HTML-Objekte hinzu.
        """
        for el in elements:
            self.add(el)

    def remove(self, element: object) -> None:
        """
        Entfernt ein HTML-Objekt aus dem Writer.

        Entspricht dem Verhalten von `list.remove()`.

        Raises:
            ValueError: Wenn das Objekt nicht enthalten ist.
        """
        self._elements.remove(element)

    def clear(self) -> None:
        """
        Entfernt alle HTML-Objekte.
        """
        self._elements.clear()

    # ==========================================================
    # Zugriff (getitem / setitem)
    # ==========================================================

    def __getitem__(self, index: Union[int, slice]):
        """
        Gibt ein oder mehrere HTML-Objekte zurück.

        Beispiele:
            writer[0]
            writer[-1]
            writer[1:3]
        """
        return self._elements[index]

    def __setitem__(self, index: Union[int, slice], value):
        """
        Ersetzt ein oder mehrere HTML-Objekte.

        Voraussetzung:
            Alle neuen Elemente besitzen eine `to_html()`-Methode.
        """
        if isinstance(index, slice):
            for el in value:
                if not hasattr(el, "to_html"):
                    raise TypeError(
                        f"{el.__class__.__name__} besitzt keine to_html()-Methode"
                    )
            self._elements[index] = value
        else:
            if not hasattr(value, "to_html"):
                raise TypeError(
                    f"{value.__class__.__name__} besitzt keine to_html()-Methode"
                )
            self._elements[index] = value

    # ==========================================================
    # Ausgabe
    # ==========================================================

    def to_html(self, pretty: bool = False) -> str:
        """
        Gibt den HTML-Code als String zurück.
        """
        if not self._elements:
            return ""

        sep = "\n" if pretty else ""
        body = sep.join(el.to_html() for el in self._elements)

        if self._auto_doctype:
            return f"<!DOCTYPE html>{sep}{body}"

        return body

    def write_to(self, file: str | Path) -> None:
        """
        Schreibt den HTML-Code in eine Datei.
        """
        path = Path(file)
        path.parent.mkdir(parents=True, exist_ok=True)

        with open(path, "w", encoding=self._encoding) as f:
            f.write(self.to_html(pretty=True))

    # ==========================================================
    # Python-Integration
    # ==========================================================

    def __len__(self) -> int:
        return len(self._elements)

    def __iter__(self):
        return iter(self._elements)

    def __iadd__(self, element: object):
        """
        Ermöglicht: writer += Paragraph("Text")
        """
        self.add(element)
        return self

    def __str__(self) -> str:
        return self.to_html(pretty=True)

    def __repr__(self) -> str:
        return (
            f"<HTMLWriter elements={len(self._elements)}, "
            f"auto_doctype={self._auto_doctype}>"
        )
