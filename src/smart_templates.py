"""
Defines the structure for "Smart Templates" and basic HTML generation for MVP.
"""
import html
import re

DEFAULT_STYLES = {
    "body": {"font-family": "sans-serif", "line-height": "1.6"},
    "h1": {"font-size": "2.5em", "margin-top": "0.8em", "margin-bottom": "0.4em", "color": "#333"},
    "h2": {"font-size": "2em", "margin-top": "0.8em", "margin-bottom": "0.4em", "color": "#444"},
    "h3": {"font-size": "1.5em", "margin-top": "0.8em", "margin-bottom": "0.4em", "color": "#555"},
    "paragraph": {"margin-bottom": "1em", "color": "#333"},
    "data_paragraph": {
        "margin-bottom": "1em",
        "color": "#003366",
        "background-color": "#f0f8ff",
        "border-left": "4px solid #4682b4",
        "padding": "10px",
        "font-family": "'Courier New', Courier, monospace",
        "font-size": "0.95em"
    },
    "quote": {
        "border-left": "4px solid #ccc",
        "padding-left": "1em",
        "margin-left": "0",
        "margin-bottom": "1em",
        "font-style": "italic",
        "color": "#555"
    },
    "list_item": {"margin-bottom": "0.5em"},
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
    "image": {
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
            **DEFAULT_STYLES,
            "h1": {"font-size": "2.8em", "margin-bottom": "0.5em", "color": "#2c3e50", "border-bottom": "2px solid #3498db"},
            "h2": {"font-size": "2.2em", "margin-bottom": "0.4em", "color": "#34495e"},
            "paragraph": {"font-size": "1.1em", "color": "#34495e", "text-align": "justify"},
            "data_paragraph": {
                **DEFAULT_STYLES["data_paragraph"],
                "background-color": "#eaf2f8",
                "border-left-color": "#2980b9",
                "color": "#2c3e50",
            },
            "quote": {"border-left": "5px solid #3498db", "padding-left": "15px", "margin-left": "10px", "color": "#555", "font-style": "italic"},
            "code_block": {
                **DEFAULT_STYLES["code_block"],
                "background-color": "#2c3e50",
                "color": "#ecf0f1",
                "border": "1px solid #34495e",
            }
        }
    },
    "modern_minimal": {
        "name": "Modern Minimal",
        "description": "A sleek, modern layout with ample whitespace.",
        "styles": {
            **DEFAULT_STYLES,
            "body": {"font-family": "'Helvetica Neue', Arial, sans-serif", "line-height": "1.7", "background-color": "#fdfdfd"},
            "h1": {"font-size": "3em", "font-weight": "bold", "margin-bottom": "0.6em", "color": "#1a1a1a", "letter-spacing": "-1px"},
            "h2": {"font-size": "2.3em", "font-weight": "bold", "margin-bottom": "0.5em", "color": "#2a2a2a", "letter-spacing": "-0.5px"},
            "h3": {"font-size": "1.8em", "font-weight": "bold", "margin-bottom": "0.4em", "color": "#3a3a3a"},
            "paragraph": {"font-size": "1.05em", "color": "#4f4f4f", "margin-bottom": "1.2em"},
            "data_paragraph": {
                **DEFAULT_STYLES["data_paragraph"],
                "background-color": "#f9f9f9",
                "border-left": "3px solid #1abc9c",
                "padding": "12px 15px",
                "font-family": "sans-serif",
                "font-size": "1em",
                "color": "#333"
            },
            "quote": {"border-left": "3px solid #1abc9c", "padding": "10px 20px", "margin": "20px 0", "background-color": "#f8f9fa", "color": "#333"},
            "image": {
                **DEFAULT_STYLES["image"],
                "border-radius": "8px",
                # "box-shadow": "0 4px 12px rgba(0,0,0,0.08);", # Removed for WeChat
                 "margin-top": "1em",
                 "margin-bottom": "1.5em"
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
            "body": {"font-family": "'Comic Sans MS', cursive, sans-serif", "line-height": "1.5", "background-color": "#fff8e1"},
            "h1": {"font-size": "2.7em", "color": "#ff6f61", "text-shadow": "2px 2px #f9a825"},
            "h2": {"font-size": "2.1em", "color": "#6a1b9a"},
            "h3": {"font-size": "1.6em", "color": "#00796b"},
            "paragraph": {"font-size": "1em", "color": "#4e342e"},
            "data_paragraph": {
                **DEFAULT_STYLES["data_paragraph"],
                "background-color": "#fff0f5",
                "border": "2px dashed #ff69b4",
                "border-left-width": "4px",
                "color": "#c71585",
                "font-family":"'Comic Sans MS', cursive, sans-serif"
            },
            "quote": {"border": "2px dashed #ff6f61", "padding": "15px", "margin": "15px", "background-color": "#fff0cb", "color": "#bf360c", "border-radius":"10px"},
            "image": {
                **DEFAULT_STYLES["image"],
                "border": "3px solid #ff6f61",
                # "transform": "rotate(-1deg);", # Removed for WeChat
                "margin-bottom": "1.5em"
            },
            "ul": {**DEFAULT_STYLES["ul"], "list-style-type": "'🎨 '"},
            "ol": {**DEFAULT_STYLES["ol"], "list-style-type": "decimal-leading-zero"},
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
    html_tag = tag if tag else element_type
    if element_type == "data_paragraph":
        html_tag = "p"
    elif element_type == "paragraph" and not tag:
        html_tag = "p"

    style_value = styles.get(element_type, {})
    style_str = ""

    if isinstance(style_value, dict):
        style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in style_value.items() if v is not None)
    elif isinstance(style_value, str):
        style_str = style_value

    escaped_content = html.escape(content) if content else ""

    if not style_str:
        return f"<{html_tag} {attributes}>{escaped_content}</{html_tag}>"

    return f"<{html_tag} style=\"{style_str}\" {attributes}>{escaped_content}</{html_tag}>"


def elements_to_html(structured_elements: list[dict], template_name: str) -> str:
    if template_name not in SMART_TEMPLATES_MVP:
        raise ValueError(f"Template '{template_name}' not found.")

    template = SMART_TEMPLATES_MVP[template_name]
    styles = template["styles"]

    html_parts = []

    body_style_value = styles.get("body", {})
    body_style_str = ""
    if isinstance(body_style_value, dict):
         body_style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in body_style_value.items() if v is not None)
    elif isinstance(body_style_value, str):
        body_style_str = body_style_value
    html_parts.append(f"<body style=\"{body_style_str}\">")

    i = 0
    while i < len(structured_elements):
        element = structured_elements[i]
        el_type = element["type"]
        el_content = element.get("content", "")

        if el_type.startswith("h"):
            html_parts.append(apply_styles_to_element(el_type, el_content, styles, tag=el_type))
        elif el_type == "paragraph" or el_type == "data_paragraph":
            html_parts.append(apply_styles_to_element(el_type, el_content, styles, tag="p"))
        elif el_type == "quote":
            html_parts.append(apply_styles_to_element(el_type, el_content, styles, tag="blockquote"))
        elif el_type == "list_item":
            list_items_html_content = []

            current_list_type_is_ordered = element.get("raw", "").strip().startswith(tuple(f"{k}." for k in range(10)))
            list_tag = "ol" if current_list_type_is_ordered else "ul"

            list_items_html_content.append(apply_styles_to_element("list_item", el_content, styles, tag="li"))

            j = i + 1
            while j < len(structured_elements) and structured_elements[j]["type"] == "list_item":
                next_item_is_ordered = structured_elements[j].get("raw", "").strip().startswith(tuple(f"{k}." for k in range(10)))
                if next_item_is_ordered == current_list_type_is_ordered:
                    list_items_html_content.append(apply_styles_to_element("list_item", structured_elements[j].get("content", ""), styles, tag="li"))
                    j += 1
                else:
                    break

            list_style_value = styles.get(list_tag, {})
            list_style_str = ""
            if isinstance(list_style_value, dict):
                list_style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in list_style_value.items() if v is not None)
            elif isinstance(list_style_value, str):
                 list_style_str = list_style_value

            html_parts.append(f"<{list_tag} style=\"{list_style_str}\">{''.join(list_items_html_content)}</{list_tag}>")
            i = j -1

        elif el_type == "code_block":
            lang = element.get("language")
            lang_class = f"language-{lang}" if lang else ""

            escaped_code = html.escape(el_content)
            pre_style_value = styles.get("code_block", {})
            pre_style_str = ""
            if isinstance(pre_style_value, dict):
                 pre_style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in pre_style_value.items() if v is not None)
            elif isinstance(pre_style_value, str):
                 pre_style_str = pre_style_value

            html_parts.append(f"<pre style=\"{pre_style_str}\"><code class=\"{lang_class}\">{escaped_code}</code></pre>")

        elif el_type == "image":
            alt_text = html.escape(element.get("alt", ""))
            src_url = element.get("src", "")

            img_style_value = styles.get("image", {})
            img_style_str = ""
            if isinstance(img_style_value, dict):
                img_style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in img_style_value.items() if v is not None)
            elif isinstance(img_style_value, str):
                 img_style_str = img_style_value
            html_parts.append(f"<img src=\"{src_url}\" alt=\"{alt_text}\" style=\"{img_style_str}\">")

        elif el_type == "horizontal_rule":
            hr_style_value = styles.get("horizontal_rule", "")
            hr_style_str = ""
            if isinstance(hr_style_value, dict):
                 hr_style_str = "; ".join(f"{k.replace('_', '-')}: {v}" for k, v in hr_style_value.items() if v is not None)
            elif isinstance(hr_style_value, str):
                 hr_style_str = hr_style_value
            html_parts.append(f"<hr style=\"{hr_style_str}\">")

        i += 1

    html_parts.append("</body>")
    return "\n".join(html_parts)


if __name__ == '__main__':
    from semantic_analyzer import SemanticAnalyzer
    analyzer = SemanticAnalyzer()

    sample_data_md = """
Regular paragraph.

2023年GDP增速6.3%，CPI同比上涨2.1%。营收达到 ￥1,234,567.89元。

Another regular paragraph.

Key metrics: Sales volume increased by 15% in Q3. User growth is 1000 per day.
The formula is A = B * (C + D) / E.
    """
    print("--- Testing Data Paragraph Styling ---")

    parsed_elements_data = analyzer.parse_markdown_to_elements(sample_data_md)
    print("\nParsed elements with data_paragraph detection:")
    for el in parsed_elements_data:
        print(el)

    for template_name in SMART_TEMPLATES_MVP.keys():
        print(f"\n--- HTML Output ({template_name}) for Data Paragraphs ---")
        html_output = elements_to_html(parsed_elements_data, template_name)
        output_filename = f"sample_data_para_{template_name}.html"
        with open(output_filename, "w", encoding="utf-8") as f:
            f.write("<!DOCTYPE html><html lang=\"en\"><head><meta charset='UTF-8'>")
            f.write(f"<title>Data Paragraph - {template_name}</title></head>")
            f.write(html_output)
            f.write("</html>")
        print(f"Saved to {output_filename}")
