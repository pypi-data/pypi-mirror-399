from typing import TextIO

class Link:
    """
    Repräsentiert ein HTML-Link-Element (<a>).

    Parameter:
        href (str): Die URL, auf die der Link zeigt.
        text (str): Der sichtbare Text des Links.
        target (str | None): Ziel-Attribut, z. B. "_blank".
        rel (str | None): Rel-Attribut, z. B. "noopener noreferrer".
        title (str | None): Title-Attribut.
    
    Methoden:
        to_html() -> str: Gibt den HTML-Code des Links zurück.
        write_to(file: TextIO) -> None: Schreibt das HTML in eine geöffnete Textdatei.
        __str__(): String-Darstellung.
        __repr__(): Offizielle String-Darstellung.

    Exemple:
        >>> link = Link("https://example.com", "Beispiel")
        >>> print(link.to_html())
        <a href="https://example.com">Beispiel</a>
        >>> with open("link.html", "w", encoding="utf-8") as f:
        ...     link.write_to(f)
    """
    def __init__(self, href: str, text: str, target: str | None = None, rel: str | None = None, title: str | None = None):
        self.href = href
        self.text = text
        self.target = target
        self.rel = rel
        self.title = title

    def to_html(self) -> str:
        attrs = [f'href="{self.href}"']
        if self.target:
            attrs.append(f'target="{self.target}"')
        if self.rel:
            attrs.append(f'rel="{self.rel}"')
        if self.title:
            attrs.append(f'title="{self.title}"')
        return f'<a {" ".join(attrs)}>{self.text}</a>'

    def write_to(self, file: TextIO) -> None:
        """
        Schreibt den HTML-Code des Links in ein geöffnetes Text-Dateiobjekt.

        Parameter:
            file (TextIO): Ein offenes Textdateiobjekt im Schreibmodus.
        """
        file.write(self.to_html())

    def __str__(self) -> str:
        return f'Link(href={self.href}, text={self.text})'

    def __repr__(self) -> str:
        return f'<Link href={self.href!r} text={self.text!r} target={self.target!r}>'
