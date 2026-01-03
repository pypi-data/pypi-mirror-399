from io import TextIOWrapper
import re
from .objects.script import Script
from .objects.paragraph import Paragraph
from .objects.image import Image
from .objects.heading import Heading
from .objects.link import Link

class HTMLReader:
    """
    HTML Reader Klasse ist dafür da, HTML-Inhalte aus einer Datei oder einem String zu lesen und zu verarbeiten.
    Parameter:
        html (TextIOWrapper | str): Entweder ein Dateiobjekt, das HTML-Inhalte enthält, oder ein String mit HTML-Code.
    Attribute:
        html (str): Der HTML-Inhalt als String.
    Raises:
        Keine spezifischen Ausnahmen werden in diesem Konstruktor behandelt.
    Exemple:
        >>> reader = HTMLReader("<html><body>Hello World</body></html>")
        >>> print(reader.to_html())
        <html><body>Hello World</body></html>
        >>> with open("example.html", "r") as file:
        ...     reader = HTMLReader(file)
        >>> print(reader.to_html())
        <html><body>Content of example.html</body></html>
    
    """
    def __init__(self, html: TextIOWrapper | str):
        if isinstance(html, TextIOWrapper):
            self.html = html.read()
        else:
            self.html = html
            
    def to_html(self) -> str:
        """
        Gibt den HTML-Inhalt als String zurück.
        Returns:
            str: Der HTML-Inhalt.
        """
        return self.html
    
    def __str__(self) -> str:
        """
        Gibt den HTML-Objekt als String zurück.
        Returns:
            str: HTML-objekt als String.
        """
        return f"HTMLReader(html={self.html})"
    
    def __repr__(self) -> str:
        """
        Gibt eine offizielle String-Darstellung des HTML-Objekts zurück.
        Returns:
            str: Offizielle String-Darstellung des HTML-Objekts.
        """
        return f"<HTMLReader object={id(self)}, html_length={len(self.html)}, html_preview={self.html[:30]}...>"
    
    def _parse_attrs(self, attr_string: str) -> dict:
        """
        Parst HTML-Attribute aus einem Tag.

        Parameters:
            attr_string (str): Attribut-String aus dem HTML-Tag.

        Returns:
            dict: Attribute als Dictionary.
        """
        return dict(re.findall(r'(\w+)=["\'](.*?)["\']', attr_string))

    def __getitem__(self, key: str):
        """
        Gibt HTML-Elemente eines bestimmten Typs als Objekte zurück.

        Unterstützte Tags:
            - "script" → Script-Objekte
            - "p"      → Paragraph-Objekte
            - "img"    → Image-Objekte
            - "h1"-"h6" → Heading-Objekte

        Parameters:
            key (str): HTML-Tag-Name (z.B. "script", "p", "img", "h1").

        Returns:
            list: Liste von HTML-Objekten der entsprechenden Klasse.

        Raises:
            KeyError: Wenn kein entsprechendes Element gefunden wurde.
        """
        key = key.lower()
        elements = []

        # Bestimmen des Regex-Musters für Tag
        if key in ["script", "p", "a"]:
            pattern = rf"<{key}([^>]*)>(.*?)</{key}>"
        elif key in ["h1","h2","h3","h4","h5","h6"]:
            pattern = rf"<{key}([^>]*)>(.*?)</{key}>"
        elif key == "img":
            pattern = rf"<{key}([^>]*)\/?>"
        else:
            raise KeyError(f"Tag '{key}' wird nicht unterstützt.")

        # Alle Matches im HTML finden
        matches = re.finditer(pattern, self.html, re.IGNORECASE | re.DOTALL)

        for match in matches:
            attr_string = match.group(1)
            if key == "img":
                content = ""
            else:
                content = match.group(2).strip()
            attrs = self._parse_attrs(attr_string)

            if key == "script":
                elements.append(
                    Script(
                        content=content,
                        src=attrs.get("src"),
                        type=attrs.get("type", "text/javascript")
                    )
                )
            elif key == "p":
                elements.append(
                    Paragraph(
                        content=content,
                        attrs=attrs
                    )
                )
            elif key == "img":
                elements.append(
                    Image(
                        attrs=attrs
                    )
                )
            elif key.startswith("h"):
                level = int(key[1])
                elements.append(
                    Heading(
                        level=level,
                        content=content,
                        attrs=attrs
                    )
                )
            elif key == "a":
                elements.append(
                    Link(
                        href=attrs.get("href", ""),
                        text=content,
                        target=attrs.get("target"),
                        rel=attrs.get("rel"),
                        title=attrs.get("title")
                    )
                )

        if not elements:
            raise KeyError(f"Kein Objekt mit dem Schlüssel '{key}' gefunden.")

        return elements
