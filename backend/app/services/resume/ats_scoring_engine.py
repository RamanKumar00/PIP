import re
import logging
from abc import ABC, abstractmethod
from typing import Dict, List, Any, Tuple

logger = logging.getLogger(__name__)

# Strong active verbs typical for professional resumes
ACTION_VERBS = {
    "developed", "designed", "implemented", "optimized", "optimised", "created", "built",
    "launched", "managed", "engineered", "integrated", "deployed", "reduced",
    "improved", "enhanced", "accelerated", "scaled", "orchestrated", "refactored",
    "authored", "automated", "executed", "formulated", "pioneered", "restructured",
    "spearheaded", "coordinated", "delivered", "led", "established"
}


class BaseSubAnalyzer(ABC):
    """Abstract base class for all resume sub-analyzers."""

    @abstractmethod
    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        pass


class FormattingAnalyzer(BaseSubAnalyzer):
    """Evaluates presence of essential resume sections and overall length/balance."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        sections = data.get("sections", {})
        suggestions = []
        score = 10

        core_sections = ["education", "experience", "projects", "skills", "certifications"]
        present_count = 0
        missing = []

        for sec in core_sections:
            content = sections.get(sec, "")
            if content and len(content.strip()) > 20:
                score += 2
                present_count += 1
            else:
                missing.append(sec.capitalize())
                suggestions.append({
                    "category": "formatting",
                    "target": f"{sec.capitalize()} Section",
                    "current": "[Section Missing or thin]",
                    "suggested": f"Add a dedicated '{sec.capitalize()}' section with descriptive details.",
                    "rationale": f"Recruiters expect a standard resume schema containing {sec} details for screening."
                })

        score = min(score, 20)

        if present_count == 5:
            explanation = "Excellent section layout. All essential resume sections are fully present and well-structured."
        elif present_count >= 3:
            explanation = f"Fair formatting structure. However, key sections like ({', '.join(missing)}) are missing or contain insufficient content."
        else:
            explanation = f"Critical layout issues. Essential sections ({', '.join(missing)}) are missing, which breaks ATS parsing schemas."

        return {
            "score": score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class ContactAnalyzer(BaseSubAnalyzer):
    """Analyzes presence of email, phone, and professional links."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        header_text = data.get("sections", {}).get("header_contact", "")
        suggestions = []
        score = 0

        search_target = (header_text + "\n" + text).strip()

        email_match = re.search(r"[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}", search_target)
        phone_match = re.search(r"\+?\d[\d\-\s\(\)]{7,15}\d", search_target)
        linkedin_match = "linkedin.com" in search_target.lower() or re.search(r"linkedin\.com/(in|company)/[\w\-]+", search_target.lower())
        github_match = "github.com" in search_target.lower() or re.search(r"github\.com/[\w\-]+", search_target.lower())

        portfolio_keywords = ["portfolio", "website", "personal site", "personal-site", "blog", "portfolio url"]
        has_portfolio_keyword = any(kw in search_target.lower() for kw in portfolio_keywords)
        portfolio_patterns = [
            r"github\.io", r"vercel\.app", r"netlify\.app", r"behance\.net", r"dribbble\.com",
            r"[\w\-]+\.me\b", r"[\w\-]+\.info\b",
            r"https?://(?!www\.google\.com|www\.linkedin\.com|github\.com|gmail\.com|yahoo\.com|outlook\.com|geeksforgeeks\.org)[\w\.-]+\.\w+"
        ]
        has_portfolio_link = any(re.search(pat, search_target.lower()) for pat in portfolio_patterns)
        portfolio_match = bool(has_portfolio_keyword or has_portfolio_link)

        checks = [
            (email_match, "Email", "Add a professional email address (e.g. name@university.edu) at the top of your resume.", "Email is the primary channel used by recruitment software to schedule assessments."),
            (phone_match, "Phone", "Include your phone number with country code in your contact header.", "Recruiters require phone contact details for HR screening calls."),
            (linkedin_match, "LinkedIn", "Include a hyperlink to your updated LinkedIn profile in the header.", "90% of recruiters cross-verify candidates against their LinkedIn profiles."),
            (github_match, "GitHub", "Include a link to your GitHub profile showing public code repositories.", "For technical roles, engineering managers value public contributions and version control activity."),
            (portfolio_match, "Portfolio", "Include a link to your personal portfolio, blog, or personal website in the header.", "Portfolios showcase independent projects, web applications, and live work to technical interviewers."),
        ]

        missing_fields = []
        found_fields = []

        for matched, name, suggested, rationale in checks:
            if matched:
                score += 2
                found_fields.append(name)
            else:
                missing_fields.append(name)
                suggestions.append({
                    "category": "contact_info",
                    "target": "Contact Details",
                    "current": f"[{name} Missing]",
                    "suggested": suggested,
                    "rationale": rationale
                })

        if missing_fields:
            logger.warning(
                "[ContactAnalyzer] Missing contact fields: %s. Found fields: %s. Score: %s/10.",
                missing_fields, found_fields, score
            )

        if score == 10:
            explanation = "Perfect contact profile. All primary contact channels and technical links are clearly listed."
        elif score >= 6:
            explanation = f"Good contact header, but missing professional networking links: {', '.join(missing_fields)}."
        else:
            explanation = f"Incomplete contact credentials. Missing crucial links: {', '.join(missing_fields)}."

        return {
            "score": score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class ReadabilityAnalyzer(BaseSubAnalyzer):
    """Approximates readability. For technical resumes, moderate complexity is preferred."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        suggestions = []

        words = re.findall(r"\b\w+\b", text)
        sentences = [s for s in re.split(r"[\.\!\?]", text) if s.strip()]

        if not words or not sentences:
            return {
                "score": 5,
                "explanation": "Extremely low content volume. Readability could not be accurately measured.",
                "suggestions": []
            }

        def count_syllables(word: str) -> int:
            word = word.lower().strip()
            if not word:
                return 0
            vowels = "aeiouy"
            count = 0
            if word[0] in vowels:
                count += 1
            for index in range(1, len(word)):
                if word[index] in vowels and word[index - 1] not in vowels:
                    count += 1
            if word.endswith("e"):
                count -= 1
            if count == 0:
                count = 1
            return count

        total_syllables = sum(count_syllables(w) for w in words)
        words_count = len(words)
        sentences_count = len(sentences)

        try:
            asl = words_count / sentences_count
            asw = total_syllables / words_count
            fre = 206.835 - (1.015 * asl) - (84.6 * asw)
            fre = max(0, min(100, fre))
        except ZeroDivisionError:
            fre = 50

        # For technical resumes, moderate complexity (30-60) is ideal.
        if 30 <= fre <= 60:
            score = 10
        elif 20 <= fre < 30 or 60 < fre <= 70:
            score = 7
        elif 10 <= fre < 20 or 70 < fre <= 80:
            score = 5
        else:
            score = 3

        if 30 <= fre <= 60:
            explanation = f"Good technical readability (Flesch Ease: {fre:.1f}). Balanced between clarity and domain-specific terminology."
        elif fre < 30:
            explanation = f"Dense readability (Flesch Ease: {fre:.1f}). Text is highly technical or academic. Consider adding bullet-point summaries."
            suggestions.append({
                "category": "readability",
                "target": "Overall Readability",
                "current": "Dense and complex sentence layouts",
                "suggested": "Shorten sentences and break down long descriptions into concise bullet points.",
                "rationale": "Recruiters skim resumes in 6 seconds; clear sentences ensure key stats are visible."
            })
        else:
            explanation = f"Very simple readability (Flesch Ease: {fre:.1f}). May lack technical depth expected for engineering roles."

        return {
            "score": score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class ActionVerbAnalyzer(BaseSubAnalyzer):
    """Measures percentage of bullet points initiating with action verbs."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        sections = data.get("sections", {})
        suggestions = []

        target_text = sections.get("projects", "") + "\n" + sections.get("experience", "")
        bullets = [b.strip() for b in re.split(r"[\n\-\*\•]", target_text) if len(b.strip()) > 15]

        if not bullets:
            return {
                "score": 5,
                "explanation": "No bullet points detected in Projects or Experience sections.",
                "suggestions": [{
                    "category": "action_verbs",
                    "target": "Projects / Experience",
                    "current": "No bullet points found",
                    "suggested": "Structure descriptions with bullet points initiating with active action verbs.",
                    "rationale": "Bullet points improve layout skim rate for recruiting engines."
                }]
            }

        verb_count = 0
        total_count = len(bullets)

        for b in bullets:
            words = re.findall(r"\b\w+\b", b.lower())
            if words and words[0] in ACTION_VERBS:
                verb_count += 1
            elif len(words) > 1 and words[0] in ["to", "for", "a"] and words[1] in ACTION_VERBS:
                verb_count += 1

        pct = int((verb_count / total_count) * 100)
        score = int((pct / 100) * 20)
        score = max(min(score, 20), 4)

        if pct >= 70:
            explanation = f"Excellent action orientation ({pct}% of bullets). Your points show initiative and direct execution."
        elif pct >= 45:
            explanation = f"Moderate action orientation ({pct}% of bullets). Some points start with passive phrases (e.g. 'worked on', 'responsible for')."
        else:
            explanation = f"Low action orientation ({pct}% of bullets). Resumes should use strong active verbs to convey capability."

        return {
            "score": score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class AchievementAnalyzer(BaseSubAnalyzer):
    """Verifies use of metric figures, percentages, and performance counters."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        sections = data.get("sections", {})
        suggestions = []

        target_text = sections.get("projects", "") + "\n" + sections.get("experience", "")
        bullets = [b.strip() for b in re.split(r"[\n\-\*\•]", target_text) if len(b.strip()) > 15]

        if not bullets:
            return {
                "score": 5,
                "explanation": "No bullet points found to analyze metrics density.",
                "suggestions": []
            }

        metric_count = 0
        total_count = len(bullets)

        for b in bullets:
            b_lower = b.lower()
            has_num = any(char.isdigit() for char in b) or any(
                m in b_lower for m in ["percent", "lpa", "seconds", "ms", "accuracy", "users", "hours", "scale", "latency", "throughput", "reduced", "improved", "increased", "decreased"]
            )
            if has_num:
                metric_count += 1

        pct = int((metric_count / total_count) * 100)
        score = int((pct / 100) * 20)
        score = max(min(score, 20), 4)

        if pct >= 60:
            explanation = f"Excellent metrics density ({pct}% of bullets). Achievements are quantified, displaying business or technical impact."
        elif pct >= 30:
            explanation = f"Moderate metrics density ({pct}% of bullets). Add more quantitative indicators to back your project accomplishments."
        else:
            explanation = f"Weak metrics density ({pct}% of bullets). Points are descriptive rather than impact-driven. Include numbers showing performance improvements."

        return {
            "score": score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class ExperienceAnalyzer(BaseSubAnalyzer):
    """Analyzes depth and relevance of work experience section."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        sections = data.get("sections", {})
        exp_text = sections.get("experience", "")
        suggestions = []

        if not exp_text or len(exp_text.strip()) < 30:
            suggestions.append({
                "category": "experience",
                "target": "Experience Section",
                "current": "[Missing or extremely thin]",
                "suggested": "Add detailed work experience with company names, roles, dates, and bullet-point achievements.",
                "rationale": "Recruiters screen for tenure, role progression, and responsibility scope."
            })
            return {
                "score": 2,
                "explanation": "No meaningful experience section detected. This severely impacts recruiter confidence.",
                "suggestions": suggestions
            }

        # Heuristic: count experience blocks (company/role headers)
        lines = [l.strip() for l in exp_text.split("\n") if l.strip()]
        header_like = sum(1 for l in lines if re.search(r"\b(20\d{2}|present|current|intern|engineer|developer|manager|specialist|analyst|architect|lead)\w*\b", l.lower()))
        bullet_count = sum(1 for l in lines if l.startswith(("-", "*", "•")))

        score = 5
        if header_like >= 1:
            score += 5
        if header_like >= 2:
            score += 2
        if bullet_count >= 1:
            score += 3
        if bullet_count >= 3:
            score += 2
        if len(exp_text) > 200:
            score += 3

        score = min(score, 20)

        if score >= 15:
            explanation = "Strong experience section with clear role definitions and achievement bullets."
        elif score >= 8:
            explanation = "Fair experience section. Consider adding more quantified bullet points and clarifying tenure."
        else:
            explanation = "Weak experience section. Expand with specific responsibilities, technologies used, and measurable outcomes."

        return {
            "score": score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class GrammarAnalyzer(BaseSubAnalyzer):
    """Evaluates grammar points and returns structured score out of 20."""

    def analyze(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        grammar_score = data.get("grammar_score", 20)
        grammar_issues = data.get("grammar_issues", [])

        suggestions = []
        for issue in grammar_issues:
            suggestions.append({
                "category": "grammar",
                "target": f"Spelling/Grammar Error: '{issue.get('current')}'",
                "current": issue.get("current", ""),
                "suggested": issue.get("suggested", "N/A"),
                "rationale": issue.get("description", "Possible grammatical issue.")
            })

        if grammar_score >= 18:
            explanation = "Perfect grammar check. The text is clean of spelling blunders, double spaces, and typos."
        elif grammar_score >= 12:
            explanation = f"Minor spelling or spacing issues found ({len(grammar_issues)} errors). Review to ensure polished layouts."
        else:
            explanation = f"High error density ({len(grammar_issues)} issues). Grammar/typo blunders severely degrade recruiter trust."

        return {
            "score": grammar_score,
            "explanation": explanation,
            "suggestions": suggestions
        }


class ScoreAggregator:
    """Combines sub-analyzer scores into unified ATS indices."""

    def aggregate(
        self,
        formatting: Dict[str, Any],
        contact: Dict[str, Any],
        readability: Dict[str, Any],
        action_verb: Dict[str, Any],
        achievement: Dict[str, Any],
        grammar: Dict[str, Any],
        experience: Dict[str, Any],
        keywords_score: int,
        project_score: int = 10
    ) -> Tuple[int, Dict[str, int], Dict[str, Any]]:

        breakdown = {
            "formatting_score": formatting["score"],
            "contact_score": contact["score"],
            "readability_score": readability["score"],
            "action_verb_score": action_verb["score"],
            "experience_score": experience["score"],
            "achievement_score": achievement["score"],
            "achievements_score": achievement["score"],
            "grammar_score": grammar["score"],
            "keyword_score": keywords_score,
            "project_score": project_score
        }

        # Sum of max: 20 + 10 + 10 + 20 + 20 + 20 + 20 + 20 = 140
        base_sum = (
            formatting["score"] +
            contact["score"] +
            readability["score"] +
            action_verb["score"] +
            achievement["score"] +
            grammar["score"] +
            experience["score"] +
            project_score          # <-- FIXED: now included
        )

        # Scale base to 80% weight, keywords to 20% weight
        overall_ats = int((base_sum / 140.0) * 80 + (keywords_score / 20.0) * 20)
        overall_ats = min(max(overall_ats, 10), 100)

        strength_meter = {
            "readability": int((formatting["score"] / 20) * 50 + (readability["score"] / 10) * 50),
            "professionalism": int((grammar["score"] / 20) * 70 + (contact["score"] / 10) * 30),
            "technical_strength": int((achievement["score"] / 20) * 50 + (keywords_score / 20) * 50),
            "ats_compatibility": overall_ats,
            "quality_label": "Excellent" if overall_ats >= 85 else ("Good" if overall_ats >= 70 else ("Fair" if overall_ats >= 50 else "Needs Improvement")),
            "stars": 5 if overall_ats >= 85 else (4 if overall_ats >= 70 else (3 if overall_ats >= 50 else 2))
        }

        return overall_ats, breakdown, strength_meter


class ATSScoringEngine:
    """Orchestrates modular resume diagnostics."""

    def __init__(self):
        self.formatting_analyzer = FormattingAnalyzer()
        self.contact_analyzer = ContactAnalyzer()
        self.readability_analyzer = ReadabilityAnalyzer()
        self.action_verb_analyzer = ActionVerbAnalyzer()
        self.achievement_analyzer = AchievementAnalyzer()
        self.grammar_analyzer = GrammarAnalyzer()
        self.experience_analyzer = ExperienceAnalyzer()
        self.aggregator = ScoreAggregator()

    def process(self, text: str, data: Dict[str, Any]) -> Dict[str, Any]:
        formatting_res = self.formatting_analyzer.analyze(text, data)
        contact_res = self.contact_analyzer.analyze(text, data)
        readability_res = self.readability_analyzer.analyze(text, data)
        action_verb_res = self.action_verb_analyzer.analyze(text, data)
        achievement_res = self.achievement_analyzer.analyze(text, data)
        grammar_res = self.grammar_analyzer.analyze(text, data)
        experience_res = self.experience_analyzer.analyze(text, data)

        keywords_score = data.get("keyword_score", 10)
        project_score = data.get("project_score", 10)

        overall_ats, breakdown, strength_meter = self.aggregator.aggregate(
            formatting_res,
            contact_res,
            readability_res,
            action_verb_res,
            achievement_res,
            grammar_res,
            experience_res,
            keywords_score,
            project_score
        )

        compiled_suggestions = []
        compiled_suggestions.extend(formatting_res["suggestions"])
        compiled_suggestions.extend(contact_res["suggestions"])
        compiled_suggestions.extend(readability_res["suggestions"])
        compiled_suggestions.extend(action_verb_res["suggestions"])
        compiled_suggestions.extend(achievement_res["suggestions"])
        compiled_suggestions.extend(grammar_res["suggestions"])
        compiled_suggestions.extend(experience_res["suggestions"])

        explanations = {
            "formatting": formatting_res["explanation"],
            "contact": contact_res["explanation"],
            "readability": readability_res["explanation"],
            "action_verb": action_verb_res["explanation"],
            "achievement": achievement_res["explanation"],
            "grammar": grammar_res["explanation"],
            "experience": experience_res["explanation"]
        }

        return {
            "ats_score": overall_ats,
            "breakdown": breakdown,
            "strength_meter": strength_meter,
            "suggestions": compiled_suggestions,
            "explanations": explanations
        }
