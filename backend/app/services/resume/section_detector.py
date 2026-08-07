import re
from typing import Dict

# Define regex patterns for typical section headings
# Now handles markdown, bullets, decorators, and extra whitespace
SECTION_PATTERNS = {
    "education": re.compile(
        r"^\s*[*•▸►▶▷#>-]*\s*(education|academic qualifications|academic background|qualification|academics)\s*[*•▸►▶▷#>-]*\s*$",
        re.IGNORECASE,
    ),
    "experience": re.compile(
        r"^\s*[*•▸►▶▷#>-]*\s*(experience|work experience|professional experience|employment history|work history|professional background|internships|internship)\s*[*•▸►▶▷#>-]*\s*$",
        re.IGNORECASE,
    ),
    "projects": re.compile(
        r"^\s*[*•▸►▶▷#>-]*\s*(projects|key projects|academic projects|personal projects|technical projects|coursework projects)\s*[*•▸►▶▷#>-]*\s*$",
        re.IGNORECASE,
    ),
    "skills": re.compile(
        r"^\s*[*•▸►▶▷#>-]*\s*(skills|technical skills|key skills|core competencies|skills & technologies|areas of expertise|languages & technologies|technical proficiencies)\s*[*•▸►▶▷#>-]*\s*$",
        re.IGNORECASE,
    ),
    "certifications": re.compile(
        r"^\s*[*•▸►▶▷#>-]*\s*(certifications|certifications & awards|awards|achievements|honors|courses|certification)\s*[*•▸►▶▷#>-]*\s*$",
        re.IGNORECASE,
    ),
}


def detect_sections(text: str) -> Dict[str, str]:
    """Segment a resume's text into logical sections based on structural headings.

    Args:
        text: Cleaned resume text.

    Returns:
        Dict[str, str]: Map of section name -> text content block.
    """
    sections = {
        "education": "",
        "experience": "",
        "projects": "",
        "skills": "",
        "certifications": "",
        "header_contact": "",
    }

    lines = text.split("\n")
    current_section = "header_contact"

    for line in lines:
        cleaned_line = line.strip()
        if not cleaned_line:
            continue

        matched_section = None
        for sec_name, pattern in SECTION_PATTERNS.items():
            if pattern.match(cleaned_line):
                matched_section = sec_name
                break

        if matched_section:
            current_section = matched_section
        else:
            if current_section == "header_contact":
                sections["header_contact"] += line + "\n"
            else:
                sections[current_section] += line + "\n"

    for key in sections:
        sections[key] = sections[key].strip()

    return sections
