import math
import re
from abc import ABC, abstractmethod
from typing import Dict, List, Any

# Simple standard English stopwords list
STOPWORDS = {
    "a", "about", "above", "after", "again", "against", "all", "am", "an", "and", "any", "are", "arent", "as", "at",
    "be", "because", "been", "before", "being", "below", "between", "both", "but", "by", "cant", "cannot", "could",
    "did", "didnt", "do", "does", "doesnt", "doing", "dont", "down", "during", "each", "few", "for", "from", "further",
    "had", "hadnt", "has", "hasnt", "have", "havent", "having", "he", "hed", "hell", "hes", "her", "here", "heres",
    "hers", "herself", "him", "himself", "his", "how", "hows", "i", "id", "ill", "im", "ive", "if", "in", "into",
    "is", "isnt", "it", "its", "itself", "lets", "me", "more", "most", "mustnt", "my", "myself", "no", "nor", "not",
    "of", "off", "on", "once", "only", "or", "other", "ought", "our", "ours", "ourselves", "out", "over", "own",
    "same", "shant", "she", "shed", "shell", "shes", "should", "shouldnt", "so", "some", "such", "than", "that",
    "thats", "the", "their", "theirs", "them", "themselves", "then", "there", "theres", "these", "they", "theyd",
    "theyll", "theyre", "theyve", "this", "those", "through", "to", "too", "under", "until", "up", "very", "was",
    "wasnt", "we", "wed", "well", "were", "weve", "werent", "what", "whats", "when", "whens", "where", "wheres",
    "which", "while", "who", "whos", "whom", "why", "whys", "with", "wont", "would", "wouldnt", "you", "youd",
    "youll", "youre", "youve", "your", "yours", "yourself", "yourselves"
}

# Lightweight synonym expansion for technical terms
SYNONYM_MAP = {
    "python": ["py"],
    "javascript": ["js", "ecmascript"],
    "typescript": ["ts"],
    "postgresql": ["postgres"],
    "machine learning": ["ml"],
    "artificial intelligence": ["ai"],
    "amazon web services": ["aws"],
    "google cloud": ["gcp"],
    "continuous integration": ["ci/cd", "cicd"],
    "reactjs": ["react"],
    "node": ["nodejs", "node.js"],
    "docker container": ["docker"],
    "kubernetes": ["k8s"],
}


def _stem_word(word: str) -> str:
    """Very light Porter-style stemming for common suffixes."""
    w = word.lower()
    # Common suffixes
    for suffix in ["ing", "ed", "er", "est", "ly", "tion", "sion", "ness", "ment", "able", "ible", "ful", "less"]:
        if w.endswith(suffix) and len(w) > len(suffix) + 2:
            w = w[:-len(suffix)]
            break
    return w


def _expand_tokens(tokens: List[str]) -> List[str]:
    """Expand tokens with synonyms and stemmed forms."""
    expanded = set(tokens)
    for token in tokens:
        # Add stemmed form
        expanded.add(_stem_word(token))
        # Add synonyms
        for key, synonyms in SYNONYM_MAP.items():
            if token == key or token in synonyms:
                expanded.add(key)
                expanded.update(synonyms)
    return list(expanded)


class BaseSemanticMatcher(ABC):
    """Abstract interface for semantic resume-to-job matching engines."""

    @abstractmethod
    def match(self, resume_text: str, target_requirements: str) -> Dict[str, Any]:
        pass


class TFIDFSemanticMatcher(BaseSemanticMatcher):
    """Improved TF-IDF Cosine Similarity with stemming and synonym expansion."""

    def _tokenize(self, text: str) -> List[str]:
        text = text.lower()
        words = re.findall(r"\b[a-z]{2,}\b", text)
        return [w for w in words if w not in STOPWORDS]

    def _compute_tf(self, tokens: List[str]) -> Dict[str, float]:
        tf = {}
        total = len(tokens)
        if total == 0:
            return tf
        for t in tokens:
            tf[t] = tf.get(t, 0.0) + 1.0
        for t in tf:
            tf[t] = tf[t] / total
        return tf

    def match(self, resume_text: str, target_requirements: str) -> Dict[str, Any]:
        if not resume_text.strip() or not target_requirements.strip():
            return {
                "match_percentage": 0,
                "similarity_score": 0.0,
                "overlap_keywords": []
            }

        resume_tokens = self._tokenize(resume_text)
        req_tokens = self._tokenize(target_requirements)

        # Expand with synonyms and stemming
        resume_tokens = _expand_tokens(resume_tokens)
        req_tokens = _expand_tokens(req_tokens)

        vocabulary = set(resume_tokens + req_tokens)

        df = {}
        for term in vocabulary:
            count = 0
            if term in resume_tokens:
                count += 1
            if term in req_tokens:
                count += 1
            df[term] = count

        idf = {}
        for term in vocabulary:
            idf[term] = math.log(1.0 + (2.0 / df[term]))

        tf_resume = self._compute_tf(resume_tokens)
        tf_req = self._compute_tf(req_tokens)

        vec_resume = {term: tf_resume.get(term, 0.0) * idf[term] for term in vocabulary}
        vec_req = {term: tf_req.get(term, 0.0) * idf[term] for term in vocabulary}

        dot_product = sum(vec_resume[term] * vec_req[term] for term in vocabulary)

        magnitude_resume = math.sqrt(sum(val ** 2 for val in vec_resume.values()))
        magnitude_req = math.sqrt(sum(val ** 2 for val in vec_req.values()))

        if magnitude_resume == 0.0 or magnitude_req == 0.0:
            similarity = 0.0
        else:
            similarity = dot_product / (magnitude_resume * magnitude_req)

        match_pct = int(similarity * 100)
        overlap_keywords = list(sorted(set(resume_tokens).intersection(set(req_tokens))))
        overlap_display = [w.capitalize() for w in overlap_keywords[:15]]

        return {
            "match_percentage": min(max(match_pct, 0), 100),
            "similarity_score": round(similarity, 4),
            "overlap_keywords": overlap_display
        }
