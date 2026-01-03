from pathlib import Path
import sys
from PIL import Image as PILImage

# Projekt-Root in sys.path aufnehmen
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from mauztoolslib.html import HTMLReader, Script, Paragraph, Image, Heading

def run_tests():
    print("HTMLReader – Tests starten")

    # Test: HTML aus String
    reader = HTMLReader("<html><body>Hello World</body></html>")
    assert reader.to_html() == "<html><body>Hello World</body></html>"
    print("✓ HTML als String lesen")

    # Test: HTML aus Datei
    with open("test_example.html", "w", encoding="utf-8") as file:
        file.write("<html><body>Content of example.html</body></html>")

    with open("test_example.html", "r", encoding="utf-8") as file:
        reader = HTMLReader(file)
        assert reader.to_html() == "<html><body>Content of example.html</body></html>"
    print("✓ HTML aus Datei lesen")
    
    # Test: Zugriff auf HTML-Elemente
    html_content = """<html>
    <head>
        <script src="app.js"></script>
    </head>
    <body>
        <p>This is a paragraph.</p>
        <img src="image.png" alt="An image">
        <h2>Heading 2</h2>
    </body>
</html>"""

    reader = HTMLReader(html_content)

    scripts = reader["script"]
    paragraphs = reader["p"]
    images = reader["img"]
    headings = reader["h2"]

    assert len(scripts) == 1
    assert isinstance(scripts[0], Script)

    assert len(paragraphs) == 1
    assert isinstance(paragraphs[0], Paragraph)

    assert len(images) == 1
    assert isinstance(images[0], Image)

    assert len(headings) == 1
    assert isinstance(headings[0], Heading)

    # Test: PIL-Image in Image
    pil_image = PILImage.new('RGB', (100, 100), color='red')
    new_image = Image(attrs={"alt":"Red image", "src":"test_image_output.png"}, pil_image=pil_image)
    html_img = new_image.to_html()
    assert "alt=" in html_img
    new_image.write_to(open("test_image_output.html", "w", encoding="utf-8"))
    new_image.save("test_image_output.png")

    print("✓ Zugriff auf HTML-Elemente funktioniert")
    print("Alle Tests OK")

if __name__ == "__main__":
    run_tests()
