"""Tests for content length analyzer."""

import pytest

from turboseo.analyzers.content_length import (
    LengthResult,
    LengthStatus,
    analyze_length,
    compare_lengths,
    get_content_types,
    get_targets,
    DEFAULT_TARGETS,
)


class TestAnalyzeLength:
    """Tests for content length analysis."""

    def test_too_short_content(self):
        """Content well below minimum should be too_short."""
        result = analyze_length(500, "blog_post")
        assert result.status == LengthStatus.TOO_SHORT
        assert result.gap_to_optimal > 0

    def test_short_content(self):
        """Content slightly below minimum should be short."""
        result = analyze_length(1400, "blog_post")
        assert result.status == LengthStatus.SHORT

    def test_good_content(self):
        """Content between min and optimal should be good."""
        result = analyze_length(2000, "blog_post")
        assert result.status == LengthStatus.GOOD

    def test_optimal_content(self):
        """Content at optimal length should be optimal."""
        result = analyze_length(2500, "blog_post")
        assert result.status == LengthStatus.OPTIMAL

    def test_long_content(self):
        """Content above max should be long."""
        result = analyze_length(5000, "blog_post")
        assert result.status == LengthStatus.LONG

    def test_returns_length_result(self):
        """Should return LengthResult model."""
        result = analyze_length(2000, "blog_post")
        assert isinstance(result, LengthResult)

    def test_calculates_gap(self):
        """Should calculate gap to optimal."""
        result = analyze_length(2000, "blog_post")
        # Blog post optimal is 2500
        assert result.gap_to_optimal == 500

    def test_no_gap_when_at_optimal(self):
        """Gap should be 0 when at or above optimal."""
        result = analyze_length(2500, "blog_post")
        assert result.gap_to_optimal == 0

    def test_calculates_percentage(self):
        """Should calculate percentage of optimal."""
        result = analyze_length(2500, "blog_post")
        assert result.percentage_of_optimal == 100.0

    def test_has_recommendation(self):
        """Should include recommendation text."""
        result = analyze_length(1000, "blog_post")
        assert len(result.recommendation) > 0

    def test_different_content_types(self):
        """Different content types should have different targets."""
        blog = analyze_length(1000, "blog_post")
        product = analyze_length(1000, "product_page")

        # 1000 words is optimal for product page but short for blog
        assert blog.status in [LengthStatus.TOO_SHORT, LengthStatus.SHORT]
        assert product.status == LengthStatus.OPTIMAL

    def test_guide_targets(self):
        """Guide should have higher targets than blog post."""
        result = analyze_length(2000, "guide")
        # Guide optimal is 3000, so 2000 is good (between min and optimal)
        assert result.status == LengthStatus.GOOD
        assert result.target_optimal == 3000

    def test_custom_targets(self):
        """Should accept custom targets."""
        custom = {"min": 1000, "optimal": 1500, "max": 2000}
        result = analyze_length(1500, custom_targets=custom)
        assert result.status == LengthStatus.OPTIMAL
        assert result.target_optimal == 1500

    def test_unknown_content_type_uses_blog_default(self):
        """Unknown content type should fall back to blog_post."""
        result = analyze_length(2000, "unknown_type")
        blog_result = analyze_length(2000, "blog_post")
        assert result.target_optimal == blog_result.target_optimal

    def test_distribution_category_very_short(self):
        """Should categorize very short content."""
        result = analyze_length(300, "blog_post")
        assert result.distribution_category == "very_short"

    def test_distribution_category_comprehensive(self):
        """Should categorize comprehensive content."""
        result = analyze_length(4500, "blog_post")
        assert result.distribution_category == "comprehensive"


class TestCompareLengths:
    """Tests for comparing multiple content lengths."""

    def test_basic_comparison(self):
        """Should compare multiple word counts."""
        result = compare_lengths([1000, 2000, 3000])
        assert "statistics" in result
        assert "distribution" in result

    def test_statistics_min_max(self):
        """Should calculate min and max."""
        result = compare_lengths([1000, 2000, 3000])
        assert result["statistics"]["min"] == 1000
        assert result["statistics"]["max"] == 3000

    def test_statistics_mean_median(self):
        """Should calculate mean and median."""
        result = compare_lengths([1000, 2000, 3000])
        assert result["statistics"]["mean"] == 2000
        assert result["statistics"]["median"] == 2000

    def test_statistics_std_dev(self):
        """Should calculate standard deviation for multiple items."""
        result = compare_lengths([1000, 2000, 3000])
        assert "std_dev" in result["statistics"]

    def test_no_std_dev_for_single(self):
        """Should not have std_dev for single item."""
        result = compare_lengths([2000])
        assert "std_dev" not in result["statistics"]

    def test_percentiles_with_enough_data(self):
        """Should calculate percentiles with 4+ items."""
        result = compare_lengths([1000, 1500, 2000, 2500, 3000])
        assert "percentile_25" in result["statistics"]
        assert "percentile_75" in result["statistics"]

    def test_distribution_counts(self):
        """Should count items in each distribution category."""
        result = compare_lengths([500, 1200, 2200, 4500])
        dist = result["distribution"]
        assert dist["short"] == 1  # 500 (500-1000)
        assert dist["medium_short"] == 1  # 1200 (1000-1500)
        assert dist["medium_long"] == 1  # 2200 (2000-2500)
        assert dist["comprehensive"] == 1  # 4500 (4000+)

    def test_empty_list_returns_error(self):
        """Empty list should return error."""
        result = compare_lengths([])
        assert "error" in result


class TestHelperFunctions:
    """Tests for helper functions."""

    def test_get_content_types(self):
        """Should return list of content types."""
        types = get_content_types()
        assert isinstance(types, list)
        assert "blog_post" in types
        assert "guide" in types
        assert "product_page" in types

    def test_get_targets_valid_type(self):
        """Should return targets for valid content type."""
        targets = get_targets("blog_post")
        assert targets is not None
        assert "min" in targets
        assert "optimal" in targets
        assert "max" in targets

    def test_get_targets_invalid_type(self):
        """Should return None for invalid content type."""
        targets = get_targets("invalid_type")
        assert targets is None

    def test_default_targets_structure(self):
        """Default targets should have correct structure."""
        for content_type, targets in DEFAULT_TARGETS.items():
            assert "min" in targets
            assert "optimal" in targets
            assert "max" in targets
            assert targets["min"] < targets["optimal"]
            assert targets["optimal"] < targets["max"]


class TestLengthRecommendations:
    """Tests for recommendation messages."""

    def test_too_short_recommendation(self):
        """Too short content should mention adding words."""
        result = analyze_length(500, "blog_post")
        assert "add" in result.recommendation.lower()

    def test_short_recommendation(self):
        """Short content should suggest expanding."""
        result = analyze_length(1400, "blog_post")
        assert "add" in result.recommendation.lower()

    def test_good_recommendation(self):
        """Good content should encourage reaching optimal."""
        result = analyze_length(2000, "blog_post")
        assert "optimal" in result.recommendation.lower()

    def test_optimal_recommendation(self):
        """Optimal content should focus on quality."""
        result = analyze_length(2500, "blog_post")
        assert "quality" in result.recommendation.lower()

    def test_long_recommendation(self):
        """Long content should mention value and possible splitting."""
        result = analyze_length(5000, "blog_post")
        assert "value" in result.recommendation.lower() or "breaking" in result.recommendation.lower()
