"""
The Layout Engine is responsible for the higher-level orchestration:
1. Taking raw content (e.g., Markdown).
2. Using the SemanticAnalyzer to get structured elements.
3. Applying basic "Content-to-Template" matching logic (MVP).
4. Using SmartTemplates to generate the final HTML.
"""

from .semantic_analyzer import SemanticAnalyzer
from .smart_templates import elements_to_html, SMART_TEMPLATES_MVP

class LayoutEngine:
    def __init__(self):
        self.analyzer = SemanticAnalyzer()
        # In a more advanced system, templates might be loaded dynamically
        self.available_templates = SMART_TEMPLATES_MVP

    def _select_template_mvp(self, structured_elements: list[dict]) -> str:
        """
        MVP Basic logic to select a template.
        This is highly simplified for now.
        PRD 3.2.3: "根据内容结构（长文/短图文）、风格偏好（极简/商务/活泼）动态生成排版方案（3套候选）"
        For MVP, we'll just use some heuristics and select one.
        User style preference is not yet implemented in MVP.
        """
        num_elements = len(structured_elements)
        num_headings = sum(1 for el in structured_elements if el["type"].startswith("h"))
        num_images = sum(1 for el in structured_elements if el["type"] == "image")
        num_code_blocks = sum(1 for el in structured_elements if el["type"] == "code_block")

        # Heuristic 1: If many code blocks, maybe a more technical/modern template
        if num_code_blocks > 2 or (num_code_blocks > 0 and "modern_minimal" in self.available_templates):
            # Prefer modern_minimal if it exists and there's code
            # (as it has specific dark code block styling)
            if "modern_minimal" in self.available_templates:
                 return "modern_minimal"
            elif "classic_reader" in self.available_templates: # Fallback
                return "classic_reader"


        # Heuristic 2: If very short with an image, could be playful or minimal
        if num_elements < 10 and num_images > 0:
            if "playful_creative" in self.available_templates:
                return "playful_creative"
            elif "modern_minimal" in self.available_templates:
                return "modern_minimal"

        # Heuristic 3: If many headings (structured article), classic reader is a safe bet
        if num_headings > 3:
            if "classic_reader" in self.available_templates:
                return "classic_reader"
            elif "modern_minimal" in self.available_templates: # Fallback
                return "modern_minimal"

        # Default fallback
        if "classic_reader" in self.available_templates:
            return "classic_reader"
        elif "modern_minimal" in self.available_templates:
            return "modern_minimal"
        elif "playful_creative" in self.available_templates:
            return "playful_creative"
        else:
            # Should not happen if SMART_TEMPLATES_MVP is populated
            return list(self.available_templates.keys())[0] if self.available_templates else None


    def generate_layout(self, markdown_text: str, template_name: str = None) -> tuple[str, str]:
        """
        Generates HTML layout from markdown text.
        If template_name is not provided, it attempts to select one.
        Returns a tuple: (html_output, selected_template_name)
        """
        structured_elements = self.analyzer.parse_markdown_to_elements(markdown_text)

        if not structured_elements:
            return "<body><p>No content to display.</p></body>", "N/A"

        selected_template_name = template_name
        if not selected_template_name:
            selected_template_name = self._select_template_mvp(structured_elements)

        if not selected_template_name:
             # Fallback if selection somehow fails and no default template exists
            return "<body><p>Error: No template available or could be selected.</p></body>", "Error"

        html_output = elements_to_html(structured_elements, selected_template_name)
        return html_output, selected_template_name


if __name__ == '__main__':
    engine = LayoutEngine()

    sample_md_tech = """
# Understanding Async in Python

This is about `async` and `await`.

```python
import asyncio

async def main():
    print("Hello")
    await asyncio.sleep(1)
    print("World")

asyncio.run(main())
```

Another code block:
```javascript
console.log("Hello from JS");
```

And one more for good measure.
```rust
fn main() {
    println!("Hello from Rust!");
}
```
Conclusion.
    """

    sample_md_short_image = """
# My Trip to the Beach

![Beach Image](https://via.placeholder.com/300x200?text=Beach+Fun)

It was sunny!
    """

    sample_md_structured_article = """
# The History of Computing

## Early Days
Bla bla bla.

## The Mainframe Era
More text.

## Personal Computers
Even more text.

### Apple vs IBM
Details.

## The Internet Age
Final words.
    """

    sample_md_generic = """
# A Simple Post
Just some text here, nothing too fancy.
This could be anything, really.
    """

    test_cases = {
        "Technical Article": sample_md_tech,
        "Short with Image": sample_md_short_image,
        "Structured Long Article": sample_md_structured_article,
        "Generic Short Article": sample_md_generic
    }

    for name, md_content in test_cases.items():
        print(f"\n--- Testing Layout Engine for: {name} ---")
        html, selected_template = engine.generate_layout(md_content)
        print(f"Input Markdown:\n{md_content[:100]}...")
        print(f"Selected Template: {selected_template}")

        output_filename = f"layout_engine_output_{name.replace(' ', '_').lower()}.html"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html lang=\"en\"><head><meta charset='UTF-8'>")
            f.write(f"<title>Layout Engine - {name} ({selected_template})</title></head>")
            f.write(html)
            f.write("</html>")
        print(f"Saved output to {output_filename}")

    # Test with a specific template
    print("\n--- Testing Layout Engine with specific template ('playful_creative') ---")
    html_playful, selected_playful = engine.generate_layout(sample_md_generic, template_name="playful_creative")
    print(f"Selected Template: {selected_playful}")
    output_filename_playful = "layout_engine_output_generic_playful.html"
    with open(output_filename_playful, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang=\"en\"><head><meta charset='UTF-8'>")
        f.write(f"<title>Layout Engine - Generic (Playful)</title></head>")
        f.write(html_playful)
        f.write("</html>")
    print(f"Saved output to {output_filename_playful}")
