import re

class RushParser:
    def __init__(self, html_content):
        self.html = html_content

    def find(self, tag):
        """Finds the first occurrence of a tag and returns its content."""
        # Simple regex for <tag>content</tag>
        # Handles attributes like <h1 class="foo">...</h1>
        pattern = f"<{tag}.*?>(.*?)</{tag}>"
        match = re.search(pattern, self.html, re.DOTALL | re.IGNORECASE)
        
        if match:
            return Element(tag, match.group(1).strip())
        return None

class Element:
    def __init__(self, tag, text):
        self.tag = tag
        self.text = text

    def get_text(self):
        return self.text
