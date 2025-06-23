"""
Defines the structure for "Smart Templates" and basic HTML generation for MVP.
"""
import html

# For MVP, smart templates are dictionaries defining basic CSS-like rules for elements.
# In a more advanced system, these could be more complex objects or even small programs.

DEFAULT_STYLES = {
    "body": {"font-family": "sans-serif", "line-height": "1.6"},
    "h1": {"font-size": "2.5em", "margin-top": "0.8em", "margin-bottom": "0.4em", "color": "#333"},
    "h2": {"font-size": "2em", "margin-top": "0.8em", "margin-bottom": "0.4em", "color": "#444"},
    "h3": {"font-size": "1.5em", "margin-top": "0.8em", "margin-bottom": "0.4em", "color": "#555"},
    "paragraph": {"margin-bottom": "1em", "color": "#333"},
    "quote": {
        "border-left": "4px solid #ccc",
        "padding-left": "1em",
        "margin-left": "0",
        "margin-bottom": "1em",
        "font-style": "italic",
        "color": "#555"
    },
    "list_item": {"margin-bottom": "0.5em"}, # Styling will be on ul/ol primarily
    "ul": {"margin-bottom": "1em", "padding-left": "2em"},
    "ol": {"margin-bottom": "1em", "padding-left": "2em"},
    "code_block": {
        "background-color": "#f4f4f4",
        "padding": "1em",
        "border-radius": "4px",
        "overflow-x": "auto",
        "font-family": "monospace",
        "margin-bottom": "1em"
    },
    "image": { # Already a dict, good. For consistency, let's make it explicit.
        "max-width": "100%",
        "height": "auto",
        "display": "block",
        "margin-top": "0.5em",
        "margin-bottom": "1em",
        "border": "1px solid #eee"
    },
    "horizontal_rule": "border: 0; border-top: 1px solid #ccc; margin: 2em 0;"
}

SMART_TEMPLATES_MVP = {
    "classic_reader": {
        "name": "Classic Reader",
        "description": "A clean, traditional layout focused on readability.",
        "styles": {
            **DEFAULT_STYLES, # Start with default and override
            "h1": "font-size: 2.8em; margin-bottom: 0.5em; color: #2c3e50; border-bottom: 2px solid #3498db;",
            "h2": "font-size: 2.2em; margin-bottom: 0.4em; color: #34495e;",
            "paragraph": "font-size: 1.1em; color: #34495e; text-align: justify;",
            "quote": "border-left: 5px solid #3498db; padding-left: 15px; margin-left: 10px; color: #555; font-style: italic;",
            "code_block": {
                **DEFAULT_STYLES["code_block"], # Now this works as expected
                "background-color": "#2c3e50", # Dark code block override
                "color": "#ecf0f1", # New property for this template
                "border": "1px solid #34495e", # New property for this template
            }
        }
    },
    "modern_minimal": {
        "name": "Modern Minimal",
        "description": "A sleek, modern layout with ample whitespace.",
        "styles": {
            **DEFAULT_STYLES,
            "body": "font-family: 'Helvetica Neue', Arial, sans-serif; line-height: 1.7; background-color: #fdfdfd;",
            "h1": "font-size: 3em; font-weight: bold; margin-bottom: 0.6em; color: #1a1a1a; letter-spacing: -1px;",
            "h2": "font-size: 2.3em; font-weight: bold; margin-bottom: 0.5em; color: #2a2a2a; letter-spacing: -0.5px;",
            "h3": "font-size: 1.8em; font-weight: bold; margin-bottom: 0.4em; color: #3a3a3a;",
            "paragraph": "font-size: 1.05em; color: #4f4f4f; margin-bottom: 1.2em;",
            "quote": "border-left: 3px solid #1abc9c; padding: 10px 20px; margin: 20px 0; background-color: #f8f9fa; color: #333;",
            "image": {
                **DEFAULT_STYLES["image"],
                "border-radius": "8px",
                "box-shadow": "0 4px 12px rgba(0,0,0,0.08);",
                 "margin-top": "1em;",
                 "margin-bottom": "1.5em;"
            },
            "code_block": {
                 **DEFAULT_STYLES["code_block"],
                "background-color": "#2d2d2d",
                "color": "#f0f0f0",
                "border": "none",
                "border-radius": "6px",
                "font-family": "'Fira Code', 'Courier New', monospace"
            }
        }
    },
    "playful_creative": {
        "name": "Playful Creative",
        "description": "A more colorful and dynamic layout.",
        "styles": {
            **DEFAULT_STYLES,
            "body": "font-family: 'Comic Sans MS', cursive, sans-serif; line-height: 1.5; background-color: #fff8e1;", # Example playful font
            "h1": "font-size: 2.7em; color: #ff6f61; text-shadow: 2px 2px #f9a825;",
            "h2": "font-size: 2.1em; color: #6a1b9a;",
            "h3": "font-size: 1.6em; color: #00796b;",
            "paragraph": "font-size: 1em; color: #4e342e;",
            "quote": "border: 2px dashed #ff6f61; padding: 15px; margin: 15px; background-color: #fff0cb; color: #bf360c; border-radius:10px;",
            "image": {
                **DEFAULT_STYLES["image"],
                "border": "3px solid #ff6f61",
                "transform": "rotate(-1deg);", # Slight rotation
                "margin-bottom": "1.5em;"
            },
            "ul": {**DEFAULT_STYLES["ul"], "list-style-type": "'🎨 '"}, # Emoji bullet
            "ol": {**DEFAULT_STYLES["ol"], "list-style-type": "decimal-leading-zero;"},
             "code_block": {
                **DEFAULT_STYLES["code_block"],
                "background-color": "#e1f5fe",
                "color": "#01579b",
                "border": "2px dotted #0277bd",
            }
        }
    }
}


def apply_styles_to_element(element_type: str, content: str, styles: dict, tag: str = None, attributes: str = "") -> str:
    """
    Applies styling to a given HTML element.
    `tag` defaults to `element_type` if not provided (e.g. 'p' for 'paragraph').
    """
    html_tag = tag if tag else element_type
    if element_type == "paragraph" and not tag: # Default tag for paragraph
        html_tag = "p"

    style_str = styles.get(element_type, "")
    if isinstance(style_str, dict): # For complex styles like image with multiple properties
        style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in style_str.items())

    # Basic HTML escaping for content to prevent XSS if content is directly used.
    # In a real scenario, use a proper templating engine or HTML builder.
    import html
    escaped_content = html.escape(content) if content else ""

    if not style_str: # Fallback if no specific style, but still wrap in tag
        return f"<{html_tag} {attributes}>{escaped_content}</{html_tag}>"

    return f"<{html_tag} style=\"{style_str}\" {attributes}>{escaped_content}</{html_tag}>"


def elements_to_html(structured_elements: list[dict], template_name: str) -> str:
    """
    Converts a list of structured elements into an HTML string using a specified smart template.
    """
    if template_name not in SMART_TEMPLATES_MVP:
        raise ValueError(f"Template '{template_name}' not found.")

    template = SMART_TEMPLATES_MVP[template_name]
    styles = template["styles"]

    html_parts = []

    # Apply body style if present
    body_style_str = styles.get("body", "")
    if isinstance(body_style_str, dict):
         body_style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in body_style_str.items())
    html_parts.append(f"<body style=\"{body_style_str}\">")

    # Process elements
    # This is a simplified direct-to-HTML conversion. A real engine might build a DOM.
    i = 0
    while i < len(structured_elements):
        element = structured_elements[i]
        el_type = element["type"]
        el_content = element.get("content", "")

        if el_type.startswith("h"): # h1, h2, h3
            html_parts.append(apply_styles_to_element(el_type, el_content, styles, tag=el_type))
        elif el_type == "paragraph":
            html_parts.append(apply_styles_to_element(el_type, el_content, styles, tag="p"))
        elif el_type == "quote":
            # Quotes might contain multiple lines of "content" if parsed from complex blockquotes
            # For MVP, we assume content is a single string or joined by semantic_analyzer
            html_parts.append(apply_styles_to_element(el_type, el_content, styles, tag="blockquote"))
        elif el_type == "list_item":
            # This requires handling ul/ol wrappers.
            # Group consecutive list items.
            list_items_content = []

            # Determine if it's part of an ordered or unordered list
            # This is a heuristic; markdown-it tokens provide bullet_list_open/ordered_list_open
            # Our current SemanticAnalyzer flattens this for MVP.
            # We'll infer based on the raw content for now.
            is_ordered = element.get("raw", "").strip().startswith(("1.", "2.", "3.", "4.", "5.", "6.", "7.", "8.", "9."))
            list_tag = "ol" if is_ordered else "ul"

            list_items_content.append(f"<li style=\"{styles.get('list_item', '')}\">{html.escape(el_content)}</li>")

            # Collect subsequent list items of the same type
            j = i + 1
            while j < len(structured_elements) and structured_elements[j]["type"] == "list_item":
                next_item_raw = structured_elements[j].get("raw", "").strip()
                # Rudimentary check if it's the same type of list.
                # This is fragile and should be improved by better semantic analysis output.
                if (is_ordered and next_item_raw.startswith(tuple(f"{k}." for k in range(10)))) or \
                   (not is_ordered and next_item_raw.startswith(("- ", "* "))):
                    list_items_content.append(f"<li style=\"{styles.get('list_item', '')}\">{html.escape(structured_elements[j].get('content', ''))}</li>")
                    j += 1
                else:
                    break # Different list type or not a list item

            list_style = styles.get(list_tag, "")
            if isinstance(list_style, dict):
                list_style = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in list_style.items())

            html_parts.append(f"<{list_tag} style=\"{list_style}\">{''.join(list_items_content)}</{list_tag}>")
            i = j -1 # Adjust outer loop index

        elif el_type == "code_block":
            lang = element.get("language")
            lang_class = f"language-{lang}" if lang else ""
            # For MVP, style is applied directly. In future, class + CSS sheet is better.
            code_style = styles.get("code_block", "")
            if isinstance(code_style, dict):
                code_style = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in code_style.items())

            # Wrap content in <pre><code> for semantic HTML and styling
            escaped_code = html.escape(el_content)
            html_parts.append(f"<pre style=\"{code_style}\"><code class=\"{lang_class}\">{escaped_code}</code></pre>")

        elif el_type == "image":
            alt_text = html.escape(element.get("alt", ""))
            src_url = element.get("src", "") # Assuming src is safe or will be sanitized later
            img_style = styles.get("image", "")
            if isinstance(img_style, dict):
                img_style = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in img_style.items())

            html_parts.append(f"<img src=\"{src_url}\" alt=\"{alt_text}\" style=\"{img_style}\">")

        elif el_type == "horizontal_rule":
            hr_style = styles.get("horizontal_rule", "")
            if isinstance(hr_style, dict):
                hr_style = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in hr_style.items())
            html_parts.append(f"<hr style=\"{hr_style}\">")

        i += 1

    html_parts.append("</body>")
    return "\n".join(html_parts)


if __name__ == '__main__':
    # Sample structured elements (output from SemanticAnalyzer)
    sample_elements_for_html = [
        {'type': 'h1', 'content': 'Main Title Example', 'raw': '# Main Title Example'},
        {'type': 'paragraph', 'content': 'This is the first paragraph of our article.', 'raw': '...'},
        {'type': 'image', 'alt': 'A beautiful scenery', 'src': 'http://example.com/scenery.jpg', 'raw': '...'},
        {'type': 'h2', 'content': 'A Subheading', 'raw': '## A Subheading'},
        {'type': 'paragraph', 'content': 'Followed by more text and details.', 'raw': '...'},
        {'type': 'quote', 'content': 'This is an insightful quote from someone important.', 'raw': '> ...'},
        {'type': 'list_item', 'content': 'First item in a list', 'raw': '- ...'},
        {'type': 'list_item', 'content': 'Second item in a list', 'raw': '- ...'},
        {'type': 'list_item', 'content': 'Third item', 'raw': '* ...'},
        {'type': 'code_block', 'language': 'python', 'content': 'print("Hello from code!")', 'raw': '```python...'},
        {'type': 'paragraph', 'content': 'An ordered list coming up.', 'raw': '...'},
        {'type': 'list_item', 'content': 'Item A', 'raw': '1. ...'},
        {'type': 'list_item', 'content': 'Item B', 'raw': '2. ...'},
        {'type': 'horizontal_rule', 'content': None, 'raw': '---'}
    ]

    print("--- Classic Reader Template Output ---")
    html_output_classic = elements_to_html(sample_elements_for_html, "classic_reader")
    print(html_output_classic)
    # with open("classic_reader_sample.html", "w", encoding="utf-8") as f:
    #     f.write(html_output_classic)

    print("\n--- Modern Minimal Template Output ---")
    html_output_modern = elements_to_html(sample_elements_for_html, "modern_minimal")
    print(html_output_modern)
    # with open("modern_minimal_sample.html", "w", encoding="utf-8") as f:
    #     f.write(html_output_modern)

    print("\n--- Playful Creative Template Output ---")
    html_output_playful = elements_to_html(sample_elements_for_html, "playful_creative")
    print(html_output_playful)
    # with open("playful_creative_sample.html", "w", encoding="utf-8") as f:
    #     f.write(html_output_playful)

    # Test with elements from semantic_analyzer
    from semantic_analyzer import SemanticAnalyzer
    analyzer = SemanticAnalyzer()
    complex_md_for_template = """
# Exploring Smart Templates

This document tests the HTML generation from structured elements.

## Images and Text

Here's an image: ![A placeholder image](https://via.placeholder.com/400x150/2c3e50/ecf0f1?text=Placeholder+Image)

Followed by a paragraph that explains the context of the image and the subsequent sections.

## Quotes and Lists

> "The only way to do great work is to love what you do." - Steve Jobs
> This is a second line in the same quote.

Let's see a list:
- Apples
- Oranges
- Bananas
  - Yellow Bananas (nested - current HTML is flat)
- Pears

And an ordered one:
1. Requirement gathering
2. Design
3. Implementation
4. Testing

## Code Blocks

A simple Python snippet:
```python
class Greeter:
    def __init__(self, name):
        self.name = name

    def greet(self):
        print(f"Hello, {self.name}!")

greeter = Greeter("World")
greeter.greet()
```

---

This concludes our test document.
    """
    parsed_elements_from_analyzer = analyzer.parse_markdown_to_elements(complex_md_for_template)

    print("\n--- Classic Reader with Analyzer Output ---")
    html_output_analyzer_classic = elements_to_html(parsed_elements_from_analyzer, "classic_reader")
    print(html_output_analyzer_classic)
    # with open("classic_analyzer_sample.html", "w", encoding="utf-8") as f:
    #     f.write(html_output_analyzer_classic)

    print("\n--- Modern Minimal with Analyzer Output ---")
    html_output_analyzer_modern = elements_to_html(parsed_elements_from_analyzer, "modern_minimal")
    # print(html_output_analyzer_modern) # Keep output smaller for agent log
    with open("modern_analyzer_sample.html", "w", encoding="utf-8") as f:
        f.write("<!DOCTYPE html><html><head><meta charset='UTF-8'><title>Modern Minimal Sample</title></head>")
        f.write(html_output_analyzer_modern)
        f.write("</html>")
    print("Saved to modern_analyzer_sample.html")
