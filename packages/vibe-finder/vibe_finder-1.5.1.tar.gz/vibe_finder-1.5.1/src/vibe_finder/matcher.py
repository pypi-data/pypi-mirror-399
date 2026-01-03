"""
Token-Based Marker Matching

Unified token matching logic for SPLIT1 and SPLIT2.
Finds marker position in text using gap-tolerant token sequence matching.

ALGORITHM OVERVIEW:
==================
1. Tokenize marker into normalized words/numbers
2. Find all positions of first token in text (exact + fuzzy)
3. For each candidate, try to match subsequent tokens with gap constraints
4. Progressively narrow candidates until single match or all tokens used
5. If multiple matches remain, use proximity to reference position

MATCHING RULES:
==============
- MAX_SINGLE_GAP: Maximum chars between consecutive matched tokens (default: 50)
- MAX_TOTAL_SKIPS: Maximum tokens that can be skipped total (default: 2)
- MAX_CONSECUTIVE_SKIPS: Maximum tokens skipped in a row (default: 1)
- MIN_TOKENS_REQUIRED: Minimum tokens that must match (default: 3)

DISAMBIGUATION:
==============
- END markers: Pick match nearest to (after) reference position
- START markers: Pick match nearest to (before) reference position

FUZZY MATCHING (for OCR typos):
==============================
- Jaro-Winkler similarity for short words (better than Levenshtein)
- Adaptive thresholds: shorter words = lower threshold (1 char = bigger impact)
- Token cloud detection: finds clusters of marker tokens even if reordered
- Transposition counting: penalizes out-of-order tokens (Kendall tau)

SEQUENCE SCORING:
================
score = W_SIMILARITY * Σ(token_scores) +
        W_COVERAGE * tokens_found +
        W_SEQUENTIAL * sequential_bonus +
        W_GAP_PENALTY * avg_gap +
        W_SKIP_PENALTY * skips +
        W_TRANSPOSITION * transpositions
"""

import re
import logging
from typing import List, Dict, Any, Tuple, Optional
from dataclasses import dataclass, field

logger = logging.getLogger(__name__)


# =============================================================================
# FUZZY MATCHING - Jaro-Winkler Similarity
# =============================================================================

def jaro_similarity(s1: str, s2: str) -> float:
    """
    Calculate Jaro similarity between two strings.

    Returns value between 0.0 (no similarity) and 1.0 (identical).
    Optimized for short strings like words.
    """
    if s1 == s2:
        return 1.0

    len1, len2 = len(s1), len(s2)

    if len1 == 0 or len2 == 0:
        return 0.0

    # Maximum matching distance
    match_distance = max(len1, len2) // 2 - 1
    if match_distance < 0:
        match_distance = 0

    s1_matches = [False] * len1
    s2_matches = [False] * len2

    matches = 0
    transpositions = 0

    # Find matches
    for i in range(len1):
        start = max(0, i - match_distance)
        end = min(i + match_distance + 1, len2)

        for j in range(start, end):
            if s2_matches[j] or s1[i] != s2[j]:
                continue
            s1_matches[i] = True
            s2_matches[j] = True
            matches += 1
            break

    if matches == 0:
        return 0.0

    # Count transpositions
    k = 0
    for i in range(len1):
        if not s1_matches[i]:
            continue
        while not s2_matches[k]:
            k += 1
        if s1[i] != s2[k]:
            transpositions += 1
        k += 1

    jaro = (
        matches / len1 +
        matches / len2 +
        (matches - transpositions / 2) / matches
    ) / 3

    return jaro


def jaro_winkler_similarity(s1: str, s2: str, prefix_weight: float = 0.1) -> float:
    """
    Calculate Jaro-Winkler similarity between two strings.

    Gives bonus for common prefix (up to 4 chars).
    Better than Levenshtein for short strings like names/words.

    Args:
        s1, s2: Strings to compare
        prefix_weight: Weight for prefix bonus (default 0.1)

    Returns:
        Similarity between 0.0 and 1.0

    Example:
        >>> jaro_winkler_similarity("могуг", "могут")
        0.92  # "могу" prefix matches, only "г" vs "т" differs
    """
    jaro = jaro_similarity(s1, s2)

    # Common prefix (up to 4 chars)
    prefix_len = 0
    for i in range(min(len(s1), len(s2), 4)):
        if s1[i] == s2[i]:
            prefix_len += 1
        else:
            break

    return jaro + prefix_len * prefix_weight * (1 - jaro)


def get_adaptive_threshold(word_len: int) -> float:
    """
    Get fuzzy matching threshold based on word length.

    Shorter words = lower threshold because 1 char error = bigger impact.

    | Word length | Threshold | Rationale |
    |-------------|-----------|-----------|
    | 3 chars     | 0.60      | 1 miss = 33% error |
    | 4 chars     | 0.70      | 1 miss = 25% error |
    | 5 chars     | 0.75      | 1 miss = 20% error |
    | 6+ chars    | 0.80      | Standard |
    """
    thresholds = {3: 0.60, 4: 0.70, 5: 0.75}
    return thresholds.get(word_len, 0.80)


@dataclass
class FuzzyMatch:
    """Result of fuzzy matching a token."""
    word_idx: int           # Index in word_list
    word: str               # The matched word
    similarity: float       # Jaro-Winkler similarity score
    is_exact: bool          # True if exact match
    is_prefix: bool         # True if prefix match (merged word)


def find_fuzzy_matches(
    word_list: List[Dict],
    token: str,
    min_similarity: float = None,
    search_start_idx: int = 0,
    min_char_offset: int = 0
) -> List[FuzzyMatch]:
    """
    Find all fuzzy matches for a token in word_list.

    Returns ALL matches (exact + fuzzy above threshold), sorted by similarity.

    Args:
        word_list: Pre-tokenized document [{word, start, end}, ...]
        token: Token to search for
        min_similarity: Minimum similarity threshold (default: adaptive by word length)
        search_start_idx: Start searching from this word index
        min_char_offset: Minimum character offset

    Returns:
        List of FuzzyMatch objects, sorted by similarity (highest first)
    """
    if min_similarity is None:
        min_similarity = get_adaptive_threshold(len(token))

    matches = []

    for idx in range(search_start_idx, len(word_list)):
        entry = word_list[idx]
        word = entry['word']

        # Skip if before min_char_offset
        if entry['end'] < min_char_offset:
            continue

        # Check exact match first
        if word == token:
            matches.append(FuzzyMatch(
                word_idx=idx,
                word=word,
                similarity=1.0,
                is_exact=True,
                is_prefix=False
            ))
            continue

        # Check prefix match (merged words like "естьи" for "есть")
        if len(token) >= 3 and len(word) > len(token) and word.startswith(token):
            matches.append(FuzzyMatch(
                word_idx=idx,
                word=word,
                similarity=0.95,  # High score for prefix match
                is_exact=False,
                is_prefix=True
            ))
            continue

        # Check fuzzy match (OCR typos like "могуг" for "могут")
        if len(token) >= 3 and len(word) >= 3:
            similarity = jaro_winkler_similarity(token, word)
            if similarity >= min_similarity:
                matches.append(FuzzyMatch(
                    word_idx=idx,
                    word=word,
                    similarity=similarity,
                    is_exact=False,
                    is_prefix=False
                ))

    # Sort by similarity (highest first)
    matches.sort(key=lambda m: -m.similarity)

    return matches


# =============================================================================
# SEQUENCE SCORING
# =============================================================================

# Scoring weights - can be tuned
W_SIMILARITY = 10.0      # Fuzzy match quality
W_COVERAGE = 20.0        # Tokens found / total
W_SEQUENTIAL = 15.0      # In-order bonus
W_GAP_PENALTY = -0.5     # Large gaps = bad
W_SKIP_PENALTY = -5.0    # Skipped tokens = bad
W_TRANSPOSITION = -3.0   # Out-of-order penalty


@dataclass
class SequenceMatch:
    """A scored sequence of matched tokens."""
    start_word_idx: int
    end_word_idx: int
    start_char: int
    end_char: int
    matched_tokens: List[Tuple[str, int, float]]  # (token, word_idx, similarity)
    skipped_tokens: List[str]
    gaps: List[int]
    transpositions: int
    score: float


def count_transpositions(found_order: List[int], expected_order: List[int]) -> int:
    """
    Count inversions - pairs that are out of order (Kendall tau distance).

    Args:
        found_order: Order of tokens as found in text (by word_idx)
        expected_order: Expected order based on marker token positions

    Returns:
        Number of inversions (minimum swaps needed)

    Example:
        Marker: "я бы мог что-то сделать"
        Text:   "я бы что-то мог сделать"

        Expected: [0, 1, 2, 3, 4]  (я=0, бы=1, мог=2, что-то=3, сделать=4)
        Found:    [0, 1, 3, 2, 4]  (я=0, бы=1, что-то=3, мог=2, сделать=4)

        Inversions: 1 (мог and что-то are swapped)
    """
    if len(found_order) <= 1:
        return 0

    inversions = 0
    for i in range(len(found_order)):
        for j in range(i + 1, len(found_order)):
            if found_order[i] > found_order[j]:
                inversions += 1

    return inversions


def score_sequence(
    matched_tokens: List[Tuple[str, int, float]],
    marker_tokens: List[str],
    gaps: List[int],
    skipped_tokens: List[str]
) -> Tuple[float, int]:
    """
    Score a matched sequence using weighted formula.

    Args:
        matched_tokens: List of (token, word_idx, similarity) for matched tokens
        marker_tokens: Original marker tokens
        gaps: Character gaps between consecutive matched tokens
        skipped_tokens: Tokens that were skipped

    Returns:
        Tuple of (score, transpositions)

    Formula:
        score = W_SIMILARITY * Σ(similarity) +
                W_COVERAGE * tokens_found +
                W_SEQUENTIAL * sequential_bonus +
                W_GAP_PENALTY * avg_gap +
                W_SKIP_PENALTY * skips +
                W_TRANSPOSITION * transpositions
    """
    if not matched_tokens:
        return (0.0, 0)

    # Similarity score
    similarity_sum = sum(sim for _, _, sim in matched_tokens)

    # Coverage
    tokens_found = len(matched_tokens)

    # Sequential bonus - ratio of tokens that are in correct order
    # Build expected order based on marker positions
    token_to_marker_idx = {t: i for i, t in enumerate(marker_tokens)}
    found_order = []
    for token, word_idx, _ in matched_tokens:
        if token in token_to_marker_idx:
            found_order.append(token_to_marker_idx[token])

    # Count transpositions
    expected_order = sorted(found_order)
    transpositions = count_transpositions(found_order, expected_order)

    # Sequential bonus: higher if tokens are in correct order
    if len(found_order) > 1:
        sequential_ratio = 1.0 - (transpositions / (len(found_order) * (len(found_order) - 1) / 2))
    else:
        sequential_ratio = 1.0
    sequential_bonus = sequential_ratio * tokens_found

    # Average gap
    avg_gap = sum(gaps) / len(gaps) if gaps else 0

    # Skip count
    skips = len(skipped_tokens)

    # Calculate final score
    score = (
        W_SIMILARITY * similarity_sum +
        W_COVERAGE * tokens_found +
        W_SEQUENTIAL * sequential_bonus +
        W_GAP_PENALTY * avg_gap +
        W_SKIP_PENALTY * skips +
        W_TRANSPOSITION * transpositions
    )

    return (score, transpositions)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class MatchConfig:
    """Configuration for token matching."""
    max_single_gap: int = 50          # Max chars between consecutive tokens
    max_total_skips: int = 2          # Max tokens that can be skipped total
    max_consecutive_skips: int = 1    # Max tokens skipped in a row
    min_tokens_required: int = 1      # Minimum tokens that must match (1 for single-word markers)
    min_tokens_in_marker: int = 1     # Minimum tokens marker must have (1 for single words like "меньше")
    enable_fuzzy: bool = True         # Enable fuzzy matching for OCR typos
    min_fuzzy_similarity: float = None  # Minimum similarity (None = adaptive by word length)


DEFAULT_CONFIG = MatchConfig()


# =============================================================================
# TOKEN EXTRACTION
# =============================================================================

def tokenize_marker(marker: str) -> List[str]:
    """
    Extract normalized tokens from marker text.

    Tokens are:
    - Words (letters only): normalized to lowercase
    - Numbers: kept as-is
    - Mixed alphanumeric: kept as-is, lowercased

    Args:
        marker: Raw marker text from LLM

    Returns:
        List of normalized tokens

    Example:
        >>> tokenize_marker("Текст 2024 года...")
        ['текст', '2024', 'года']
    """
    if not marker:
        return []

    # Extract word/number tokens using \w+ (letters, digits, underscore)
    raw_tokens = re.findall(r'\w+', marker)

    # Normalize: lowercase all tokens
    normalized = [t.lower() for t in raw_tokens]

    # Filter out single-char tokens that aren't meaningful
    # Keep: single digits, single letters that are words (а, я, и, о, в, etc.)
    meaningful = []
    for token in normalized:
        if len(token) == 1:
            # Keep single digits and common single-letter words
            if token.isdigit() or token in {'а', 'я', 'и', 'о', 'в', 'к', 'с', 'у', 'a', 'i'}:
                meaningful.append(token)
        else:
            meaningful.append(token)

    return meaningful


def build_word_index(word_list: List[Dict]) -> Dict[str, List[int]]:
    """
    Build inverted index: word -> list of positions in word_list.

    Args:
        word_list: Pre-tokenized document [{word, start, end}, ...]

    Returns:
        Dict mapping each word to list of indices where it appears

    Example:
        >>> idx = build_word_index([{word:'hello',...}, {word:'world',...}, {word:'hello',...}])
        >>> idx['hello']
        [0, 2]
    """
    index = {}
    for i, entry in enumerate(word_list):
        word = entry['word']
        if word not in index:
            index[word] = []
        index[word].append(i)
    return index


def find_prefix_matches(word_list: List[Dict], token: str, min_len: int = 3) -> List[int]:
    """
    Find words in word_list that START WITH the given token.

    Handles OCR merged words like "естьи" matching token "есть".
    Only matches if token is at least min_len chars (avoid false positives).

    Args:
        word_list: Pre-tokenized document [{word, start, end}, ...]
        token: Token to search for as prefix
        min_len: Minimum token length to attempt prefix matching

    Returns:
        List of indices where word starts with token

    Example:
        >>> find_prefix_matches([{word:'естьи',...}], 'есть')
        [0]  # "естьи" starts with "есть"
    """
    if len(token) < min_len:
        return []

    matches = []
    for i, entry in enumerate(word_list):
        word = entry['word']
        # Check if word starts with token (merged word scenario)
        # Token must be shorter than word (otherwise it's not merged)
        if len(word) > len(token) and word.startswith(token):
            matches.append(i)
    return matches


# =============================================================================
# CANDIDATE TRACKING
# =============================================================================

@dataclass
class MatchCandidate:
    """Tracks a potential marker match through progressive token matching."""
    start_word_idx: int           # Index in word_list where match starts
    end_word_idx: int             # Index in word_list where match currently ends
    start_char: int               # Character position where match starts
    end_char: int                 # Character position where match ends
    tokens_matched: int           # Number of tokens successfully matched
    tokens_skipped: int           # Total tokens skipped
    consecutive_skips: int        # Current consecutive skip count
    gaps: List[int]               # Gaps between consecutive matched tokens
    matched_tokens: List[str]     # Which tokens were matched
    skipped_tokens: List[str]     # Which tokens were skipped
    # Fuzzy matching additions
    token_similarities: List[float] = field(default_factory=list)  # Similarity for each matched token
    fuzzy_matches: List[str] = field(default_factory=list)  # Words that were fuzzy-matched (non-exact)


# =============================================================================
# MAIN MATCHING FUNCTION
# =============================================================================

def find_marker_tokens(
    word_list: List[Dict],
    marker: str,
    text: str,
    search_start_idx: int = 0,
    min_char_offset: int = 0,
    marker_type: str = "end",
    reference_position: int = 0,
    config: MatchConfig = None
) -> Tuple[int, int, List[int], dict]:
    """
    Find marker in text using gap-tolerant token sequence matching.

    ALGORITHM:
    =========
    1. Tokenize marker → ['token1', 'token2', 'token3', ...]
    2. Find all occurrences of token1 in word_list (after search_start_idx)
    3. For each candidate:
       a. Try to find token2 within MAX_SINGLE_GAP chars
       b. If found: add to candidate, continue to token3
       c. If not found: increment skip counter, try token3
       d. Stop if skip limits exceeded
    4. After processing all tokens:
       - If 1 candidate: return it
       - If multiple: pick by proximity to reference_position
       - If 0 with MIN_TOKENS: return best partial match

    Args:
        word_list: Pre-tokenized document [{word, start, end}, ...]
        marker: Marker text to find
        text: Original document text (for offset calculation)
        search_start_idx: Start searching from this word index
        min_char_offset: Minimum character offset (prevents backward matches)
        marker_type: "end" or "start" - affects disambiguation
        reference_position: Position to use for proximity disambiguation
        config: Matching configuration (uses DEFAULT_CONFIG if None)

    Returns:
        Tuple of:
        - word_idx: Index in word_list where match starts (-1 if not found)
        - char_offset: Character offset where marker ends (-1 if not found)
        - gaps: List of character gaps between matched tokens
        - debug_info: Dict with matching details for logging
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Step 1: Tokenize marker
    marker_tokens = tokenize_marker(marker)

    debug_info = {
        'marker_raw': marker,
        'marker_tokens': marker_tokens,
        'tokens_count': len(marker_tokens),
        'search_start_idx': search_start_idx,
        'min_char_offset': min_char_offset,
        'marker_type': marker_type
    }

    # Step 2: Build word index for fast lookup
    word_index = build_word_index(word_list)

    # Handle single-token markers specially - just find first occurrence
    if len(marker_tokens) == 1:
        single_token = marker_tokens[0]
        if single_token not in word_index:
            logger.debug(f"Single token '{single_token}' not found in document")
            debug_info['error'] = 'single_token_not_found'
            return (-1, -1, -1, [], debug_info)

        # Find first occurrence after min_char_offset
        for idx in word_index[single_token]:
            if idx >= search_start_idx and word_list[idx]['end'] >= min_char_offset:
                entry = word_list[idx]
                end_offset = entry['end']
                # Include trailing punctuation
                while end_offset < len(text) and text[end_offset] in '.,!?;:—–-…»"\')\]':
                    end_offset += 1
                debug_info['result'] = {
                    'method': 'single_token',
                    'word_idx': idx,
                    'start_offset': entry['start'],
                    'end_offset': end_offset
                }
                logger.debug(f"Single token match at word[{idx}], offset {end_offset}")
                return (idx, entry['start'], end_offset, [], debug_info)

        debug_info['error'] = 'single_token_not_in_range'
        return (-1, -1, -1, [], debug_info)

    if len(marker_tokens) < config.min_tokens_in_marker:
        logger.warning(f"Marker has only {len(marker_tokens)} tokens, minimum is {config.min_tokens_in_marker}: {marker}")
        debug_info['error'] = 'insufficient_tokens'
        return (-1, -1, -1, [], debug_info)

    first_token = marker_tokens[0]

    # Step 3: Find all starting positions for first token
    # Use FUZZY matching (if enabled) to handle OCR typos
    first_token_matches: List[FuzzyMatch] = []

    if config.enable_fuzzy:
        # Use fuzzy matching - finds exact, prefix, AND similar words
        first_token_matches = find_fuzzy_matches(
            word_list=word_list,
            token=first_token,
            min_similarity=config.min_fuzzy_similarity,
            search_start_idx=search_start_idx,
            min_char_offset=min_char_offset
        )
        if first_token_matches:
            debug_info['fuzzy_first_token'] = True
            fuzzy_count = sum(1 for m in first_token_matches if not m.is_exact and not m.is_prefix)
            if fuzzy_count > 0:
                logger.debug(f"First token '{first_token}': {fuzzy_count} fuzzy matches found")
    else:
        # Legacy exact + prefix matching
        if first_token in word_index:
            for idx in word_index[first_token]:
                if idx >= search_start_idx and word_list[idx]['end'] >= min_char_offset:
                    first_token_matches.append(FuzzyMatch(
                        word_idx=idx,
                        word=word_list[idx]['word'],
                        similarity=1.0,
                        is_exact=True,
                        is_prefix=False
                    ))

        # Also get prefix matches (merged words)
        prefix_matches = find_prefix_matches(word_list, first_token, min_len=3)
        for idx in prefix_matches:
            if idx >= search_start_idx and word_list[idx]['end'] >= min_char_offset:
                first_token_matches.append(FuzzyMatch(
                    word_idx=idx,
                    word=word_list[idx]['word'],
                    similarity=0.95,
                    is_exact=False,
                    is_prefix=True
                ))
                debug_info['prefix_match_used'] = True

    # Remove duplicates by word_idx and sort by position
    seen_idx = set()
    unique_matches = []
    for m in first_token_matches:
        if m.word_idx not in seen_idx:
            seen_idx.add(m.word_idx)
            unique_matches.append(m)
    first_token_matches = sorted(unique_matches, key=lambda m: m.word_idx)

    if not first_token_matches:
        logger.debug(f"First token '{first_token}' not found in document")
        debug_info['error'] = 'first_token_not_found'
        return (-1, -1, -1, [], debug_info)

    logger.debug(f"Found {len(first_token_matches)} candidates for first token '{first_token}'")

    # Step 4: Initialize candidates from first token matches
    candidates: List[MatchCandidate] = []
    for fm in first_token_matches:
        entry = word_list[fm.word_idx]
        candidates.append(MatchCandidate(
            start_word_idx=fm.word_idx,
            end_word_idx=fm.word_idx,
            start_char=entry['start'],
            end_char=entry['end'],
            tokens_matched=1,
            tokens_skipped=0,
            consecutive_skips=0,
            gaps=[],
            matched_tokens=[first_token],
            skipped_tokens=[],
            token_similarities=[fm.similarity],
            fuzzy_matches=[fm.word] if not fm.is_exact else []
        ))

    # Step 5: Progressive token matching
    for token_idx in range(1, len(marker_tokens)):
        token = marker_tokens[token_idx]

        if not candidates:
            logger.debug(f"No candidates remaining at token {token_idx} '{token}'")
            break

        new_candidates = []

        for cand in candidates:
            # Search for this token starting after current match end
            search_from = cand.end_word_idx + 1

            # First check: Is this token part of the SAME merged word as previous token?
            # E.g., "естьи" contains both "есть" and "и" - so after matching "есть",
            # check if "и" is the suffix of "естьи"
            found = False
            if cand.end_word_idx < len(word_list):
                last_matched_word = word_list[cand.end_word_idx]['word']
                last_token = cand.matched_tokens[-1] if cand.matched_tokens else ""
                # Check if last_matched_word is a merged word containing current token as suffix
                # e.g., last_matched_word="естьи", last_token="есть", current token="и"
                # "естьи"[len("есть"):] = "и" which matches token
                if (len(last_matched_word) > len(last_token) and
                    last_matched_word[len(last_token):] == token):
                    # Token is part of the merged word - consume it without moving position
                    new_cand = MatchCandidate(
                        start_word_idx=cand.start_word_idx,
                        end_word_idx=cand.end_word_idx,  # Stay at same word
                        start_char=cand.start_char,
                        end_char=cand.end_char,  # Same end position
                        tokens_matched=cand.tokens_matched + 1,
                        tokens_skipped=cand.tokens_skipped,
                        consecutive_skips=0,
                        gaps=cand.gaps + [0],  # Zero gap - same word
                        matched_tokens=cand.matched_tokens + [token],
                        skipped_tokens=cand.skipped_tokens.copy(),
                        token_similarities=cand.token_similarities + [0.95],  # High score for suffix match
                        fuzzy_matches=cand.fuzzy_matches.copy()  # Suffix is part of merged word, not truly fuzzy
                    )
                    new_candidates.append(new_cand)
                    found = True
                    logger.debug(f"Token '{token}' matched as suffix of merged word '{last_matched_word}'")

            # If not a merged suffix, search for the token in upcoming words
            if not found:
                # Use fuzzy matching if enabled
                if config.enable_fuzzy:
                    # Get all fuzzy matches for this token starting from search_from
                    token_matches = find_fuzzy_matches(
                        word_list=word_list,
                        token=token,
                        min_similarity=config.min_fuzzy_similarity,
                        search_start_idx=search_from,
                        min_char_offset=cand.end_char  # Must be after current position
                    )

                    # Find the best match within gap limit
                    for tm in token_matches:
                        gap = word_list[tm.word_idx]['start'] - cand.end_char
                        if gap <= config.max_single_gap:
                            new_cand = MatchCandidate(
                                start_word_idx=cand.start_word_idx,
                                end_word_idx=tm.word_idx,
                                start_char=cand.start_char,
                                end_char=word_list[tm.word_idx]['end'],
                                tokens_matched=cand.tokens_matched + 1,
                                tokens_skipped=cand.tokens_skipped,
                                consecutive_skips=0,
                                gaps=cand.gaps + [gap],
                                matched_tokens=cand.matched_tokens + [token],
                                skipped_tokens=cand.skipped_tokens.copy(),
                                token_similarities=cand.token_similarities + [tm.similarity],
                                fuzzy_matches=cand.fuzzy_matches + ([tm.word] if not tm.is_exact else [])
                            )
                            new_candidates.append(new_cand)
                            found = True
                            break  # Take first (best similarity) match within gap
                else:
                    # Legacy exact + prefix matching
                    for next_idx in range(search_from, min(search_from + 20, len(word_list))):
                        next_word = word_list[next_idx]['word']
                        # Exact match OR prefix match (merged word: "естьи" matches "есть")
                        is_match = (next_word == token or
                                   (len(token) >= 3 and len(next_word) > len(token) and next_word.startswith(token)))
                        if is_match:
                            gap = word_list[next_idx]['start'] - cand.end_char

                            if gap <= config.max_single_gap:
                                # Token found within gap limit
                                new_cand = MatchCandidate(
                                    start_word_idx=cand.start_word_idx,
                                    end_word_idx=next_idx,
                                    start_char=cand.start_char,
                                    end_char=word_list[next_idx]['end'],
                                    tokens_matched=cand.tokens_matched + 1,
                                    tokens_skipped=cand.tokens_skipped,
                                    consecutive_skips=0,  # Reset consecutive skips
                                    gaps=cand.gaps + [gap],
                                    matched_tokens=cand.matched_tokens + [token],
                                    skipped_tokens=cand.skipped_tokens.copy(),
                                    token_similarities=cand.token_similarities + [1.0],
                                    fuzzy_matches=cand.fuzzy_matches.copy()
                                )
                                new_candidates.append(new_cand)
                                found = True
                                break

            if not found:
                # Token not found - try to skip it
                if (cand.tokens_skipped < config.max_total_skips and
                    cand.consecutive_skips < config.max_consecutive_skips):
                    # Allow skip
                    skip_cand = MatchCandidate(
                        start_word_idx=cand.start_word_idx,
                        end_word_idx=cand.end_word_idx,
                        start_char=cand.start_char,
                        end_char=cand.end_char,
                        tokens_matched=cand.tokens_matched,
                        tokens_skipped=cand.tokens_skipped + 1,
                        consecutive_skips=cand.consecutive_skips + 1,
                        gaps=cand.gaps.copy(),
                        matched_tokens=cand.matched_tokens.copy(),
                        skipped_tokens=cand.skipped_tokens + [token],
                        token_similarities=cand.token_similarities.copy(),
                        fuzzy_matches=cand.fuzzy_matches.copy()
                    )
                    new_candidates.append(skip_cand)
                    logger.debug(f"Skipped token '{token}' for candidate starting at {cand.start_word_idx}")

        # Check if we went from N candidates to 0
        if not new_candidates and candidates:
            logger.debug(f"Token '{token}' reduced candidates from {len(candidates)} to 0, keeping previous")
            break  # Keep previous candidates

        candidates = new_candidates

        # Note: Don't exit early - continue matching all tokens for best quality
        # Early exit only when NO candidates remain
        if len(candidates) == 0:
            logger.debug(f"No candidates at token {token_idx}")
            break

    # Step 6: Filter candidates by minimum tokens
    valid_candidates = [c for c in candidates if c.tokens_matched >= config.min_tokens_required]

    debug_info['candidates_total'] = len(candidates)
    debug_info['candidates_valid'] = len(valid_candidates)

    if not valid_candidates:
        logger.debug(f"No candidates with >= {config.min_tokens_required} tokens matched")
        debug_info['error'] = 'insufficient_matches'
        return (-1, -1, -1, [], debug_info)

    # Step 7: Select best candidate using sequence scoring
    if len(valid_candidates) == 1:
        best = valid_candidates[0]
        best_score = 0.0
        best_transpositions = 0
    else:
        # Multiple candidates - use sequence scoring + proximity
        scored_candidates = []
        for cand in valid_candidates:
            # Build matched_tokens with word indices for transposition counting
            matched_data = list(zip(
                cand.matched_tokens,
                range(len(cand.matched_tokens)),  # word positions in marker
                cand.token_similarities if cand.token_similarities else [1.0] * len(cand.matched_tokens)
            ))

            score, transpositions = score_sequence(
                matched_tokens=matched_data,
                marker_tokens=marker_tokens,
                gaps=cand.gaps,
                skipped_tokens=cand.skipped_tokens
            )

            # Add proximity bonus/penalty for tie-breaking
            if marker_type == "end":
                if cand.end_char >= reference_position:
                    proximity_bonus = -0.01 * (cand.end_char - reference_position)  # Small penalty for distance
                else:
                    proximity_bonus = -10.0  # Larger penalty for being before reference
            else:
                if cand.start_char <= reference_position:
                    proximity_bonus = -0.01 * (reference_position - cand.start_char)
                else:
                    proximity_bonus = -10.0

            final_score = score + proximity_bonus
            scored_candidates.append((cand, final_score, score, transpositions))

        # Sort by final score (highest first) and pick best
        scored_candidates.sort(key=lambda x: -x[1])
        best, best_final_score, best_score, best_transpositions = scored_candidates[0]

        debug_info['candidate_scores'] = [
            {'start_word_idx': c.start_word_idx, 'score': s, 'transpositions': t}
            for c, _, s, t in scored_candidates[:5]  # Top 5 for debugging
        ]

        logger.debug(f"Selected from {len(valid_candidates)} candidates using sequence scoring (score={best_score:.1f})")

    # Step 8: Calculate final offsets from RAW TEXT positions
    # - start_offset: First char of first matched word in raw text
    # - end_offset: Last char of last matched word in raw text (+ trailing punctuation)
    start_offset = best.start_char  # First word's first char position
    end_offset = best.end_char      # Last word's last char position

    # Include trailing punctuation for end position
    while end_offset < len(text) and text[end_offset] in '.,!?;:—–-…»"\')\]':
        end_offset += 1

    debug_info['result'] = {
        'start_word_idx': best.start_word_idx,
        'end_word_idx': best.end_word_idx,
        'start_offset': start_offset,   # First char of first matched word
        'end_offset': end_offset,       # Last char of last matched word + punctuation
        'tokens_matched': best.tokens_matched,
        'tokens_skipped': best.tokens_skipped,
        'matched_tokens': best.matched_tokens,
        'skipped_tokens': best.skipped_tokens,
        'gaps': best.gaps,
        # Fuzzy matching additions
        'token_similarities': best.token_similarities,
        'fuzzy_matches': best.fuzzy_matches,
        'sequence_score': best_score if 'best_score' in dir() else 0.0,
        'transpositions': best_transpositions if 'best_transpositions' in dir() else 0
    }

    # Log with fuzzy info if present
    fuzzy_info = f", fuzzy: {best.fuzzy_matches}" if best.fuzzy_matches else ""
    logger.debug(
        f"Match found: {best.tokens_matched}/{len(marker_tokens)} tokens, "
        f"skipped: {best.skipped_tokens}{fuzzy_info}, "
        f"raw text offsets: [{start_offset}:{end_offset}]"
    )

    return (best.start_word_idx, start_offset, end_offset, best.gaps, debug_info)


# =============================================================================
# CONVENIENCE WRAPPERS
# =============================================================================

@dataclass
class MarkerMatch:
    """Result of marker search."""
    found: bool
    word_idx: int           # Index in word_list where match starts
    start_offset: int       # First char of first matched word in RAW TEXT
    end_offset: int         # Last char of last matched word in RAW TEXT
    gaps: List[int]         # Gaps between consecutive matched tokens
    tokens_matched: int     # How many tokens were matched
    tokens_skipped: int     # How many tokens were skipped
    debug_info: dict        # Full debug information


def find_end_marker(
    word_list: List[Dict],
    marker: str,
    text: str,
    search_start_idx: int = 0,
    min_char_offset: int = 0,
    config: MatchConfig = None
) -> MarkerMatch:
    """
    Find END marker position with progressive truncation fallback.

    For END markers:
    - start_offset: First char of first matched word
    - end_offset: Last char of last matched word (use this for segment end)

    PROGRESSIVE TRUNCATION:
    If full marker not found, tries progressively shorter suffixes:
    - "word1 word2 word3 word4" → try "word2 word3 word4" → try "word3 word4"
    This handles LLM hallucination where beginning is wrong but end is correct.

    Args:
        word_list: Pre-tokenized document. Each entry MUST have:
                   - 'word': lowercase token
                   - 'start': first char position in RAW TEXT
                   - 'end': last char position in RAW TEXT
        marker: END marker text from LLM
        text: Original RAW TEXT (for punctuation detection)
        search_start_idx: Start searching from this word index
        min_char_offset: Minimum char offset (prevents backward matches)
        config: Matching configuration

    Returns:
        MarkerMatch with found=True/False and offsets
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Tokenize marker to check length
    marker_tokens = tokenize_marker(marker)

    # Try full marker first
    word_idx, start_offset, end_offset, gaps, debug_info = find_marker_tokens(
        word_list=word_list,
        marker=marker,
        text=text,
        search_start_idx=search_start_idx,
        min_char_offset=min_char_offset,
        marker_type="end",
        reference_position=min_char_offset,
        config=config
    )

    # If found, return immediately
    if word_idx != -1:
        result = debug_info.get('result', {})
        return MarkerMatch(
            found=True,
            word_idx=word_idx,
            start_offset=start_offset,
            end_offset=end_offset,
            gaps=gaps,
            tokens_matched=result.get('tokens_matched', 0),
            tokens_skipped=result.get('tokens_skipped', 0),
            debug_info=debug_info
        )

    # PROGRESSIVE TRUNCATION: Try shorter suffixes
    # Only if marker has 4+ tokens, try removing first 1-2 tokens
    # Use strict config (no skips) to avoid false matches
    if len(marker_tokens) >= 4:
        strict_config = MatchConfig(
            max_single_gap=config.max_single_gap,
            max_total_skips=0,           # NO token skipping during truncation
            max_consecutive_skips=0,      # NO token skipping during truncation
            min_tokens_required=2,
            min_tokens_in_marker=2
        )

        for skip_count in [1, 2]:
            if len(marker_tokens) - skip_count < strict_config.min_tokens_in_marker:
                break

            truncated_tokens = marker_tokens[skip_count:]
            truncated_marker = ' '.join(truncated_tokens)

            logger.debug(f"Truncation fallback: trying '{truncated_marker}' (skipped {skip_count} tokens, strict mode)")

            word_idx, start_offset, end_offset, gaps, trunc_debug = find_marker_tokens(
                word_list=word_list,
                marker=truncated_marker,
                text=text,
                search_start_idx=search_start_idx,
                min_char_offset=min_char_offset,
                marker_type="end",
                reference_position=min_char_offset,
                config=strict_config  # Use strict config
            )

            if word_idx != -1:
                result = trunc_debug.get('result', {})
                trunc_debug['truncation_used'] = True
                trunc_debug['tokens_skipped_from_start'] = skip_count
                trunc_debug['original_marker'] = marker
                logger.info(f"Truncation fallback SUCCESS: '{truncated_marker}' found after skipping {skip_count} tokens")
                return MarkerMatch(
                    found=True,
                    word_idx=word_idx,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    gaps=gaps,
                    tokens_matched=result.get('tokens_matched', 0),
                    tokens_skipped=result.get('tokens_skipped', 0) + skip_count,
                    debug_info=trunc_debug
                )

    # Nothing found
    return MarkerMatch(
        found=False,
        word_idx=-1,
        start_offset=-1,
        end_offset=-1,
        gaps=[],
        tokens_matched=0,
        tokens_skipped=0,
        debug_info=debug_info
    )


def find_start_marker(
    word_list: List[Dict],
    marker: str,
    text: str,
    search_start_idx: int = 0,
    max_char_offset: int = 0,
    config: MatchConfig = None
) -> MarkerMatch:
    """
    Find START marker position with progressive truncation fallback.

    For START markers:
    - start_offset: First char of first matched word (use this for segment start)
    - end_offset: Last char of last matched word

    PROGRESSIVE TRUNCATION (from END):
    If full marker not found, tries progressively shorter prefixes:
    - "word1 word2 word3 word4" → try "word1 word2 word3" → try "word1 word2"
    This handles LLM hallucination where end is wrong but start is correct.

    Args:
        word_list: Pre-tokenized document. Each entry MUST have:
                   - 'word': lowercase token
                   - 'start': first char position in RAW TEXT
                   - 'end': last char position in RAW TEXT
        marker: START marker text from LLM
        text: Original RAW TEXT
        search_start_idx: Start searching from this word index
        max_char_offset: Maximum char offset for proximity
        config: Matching configuration

    Returns:
        MarkerMatch with found=True/False and offsets
    """
    if config is None:
        config = DEFAULT_CONFIG

    # Tokenize marker to check length
    marker_tokens = tokenize_marker(marker)

    # Try full marker first
    word_idx, start_offset, end_offset, gaps, debug_info = find_marker_tokens(
        word_list=word_list,
        marker=marker,
        text=text,
        search_start_idx=search_start_idx,
        min_char_offset=0,
        marker_type="start",
        reference_position=max_char_offset,
        config=config
    )

    # If found, return immediately
    if word_idx != -1:
        result = debug_info.get('result', {})
        return MarkerMatch(
            found=True,
            word_idx=word_idx,
            start_offset=start_offset,
            end_offset=end_offset,
            gaps=gaps,
            tokens_matched=result.get('tokens_matched', 0),
            tokens_skipped=result.get('tokens_skipped', 0),
            debug_info=debug_info
        )

    # PROGRESSIVE TRUNCATION FROM END: Try shorter prefixes
    # Only if marker has 4+ tokens, try removing last 1-2 tokens
    # Use strict config (no skips) to avoid false matches
    if len(marker_tokens) >= 4:
        strict_config = MatchConfig(
            max_single_gap=config.max_single_gap,
            max_total_skips=0,           # NO token skipping during truncation
            max_consecutive_skips=0,      # NO token skipping during truncation
            min_tokens_required=2,
            min_tokens_in_marker=2
        )

        for skip_count in [1, 2]:
            if len(marker_tokens) - skip_count < strict_config.min_tokens_in_marker:
                break

            # For START markers, keep first N tokens (truncate from end)
            truncated_tokens = marker_tokens[:-skip_count]
            truncated_marker = ' '.join(truncated_tokens)

            logger.debug(f"Truncation fallback (start): trying '{truncated_marker}' (removed {skip_count} from end)")

            word_idx, start_offset, end_offset, gaps, trunc_debug = find_marker_tokens(
                word_list=word_list,
                marker=truncated_marker,
                text=text,
                search_start_idx=search_start_idx,
                min_char_offset=0,
                marker_type="start",
                reference_position=max_char_offset,
                config=strict_config
            )

            if word_idx != -1:
                result = trunc_debug.get('result', {})
                trunc_debug['truncation_used'] = True
                trunc_debug['tokens_removed_from_end'] = skip_count
                trunc_debug['original_marker'] = marker
                logger.info(f"Truncation fallback SUCCESS (start): '{truncated_marker}' found after removing {skip_count} from end")
                return MarkerMatch(
                    found=True,
                    word_idx=word_idx,
                    start_offset=start_offset,
                    end_offset=end_offset,
                    gaps=gaps,
                    tokens_matched=result.get('tokens_matched', 0),
                    tokens_skipped=result.get('tokens_skipped', 0) + skip_count,
                    debug_info=trunc_debug
                )

    # Nothing found
    return MarkerMatch(
        found=False,
        word_idx=-1,
        start_offset=-1,
        end_offset=-1,
        gaps=[],
        tokens_matched=0,
        tokens_skipped=0,
        debug_info=debug_info
    )


# =============================================================================
# WORD LIST BUILDER
# =============================================================================

def tokenize_text(text: str) -> List[Dict]:
    """
    Tokenize text into word list with RAW TEXT positions.

    Each token entry contains:
    - 'word': lowercase normalized token
    - 'start': first char position in RAW TEXT
    - 'end': last char position in RAW TEXT (exclusive)

    Args:
        text: Raw document text

    Returns:
        List of token dictionaries

    Example:
        >>> tokens = tokenize_text("Hello, World!")
        >>> tokens[0]
        {'word': 'hello', 'start': 0, 'end': 5}
        >>> tokens[1]
        {'word': 'world', 'start': 7, 'end': 12}
    """
    word_list = []
    for match in re.finditer(r'\w+', text):
        word_list.append({
            'word': match.group().lower(),
            'start': match.start(),  # First char position in RAW TEXT
            'end': match.end()       # Last char position in RAW TEXT (exclusive)
        })
    return word_list
