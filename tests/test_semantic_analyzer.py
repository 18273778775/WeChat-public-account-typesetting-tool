import unittest
from src.semantic_analyzer import SemanticAnalyzer

class TestSemanticAnalyzer(unittest.TestCase):

    def setUp(self):
        self.analyzer = SemanticAnalyzer()

    def test_empty_input(self):
        elements = self.analyzer.parse_markdown_to_elements("")
        self.assertEqual(elements, [])

    def test_simple_paragraph(self):
        md = "This is a simple paragraph."
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["type"], "paragraph")
        self.assertEqual(elements[0]["content"], "This is a simple paragraph.")

    def test_headings(self):
        md = "# H1\n## H2\n### H3"
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0]["type"], "h1")
        self.assertEqual(elements[0]["content"], "H1")
        self.assertEqual(elements[1]["type"], "h2")
        self.assertEqual(elements[1]["content"], "H2")
        self.assertEqual(elements[2]["type"], "h3")
        self.assertEqual(elements[2]["content"], "H3")

    def test_blockquote(self):
        md = "> This is a quote.\n> Second line of quote."
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["type"], "quote")
        self.assertEqual(elements[0]["content"], "This is a quote.\nSecond line of quote.")

    def test_unordered_list(self):
        md = "- Item 1\n- Item 2\n* Item 3" # Mixed markers
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 3)
        self.assertTrue(all(el["type"] == "list_item" for el in elements))
        self.assertEqual(elements[0]["content"], "Item 1")
        self.assertEqual(elements[1]["content"], "Item 2")
        self.assertEqual(elements[2]["content"], "Item 3")

    def test_ordered_list(self):
        md = "1. First\n2. Second"
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 2)
        self.assertTrue(all(el["type"] == "list_item" for el in elements))
        self.assertEqual(elements[0]["content"], "First")
        self.assertEqual(elements[1]["content"], "Second")

    def test_image_standalone(self):
        md = "![Alt text](image.png)"
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["type"], "image")
        self.assertEqual(elements[0]["alt"], "Alt text")
        self.assertEqual(elements[0]["src"], "image.png")

    def test_image_between_paragraphs(self):
        md = "Leading text.\n\n![Alt](src.png)\n\nTrailing text."
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0]["type"], "paragraph")
        self.assertEqual(elements[0]["content"], "Leading text.")
        self.assertEqual(elements[1]["type"], "image")
        self.assertEqual(elements[1]["alt"], "Alt")
        self.assertEqual(elements[2]["type"], "paragraph")
        self.assertEqual(elements[2]["content"], "Trailing text.")

    def test_image_inline_with_text(self):
        md = "Text before ![Alt text](image.png) and text after."
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 2)

        image_el = None
        para_el = None

        if elements[0]['type'] == 'image':
            image_el = elements[0]
            if len(elements) > 1: para_el = elements[1]
        elif len(elements) > 1 and elements[1]['type'] == 'image':
            image_el = elements[1]
            para_el = elements[0]
        else:
             if elements and elements[0]['type'] == 'paragraph': para_el = elements[0]

        self.assertIsNotNone(image_el, "Image element not found or not separated.")
        if image_el:
            self.assertEqual(image_el["type"], "image")
            self.assertEqual(image_el["alt"], "Alt text")
            self.assertEqual(image_el["src"], "image.png")

        self.assertIsNotNone(para_el, "Paragraph element not found or image not separated.")
        if para_el:
            self.assertEqual(para_el["type"], "paragraph")
            self.assertEqual(para_el["content"].strip(), "Text before and text after.")


    def test_code_block(self):
        md = "```python\ndef hello():\n    print('Hello')\n```"
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 1)
        self.assertEqual(elements[0]["type"], "code_block")
        self.assertEqual(elements[0]["language"], "python")
        self.assertEqual(elements[0]["content"], "def hello():\n    print('Hello')")

    def test_horizontal_rule(self):
        md = "Text\n\n---\n\nMore text"
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 3)
        self.assertEqual(elements[0]["type"], "paragraph")
        self.assertEqual(elements[1]["type"], "horizontal_rule")
        self.assertEqual(elements[2]["type"], "paragraph")

    def test_mixed_content(self):
        md = "# Title\n\nPara 1.\n\n> Quote\n\n- List item\n\n![img](src.png)"
        elements = self.analyzer.parse_markdown_to_elements(md)
        self.assertEqual(len(elements), 5)
        self.assertEqual(elements[0]["type"], "h1")
        self.assertEqual(elements[1]["type"], "paragraph")
        self.assertEqual(elements[2]["type"], "quote")
        self.assertEqual(elements[3]["type"], "list_item")
        self.assertEqual(elements[4]["type"], "image")

if __name__ == '__main__':
    unittest.main()
