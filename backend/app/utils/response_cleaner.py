"""
Response formatting utilities for IntelliFinance.
Strips markdown/HTML symbols so responses display as clean plain text.
"""

import re


def clean_response(text: str) -> str:
    """
    Remove markdown and HTML formatting symbols from LLM output.

    Handles:
      - Headings        : ## Heading  →  Heading
      - Bold/italic     : **text**, *text*, __text__, _text_  →  text
      - Inline code     : `code`  →  code
      - Code blocks     : ```...```  →  (contents preserved, fences removed)
      - HTML tags       : <b>, <br>, <strong>, etc.  →  removed
      - Horizontal rule : --- / *** / ___  →  removed
      - Bullet markers  : * item  →  - item  (normalise to dash)
      - Excess blanks   : more than 2 consecutive newlines  →  2 newlines
    """
    if not text:
        return text

    # 1. Remove code fences (keep content inside)
    text = re.sub(r'```[a-zA-Z]*\n?', '', text)
    text = re.sub(r'```', '', text)

    # 2. Remove ATX headings (##, ###, ####, etc.) — keep the heading text
    text = re.sub(r'^#{1,6}\s+', '', text, flags=re.MULTILINE)

    # 3. Remove bold/italic markers (**text**, *text*, __text__, _text_)
    text = re.sub(r'\*{3}(.+?)\*{3}', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*{2}(.+?)\*{2}', r'\1', text, flags=re.DOTALL)
    text = re.sub(r'\*(.+?)\*',       r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_{3}(.+?)_{3}',   r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_{2}(.+?)_{2}',   r'\1', text, flags=re.DOTALL)
    text = re.sub(r'_(.+?)_',         r'\1', text, flags=re.DOTALL)

    # 4. Remove inline backtick code markers
    text = re.sub(r'`(.+?)`', r'\1', text)

    # 5. Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)

    # 6. Remove horizontal rules (---, ***, ___)
    text = re.sub(r'^[-*_]{3,}\s*$', '', text, flags=re.MULTILINE)

    # 7. Normalise bullet points: leading * or + to -
    text = re.sub(r'^\s*[*+]\s+', '- ', text, flags=re.MULTILINE)

    # 8. Collapse more than 2 consecutive blank lines
    text = re.sub(r'\n{3,}', '\n\n', text)

    return text.strip()
