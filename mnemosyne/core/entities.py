"""
Entity Sketching System
Lightweight entity extraction and fuzzy matching without heavy NLP dependencies.

Uses regex patterns for entity extraction and pure Python Levenshtein distance
for fuzzy matching. No spaCy, no PyTorch, no external NLP libraries.

Storage: TripleStore triples (subject=memory_id, predicate="mentions", object="entity_name")
"""

import re
from typing import List, Optional, Set, Tuple


# =============================================================================
# STOP WORDS — filtered from entity extraction
# =============================================================================

ENTITY_EXTRACTION_STOP_WORDS: Set[str] = {
    # Standard stop words
    "the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for",
    "of", "with", "by", "from", "as", "is", "was", "are", "were", "be",
    "been", "being", "have", "has", "had", "do", "does", "did", "will",
    "would", "could", "should", "may", "might", "can", "shall",
    "i", "you", "he", "she", "it", "we", "they", "me", "him", "her",
    "us", "them", "my", "your", "his", "its", "our", "their",
    "this", "that", "these", "those", "here", "there", "where",
    "when", "what", "which", "who", "whom", "whose", "how", "why",
    # Meta/system words that are NOT meaningful entities — extracted noise
    # from LLM-generated summaries and extraction prompts
    "assistant", "user", "skill", "review", "target", "class",
    "level", "signals", "phase", "api", "pi", "summary", "added",
    "active", "be", "not", "whether", "all", "no", "replying",
    "ai", "memory", "conversation", "fact",
    "false", "true", "none", "null", "signal",
    "hermes", "assistant", "agent", "model", "system", "memory",
    "note", "task", "project", "result", "output", "input", "data",
    "step", "process", "point", "way", "thing", "time", "work",
}

# Backward compatibility alias
_STOP_WORDS = ENTITY_EXTRACTION_STOP_WORDS


# =============================================================================
# COMMON WORDS — lone capitalized common words that start sentences are NOT
# entities.  This list is the "if it's a common word and it's alone, drop it"
# guard for the entity extractor.  Multi-word phrases and true proper nouns
# (ComfyUI, London, Python) pass through because they are either multi-word
# or misspelled enough (or domain-specific enough) that a dictionary check
# would be wrong.
#
# This is the same pattern Milgauss applied to prefetch in #249 and to the
# fact-extraction object side in #248 — the entity extractor (which feeds the
# 'mentions' table) was the last path without this guard (issue #251).
# =============================================================================

_COMMON_WORDS: Set[str] = {
    # Days / months (very common sentence starters)
    "monday", "tuesday", "wednesday", "thursday", "friday", "saturday", "sunday",
    "january", "february", "march", "april", "may", "june", "july", "august",
    "september", "october", "november", "december",
    # Temporal / narrative sentence starters
    "today", "tomorrow", "yesterday", "now", "then", "next", "last", "ago",
    "soon", "later", "earlier", "already", "yet", "still", "always", "never",
    "sometimes", "often", "rarely", "usually", "finally", "eventually",
    "recently", "currently", "previously", "initially", "subsequently",
    # Discourse markers / conversational openers
    "about", "actually", "basically", "essentially", "generally", "honestly",
    "ideally", "literally", "normally", "originally", "probably", "really",
    "seriously", "technically", "typically", "unfortunately", "interestingly",
    "apparently", "admittedly", "hopefully",
    "also", "anyway", "besides", "furthermore", "meanwhile", "moreover",
    "nevertheless", "nonetheless", "otherwise", "therefore", "thus",
    "first", "second", "third", "lastly",
    # Quantifiers / determiners
    "another", "any", "each", "every", "many", "most", "several", "some",
    "both", "either", "neither", "such", "what", "which",
    # Prepositions that can start sentences
    "after", "before", "beyond", "during", "inside", "outside", "since",
    "through", "throughout", "under", "until", "upon", "within", "without",
    "across", "against", "along", "among", "around", "behind", "below",
    "beneath", "beside", "between",
    # Common adjectives that appear sentence-initially
    "different", "same", "other", "another", "multiple", "various",
    "certain", "specific", "particular", "individual", "separate",
    "possible", "likely", "unlikely", "necessary", "important", "relevant",
    "simple", "complex", "basic", "advanced", "modern", "traditional",
    "current", "previous", "future", "present", "past",
    "full", "empty", "large", "small", "high", "low", "long", "short",
    "fast", "slow", "easy", "hard", "good", "bad", "new", "old",
    "big", "little", "much", "less", "more", "extra",
    # Common verbs as sentence starters
    "consider", "note", "notice", "remember", "imagine", "suppose",
    "assume", "guess", "wonder", "expect", "hope", "think", "know",
    "believe", "feel", "see", "look", "seem", "appear", "sound",
    "try", "use", "make", "take", "get", "give", "put", "set",
    "let", "keep", "find", "show", "mean", "need", "want", "ask",
    "answer", "respond", "reply", "explain", "describe", "discuss",
    "mention", "suggest", "recommend", "propose", "require", "allow",
    "enable", "prevent", "cause", "create", "produce", "provide",
    "include", "contain", "consist", "involve", "concern",
    "start", "stop", "begin", "continue", "finish", "complete",
    "follow", "lead", "result", "allow", "change",
    # Other high-frequency sentence-initial common words
    "however", "though", "although", "while", "whereas",
    "instead", "rather", "rather", "indeed", "well",
    "please", "thanks", "thank", "yes", "no", "ok", "okay",
    "sure", "fine", "great", "perfect", "awesome", "cool", "nice",
    "interesting", "amazing", "wonderful", "terrible", "horrible",
    # Single-word quantifiers that are numeric/ordinal
    "one", "two", "three", "four", "five", "six", "seven", "eight", "nine", "ten",
    "firstly", "secondly", "thirdly",
    # Text/email meta
    "subject", "regarding", "re", "fwd", "fw",
    # Frequency / adverbs
    "always", "never", "often", "seldom", "rarely", "frequently",
    "usually", "normally", "typically", "commonly", "occasionally",
    "regularly", "constantly", "continuously", "repeatedly",
    "once", "twice", "again",
}


# =============================================================================
# REGEX PATTERNS FOR ENTITY EXTRACTION
# =============================================================================

_ENTITY_PATTERNS = [
    # @mentions: @username
    re.compile(r'@(\w{2,30})'),
    # Hashtags: #topic
    re.compile(r'#(\w{2,30})'),
    # Quoted phrases: "Hello World"
    re.compile(r'"([^"]{2,50})"'),
    # Single-quoted phrases: 'Hello World'
    re.compile(r"'([^']{2,50})'"),
    # Capitalized word sequences (2-5 words): New York, Abdias J, San Francisco Bay Area
    re.compile(r'\b([A-Z][a-zA-Z]*(?:\s+[A-Z][a-zA-Z]*){1,4})\b'),
    # Single capitalized word (fallback): Abdias, Python, John
    re.compile(r'\b([A-Z][a-zA-Z]{1,20})\b'),
]


# =============================================================================
# 1. PURE PYTHON LEVENSHTEIN
# =============================================================================

def levenshtein_distance(s1: str, s2: str) -> int:
    """
    Compute the Levenshtein edit distance between two strings.
    Pure Python, zero dependencies.  O(len(s1) * len(s2)) time, O(min) space.
    """
    if len(s1) < len(s2):
        s1, s2 = s2, s1  # ensure s2 is the shorter one

    if not s2:
        return len(s1)

    # Use two rows (current and previous) to keep space O(min(len1, len2))
    previous_row = list(range(len(s2) + 1))
    current_row = [0] * (len(s2) + 1)

    for i, c1 in enumerate(s1):
        current_row[0] = i + 1

        for j, c2 in enumerate(s2):
            # Cost: 0 if same character, 1 if different
            insertions = previous_row[j + 1] + 1
            deletions = current_row[j] + 1
            substitutions = previous_row[j] + (0 if c1 == c2 else 1)
            current_row[j + 1] = min(insertions, deletions, substitutions)

        # Swap rows
        previous_row, current_row = current_row, previous_row

    return previous_row[len(s2)]


def similarity(s1: str, s2: str) -> float:
    """
    Entity-aware similarity score: 1.0 = identical, 0.0 = completely different.

    Uses case-insensitive comparison with prefix/substring bonuses for
    entity name matching (e.g., "Abdias" vs "Abdias J" = 0.925).
    """
    s1_lower = s1.lower().strip()
    s2_lower = s2.lower().strip()

    if s1_lower == s2_lower:
        return 1.0

    max_len = max(len(s1_lower), len(s2_lower))
    if max_len == 0:
        return 1.0

    # Prefix match bonus: 'Abdias' vs 'Abdias J'
    if s1_lower.startswith(s2_lower) or s2_lower.startswith(s1_lower):
        longer = max(len(s1_lower), len(s2_lower))
        shorter = min(len(s1_lower), len(s2_lower))
        # Require at least 30% length ratio to avoid short prefix noise
        # (e.g. "her" prefix-matching "Hermes" with only 3/7 ratio)
        if shorter / longer < 0.3:
            return 0.0
        return 0.7 + (shorter / longer) * 0.3  # 0.7 base + scaled bonus

    # Substring match: 'Mr. Smith' contains 'Smith'
    if s1_lower in s2_lower or s2_lower in s1_lower:
        longer = max(len(s1_lower), len(s2_lower))
        shorter = min(len(s1_lower), len(s2_lower))
        return 0.5 + (shorter / longer) * 0.3

    dist = levenshtein_distance(s1_lower, s2_lower)
    return 1.0 - (dist / max_len)


def extract_entities_regex(text: str) -> List[str]:
    """
    Extract entity candidates from text using regex patterns.

    Returns list of unique entity strings. No external dependencies.
    Filters out stop words, single lowercase words, and pure numbers.
    """
    if not text or not isinstance(text, str):
        return []

    entities: Set[str] = set()

    for pattern in _ENTITY_PATTERNS:
        for match in pattern.finditer(text):
            entity = match.group(1).strip()
            # Filter: must be at least 2 chars
            if len(entity) < 2:
                continue
            # Filter out stop words (single word only); case-insensitive
            words = entity.split()
            if len(words) == 1 and entity.lower() in _STOP_WORDS:
                continue
            # Filter out lone common words that start sentences but are not
            # proper nouns (e.g. "About", "Today", "Different", "Actually")
            # Multi-word phrases always pass; proper nouns pass because they
            # are not in _COMMON_WORDS.
            if len(words) == 1 and entity[0].isupper() and entity.lower() in _COMMON_WORDS:
                continue
            # Filter entities where ANY word is a stopword (e.g. "The USER",
            # "Active Signal" -- the stopword contaminates the whole phrase)
            if any(w.lower() in _STOP_WORDS for w in words):
                continue
            # Filter out pure numbers
            if entity.replace('.', '').replace(',', '').isdigit():
                continue
            # Filter out standalone lowercase words (unless quoted/mentioned)
            # But allow @mentions and hashtags which are lowercase by nature
            if len(words) == 1 and entity[0].islower() and not entity.startswith('@') and not entity.startswith('#'):
                # Check if this entity came from an @mention or #hashtag pattern
                # by looking at the original match position in the text
                match_start = match.start(1)  # start of group 1 (the captured entity)
                if match_start > 0:
                    prefix_char = text[match_start - 1] if match_start > 0 else ''
                    if prefix_char in ('@', '#'):
                        pass  # Allow @mentions and hashtags
                    else:
                        continue
                else:
                    continue
            entities.add(entity)

    # Post-process: merge adjacent capitalized words that appear together
    # e.g., if we have "New" and "York" separately, but "New York" also matched,
    # keep only the longest match
    result = sorted(list(entities))
    
    # Remove substrings that are part of longer entities
    # But only for word-like entities (not @mentions or hashtags)
    filtered: Set[str] = set()
    for entity in result:
        is_substring = False
        for other in result:
            if other != entity and entity in other:
                # Don't remove @mentions or hashtags that happen to be substrings
                if entity.startswith('@') or entity.startswith('#'):
                    continue
                # Don't remove if the containing entity starts with @ or #
                if other.startswith('@') or other.startswith('#'):
                    continue
                is_substring = True
                break
        if not is_substring:
            filtered.add(entity)

    return sorted(list(filtered))


def find_similar_entities(entity: str, known_entities: List[str], threshold: float = 0.8) -> List[Tuple[str, float]]:
    """
    Find known entities similar to the given entity.

    Returns list of (entity_name, similarity_score) tuples, sorted by score descending.
    """
    # Bound the fuzzy-match cost: entity names are short, so an over-long input is
    # a sentence/query, not an entity. Matching it against every known entity is
    # O(len(entity) * N) pure-Python Levenshtein and can pin a CPU core for
    # minutes; refuse it rather than melt down. Callers should pass extracted
    # entities, not raw text.
    if len(entity) > 64:
        return []
    matches: List[Tuple[str, float]] = []
    for known in known_entities:
        if known == entity:
            matches.append((known, 1.0))
            continue
        sim = similarity(entity, known)
        if sim >= threshold:
            matches.append((known, sim))

    matches.sort(key=lambda x: x[1], reverse=True)
    return matches


def entity_extraction_performance(text: str, iterations: int = 1000) -> float:
    """
    Measure entity extraction performance.
    Returns average time per extraction in milliseconds.
    """
    import time
    start = time.perf_counter()
    for _ in range(iterations):
        extract_entities_regex(text)
    elapsed = time.perf_counter() - start
    return (elapsed / iterations) * 1000
