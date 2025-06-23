import re
from markdown_it import MarkdownIt

class SemanticAnalyzer:
    def __init__(self):
        self.md = MarkdownIt()

    def _extract_inline_content(self, tokens: list, start_index: int, stop_token_type: str) -> tuple[str, str, list[dict], int]:
        """
        Helper to extract inline content (text, code_inline, image) until a stop_token_type.
        Returns (text_content, raw_content, image_elements, next_index)
        """
        content_parts = []
        image_elements = []
        current_idx = start_index
        raw_parts = []

        while current_idx < len(tokens) and tokens[current_idx].type != stop_token_type:
            outer_token = tokens[current_idx]

            if outer_token.type == "inline" and outer_token.children:
                for token in outer_token.children:
                    # print(f"DEBUG _extract:   Inline child: {token}")
                    if token.type == "text":
                        content_parts.append(token.content)
                        raw_parts.append(token.content)
                    elif token.type == "code_inline":
                        content_parts.append(f"`{token.content}`")
                        raw_parts.append(f"`{token.content}`")
                    elif token.type == "image":
                        alt = token.content
                        src = dict(token.attrs).get('src', '')
                        image_elements.append({
                            "type": "image", "alt": alt, "src": src,
                            "raw": f"![{alt}]({src})"
                        })
                        raw_parts.append(f"![{alt}]({src})")
                        # content_parts.append(f"![{alt}]({src})") # image raw is part of text_content for replacement
                    elif token.type == "softbreak":
                        content_parts.append("\n") # Changed from space to newline
                        raw_parts.append("\n")
                    elif token.type == "hardbreak":
                        content_parts.append("\n")
                        raw_parts.append("\\\n")
            elif outer_token.type == "text":
                content_parts.append(outer_token.content)
                raw_parts.append(outer_token.content)
            elif outer_token.type == "image":
                alt = outer_token.content
                src = dict(outer_token.attrs).get('src', '')
                image_elements.append({ "type": "image", "alt": alt, "src": src, "raw": f"![{alt}]({src})" })
                raw_parts.append(f"![{alt}]({src})")
                # content_parts.append(f"![{alt}]({src})")

            current_idx += 1

        return "".join(content_parts), "".join(raw_parts), image_elements, current_idx


    def parse_markdown_to_elements(self, markdown_text: str) -> list[dict]:
        elements = []
        if not markdown_text.strip():
            return elements

        # print(f"DEBUG SRC: Input Markdown: '{markdown_text}'")
        tokens = self.md.parse(markdown_text)
        # print(f"DEBUG SRC: Tokens: {tokens}")

        i = 0
        while i < len(tokens):
            token = tokens[i]
            # print(f"DEBUG SRC: Processing token {i}: {token}")

            if token.type == "heading_open":
                # print(f"DEBUG SRC: Found heading_open at {i}")
                level = int(token.tag[1])
                inline_token = tokens[i+1]
                content = inline_token.content.strip()
                elements.append({
                    "type": f"h{level}",
                    "content": content,
                    "raw": f"{'#' * level} {content}"
                })
                i += 3
                continue

            elif token.type == "paragraph_open":
                # print(f"DEBUG SRC: Found paragraph_open at {i}")
                text_content, raw_content, images_in_para, next_idx = self._extract_inline_content(tokens, i + 1, "paragraph_close")

                # The text_content from _extract_inline_content now includes the raw markdown of images.
                # We need to add image elements first, then create a paragraph from the text
                # *after* removing the raw markdown of those images from it.

                current_paragraph_text_parts = []
                last_idx = 0

                # Reconstruct raw_content to include only text segments for the paragraph
                # This is tricky if text_content itself was used for this. Let's use raw_content from _extract.
                # The goal is: images are separate elements. Paragraphs contain text around them.

                # Add images found
                elements.extend(images_in_para)

                # Create text content for paragraph by removing image raw markdown
                actual_text_for_paragraph = text_content
                if images_in_para:
                    temp_text = text_content
                    for img_el in images_in_para:
                        # Replace only the first occurrence in case of identical image markdown strings
                        temp_text = temp_text.replace(img_el["raw"], "", 1)
                    actual_text_for_paragraph = temp_text.strip()

                # Consolidate multiple newlines resulting from image removal into single newlines or spaces
                # This step is important if images were on their own lines within the original paragraph block
                if actual_text_for_paragraph:
                    actual_text_for_paragraph = re.sub(r'\n\s*\n', '\n', actual_text_for_paragraph).strip()
                    # Also consolidate multiple spaces into single spaces
                    actual_text_for_paragraph = re.sub(r'\s{2,}', ' ', actual_text_for_paragraph).strip()


                if actual_text_for_paragraph:
                    elements.append({
                        "type": "paragraph",
                        "content": actual_text_for_paragraph,
                        "raw": raw_content # Keep original raw of the paragraph block
                    })

                i = next_idx + 1
                # print(f"DEBUG SRC: Paragraph processed, next i = {i}")
                continue

            elif token.type == "blockquote_open":
                # print(f"DEBUG SRC: Found blockquote_open at {i}")
                blockquote_collected_texts = []

                j = i + 1
                while j < len(tokens) and tokens[j].type != "blockquote_close":
                    # print(f"DEBUG SRC:   Blockquote inner token {j}: {tokens[j]}")
                    if tokens[j].type == "paragraph_open":
                        # print(f"DEBUG SRC:     Found paragraph_open in BQ at {j}")
                        text_c, raw_p_c, images_in_bq_p, next_p_idx = self._extract_inline_content(tokens, j + 1, "paragraph_close")
                        # print(f"DEBUG SRC:     _extract_inline_content from BQ para returned: text='{text_c[:30]}...', images={len(images_in_bq_p)}, next_idx={next_p_idx}")
                        elements.extend(images_in_bq_p)

                        actual_text_for_bq_para = text_c
                        if images_in_bq_p:
                            temp_text = text_c
                            for img_el in images_in_bq_p:
                                temp_text = temp_text.replace(img_el["raw"], "",1)
                            actual_text_for_bq_para = temp_text.strip()

                        if actual_text_for_bq_para:
                            actual_text_for_bq_para = re.sub(r'\n\s*\n', '\n', actual_text_for_bq_para).strip()
                            if actual_text_for_bq_para: # Add only if text remains
                                blockquote_collected_texts.append(actual_text_for_bq_para)
                        j = next_p_idx
                        # print(f"DEBUG SRC:     BQ paragraph processed, j is now {j} (points to paragraph_close)")

                    j += 1

                if blockquote_collected_texts:
                    full_quote_content = "\n".join(blockquote_collected_texts)
                    elements.append({
                        "type": "quote",
                        "content": full_quote_content,
                        "raw": "> " + full_quote_content.replace("\n", "\n> ")
                    })
                i = j + 1
                # print(f"DEBUG SRC: Blockquote processed, next i = {i}")
                continue

            elif token.type == "bullet_list_open" or token.type == "ordered_list_open":
                # print(f"DEBUG SRC: Found list_open at {i} (type: {token.type})")
                is_ordered_list = token.type == "ordered_list_open"

                j = i + 1
                item_counter = 1
                while j < len(tokens) and tokens[j].type not in ["bullet_list_close", "ordered_list_close"]:
                    if tokens[j].type == "list_item_open":
                        # print(f"DEBUG SRC:   Found list_item_open at {j}")
                        k = j + 1
                        item_text_content = ""

                        if k < len(tokens) and tokens[k].type == "paragraph_open":
                            text_c, raw_li_p_c, images_in_li, next_li_p_idx = self._extract_inline_content(tokens, k + 1, "paragraph_close")
                            elements.extend(images_in_li)

                            actual_text_for_li = text_c
                            if images_in_li:
                                temp_text = text_c
                                for img_el in images_in_li:
                                    temp_text = temp_text.replace(img_el["raw"], "", 1)
                                actual_text_for_li = temp_text.strip()

                            actual_text_for_li = re.sub(r'\n\s*\n', '\n', actual_text_for_li).strip()
                            if actual_text_for_li:
                                item_text_content = actual_text_for_li
                            k = next_li_p_idx

                        while k < len(tokens) and tokens[k].type != "list_item_close":
                            k += 1

                        if item_text_content:
                            list_marker_char = f"{item_counter}." if is_ordered_list else "-"
                            elements.append({
                                "type": "list_item",
                                "content": item_text_content,
                                "raw": f"{list_marker_char} {item_text_content}"
                            })
                            if is_ordered_list:
                                item_counter += 1
                        j = k
                    j += 1

                i = j + 1
                # print(f"DEBUG SRC: List processed, next i = {i}")
                continue

            elif token.type == "fence":
                # print(f"DEBUG SRC: Found fence at {i}")
                elements.append({
                    "type": "code_block",
                    "language": token.info.strip() if token.info else None,
                    "content": token.content.strip(),
                    "raw": f"```{token.info if token.info else ''}\n{token.content.strip()}\n```"
                })
                i += 1
                # print(f"DEBUG SRC: Fence processed, next i = {i}")
                continue

            elif token.type == "hr":
                # print(f"DEBUG SRC: Found hr at {i}")
                elements.append({"type": "horizontal_rule", "content": None, "raw": "---"})
                i += 1
                # print(f"DEBUG SRC: HR processed, next i = {i}")
                continue

            # print(f"DEBUG SRC: Unhandled or part-of-processed token {i}: {token}, advancing.")
            i += 1

        # print(f"DEBUG SRC: Parsing finished. Total elements: {len(elements)}")
        return elements


if __name__ == '__main__':
    analyzer = SemanticAnalyzer()

    def print_elements(md_string, title="Test Case"):
        # print(f"\n--- {title} ---")
        # print(f"Markdown:\n{md_string}")
        parsed = analyzer.parse_markdown_to_elements(md_string)
        # print("Parsed Elements:")
        # if not parsed:
            # print(" (No elements parsed)")
        # for el_idx, element in enumerate(parsed):
            # print(f"  {el_idx}: {element}")
    pass

    # print_elements("> This is a quote.\n> Second line of quote.", "Blockquote Test")
    # print_elements("This is a simple paragraph.", "Simple Paragraph Test")
    # ... all other print_elements calls commented out ...
