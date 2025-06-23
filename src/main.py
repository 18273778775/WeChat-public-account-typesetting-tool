# src/main.py - for testing
#from semantic_analyzer import SemanticAnalyzer # Keep for direct use if needed
from smart_templates import SMART_TEMPLATES_MVP # Keep for direct use if needed
from layout_engine import LayoutEngine

def run_layout_engine_test(markdown_text: str, test_name: str, specific_template:str=None):
    engine = LayoutEngine()

    print(f"\n--- Running Layout Engine for: {test_name} ---")
    if specific_template:
        print(f"Attempting with specific template: {specific_template}")

    html_output, selected_template_name = engine.generate_layout(markdown_text, template_name=specific_template)

    print(f"Selected Template by Engine: {selected_template_name}")

    output_filename = f"main_test_{test_name.replace(' ', '_').lower()}"
    if specific_template:
        output_filename += f"_{specific_template.replace(' ', '_').lower()}"
    output_filename += ".html"

    with open(output_filename, "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html lang=\"en\"><head><meta charset='UTF-8'>")
        f.write(f"<title>Main Test - {test_name} ({selected_template_name})</title></head>")
        f.write(html_output)
        f.write("</html>")
    print(f"Saved Layout Engine output to {output_filename}")


if __name__ == '__main__':
    sample_md_content = """
# My Grand Article on Everything

Welcome to this comprehensive piece. We'll cover a lot.
An image to start: ![Placeholder](https://via.placeholder.com/350x100?text=Main+Image)

## Chapter 1: The Beginning
It all started a long time ago.
- Point A
- Point B

## Chapter 2: The Middle
Things got interesting.
```python
# Some python code
x = 10
y = 20
print(x+y)
```

> "A quote that fits here."

## Chapter 3: The End
And that's how it concluded.
1. Step 1
2. Step 2

---
The end.
"""

    # Test automatic selection
    run_layout_engine_test(sample_md_content, "ComprehensiveArticle_Auto")

    # Test with each specific template
    if SMART_TEMPLATES_MVP: # Ensure templates are loaded
        for template_id in SMART_TEMPLATES_MVP.keys():
            run_layout_engine_test(sample_md_content, f"ComprehensiveArticle_Specific_{template_id}", specific_template=template_id)
    else:
        print("Warning: SMART_TEMPLATES_MVP is empty. Skipping specific template tests.")


    # Test a short, image-heavy one for auto-selection
    short_image_md = """
# Quick Update!
![A Pic](https://via.placeholder.com/200x200?text=Update+Pic)
Just a quick one!
    """
    run_layout_engine_test(short_image_md, "ShortImageArticle_Auto")

    # Test a code-heavy one for auto-selection
    code_heavy_md = """
# Code Snippets Galore

```javascript
const arr = [1,2,3];
arr.map(x => x * 2);
```

```python
my_list = [i**2 for i in range(5)]
```

```java
public class HelloWorld {
    public static void main(String[] args) {
        System.out.println("Hello!");
    }
}
```
    """
    run_layout_engine_test(code_heavy_md, "CodeHeavyArticle_Auto")


    print("\nAll main.py layout engine tests complete. Check the generated HTML files.")
