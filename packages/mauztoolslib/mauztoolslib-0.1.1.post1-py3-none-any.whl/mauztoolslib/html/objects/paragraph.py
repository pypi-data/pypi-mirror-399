from typing import TextIO

class Paragraph:
    """
    Repräsentiert ein HTML-<p>-Element.

    Diese Klasse kapselt den Textinhalt eines Absatzes sowie optionale
    HTML-Attribute (z. B. class, id) und erlaubt die Serialisierung
    zurück in HTML.
    """

    def __init__(self, content: str, attrs: dict | None = None):
        """
        Initialisiert ein Paragraph-Objekt.

        Parameters:
            content (str): Textinhalt des Absatzes.
            attrs (dict | None): Optionale HTML-Attribute.
        """
        self.content = content
        self.attrs = attrs or {}

    def to_html(self) -> str:
        """
        Gibt den Paragraph als HTML-String zurück.

        Returns:
            str: HTML-Repräsentation des <p>-Elements.
        """
        attr_string = ""
        if self.attrs:
            attr_string = " " + " ".join(
                f'{k}="{v}"' for k, v in self.attrs.items()
            )

        return f"<p{attr_string}>{self.content}</p>"

    def write_to(self, target: TextIO) -> None:
        """
        Schreibt den Paragraph direkt in ein Datei- oder Stream-Objekt.

        Parameters:
            target (TextIO): Schreibbares Objekt mit write()-Methode.
        """
        if not hasattr(target, "write"):
            raise TypeError("write_to() erwartet ein schreibbares TextIO-Objekt")

        target.write(self.to_html())

    def __str__(self) -> str:
        """
        Gibt die HTML-Darstellung zurück.

        Returns:
            str: HTML-String.
        """
        return self.to_html()

    def __repr__(self) -> str:
        """
        Gibt eine Debug-Repräsentation zurück.

        Returns:
            str: Technische Darstellung des Paragraph-Objekts.
        """
        return (
            f"<Paragraph length={len(self.content)} "
            f"attrs={self.attrs}>"
        )
