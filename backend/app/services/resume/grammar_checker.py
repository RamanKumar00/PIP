import os
import re
import threading
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

# Thread-safe singleton for LanguageTool
_lt_tool = None
_lt_lock = threading.Lock()


def _get_grammar_tool():
    """Lazy-initialize LanguageTool once per process."""
    global _lt_tool
    if _lt_tool is None:
        with _lt_lock:
            if _lt_tool is None:
                # Allow disabling local JRE server in restricted environments (serverless, locked containers)
                if os.getenv("USE_LOCAL_LANGUAGETOOL", "true").lower() == "false":
                    _lt_tool = False
                    return _lt_tool
                try:
                    import language_tool_python
                    _lt_tool = language_tool_python.LanguageTool("en-US")
                except Exception:
                    _lt_tool = False
    return _lt_tool


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

    tool = _get_grammar_tool()

    if tool and tool is not False:
        try:
            matches = tool.check(text)
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
            tool = False

    if not tool or tool is False:
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
