import re
from typing import Dict, List, Tuple

# Common spelling mistakes list as fallback
COMMON_MISSPELLINGS = {
    "recieve": "receive",
    "seperate": "separate",
    "definately": "definitely",
    "occured": "occurred",
    "untill": "until",
    "fullfill": "fulfill",
    "goverment": "government",
    "enviroment": "environment",
    "refering": "referring",
    "writting": "writing",
    "commited": "committed",
    "succesful": "successful",
}


def check_grammar_and_spelling(text: str) -> Tuple[int, List[Dict[str, str]]]:
    """Verify spelling and grammar errors in resume text.

    Args:
        text: Cleaned resume text.

    Returns:
        Tuple: (grammar_score out of 20, issues_list)
    """
    issues = []
    grammar_score = 20

    if not text:
        return 0, []

    # Attempt to use language-tool-python
    try:
        import language_tool_python
        # Using a context manager or local client. Note: download happens on first init.
        # To avoid blocking, we limit download time or wrap in try
        tool = language_tool_python.LanguageTool("en-US")
        matches = tool.check(text)
        tool.close()

        for match in matches:
            issues.append(
                {
                    "issue_type": "grammar_or_spelling",
                    "description": match.message,
                    "current": text[match.offset : match.offset + match.errorLength],
                    "suggested": ", ".join(match.replacements[:3]) if match.replacements else "N/A",
                }
            )
    except Exception:
        # Graceful fallback: Rule-based custom checks
        # 1. Check duplicate words (e.g., "the the")
        dup_pattern = re.compile(r"\b(\w+)\s+\1\b", re.IGNORECASE)
        for match in dup_pattern.finditer(text):
            issues.append(
                {
                    "issue_type": "grammar",
                    "description": f"Duplicate word found: '{match.group(1)}'",
                    "current": match.group(0),
                    "suggested": match.group(1),
                }
            )

        # 2. Local common misspellings check
        words = re.findall(r"\b\w+\b", text.lower())
        for word in words:
            if word in COMMON_MISSPELLINGS:
                issues.append(
                    {
                        "issue_type": "spelling",
                        "description": f"Common spelling mistake: '{word}'",
                        "current": word,
                        "suggested": COMMON_MISSPELLINGS[word],
                    }
                )

        # 3. Punctuation spacing (e.g., word ,word -> word, word)
        punc_pattern = re.compile(r"\w+\s+[\,\.\;\:]\s*\w+")
        for match in punc_pattern.finditer(text):
            issues.append(
                {
                    "issue_type": "formatting_grammar",
                    "description": "Incorrect spacing before punctuation.",
                    "current": match.group(0),
                    "suggested": re.sub(r"\s+([\,\.\;\:])", r"\1", match.group(0)),
                }
            )

    # Calculate Grammar Score out of 20 points
    # Deduct 2 points per issue, minimum score 6.
    deductions = len(issues) * 2
    grammar_score = max(20 - deductions, 6)

    return grammar_score, issues
