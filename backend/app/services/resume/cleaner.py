import re
import unicodedata


def clean_text(text: str) -> str:
    """Clean and normalize raw text extracted from a resume.
    
    Args:
        text: Raw text string.

    Returns:
        str: Cleaned and normalized text.
    """
    if not text:
        return ""

    # Normalize unicode characters
    text = unicodedata.normalize("NFKC", text)

    # Replace smart quotes and double hyphens
    text = text.replace("“", '"').replace("”", '"').replace("’", "'").replace("‘", "'")
    text = text.replace("–", "-").replace("—", "-")

    # Remove non-printable control characters
    text = "".join(ch for ch in text if unicodedata.category(ch)[0] != "C" or ch in "\n\t ")

    # Collapse multiple vertical spaces
    text = re.sub(r"\n\s*\n+", "\n\n", text)
    
    # Collapse multiple horizontal spaces
    text = re.sub(r"[ \t]+", " ", text)

    return text.strip()
