"""
Fuzzy Finder - Gap-tolerant fuzzy phrase matching in documents.

Find inexact phrases in text with:
- Jaro-Winkler fuzzy matching for typos/OCR errors
- Gap-tolerant token sequence matching
- Multi-factor scoring with transposition penalty
- Exact character offset calculation

Usage:
    from fuzzy_finder import FuzzyFinder

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
from typing import List, Dict, Any, Optional, Union

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

__version__ = "1.1.0"
__all__ = [
    "FuzzyFinder",
    "SearchResult",
    "SearchOptions",
    "ScoringCoefficients",
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
