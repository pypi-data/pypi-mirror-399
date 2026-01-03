"""
Content Length Analyzer

Analyzes content length against targets and provides recommendations.
Works without external APIs using configurable target ranges.
"""

import statistics
from enum import Enum

from pydantic import BaseModel


class LengthStatus(str, Enum):
    """Content length status."""

    TOO_SHORT = "too_short"
    SHORT = "short"
    GOOD = "good"
    OPTIMAL = "optimal"
    LONG = "long"


class LengthResult(BaseModel):
    """Result of content length analysis."""

    word_count: int
    status: LengthStatus
    target_min: int
    target_optimal: int
    target_max: int
    gap_to_optimal: int
    percentage_of_optimal: float
    recommendation: str
    distribution_category: str


# Default targets by content type
DEFAULT_TARGETS = {
    "blog_post": {"min": 1500, "optimal": 2500, "max": 4000},
    "guide": {"min": 2000, "optimal": 3000, "max": 5000},
    "product_page": {"min": 500, "optimal": 800, "max": 1500},
    "landing_page": {"min": 800, "optimal": 1200, "max": 2000},
    "listicle": {"min": 1500, "optimal": 2000, "max": 3500},
    "how_to": {"min": 1500, "optimal": 2500, "max": 4000},
    "comparison": {"min": 2000, "optimal": 3000, "max": 4500},
    "news": {"min": 500, "optimal": 800, "max": 1500},
}


def _get_distribution_category(word_count: int) -> str:
    """Categorize content by word count range."""
    if word_count < 500:
        return "very_short"
    elif word_count < 1000:
        return "short"
    elif word_count < 1500:
        return "medium_short"
    elif word_count < 2000:
        return "medium"
    elif word_count < 2500:
        return "medium_long"
    elif word_count < 3000:
        return "long"
    elif word_count < 4000:
        return "very_long"
    else:
        return "comprehensive"


def _get_status(
    word_count: int, target_min: int, target_optimal: int, target_max: int
) -> LengthStatus:
    """Determine content length status."""
    if word_count < target_min * 0.7:
        return LengthStatus.TOO_SHORT
    elif word_count < target_min:
        return LengthStatus.SHORT
    elif word_count < target_optimal:
        return LengthStatus.GOOD
    elif word_count <= target_max:
        return LengthStatus.OPTIMAL
    else:
        return LengthStatus.LONG


def _get_recommendation(
    word_count: int,
    status: LengthStatus,
    target_optimal: int,
    gap: int,
) -> str:
    """Generate recommendation based on analysis."""
    if status == LengthStatus.TOO_SHORT:
        return (
            f"Content is significantly below target. Add {gap} words to reach "
            f"optimal length of {target_optimal}. Consider expanding each section."
        )
    elif status == LengthStatus.SHORT:
        return (
            f"Content is slightly below target. Add {gap} words to reach "
            f"optimal length. Add more examples or expand key points."
        )
    elif status == LengthStatus.GOOD:
        return (
            f"Content length is acceptable. Consider adding {gap} more words "
            f"to reach optimal length and improve competitiveness."
        )
    elif status == LengthStatus.OPTIMAL:
        return "Content length is optimal for this content type. Focus on quality over adding more words."
    else:  # LONG
        excess = word_count - target_optimal
        return (
            f"Content is {excess} words over optimal. Ensure all content adds value. "
            "Consider breaking into multiple articles if topics diverge."
        )


def analyze_length(
    word_count: int,
    content_type: str = "blog_post",
    custom_targets: dict[str, int] | None = None,
) -> LengthResult:
    """
    Analyze content length against targets.

    Args:
        word_count: Number of words in the content
        content_type: Type of content (blog_post, guide, product_page, etc.)
        custom_targets: Custom target dict with 'min', 'optimal', 'max' keys

    Returns:
        LengthResult with analysis and recommendations
    """
    # Get targets
    if custom_targets:
        targets = custom_targets
    elif content_type in DEFAULT_TARGETS:
        targets = DEFAULT_TARGETS[content_type]
    else:
        targets = DEFAULT_TARGETS["blog_post"]

    target_min = targets["min"]
    target_optimal = targets["optimal"]
    target_max = targets["max"]

    # Calculate metrics
    status = _get_status(word_count, target_min, target_optimal, target_max)
    gap_to_optimal = max(0, target_optimal - word_count)
    percentage = round((word_count / target_optimal) * 100, 1)
    category = _get_distribution_category(word_count)
    recommendation = _get_recommendation(word_count, status, target_optimal, gap_to_optimal)

    return LengthResult(
        word_count=word_count,
        status=status,
        target_min=target_min,
        target_optimal=target_optimal,
        target_max=target_max,
        gap_to_optimal=gap_to_optimal,
        percentage_of_optimal=percentage,
        recommendation=recommendation,
        distribution_category=category,
    )


def compare_lengths(word_counts: list[int]) -> dict:
    """
    Compare multiple content pieces by length.

    Args:
        word_counts: List of word counts to compare

    Returns:
        Dictionary with statistics and distribution
    """
    if not word_counts:
        return {"error": "No word counts provided"}

    # Calculate statistics
    stats = {
        "count": len(word_counts),
        "min": min(word_counts),
        "max": max(word_counts),
        "mean": round(statistics.mean(word_counts)),
        "median": round(statistics.median(word_counts)),
    }

    if len(word_counts) > 1:
        stats["std_dev"] = round(statistics.stdev(word_counts))

    if len(word_counts) >= 4:
        quantiles = statistics.quantiles(word_counts, n=4)
        stats["percentile_25"] = round(quantiles[0])
        stats["percentile_75"] = round(quantiles[2])

    # Categorize distribution
    distribution = {
        "very_short": 0,
        "short": 0,
        "medium_short": 0,
        "medium": 0,
        "medium_long": 0,
        "long": 0,
        "very_long": 0,
        "comprehensive": 0,
    }

    for count in word_counts:
        category = _get_distribution_category(count)
        distribution[category] += 1

    return {
        "statistics": stats,
        "distribution": distribution,
    }


def get_content_types() -> list[str]:
    """Return list of available content types."""
    return list(DEFAULT_TARGETS.keys())


def get_targets(content_type: str) -> dict[str, int] | None:
    """Get targets for a content type."""
    return DEFAULT_TARGETS.get(content_type)
