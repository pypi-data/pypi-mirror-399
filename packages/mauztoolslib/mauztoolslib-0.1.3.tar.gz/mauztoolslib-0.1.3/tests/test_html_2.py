# Test nur HTML-Ausgabe mit HTMLWriter
from mauztoolslib.html import HTMLWriter, Paragraph, Script, Heading, Image

def test_htmlwriter_minimal():
    print("=== HTMLWriter Minimal Test ===")

    # Neues HTMLWriter-Objekt
    writer = HTMLWriter(auto_doctype=True)

    # Paragraph hinzufügen
    writer.add(Paragraph("Dies ist ein Paragraph."))

    # Heading hinzufügen
    writer.add(Heading(content="Überschrift H1", level=1))

    # Script hinzufügen
    writer.add(Script("console.log('Hallo Welt');"))

    # Image hinzufügen (nur HTML-Attribute, kein PIL)
    writer.add(Image(attrs={"src": "bild.png", "alt": "Beispielbild"}))

    # HTML generieren
    html_code = writer.to_html(pretty=True)
    print("Generiertes HTML:\n")
    print(html_code)
    
    script = Script("""
    function begruessung() {
        alert('Willkommen auf der Seite!');
    }
    function verabschiedung() {
        alert('Auf Wiedersehen!');
    }
                    """)
    
    script.write_to()
    
    print("\nExternes Script 'test_script.js' wurde erstellt.")
    with HTMLWriter("test_with_example_2.html", auto_doctype=True) as writer_cm:
        writer_cm.add(Paragraph("Paragraph im Context Manager"))
        writer_cm.add(Heading(content="Überschrift H2 im CM", level=2))
        writer_cm.add(script)
        writer_cm.add(Image(attrs={"src": "test_image_output.png", "alt": "CM Bild"}))
        writer_cm.add()
        html_code_cm = writer_cm.to_html(pretty=True)
        
    print("\nGeneriertes HTML im Context Manager:\n")
    print(html_code_cm)

if __name__ == "__main__":
    test_htmlwriter_minimal()
