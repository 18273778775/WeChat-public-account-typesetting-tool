import re
from markdown_it import MarkdownIt

class SemanticAnalyzer:
    def __init__(self):
        self.md = MarkdownIt()
        # Regex for data paragraphs:
        # Looks for percentages, currency, multiple numbers, or data-related keywords.
        self.data_paragraph_keywords = re.compile(
            r'\b(同比|环比|增长|下降|上涨|减少|季度|年度|营收|利润|指标|数据)\b',
            re.IGNORECASE
        )
        self.data_paragraph_patterns = re.compile(
            r'(?:(\d{1,3}(,\d{3})*(\.\d+)?%|\d+(\.\d+)?%))|'  # Percentages like 1,234.56% or 10%
            r'(?:[￥$€£¥]\s*\d{1,3}(,\d{3})*(\.\d+)?)|'    # Currency like ¥ 1,234.50 or $500
            r'(?:\b\d{4}年|\bQ[1-4]\b)|'                     # Dates like 2023年 or Q1
            # r'(\b\d[\d,.]*\b\s*){3,}|'                    # Removed: Three or more numbers in sequence, rely on distinct_number_hits
            r'(=|\+|-|\*|/)',                              # Basic formula indicators
            re.IGNORECASE
        )
        # Threshold for number of data indicators to qualify as a data paragraph
        self.data_paragraph_threshold = 2


    def _is_data_paragraph(self, text_content: str) -> bool:
        """
        Determines if a paragraph content qualifies as a data paragraph.
        """
        if not text_content or len(text_content) > 500: # Avoid overly long paragraphs
            return False

        keyword_hits = len(self.data_paragraph_keywords.findall(text_content))
        pattern_hits = len(self.data_paragraph_patterns.findall(text_content))

        numbers = re.findall(r'\d[\d,.]*', text_content) # Removed \b for more general number finding
        distinct_number_hits = len(set(numbers))

        # print(f"DEBUG DATA PARA: Text: '{text_content[:50]}...' | Keywords: {keyword_hits} | Patterns: {pattern_hits} | Distinct Numbers: {distinct_number_hits}") # Commented out

        if pattern_hits >= self.data_paragraph_threshold:
            return True
        if pattern_hits >= 1 and keyword_hits >= 1:
            return True
        if keyword_hits >= 2 and distinct_number_hits >=1:
            return True
        if distinct_number_hits >= 4:
             return True
        if distinct_number_hits == 3 and len(text_content) < 150:
            return True
        if distinct_number_hits == 2 and len(text_content) < 70 and keyword_hits >= 1:
            return True
        if distinct_number_hits >= 2 and len(text_content) < 70 and pattern_hits >=1 :
            return True
        if distinct_number_hits >= 2 and len(text_content) < 50 :
            return True

        return False

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
                        content_parts.append("\n")
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

                elements.extend(images_in_para)

                actual_text_for_paragraph = text_content
                if images_in_para:
                    temp_text = text_content
                    for img_el in images_in_para:
                        temp_text = temp_text.replace(img_el["raw"], "", 1)
                    actual_text_for_paragraph = temp_text.strip()

                if actual_text_for_paragraph:
                    actual_text_for_paragraph = re.sub(r'\n\s*\n', '\n', actual_text_for_paragraph).strip()
                    actual_text_for_paragraph = re.sub(r'\s{2,}', ' ', actual_text_for_paragraph).strip()


                if actual_text_for_paragraph:
                    para_type = "data_paragraph" if self._is_data_paragraph(actual_text_for_paragraph) else "paragraph"
                    elements.append({
                        "type": para_type,
                        "content": actual_text_for_paragraph,
                        "raw": raw_content
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
                        elements.extend(images_in_bq_p)

                        actual_text_for_bq_para = text_c
                        if images_in_bq_p:
                            temp_text = text_c
                            for img_el in images_in_bq_p:
                                temp_text = temp_text.replace(img_el["raw"], "",1)
                            actual_text_for_bq_para = temp_text.strip()

                        if actual_text_for_bq_para:
                            actual_text_for_bq_para = re.sub(r'\n\s*\n', '\n', actual_text_for_bq_para).strip()
                            actual_text_for_bq_para = re.sub(r'\s{2,}', ' ', actual_text_for_bq_para).strip()
                            if actual_text_for_bq_para:
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
                            actual_text_for_li = re.sub(r'\s{2,}', ' ', actual_text_for_li).strip()
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

    def print_elements(md_string, title="Test Case"): # Keep this for potential direct debugging
        print(f"\n--- {title} ---")
        # print(f"Markdown:\n{md_string}")
        parsed = analyzer.parse_markdown_to_elements(md_string)
        print("Parsed Elements:")
        if not parsed:
            print(" (No elements parsed)")
        for el_idx, element in enumerate(parsed):
            print(f"  {el_idx}: {element}")

    print("\n--- Data Paragraph Detection Debug ---")
    data_test_cases = {
        "percentage_and_currency": "营收达到 ￥1,234,567.89元，利润增长了15.5%。",
        "keywords_and_numbers": "2023年第四季度，活跃用户同比增长20%，达到500万。",
        "multiple_numbers": "数据显示：A为100，B是2500，C为30.5，D是0.5。",
        "formula_like": "计算公式为：X = (Y + Z) / 2 * 用户数。",
        "mixed_financial": "公司年度财报显示，收入为 $5.2M，同比增长 12%。",
        "simple_stats": "平均值为 50.2，标准差为 3.1，最大值为 99.",
        "non_data_para": "这是一段普通的文本，不包含特定的数据指标或金融术语。",
        "borderline_few_numbers": "库存剩余 3 箱，单价 50 元。",
        "long_text_with_few_numbers": "这是一个非常长的段落，它碰巧包含了一个数字，比如 100，但主要内容是关于历史事件的详细描述，而不是数据报告。" * 3
    }

    for name, text in data_test_cases.items():
        print(f"\n--- Testing case: '{name}' ---")
        # print(f"Input text: {text}") # Keep output cleaner
        # is_data = analyzer._is_data_paragraph(text) # _is_data_paragraph is called by parse_markdown_to_elements
        # print(f"Result of _is_data_paragraph: {is_data}")

        elements = analyzer.parse_markdown_to_elements(text) # This will call _is_data_paragraph and print its debug line
        if elements:
            para_like_elements = [el for el in elements if el['type'] in ['paragraph', 'data_paragraph']]
            if para_like_elements:
                 print(f"Full parse element type for '{name}': {para_like_elements[0]['type']}")
            else:
                print(f"Full parse for '{name}' did not yield a paragraph-like element.")
        else:
            print(f"Full parse for '{name}' yielded no elements.")

    # print("\n--- Full parsing for a data-rich example ---")
    # sample_data_md = """
# Regular paragraph.

# 2023年GDP增速6.3%，CPI同比上涨2.1%。营收达到 ￥1,234,567.89元。

# Another regular paragraph.

# Key metrics: Sales volume increased by 15% in Q3. User growth is 1000 per day.
# The formula is A = B * (C + D) / E.
    # """
    # print_elements(sample_data_md, "Data Rich Document")
