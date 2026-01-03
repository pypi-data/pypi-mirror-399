from typing import TextIO

class Script:
    """
    Repräsentiert ein HTML-<script>-Element.

    Unterstützt Inline- und externe Skripte und erlaubt die
    Serialisierung in HTML sowie das direkte Schreiben in
    Datei- oder Stream-Objekte.
    """

    def __init__(
        self,
        content: str,
        type: str = "text/javascript",
        src: str | None = None
    ):
        """
        Initialisiert ein Script-Objekt.

        Parameters:
            content (str): JavaScript-Code.
            type (str): MIME-Type des Skripts.
            src (str | None): Optionaler Pfad oder URL zu einem externen Skript.
        """
        self.content = content
        self.type = type
        self.src = src

    def to_html(self) -> str:
        """
        Gibt das Script als HTML-String zurück.

        Returns:
            str: HTML-Repräsentation des <script>-Tags.
        """
        if self.src:
            return f'<script type="{self.type}" src="{self.src}"></script>'
        return f'<script type="{self.type}">{self.content}</script>'

    def write_to(self, target: TextIO) -> None:
        """
        Schreibt das HTML-Script direkt in ein Datei- oder Stream-Objekt.

        Parameters:
            target (TextIO): Ein schreibbares Objekt mit write()-Methode
                             (z. B. offene Datei, StringIO, sys.stdout).

        Raises:
            TypeError: Wenn das Ziel keine write()-Methode besitzt.
        """
        if not hasattr(target, "write"):
            raise TypeError("write_to() erwartet ein schreibbares TextIO-Objekt")

        target.write(self.to_html())

    def is_external(self) -> bool:
        """
        Prüft, ob es sich um ein externes Skript handelt.

        Returns:
            bool: True, wenn src gesetzt ist.
        """
        return self.src is not None

    def __str__(self) -> str:
        """
        Gibt die HTML-Darstellung zurück.

        Returns:
            str: HTML-String.
        """
        return self.to_html()

    def __repr__(self) -> str:
        """
        Gibt eine technische Debug-Darstellung zurück.

        Returns:
            str: Repräsentation des Script-Objekts.
        """
        location = f"src='{self.src}'" if self.src else "inline"
        return (
            f"<Script type='{self.type}' "
            f"{location} "
            f"length={len(self.content)}>"
        )
