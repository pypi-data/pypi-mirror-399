from typing import TextIO

class Heading:
    """
    Repräsentiert ein HTML-Heading-Element (<h1> bis <h6>).

    Mit dieser Klasse können Überschriften im HTML-Format erstellt, 
    Attribute hinzugefügt und das Tag direkt als String oder in eine Datei 
    geschrieben werden.

    Attributes:
        level (int): Die Ebene der Überschrift (1 bis 6).
        content (str): Der Textinhalt der Überschrift.
        attrs (dict): Optionales Wörterbuch mit HTML-Attributen (z. B. 'id', 'class', 'style').

    Methods:
        to_html() -> str:
            Gibt das HTML-Tag als String zurück.
        write_to(target: TextIO):
            Schreibt das HTML-Tag direkt in eine Datei oder einen Stream.

    Example:
        >>> h = Heading(2, "Kapitel 1", {"class": "title"})
        >>> print(h.to_html())
        <h2 class="title">Kapitel 1</h2>

        >>> with open("test.html", "w") as f:
        ...     h.write_to(f)
    """

    def __init__(self, level: int, content: str, attrs: dict | None = None):
        self.level = max(1, min(level, 6))  # Level auf 1–6 begrenzen
        self.content = content
        self.attrs = attrs or {}

    def to_html(self) -> str:
        """
        Gibt das HTML-Heading-Tag als String zurück.

        Returns:
            str: HTML-String des Headings mit Attributen, falls vorhanden.
        """
        attr_str = " ".join(f'{k}="{v}"' for k, v in self.attrs.items())
        if attr_str:
            return f"<h{self.level} {attr_str}>{self.content}</h{self.level}>"
        return f"<h{self.level}>{self.content}</h{self.level}>"

    def write_to(self, target: TextIO):
        """
        Schreibt das HTML-Heading-Tag in eine Datei oder einen Stream.

        Args:
            target (TextIO): Datei- oder Stream-Objekt, in das das HTML geschrieben wird.
        """
        target.write(self.to_html())

    def __str__(self) -> str:
        return self.to_html()

    def __repr__(self) -> str:
        return f"<Heading level={self.level} content='{self.content[:30]}' attrs={self.attrs}>"
