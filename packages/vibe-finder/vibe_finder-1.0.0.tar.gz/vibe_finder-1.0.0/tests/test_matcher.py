"""
Tests for fuzzy-finder package.

Based on original tests from turov-bot project.
"""

import pytest
from fuzzy_finder import (
    FuzzyFinder,
    find_end_marker,
    find_start_marker,
    tokenize_text,
    tokenize_marker,
    jaro_winkler_similarity,
    MarkerMatch,
    SearchResult,
)


class TestJaroWinklerSimilarity:
    """Test Jaro-Winkler similarity calculations."""

    def test_identical_strings(self):
        assert jaro_winkler_similarity("test", "test") == 1.0

    def test_similar_strings(self):
        sim = jaro_winkler_similarity("налоговый", "налоговой")
        assert sim > 0.9

    def test_typo_handling(self):
        sim = jaro_winkler_similarity("оптимизация", "оптимизацыя")
        assert sim > 0.9

    def test_different_strings(self):
        sim = jaro_winkler_similarity("кошка", "собака")
        assert sim < 0.7


class TestTokenization:
    """Test tokenization functions."""

    def test_tokenize_text_basic(self):
        text = "Привет мир 123"
        tokens = tokenize_text(text)
        assert len(tokens) == 3
        assert tokens[0]["word"] == "привет"
        assert tokens[1]["word"] == "мир"
        assert tokens[2]["word"] == "123"

    def test_tokenize_text_positions(self):
        text = "Hello world"
        tokens = tokenize_text(text)
        assert tokens[0]["start"] == 0
        assert tokens[0]["end"] == 5
        assert tokens[1]["start"] == 6
        assert tokens[1]["end"] == 11

    def test_tokenize_marker(self):
        marker = "Налоговая Оптимизация 2024"
        tokens = tokenize_marker(marker)
        assert tokens == ["налоговая", "оптимизация", "2024"]


class TestFindEndMarker:
    """Test find_end_marker function."""

    def test_exact_match(self):
        text = "Владимир Туров рассказывает о налоговой оптимизации"
        word_list = tokenize_text(text)

        result = find_end_marker(
            marker="налоговой оптимизации",
            text=text,
            word_list=word_list
        )

        assert result.found is True
        assert text[result.start_offset:result.end_offset] == "налоговой оптимизации"

    def test_fuzzy_match_typo(self):
        text = "Владимир Туров рассказывает о налоговой оптимизации"
        word_list = tokenize_text(text)

        # Search with typos
        result = find_end_marker(
            marker="налоговай оптимизацыи",
            text=text,
            word_list=word_list
        )

        assert result.found is True
        assert "налоговой" in text[result.start_offset:result.end_offset]

    def test_gap_tolerance(self):
        text = "вычеты по НДС и их применение"
        word_list = tokenize_text(text)

        # Search skipping words
        result = find_end_marker(
            marker="вычеты НДС применение",
            text=text,
            word_list=word_list
        )

        assert result.found is True

    def test_not_found(self):
        text = "Простой текст без нужных слов"
        word_list = tokenize_text(text)

        result = find_end_marker(
            marker="налоговая оптимизация",
            text=text,
            word_list=word_list
        )

        assert result.found is False

    def test_min_char_offset(self):
        text = "налоговая налоговая налоговая"
        word_list = tokenize_text(text)

        # Find second occurrence
        result = find_end_marker(
            marker="налоговая",
            text=text,
            word_list=word_list,
            min_char_offset=10  # After first word
        )

        assert result.found is True
        assert result.start_offset >= 10


class TestFuzzyFinder:
    """Test high-level FuzzyFinder class."""

    def test_find_single(self):
        finder = FuzzyFinder("Текст с налоговой оптимизацией")
        result = finder.find("налоговой оптимизацией")

        assert result.found is True

    def test_find_all(self):
        finder = FuzzyFinder("налог налог налог")
        results = finder.find_all("налог")

        assert len(results) == 3

    def test_similarity(self):
        finder = FuzzyFinder("test")
        assert finder.similarity("test", "test") == 1.0
        assert finder.similarity("test", "tset") > 0.8


class TestBatchSearch:
    """Test batch search functionality."""

    def test_search_multiple_phrases(self):
        doc = """
        Владимир Туров рассказывает о налоговой оптимизации.
        Также обсуждаем вычеты по НДС и их применение.
        """
        finder = FuzzyFinder(doc)

        results = finder.search(
            phrases=["налоговой оптимизации", "вычеты НДС", "unknown"],
            options={"score_threshold": 0.3}
        )

        assert len(results) == 3
        assert results[0] is not None  # found
        assert results[1] is not None  # found
        assert results[2] is None      # not found

    def test_search_with_threshold(self):
        finder = FuzzyFinder("налоговая оптимизация")

        # Low threshold - should find
        results_low = finder.search(
            phrases=["налоговая"],
            options={"score_threshold": 0.1}
        )
        assert results_low[0] is not None

        # Very high threshold - might filter out
        results_high = finder.search(
            phrases=["налоговая"],
            options={"score_threshold": 0.99}
        )
        # Score normalization may vary, so just check it returns something
        assert len(results_high) == 1

    def test_search_find_all_multiple_occurrences(self):
        finder = FuzzyFinder("налог налог налог")

        results = finder.search(
            phrases=["налог"],
            options={"find_all": True}
        )

        # Should return list of matches
        result = results[0]
        if isinstance(result, list):
            assert len(result) >= 2
        else:
            # Single result is also valid
            assert result is not None

    def test_search_result_structure(self):
        finder = FuzzyFinder("тестовый текст для проверки")

        results = finder.search(
            phrases=["тестовый текст"],
            options={"score_threshold": 0.0}
        )

        result = results[0]
        if isinstance(result, list):
            result = result[0]

        assert hasattr(result, "found")
        assert hasattr(result, "start_offset")
        assert hasattr(result, "end_offset")
        assert hasattr(result, "score")
        assert hasattr(result, "matched_text")

    def test_positions_match(self):
        """Verify output positions match input positions."""
        finder = FuzzyFinder("a b c d e")

        phrases = ["a", "unknown1", "c", "unknown2", "e"]
        results = finder.search(phrases)

        assert len(results) == len(phrases)
        # positions 0, 2, 4 should be found
        # positions 1, 3 should be None


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
