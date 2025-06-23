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

    def test_data_paragraph_identification(self):
        test_cases = {
            "percentage_and_currency": "营收达到 ￥1,234,567.89元，利润增长了15.5%。",
            "keywords_and_numbers": "2023年第四季度，活跃用户同比增长20%，达到500万。",
            "multiple_numbers": "数据显示：A为100，B是2500，C为30.5，D是0.5。",
            "formula_like": "计算公式为：X = (Y + Z) / 2 * 用户数。",
            "mixed_financial": "公司年度财报显示，收入为 $5.2M，同比增长 12%。",
            "simple_stats": "平均值为 50.2，标准差为 3.1，最大值为 99.",
            "non_data_para": "这是一段普通的文本，不包含特定的数据指标或金融术语。",
            "borderline_few_numbers": "库存剩余 3 箱，单价 50 元。", # Might be data, might not, depends on threshold
            "long_text_with_few_numbers": "这是一个非常长的段落，它碰巧包含了一个数字，比如 100，但主要内容是关于历史事件的详细描述，而不是数据报告。" * 3 # >500 chars
        }

        expected_types = {
            "percentage_and_currency": "data_paragraph",
            "keywords_and_numbers": "data_paragraph",
            "multiple_numbers": "data_paragraph",
            "formula_like": "data_paragraph", # Basic formula indicators
            "mixed_financial": "data_paragraph",
            "simple_stats": "data_paragraph",
            "non_data_para": "paragraph",
            "borderline_few_numbers": "data_paragraph", # Current regex/heuristics might pick this up due to 2 numbers
            "long_text_with_few_numbers": "paragraph" # Should be paragraph due to length constraint
        }

        for name, md_text in test_cases.items():
            with self.subTest(name=name):
                elements = self.analyzer.parse_markdown_to_elements(md_text)
                self.assertTrue(len(elements) > 0, f"No elements parsed for '{name}'")
                # Assuming these simple test cases result in one primary element (paragraph/data_paragraph)
                # after image extraction (if any, though none here)

                # Filter for paragraph types to test, as other elements like images might be extracted
                para_elements = [el for el in elements if el['type'] in ['paragraph', 'data_paragraph']]
                self.assertTrue(len(para_elements) > 0, f"No paragraph/data_paragraph element found for '{name}'")

                # For these specific tests, we expect exactly one paragraph-like element.
                self.assertEqual(len(para_elements), 1, f"Expected 1 paragraph-like element for '{name}', got {len(para_elements)}")
                self.assertEqual(para_elements[0]["type"], expected_types[name], f"Type mismatch for '{name}'")


if __name__ == '__main__':
    unittest.main()
