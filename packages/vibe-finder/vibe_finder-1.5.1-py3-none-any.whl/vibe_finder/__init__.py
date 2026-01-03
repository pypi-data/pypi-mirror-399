"""
Vibe Finder - Gap-tolerant fuzzy phrase matching for OCR and AI/LLM text search.

Find phrases even when text is altered, prettified, or contains OCR errors.
Single-pass alternative to slow agentic multi-iteration search approaches.

Features:
- Jaro-Winkler fuzzy matching for typos/OCR errors
- Gap-tolerant token sequence matching
- Multi-factor scoring with transposition penalty
- Exact character offset calculation

Usage:
    from vibe_finder import FuzzyFinder

    # Single phrase search
    finder = FuzzyFinder(document_text)
    result = finder.find("искомая фраза")

    # Batch search (multiple phrases)
    results = finder.search(
        phrases=["фраза 1", "фраза 2", "фраза 3"],
        options={"score_threshold": 0.5}
    )
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional, Union, Tuple

from .matcher import (
    # Core functions
    tokenize_text,
    tokenize_marker,
    find_marker_tokens,
    find_end_marker,
    find_start_marker,

    # Fuzzy matching
    jaro_similarity,
    jaro_winkler_similarity,
    get_adaptive_threshold,
    find_fuzzy_matches,

    # Scoring
    score_sequence,
    count_transpositions,

    # Data classes
    MarkerMatch,
    MatchCandidate,
    SequenceMatch,
    FuzzyMatch,
    MatchConfig,
)

__version__ = "1.5.1"
__all__ = [
    # Phrase matching
    "FuzzyFinder",
    "SearchResult",
    "SearchOptions",
    "ScoringCoefficients",
    # Hotspot/cloud detection
    "CloudFinder",
    "HotspotMatch",
    "DistributionStats",
    # Token map (v1.5+)
    "TokenMatch",
    "KeywordMapResult",
    "find_keyword_map",
    # Presets
    "MatchPreset",
    "PRESETS",
    "get_preset",
    # Core functions
    "tokenize_text",
    "tokenize_marker",
    "find_marker_tokens",
    "find_end_marker",
    "find_start_marker",
    "jaro_similarity",
    "jaro_winkler_similarity",
    "get_adaptive_threshold",
    "find_fuzzy_matches",
    "score_sequence",
    "count_transpositions",
    "MarkerMatch",
    "MatchCandidate",
    "SequenceMatch",
    "FuzzyMatch",
    "MatchConfig",
]


# =============================================================================
# MATCHING PRESETS
# =============================================================================

@dataclass
class MatchPreset:
    """
    Preset configuration for fuzzy matching.

    Parameters can be overridden when using the preset.
    """
    name: str
    description: str
    fuzzy_threshold: float  # Jaro-Winkler similarity threshold
    max_edit_ratio: float   # Max edit distance as ratio of word length

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "fuzzy_threshold": self.fuzzy_threshold,
            "max_edit_ratio": self.max_edit_ratio,
        }


# Predefined presets for common use cases
PRESETS: Dict[str, MatchPreset] = {
    "exact": MatchPreset(
        name="exact",
        description="Almost exact matching. For legal docs, code, identifiers.",
        fuzzy_threshold=0.98,
        max_edit_ratio=0.05,
    ),
    "strict": MatchPreset(
        name="strict",
        description="Strict matching with OCR tolerance. Good default for most cases.",
        fuzzy_threshold=0.86,
        max_edit_ratio=0.15,
    ),
    "ocr": MatchPreset(
        name="ocr",
        description="Tolerant of OCR errors (typos, latin/cyrillic confusion).",
        fuzzy_threshold=0.84,
        max_edit_ratio=0.20,
    ),
    "morphological": MatchPreset(
        name="morphological",
        description="For languages with rich morphology (Russian, Polish). Matches word forms.",
        fuzzy_threshold=0.80,
        max_edit_ratio=0.25,
    ),
    "relaxed": MatchPreset(
        name="relaxed",
        description="Permissive matching. High recall, some false positives possible.",
        fuzzy_threshold=0.81,
        max_edit_ratio=0.30,
    ),
}


def get_preset(
    name: str = "strict",
    *,
    fuzzy_threshold: Optional[float] = None,
    max_edit_ratio: Optional[float] = None,
) -> MatchPreset:
    """
    Get a preset with optional parameter overrides.

    Args:
        name: Preset name ("exact", "strict", "ocr", "morphological", "relaxed")
        fuzzy_threshold: Override the preset's fuzzy_threshold
        max_edit_ratio: Override the preset's max_edit_ratio

    Returns:
        MatchPreset with applied overrides

    Examples:
        # Use preset as-is
        preset = get_preset("ocr")

        # Override specific parameter
        preset = get_preset("ocr", fuzzy_threshold=0.82)

        # Override multiple parameters
        preset = get_preset("strict", fuzzy_threshold=0.88, max_edit_ratio=0.12)
    """
    if name not in PRESETS:
        raise ValueError(f"Unknown preset '{name}'. Available: {list(PRESETS.keys())}")

    base = PRESETS[name]

    return MatchPreset(
        name=f"{base.name}_custom" if fuzzy_threshold or max_edit_ratio else base.name,
        description=base.description,
        fuzzy_threshold=fuzzy_threshold if fuzzy_threshold is not None else base.fuzzy_threshold,
        max_edit_ratio=max_edit_ratio if max_edit_ratio is not None else base.max_edit_ratio,
    )


# =============================================================================
# BATCH SEARCH DATA STRUCTURES
# =============================================================================

@dataclass
class ScoringCoefficients:
    """
    Coefficients for the scoring formula.

    score = w_similarity * Σ(token_scores) +
            w_coverage * tokens_found +
            w_sequential * sequential_bonus +
            w_gap_penalty * avg_gap +
            w_skip_penalty * skips +
            w_transposition * transpositions

    All weights should be positive except penalties (gap, skip, transposition)
    which should be negative or zero.
    """
    w_similarity: float = 1.0
    w_coverage: float = 0.3
    w_sequential: float = 0.2
    w_gap_penalty: float = -0.01
    w_skip_penalty: float = -0.1
    w_transposition: float = -0.05

    # Reserved for future extensions
    _reserved: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, float]:
        return {
            "w_similarity": self.w_similarity,
            "w_coverage": self.w_coverage,
            "w_sequential": self.w_sequential,
            "w_gap_penalty": self.w_gap_penalty,
            "w_skip_penalty": self.w_skip_penalty,
            "w_transposition": self.w_transposition,
        }


@dataclass
class SearchOptions:
    """
    Options for batch search.

    Attributes:
        score_threshold: Minimum score to consider a match valid (0.0-1.0).
                        Matches below this threshold are not returned.
        coefficients: Custom scoring coefficients. If None, defaults used.
        find_all: If True, find all occurrences of each phrase.
                 If False, find only first occurrence.
        min_offset: Start searching from this character position.
        direction: "forward" or "backward" search direction.

    Reserved for future:
        _extensions: Dict for additional parameters without breaking compatibility.
    """
    score_threshold: float = 0.0
    coefficients: Optional[ScoringCoefficients] = None
    find_all: bool = True
    min_offset: int = 0
    direction: str = "forward"

    # Reserved for future extensions (backwards compatible)
    _extensions: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "SearchOptions":
        """Create SearchOptions from dictionary (for easy JSON input)."""
        coefficients = None
        if "coefficients" in data:
            coef_data = data["coefficients"]
            if isinstance(coef_data, ScoringCoefficients):
                coefficients = coef_data
            elif isinstance(coef_data, dict):
                coefficients = ScoringCoefficients(**coef_data)

        return cls(
            score_threshold=data.get("score_threshold", 0.0),
            coefficients=coefficients,
            find_all=data.get("find_all", True),
            min_offset=data.get("min_offset", 0),
            direction=data.get("direction", "forward"),
            _extensions=data.get("_extensions", {}),
        )


@dataclass
class SearchResult:
    """
    Result for a single match occurrence.

    Attributes:
        found: Whether match was found
        start_offset: First character position in raw text
        end_offset: Last character position in raw text (exclusive)
        score: Final detection score (0.0-1.0 normalized)
        raw_score: Raw score before normalization
        matched_text: The actual text that was matched (optional)
        debug_info: Additional scoring details

    Note: If phrase is found multiple times, multiple SearchResult
          objects are returned in a list.
    """
    found: bool
    start_offset: int
    end_offset: int
    score: float
    raw_score: float = 0.0
    matched_text: Optional[str] = None
    debug_info: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for JSON serialization."""
        return {
            "found": self.found,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "score": self.score,
            "raw_score": self.raw_score,
            "matched_text": self.matched_text,
            "debug_info": self.debug_info,
        }


# Type alias for batch search output
# Each element is either:
# - None (not found or below threshold)
# - SearchResult (single match)
# - List[SearchResult] (multiple matches when find_all=True)
BatchSearchOutput = List[Optional[Union[SearchResult, List[SearchResult]]]]


class FuzzyFinder:
    """
    High-level API for fuzzy phrase finding in documents.

    Example (single search):
        >>> finder = FuzzyFinder("Это текст документа с опечатками и ошибками")
        >>> result = finder.find("текст документа")
        >>> result.found
        True

    Example (batch search):
        >>> finder = FuzzyFinder(document_text)
        >>> results = finder.search(
        ...     phrases=["фраза 1", "фраза 2", "фраза 3"],
        ...     options={"score_threshold": 0.5}
        ... )
        >>> # results[0] corresponds to "фраза 1", etc.
    """

    # Default scoring coefficients
    DEFAULT_COEFFICIENTS = ScoringCoefficients()

    def __init__(self, text: str):
        """
        Initialize finder with document text.

        Args:
            text: Document text to search in
        """
        self.text = text
        self.word_list = tokenize_text(text)

    def find(
        self,
        phrase: str,
        min_offset: int = 0,
        max_offset: int = None,
        direction: str = "forward"
    ) -> MarkerMatch:
        """
        Find phrase in document with fuzzy matching.

        Args:
            phrase: Phrase to find (can have typos, missing words)
            min_offset: Start searching from this character position
            max_offset: For backward search, reference position
            direction: "forward" (find after min_offset) or "backward" (find before max_offset)

        Returns:
            MarkerMatch with:
                - found: bool
                - start_offset: First char of match in raw text
                - end_offset: Last char of match in raw text
                - debug_info: Scoring details
        """
        if direction == "forward":
            return find_end_marker(
                marker=phrase,
                text=self.text,
                word_list=self.word_list,
                min_char_offset=min_offset
            )
        else:
            return find_start_marker(
                marker=phrase,
                text=self.text,
                word_list=self.word_list,
                max_char_offset=max_offset or len(self.text)
            )

    def find_all(
        self,
        phrase: str,
        min_offset: int = 0
    ) -> List[MarkerMatch]:
        """
        Find all occurrences of phrase in document.

        Args:
            phrase: Phrase to find
            min_offset: Start searching from this position

        Returns:
            List of MarkerMatch objects for each occurrence
        """
        results = []
        current_offset = min_offset

        while current_offset < len(self.text):
            result = self.find(phrase, min_offset=current_offset)
            if not result.found:
                break
            results.append(result)
            current_offset = result.end_offset + 1

        return results

    def search(
        self,
        phrases: List[str],
        options: Optional[Union[Dict[str, Any], SearchOptions]] = None
    ) -> BatchSearchOutput:
        """
        Search for multiple phrases in document.

        This is the main batch search API. Returns results array where each
        position corresponds to input phrase at same position.

        Args:
            phrases: List of phrases to search for
            options: Search options (dict or SearchOptions object)
                - score_threshold: Minimum score (0.0-1.0), below = not returned
                - coefficients: Custom ScoringCoefficients
                - find_all: True = find all occurrences, False = first only
                - min_offset: Start position
                - direction: "forward" or "backward"

        Returns:
            List where each element corresponds to phrase at same index:
            - None: Not found or below threshold
            - SearchResult: Single match (when find_all=False or single occurrence)
            - List[SearchResult]: Multiple matches (when find_all=True)

        Example:
            >>> finder = FuzzyFinder(document)
            >>> results = finder.search(
            ...     phrases=["налоговый вычет", "НДС ставка", "unknown phrase"],
            ...     options={"score_threshold": 0.4, "find_all": True}
            ... )
            >>> len(results) == 3  # Same length as input
            True
            >>> results[2] is None  # "unknown phrase" not found
            True
            >>> isinstance(results[0], list)  # Multiple matches
            True
        """
        # Parse options
        if options is None:
            opts = SearchOptions()
        elif isinstance(options, dict):
            opts = SearchOptions.from_dict(options)
        else:
            opts = options

        # Get coefficients (for future custom scoring)
        coefficients = opts.coefficients or self.DEFAULT_COEFFICIENTS

        # Process each phrase
        output: BatchSearchOutput = []

        for phrase in phrases:
            if opts.find_all:
                # Find all occurrences
                matches = self._find_all_scored(
                    phrase=phrase,
                    min_offset=opts.min_offset,
                    direction=opts.direction,
                    score_threshold=opts.score_threshold,
                    coefficients=coefficients
                )

                if not matches:
                    output.append(None)
                elif len(matches) == 1:
                    # Single match - return as single object for convenience
                    # (backwards compatible: can check isinstance for list vs single)
                    output.append(matches[0])
                else:
                    output.append(matches)
            else:
                # Find first only
                result = self._find_scored(
                    phrase=phrase,
                    min_offset=opts.min_offset,
                    direction=opts.direction,
                    coefficients=coefficients
                )

                if not result.found or result.score < opts.score_threshold:
                    output.append(None)
                else:
                    output.append(result)

        return output

    def _find_scored(
        self,
        phrase: str,
        min_offset: int = 0,
        direction: str = "forward",
        coefficients: ScoringCoefficients = None
    ) -> SearchResult:
        """
        Find phrase and return SearchResult with normalized score.
        """
        match = self.find(phrase, min_offset=min_offset, direction=direction)

        if not match.found:
            return SearchResult(
                found=False,
                start_offset=-1,
                end_offset=-1,
                score=0.0,
                raw_score=0.0,
                matched_text=None,
                debug_info=match.debug_info
            )

        # Extract scoring info from debug_info.result
        result_info = match.debug_info.get("result", {})
        token_similarities = result_info.get("token_similarities", [])
        tokens_matched = result_info.get("tokens_matched", 0)
        tokens_skipped = result_info.get("tokens_skipped", 0)
        gaps = result_info.get("gaps", [])
        transpositions = result_info.get("transpositions", 0)

        # Calculate raw score based on token similarities and penalties
        if token_similarities:
            similarity_sum = sum(token_similarities)
            avg_gap = sum(gaps) / len(gaps) if gaps else 0

            # Apply scoring formula
            coef = coefficients or self.DEFAULT_COEFFICIENTS
            raw_score = (
                coef.w_similarity * similarity_sum +
                coef.w_coverage * tokens_matched +
                coef.w_gap_penalty * avg_gap +
                coef.w_skip_penalty * tokens_skipped +
                coef.w_transposition * transpositions
            )
        else:
            raw_score = result_info.get("sequence_score", 0.0)

        # Normalize score to 0.0-1.0 range
        normalized_score = self._normalize_score(raw_score, phrase, tokens_matched)

        # Get matched text
        matched_text = self.text[match.start_offset:match.end_offset]

        return SearchResult(
            found=True,
            start_offset=match.start_offset,
            end_offset=match.end_offset,
            score=normalized_score,
            raw_score=raw_score,
            matched_text=matched_text,
            debug_info=match.debug_info
        )

    def _find_all_scored(
        self,
        phrase: str,
        min_offset: int = 0,
        direction: str = "forward",
        score_threshold: float = 0.0,
        coefficients: ScoringCoefficients = None
    ) -> List[SearchResult]:
        """
        Find all occurrences and return list of SearchResult with scores.
        """
        results = []
        current_offset = min_offset

        while current_offset < len(self.text):
            result = self._find_scored(
                phrase=phrase,
                min_offset=current_offset,
                direction=direction,
                coefficients=coefficients
            )

            if not result.found:
                break

            # Apply threshold filter
            if result.score >= score_threshold:
                results.append(result)

            current_offset = result.end_offset + 1

        return results

    def _normalize_score(
        self,
        raw_score: float,
        phrase: str,
        tokens_matched: int = 0
    ) -> float:
        """
        Normalize raw score to 0.0-1.0 range.

        The normalization considers:
        - Number of tokens in phrase (more tokens = higher potential score)
        - Actual tokens matched
        - Typical score ranges from the algorithm
        """
        if raw_score <= 0:
            return 0.0

        # Estimate expected max score based on phrase tokens
        tokens = tokenize_marker(phrase)
        num_tokens = len(tokens)

        if num_tokens == 0:
            return 0.0

        # Expected max score:
        # - similarity: 1.0 per token (perfect match)
        # - coverage: 0.3 per token
        # Total: ~1.3 per token for perfect match
        expected_max = num_tokens * 1.3

        # Normalize
        normalized = raw_score / expected_max

        # Boost based on coverage ratio (how many tokens were actually matched)
        if tokens_matched > 0:
            coverage_ratio = tokens_matched / num_tokens
            # Apply coverage as a multiplier (full coverage = 1.0, half = 0.5)
            normalized = normalized * (0.5 + 0.5 * coverage_ratio)

        # Clamp to 0.0-1.0
        return max(0.0, min(1.0, normalized))

    def similarity(self, s1: str, s2: str) -> float:
        """
        Calculate Jaro-Winkler similarity between two strings.

        Args:
            s1: First string
            s2: Second string

        Returns:
            Similarity score 0.0-1.0
        """
        return jaro_winkler_similarity(s1.lower(), s2.lower())


# =============================================================================
# CONVENIENCE FUNCTIONS
# =============================================================================

def search_in_text(
    text: str,
    phrases: List[str],
    options: Optional[Dict[str, Any]] = None
) -> BatchSearchOutput:
    """
    Convenience function for one-shot batch search.

    Args:
        text: Document text to search in
        phrases: List of phrases to find
        options: Search options dict

    Returns:
        BatchSearchOutput (list matching input phrases positions)

    Example:
        >>> results = search_in_text(
        ...     "Document text here",
        ...     ["phrase 1", "phrase 2"],
        ...     {"score_threshold": 0.5}
        ... )
    """
    finder = FuzzyFinder(text)
    return finder.search(phrases, options)


# =============================================================================
# KEYWORD CLOUD / HOTSPOT DETECTION
# =============================================================================

@dataclass
class DistributionStats:
    """
    Statistics about keyword distribution within a hotspot.

    More concentrated distributions indicate higher topic relevance.

    Key metrics:
    - clustering_ratio: How much more clustered than even distribution (>1 = clustered)
    - concentration_score: 0-1 normalized, higher = more concentrated
    - cv (Coefficient of Variation): std_dev/mean of inter-keyword spacings
    """
    span: int                    # Total span in chars (end - start)
    density: float               # Keywords per 100 chars
    compactness: float           # 0-1, higher = more concentrated
    std_deviation: float         # Spread of keyword positions
    keyword_positions: List[Tuple[int, int, str]]  # (start, end, word) for each found keyword

    # Advanced density metrics (relative to document size)
    clustering_ratio: float = 1.0      # expected_span / actual_span (>1 = concentrated)
    concentration_score: float = 0.0   # 1 - (span / doc_length)
    expected_spacing: float = 0.0      # doc_length / (n+1)
    actual_avg_spacing: float = 0.0    # Mean distance between consecutive keywords
    cv: float = 0.0                    # Coefficient of Variation (std/mean of spacings)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "span": self.span,
            "density": self.density,
            "compactness": self.compactness,
            "std_deviation": self.std_deviation,
            "keyword_positions": self.keyword_positions,
            "clustering_ratio": self.clustering_ratio,
            "concentration_score": self.concentration_score,
            "expected_spacing": self.expected_spacing,
            "actual_avg_spacing": self.actual_avg_spacing,
            "cv": self.cv,
        }

    @property
    def interpretation(self) -> str:
        """Human-readable interpretation of clustering."""
        if self.clustering_ratio > 2:
            return "highly_concentrated"
        elif self.clustering_ratio > 1.5:
            return "moderately_concentrated"
        elif self.clustering_ratio > 1:
            return "slightly_concentrated"
        elif self.clustering_ratio > 0.7:
            return "near_even"
        else:
            return "spread_out"


@dataclass
class HotspotMatch:
    """
    A concentration of keywords found in text (hotspot/cloud).

    Attributes:
        center_offset: Center position of the hotspot
        start_offset: Start of the region containing keywords
        end_offset: End of the region containing keywords
        score: Overall hotspot score (0-1), based on coverage + density + compactness
        keywords_found: List of keywords that were found (with fuzzy matches)
        keywords_missing: List of keywords not found in this region
        coverage: Percentage of keywords found (0-1)
        distribution: Detailed distribution statistics
        text_preview: Preview of the matched region
    """
    center_offset: int
    start_offset: int
    end_offset: int
    score: float
    keywords_found: List[str]
    keywords_missing: List[str]
    coverage: float
    distribution: DistributionStats
    text_preview: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "center_offset": self.center_offset,
            "start_offset": self.start_offset,
            "end_offset": self.end_offset,
            "score": self.score,
            "keywords_found": self.keywords_found,
            "keywords_missing": self.keywords_missing,
            "coverage": self.coverage,
            "distribution": self.distribution.to_dict(),
            "text_preview": self.text_preview,
        }


def _levenshtein_distance(s1: str, s2: str) -> int:
    """Calculate Levenshtein (edit) distance between two strings."""
    if len(s1) < len(s2):
        return _levenshtein_distance(s2, s1)
    if len(s2) == 0:
        return len(s1)
    prev_row = list(range(len(s2) + 1))
    for i, c1 in enumerate(s1):
        curr_row = [i + 1]
        for j, c2 in enumerate(s2):
            curr_row.append(min(prev_row[j + 1] + 1, curr_row[j] + 1, prev_row[j] + (c1 != c2)))
        prev_row = curr_row
    return prev_row[-1]


def _is_fuzzy_match(keyword: str, candidate: str, jw_threshold: float = 0.86, max_edit_ratio: float = 0.15) -> bool:
    """
    Improved fuzzy matching combining Jaro-Winkler with edit distance.

    Fixes false positives like "космические" matching "экономически".

    Rules:
    1. Jaro-Winkler >= threshold (0.86, stricter than old 0.85)
    2. Edit distance <= 15% of longer word (minimum 1 edit allowed)
    """
    kw = keyword.lower()
    cand = candidate.lower()

    # Jaro-Winkler similarity check
    jw_score = jaro_winkler_similarity(kw, cand)
    if jw_score < jw_threshold:
        return False

    # Edit distance check (prevents false positives)
    edit_dist = _levenshtein_distance(kw, cand)
    max_len = max(len(kw), len(cand))
    max_edits = max(int(max_len * max_edit_ratio), 1)  # At least 1 edit allowed

    return edit_dist <= max_edits


# =============================================================================
# TOKEN MAP (v1.5+) - Keyword mapping for cloud-finder
# =============================================================================

@dataclass
class TokenMatch:
    """
    Single token from document with optional keyword match info.

    Used by find_keyword_map() to return full tokenized document
    with keyword match annotations.
    """
    token_idx: int          # Position in token list (0-based)
    word: str               # Original word from document
    start: int              # Character offset start
    end: int                # Character offset end

    # Match info (None/0 if no match)
    match_id: Optional[str] = None      # "A", "B", "C"... or None
    match_keyword: Optional[str] = None # Original keyword that matched
    match_score: float = 0.0            # Jaro-Winkler similarity score
    edit_distance: int = 0              # Levenshtein edit distance
    edit_ratio: float = 0.0             # edit_distance / max(len(word), len(keyword))


@dataclass
class KeywordMapResult:
    """
    Complete tokenized document with keyword mapping.

    Provides all data needed for cloud-finder to analyze keyword
    distribution without re-finding matches.

    Example:
        result = find_keyword_map(doc, ["налоговая", "оптимизация", "НДС"])

        # Legend maps IDs to keywords
        result.legend  # {"A": "налоговая", "B": "оптимизация", "C": "НДС"}

        # Compact string for pattern matching
        result.compact  # "__AB_______C__"

        # Match sequence vs expected
        result.match_sequence    # "ABC" (order found in text)
        result.expected_sequence # "ABC" (order in query)

        # Get real offsets back
        for m in result.matches:
            print(f"{m.match_id}: '{m.word}' at [{m.start}:{m.end}]")
    """
    # Legend: ID → keyword
    legend: Dict[str, str]  # {"A": "налоговая", "B": "оптимизация", ...}

    # Reverse legend: keyword → ID
    keyword_to_id: Dict[str, str]  # {"налоговая": "A", ...}

    # Full token map with all data
    tokens: List[TokenMatch]

    # Quick access to matches only (tokens where match_id is not None)
    matches: List[TokenMatch]

    # Compact string representation ("__AB_______C__")
    compact: str

    # Sequences for order analysis
    match_sequence: str      # "ABC" (order found in document)
    expected_sequence: str   # "ABC" (order in original query)

    # Pre-calculated gaps (between consecutive matches)
    token_gaps: List[int]    # [1, 7] gaps in token count
    char_gaps: List[int]     # [11, 89] gaps in character count

    # Span info
    total_span_tokens: int   # Total tokens from first to last match
    total_span_chars: int    # Total chars from first to last match
    first_match_offset: int  # Char offset of first match
    last_match_offset: int   # Char offset of last match (end)

    # Statistics
    found_count: int         # Number of keywords found
    total_count: int         # Total keywords searched
    coverage: float          # found_count / total_count

    def get_match_offsets(self) -> List[Tuple[int, int, str, str]]:
        """
        Get (start, end, match_id, word) for all matches.

        Returns list sorted by position in document.
        """
        return [(m.start, m.end, m.match_id, m.word) for m in self.matches]

    def get_missing_keywords(self) -> List[str]:
        """Get keywords that were not found in document."""
        found_ids = {m.match_id for m in self.matches}
        return [kw for id_, kw in self.legend.items() if id_ not in found_ids]


def find_keyword_map(
    text: str,
    keywords: List[str],
    preset: Optional[str] = None,
    fuzzy_threshold: Optional[float] = None,
    max_edit_ratio: Optional[float] = None,
) -> KeywordMapResult:
    """
    Create a keyword map of the document for cloud-finder.

    Tokenizes the entire document and marks which tokens match
    which keywords, returning all data needed for pattern analysis.

    Args:
        text: Document text to analyze
        keywords: List of keywords to find (order matters for sequence analysis)
        preset: Preset name ("exact", "strict", "ocr", "morphological", "relaxed")
        fuzzy_threshold: Override Jaro-Winkler threshold
        max_edit_ratio: Override max edit distance ratio

    Returns:
        KeywordMapResult with complete token map and match data

    Example:
        result = find_keyword_map(
            "Тема семинара — налоговая оптимизация бизнеса...",
            ["налоговая", "оптимизация", "НДС"],
            preset="ocr"
        )

        print(result.legend)       # {"A": "налоговая", "B": "оптимизация", "C": "НДС"}
        print(result.compact)      # "__AB_______C__"
        print(result.match_sequence)  # "ABC"
        print(result.char_gaps)    # [11, 89]
    """
    # Resolve preset
    p = get_preset(preset or "strict", fuzzy_threshold=fuzzy_threshold, max_edit_ratio=max_edit_ratio)
    jw_threshold = p.fuzzy_threshold
    edit_ratio = p.max_edit_ratio

    # Create legend: A, B, C, ... for keywords
    # Support up to 26 keywords (A-Z)
    legend = {}
    keyword_to_id = {}
    for i, kw in enumerate(keywords):
        if i >= 26:
            break  # Max 26 keywords (A-Z)
        id_ = chr(ord('A') + i)
        legend[id_] = kw
        keyword_to_id[kw.lower()] = id_

    expected_sequence = "".join(legend.keys())

    # Tokenize document
    doc_tokens = tokenize_text(text)

    # Build token map with match info
    token_map: List[TokenMatch] = []
    matches: List[TokenMatch] = []
    compact_chars = []

    for idx, tok in enumerate(doc_tokens):
        word = tok['word']
        start = tok['start']
        end = tok['end']

        # Check against each keyword
        match_id = None
        match_keyword = None
        match_score = 0.0
        match_edit = 0
        match_edit_ratio = 0.0

        word_lower = word.lower()

        for kw, id_ in keyword_to_id.items():
            # Calculate similarity
            jw_score = jaro_winkler_similarity(word_lower, kw)

            if jw_score >= jw_threshold:
                # Check edit distance
                edit_dist = _levenshtein_distance(word_lower, kw)
                max_len = max(len(word_lower), len(kw))
                max_edits = max(int(max_len * edit_ratio), 1)

                if edit_dist <= max_edits:
                    # Match found! Take best match if multiple
                    if jw_score > match_score:
                        match_id = id_
                        match_keyword = legend[id_]
                        match_score = jw_score
                        match_edit = edit_dist
                        match_edit_ratio = edit_dist / max_len if max_len > 0 else 0

        token_match = TokenMatch(
            token_idx=idx,
            word=word,
            start=start,
            end=end,
            match_id=match_id,
            match_keyword=match_keyword,
            match_score=match_score,
            edit_distance=match_edit,
            edit_ratio=match_edit_ratio,
        )

        token_map.append(token_match)

        if match_id:
            matches.append(token_match)
            compact_chars.append(match_id)
        else:
            compact_chars.append('_')

    compact = "".join(compact_chars)

    # Build match sequence (order found in document)
    match_sequence = "".join(m.match_id for m in matches)

    # Calculate gaps between consecutive matches
    token_gaps = []
    char_gaps = []

    for i in range(1, len(matches)):
        prev = matches[i - 1]
        curr = matches[i]
        token_gaps.append(curr.token_idx - prev.token_idx - 1)
        char_gaps.append(curr.start - prev.end)

    # Calculate span
    if matches:
        total_span_tokens = matches[-1].token_idx - matches[0].token_idx + 1
        total_span_chars = matches[-1].end - matches[0].start
        first_offset = matches[0].start
        last_offset = matches[-1].end
    else:
        total_span_tokens = 0
        total_span_chars = 0
        first_offset = 0
        last_offset = 0

    return KeywordMapResult(
        legend=legend,
        keyword_to_id=keyword_to_id,
        tokens=token_map,
        matches=matches,
        compact=compact,
        match_sequence=match_sequence,
        expected_sequence=expected_sequence,
        token_gaps=token_gaps,
        char_gaps=char_gaps,
        total_span_tokens=total_span_tokens,
        total_span_chars=total_span_chars,
        first_match_offset=first_offset,
        last_match_offset=last_offset,
        found_count=len(matches),
        total_count=len(keywords),
        coverage=len(matches) / len(keywords) if keywords else 0,
    )


class CloudFinder:
    """
    Find keyword concentrations/hotspots in documents.

    Unlike FuzzyFinder which finds ordered phrases, CloudFinder finds
    regions where a SET of keywords are concentrated, regardless of order.

    Use cases:
    - Topic detection: Find paragraphs discussing specific topics
    - Keyword density analysis: Find where keywords cluster together
    - Semantic search: Find relevant regions without exact phrase match

    Example:
        >>> finder = CloudFinder(document_text)
        >>> hotspots = finder.find_hotspots(
        ...     keywords=["налоговая", "оптимизация", "вычеты", "НДС"],
        ...     min_score=0.3,
        ...     window_size=300
        ... )
        >>> for h in hotspots:
        ...     print(f"Score: {h.score:.2f}, Coverage: {h.coverage:.0%}")
        ...     print(f"Found: {h.keywords_found}")
    """

    def __init__(
        self,
        text: str,
        preset: Optional[str] = None,
        fuzzy_threshold: Optional[float] = None,
        max_edit_ratio: Optional[float] = None,
    ):
        """
        Initialize CloudFinder with document text.

        Args:
            text: Document text to analyze
            preset: Preset name ("exact", "strict", "ocr", "morphological", "relaxed")
                   Default is "strict" if no preset or parameters specified
            fuzzy_threshold: Override preset's Jaro-Winkler threshold
            max_edit_ratio: Override preset's max edit ratio

        Presets:
            - "exact": Almost exact (jw=0.98, edit=5%) - legal docs, identifiers
            - "strict": Default (jw=0.86, edit=15%) - balanced precision/recall
            - "ocr": OCR tolerant (jw=0.84, edit=20%) - scanned documents
            - "morphological": Word forms (jw=0.80, edit=25%) - Russian, Polish
            - "relaxed": Permissive (jw=0.75, edit=30%) - high recall

        Examples:
            # Default (strict preset)
            finder = CloudFinder(text)

            # OCR preset for scanned documents
            finder = CloudFinder(text, preset="ocr")

            # Morphological with custom threshold
            finder = CloudFinder(text, preset="morphological", fuzzy_threshold=0.82)

            # Direct parameters (no preset, uses strict as base)
            finder = CloudFinder(text, fuzzy_threshold=0.90, max_edit_ratio=0.10)
        """
        self.text = text
        self.tokens = tokenize_text(text)

        # Resolve preset + overrides
        p = get_preset(preset or "strict", fuzzy_threshold=fuzzy_threshold, max_edit_ratio=max_edit_ratio)
        self.fuzzy_threshold = p.fuzzy_threshold
        self.max_edit_ratio = p.max_edit_ratio
        self.preset_name = p.name

    def find_hotspots(
        self,
        keywords: List[str],
        min_score: float = 0.2,
        min_coverage: float = 0.3,
        window_size: int = 500,
        max_results: int = 10,
    ) -> List[HotspotMatch]:
        """
        Find regions where keywords are concentrated.

        Args:
            keywords: List of keywords to find (can be multi-word)
            min_score: Minimum score cutoff for hotspots (0-1)
            min_coverage: Minimum keyword coverage to consider (0-1)
            window_size: Size of sliding window in characters
            max_results: Maximum number of hotspots to return

        Returns:
            List of HotspotMatch sorted by score (highest first)
        """
        from collections import defaultdict
        import math

        # Normalize keywords to token lists
        keyword_tokens = []
        for kw in keywords:
            kw_toks = tokenize_text(kw)
            keyword_tokens.append([t['word'] for t in kw_toks])

        # Find all positions where each keyword appears (with fuzzy matching)
        keyword_positions = defaultdict(list)  # keyword_idx -> [(start, end, matched_word)]

        for ki, kw_toks in enumerate(keyword_tokens):
            if len(kw_toks) == 1:
                # Single word keyword - use improved fuzzy match
                target = kw_toks[0]
                for tok in self.tokens:
                    if _is_fuzzy_match(target, tok['word'], self.fuzzy_threshold, self.max_edit_ratio):
                        keyword_positions[ki].append((tok['start'], tok['end'], tok['word']))
            else:
                # Multi-word keyword - find sequence with improved fuzzy match
                for i, tok in enumerate(self.tokens):
                    if i + len(kw_toks) > len(self.tokens):
                        break
                    matched = True
                    for j, kw_tok in enumerate(kw_toks):
                        if not _is_fuzzy_match(kw_tok, self.tokens[i+j]['word'], self.fuzzy_threshold, self.max_edit_ratio):
                            matched = False
                            break
                    if matched:
                        start = self.tokens[i]['start']
                        end = self.tokens[i + len(kw_toks) - 1]['end']
                        matched_text = ' '.join(t['word'] for t in self.tokens[i:i+len(kw_toks)])
                        keyword_positions[ki].append((start, end, matched_text))

        # Sliding window to find hotspots
        hotspots = []
        step = max(window_size // 4, 50)

        for window_start in range(0, len(self.text) - window_size + 1, step):
            window_end = window_start + window_size

            # Find keywords in this window
            found_keywords = []  # (keyword_idx, matched_word)
            found_positions = []  # (start, end)

            for ki, positions in keyword_positions.items():
                for start, end, word in positions:
                    if start >= window_start and end <= window_end:
                        if ki not in [k[0] for k in found_keywords]:
                            found_keywords.append((ki, word))
                            found_positions.append((start, end, word))
                        break

            coverage = len(found_keywords) / len(keywords) if keywords else 0

            if coverage >= min_coverage and found_positions:
                # Calculate distribution stats
                all_starts = [p[0] for p in found_positions]
                all_ends = [p[1] for p in found_positions]

                actual_start = min(all_starts)
                actual_end = max(all_ends)
                span = max(actual_end - actual_start, 1)
                center = (actual_start + actual_end) // 2

                # Density: keywords per 100 chars
                density = len(found_keywords) / span * 100

                # Compactness: how tight the cluster is relative to window
                compactness = 1 - (span / window_size)

                # Standard deviation of positions
                mean_pos = sum(all_starts) / len(all_starts)
                variance = sum((p - mean_pos) ** 2 for p in all_starts) / len(all_starts)
                std_dev = math.sqrt(variance)

                # Score formula:
                # - Base: coverage (what % of keywords found)
                # - Boost: compactness (tighter = better)
                # - Boost: density (more keywords per char = better)
                density_factor = min(1.0, density / 10)  # Cap at 10 keywords per 100 chars
                score = coverage * (0.4 + 0.3 * compactness + 0.3 * density_factor)

                if score >= min_score:
                    missing = [keywords[i] for i in range(len(keywords))
                              if i not in [k[0] for k in found_keywords]]

                    # Text preview
                    preview_text = self.text[actual_start:actual_end]
                    if len(preview_text) > 150:
                        preview_text = preview_text[:150] + "..."

                    # Advanced density metrics (relative to full document)
                    doc_length = len(self.text)
                    n_keywords = len(found_keywords)

                    # Expected spacing if keywords were evenly distributed
                    expected_spacing = doc_length / (n_keywords + 1) if n_keywords > 0 else doc_length

                    # Calculate inter-keyword spacings
                    sorted_starts = sorted(all_starts)
                    if len(sorted_starts) >= 2:
                        spacings = [sorted_starts[i+1] - sorted_starts[i]
                                   for i in range(len(sorted_starts)-1)]
                        actual_avg_spacing = sum(spacings) / len(spacings)

                        # CV (Coefficient of Variation)
                        if actual_avg_spacing > 0:
                            spacing_variance = sum((s - actual_avg_spacing) ** 2 for s in spacings) / len(spacings)
                            cv = math.sqrt(spacing_variance) / actual_avg_spacing
                        else:
                            cv = 0.0

                        # Clustering ratio: expected_span / actual_span
                        expected_span = expected_spacing * (n_keywords - 1)
                        clustering_ratio = expected_span / span if span > 0 else 1.0
                    else:
                        actual_avg_spacing = 0.0
                        cv = 0.0
                        clustering_ratio = 1.0

                    # Concentration score relative to document
                    doc_concentration_score = 1 - (span / doc_length) if doc_length > 0 else 0

                    distribution = DistributionStats(
                        span=span,
                        density=density,
                        compactness=compactness,
                        std_deviation=std_dev,
                        keyword_positions=found_positions,
                        clustering_ratio=clustering_ratio,
                        concentration_score=doc_concentration_score,
                        expected_spacing=expected_spacing,
                        actual_avg_spacing=actual_avg_spacing,
                        cv=cv,
                    )

                    hotspots.append(HotspotMatch(
                        center_offset=center,
                        start_offset=actual_start,
                        end_offset=actual_end,
                        score=score,
                        keywords_found=[k[1] for k in found_keywords],
                        keywords_missing=missing,
                        coverage=coverage,
                        distribution=distribution,
                        text_preview=preview_text,
                    ))

        # Merge overlapping hotspots, keep highest scoring
        merged = []
        hotspots.sort(key=lambda h: h.score, reverse=True)

        for hotspot in hotspots:
            overlaps = False
            for existing in merged:
                if abs(hotspot.center_offset - existing.center_offset) < window_size // 2:
                    overlaps = True
                    break
            if not overlaps:
                merged.append(hotspot)

        return merged[:max_results]

    def find_best_hotspot(
        self,
        keywords: List[str],
        min_coverage: float = 0.3,
        window_size: int = 500,
    ) -> Optional[HotspotMatch]:
        """
        Find the single best hotspot for given keywords.

        Convenience method that returns only the highest-scoring hotspot.

        Args:
            keywords: List of keywords to find
            min_coverage: Minimum keyword coverage required
            window_size: Search window size

        Returns:
            Best HotspotMatch or None if no hotspot found
        """
        hotspots = self.find_hotspots(
            keywords=keywords,
            min_score=0.0,  # No score cutoff, we want the best one
            min_coverage=min_coverage,
            window_size=window_size,
            max_results=1,
        )
        return hotspots[0] if hotspots else None


def find_keyword_hotspots(
    text: str,
    keywords: List[str],
    min_score: float = 0.2,
    min_coverage: float = 0.3,
    window_size: int = 500,
    fuzzy_threshold: float = 0.85,
) -> List[HotspotMatch]:
    """
    Convenience function for one-shot hotspot detection.

    Args:
        text: Document text
        keywords: Keywords to find
        min_score: Minimum hotspot score (0-1)
        min_coverage: Minimum keyword coverage (0-1)
        window_size: Search window size in chars
        fuzzy_threshold: Similarity threshold for fuzzy matching

    Returns:
        List of HotspotMatch sorted by score

    Example:
        >>> hotspots = find_keyword_hotspots(
        ...     document,
        ...     ["налоговая", "оптимизация", "НДС"],
        ...     min_score=0.3
        ... )
    """
    finder = CloudFinder(text, fuzzy_threshold=fuzzy_threshold)
    return finder.find_hotspots(
        keywords=keywords,
        min_score=min_score,
        min_coverage=min_coverage,
        window_size=window_size,
    )
