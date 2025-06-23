import unittest
from src.layout_engine import LayoutEngine
from src.smart_templates import SMART_TEMPLATES_MVP

class TestLayoutEngine(unittest.TestCase):

    def setUp(self):
        self.engine = LayoutEngine()

    def test_generate_layout_empty_input(self):
        html, template_name = self.engine.generate_layout("")
        self.assertIn("No content to display", html)
        self.assertEqual(template_name, "N/A")

    def test_generate_layout_simple_paragraph_auto_template(self):
        md = "This is a test paragraph."
        html, template_name = self.engine.generate_layout(md)
        self.assertTrue(len(html) > 0)
        self.assertIn(template_name, SMART_TEMPLATES_MVP.keys())
        self.assertIn("This is a test paragraph.", html)
        # Check if body and paragraph styles are applied (presence of style=)
        self.assertIn("<body style=", html)
        self.assertIn("<p style=", html)


    def test_generate_layout_with_specific_template(self):
        md = "# Title\n\nTest content."
        template_to_test = "modern_minimal"
        if template_to_test not in SMART_TEMPLATES_MVP:
            self.skipTest(f"{template_to_test} template not defined.")

        html, template_name = self.engine.generate_layout(md, template_name=template_to_test)
        self.assertEqual(template_name, template_to_test)
        self.assertIn("Title", html)
        self.assertIn("Test content", html)

        # Check for a style specific to modern_minimal if possible
        # For example, modern_minimal h1 has "letter-spacing: -1px"
        # This requires knowing template internals, which is okay for this kind of test.
        expected_h1_style_fragment = SMART_TEMPLATES_MVP[template_to_test]["styles"]["h1"]
        if isinstance(expected_h1_style_fragment, str) and "letter-spacing: -1px" in expected_h1_style_fragment:
             self.assertIn("letter-spacing: -1px", html) # Check if the specific style part is there
        elif isinstance(expected_h1_style_fragment, dict) and expected_h1_style_fragment.get("letter-spacing") == "-1px":
             self.assertIn("letter-spacing: -1px", html)


    def test_template_selection_code_heavy(self):
        md = """
# Code heavy
```python
def foo(): pass
```
```javascript
function bar() {}
```
```java
class Baz {}
```
        """
        _, template_name = self.engine.generate_layout(md)
        # Based on current heuristics, this should pick modern_minimal or classic_reader
        self.assertIn(template_name, ["modern_minimal", "classic_reader"])
        if "modern_minimal" in SMART_TEMPLATES_MVP: # If modern_minimal exists, it should be preferred
            self.assertEqual(template_name, "modern_minimal")


    def test_template_selection_short_with_image(self):
        md = "# Short\n![img](src.png)\nText."
        _, template_name = self.engine.generate_layout(md)
        # Heuristic might pick playful_creative or modern_minimal
        # This test is a bit more volatile if heuristics change often.
        possible_templates = []
        if "playful_creative" in SMART_TEMPLATES_MVP: possible_templates.append("playful_creative")
        if "modern_minimal" in SMART_TEMPLATES_MVP: possible_templates.append("modern_minimal")
        if not possible_templates and "classic_reader" in SMART_TEMPLATES_MVP: possible_templates.append("classic_reader")

        self.assertTrue(template_name in possible_templates if possible_templates else True)


    def test_template_selection_structured_article(self):
        md = "# Title\n## H2_1\nText\n## H2_2\nText\n### H3_1\nText"
        _, template_name = self.engine.generate_layout(md)
        # Heuristic likely picks classic_reader or modern_minimal
        self.assertIn(template_name, ["classic_reader", "modern_minimal"])


    def test_all_templates_run(self):
        md = "# Generic Title\n\nSome generic content for testing all templates."
        if not SMART_TEMPLATES_MVP:
            self.skipTest("No smart templates defined to test.")

        for t_name in SMART_TEMPLATES_MVP.keys():
            with self.subTest(template=t_name):
                html, selected_template = self.engine.generate_layout(md, template_name=t_name)
                self.assertEqual(selected_template, t_name)
                self.assertTrue(len(html) > 0)
                self.assertIn("Generic Title", html)
                self.assertIn("generic content", html)

if __name__ == '__main__':
    unittest.main()
