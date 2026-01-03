"""
Search Intent Analyzer

Determines the search intent of a query by analyzing keyword patterns.
Classifies queries as: Informational, Navigational, Transactional, or Commercial.
"""

import re
from enum import Enum

from pydantic import BaseModel


class SearchIntent(str, Enum):
    """Search intent types."""

    INFORMATIONAL = "informational"
    NAVIGATIONAL = "navigational"
    TRANSACTIONAL = "transactional"
    COMMERCIAL = "commercial"


class IntentResult(BaseModel):
    """Result of search intent analysis."""

    keyword: str
    primary_intent: SearchIntent
    secondary_intent: SearchIntent | None = None
    confidence: dict[str, float]
    signals_detected: dict[str, list[str]]
    recommendations: list[str]


# Intent signal keywords
INFORMATIONAL_SIGNALS = [
    "what",
    "why",
    "how",
    "when",
    "where",
    "who",
    "guide",
    "tutorial",
    "learn",
    "tips",
    "best practices",
    "explained",
    "definition",
    "meaning",
    "examples",
    "ideas",
]

NAVIGATIONAL_SIGNALS = [
    "login",
    "sign in",
    "website",
    "official",
    "home page",
    "account",
    "dashboard",
    "portal",
    "app",
]

TRANSACTIONAL_SIGNALS = [
    "buy",
    "purchase",
    "order",
    "download",
    "get",
    "pricing",
    "cost",
    "free trial",
    "sign up",
    "subscribe",
    "install",
    "coupon",
    "deal",
    "discount",
    "cheap",
    "affordable",
]

COMMERCIAL_SIGNALS = [
    "best",
    "top",
    "review",
    "vs",
    "versus",
    "compare",
    "comparison",
    "alternative",
    "alternatives",
    "like",
    "similar",
    "better than",
    "instead of",
    "or",
    "option",
    "choice",
]

# Content recommendations by intent
INTENT_RECOMMENDATIONS = {
    SearchIntent.INFORMATIONAL: [
        "Create comprehensive, educational content",
        "Include step-by-step instructions or explanations",
        "Answer common questions (People Also Ask)",
        "Use FAQ sections and definition boxes",
        "Target featured snippet optimization",
        "Include visuals, diagrams, and examples",
    ],
    SearchIntent.NAVIGATIONAL: [
        "Optimize for brand-related searches",
        "Ensure homepage/key pages rank well",
        "Include site navigation and clear CTAs",
        "Strengthen brand presence and awareness",
        "Focus on brand + product name combinations",
    ],
    SearchIntent.TRANSACTIONAL: [
        "Focus on product/service pages",
        "Include clear pricing and purchase options",
        "Add trust signals (reviews, testimonials)",
        "Optimize for conversion, not just traffic",
        "Include strong, action-oriented CTAs",
        "Consider local SEO if applicable",
    ],
    SearchIntent.COMMERCIAL: [
        "Create comparison and review content",
        "Include pros/cons and alternatives",
        "Add detailed feature breakdowns",
        "Include data tables and comparisons",
        "Show 'best for' categories",
        "Help users make informed decisions",
    ],
}


def _analyze_keyword_patterns(keyword: str) -> dict[SearchIntent, float]:
    """Score keyword based on pattern matching."""
    scores: dict[SearchIntent, float] = {intent: 0.0 for intent in SearchIntent}
    keyword_lower = keyword.lower()

    # Check for signal words
    for signal in INFORMATIONAL_SIGNALS:
        if signal in keyword_lower:
            scores[SearchIntent.INFORMATIONAL] += 2

    for signal in NAVIGATIONAL_SIGNALS:
        if signal in keyword_lower:
            scores[SearchIntent.NAVIGATIONAL] += 3

    for signal in TRANSACTIONAL_SIGNALS:
        if signal in keyword_lower:
            scores[SearchIntent.TRANSACTIONAL] += 2

    for signal in COMMERCIAL_SIGNALS:
        if signal in keyword_lower:
            scores[SearchIntent.COMMERCIAL] += 2

    # Pattern-based scoring
    # Questions are typically informational
    if re.match(
        r"^(what|why|how|when|where|who|can|should|is|are|does)", keyword_lower
    ):
        scores[SearchIntent.INFORMATIONAL] += 3

    # Brand + generic term = navigational (2 word queries)
    if len(keyword.split()) == 2:
        scores[SearchIntent.NAVIGATIONAL] += 1

    # Lists and comparisons = commercial
    if re.search(r"\d+\s+(best|top)", keyword_lower):
        scores[SearchIntent.COMMERCIAL] += 3

    # "X vs Y" pattern = commercial
    if re.search(r"\bvs\.?\b|\bversus\b", keyword_lower):
        scores[SearchIntent.COMMERCIAL] += 3

    return scores


def _get_detected_signals(keyword: str) -> dict[str, list[str]]:
    """Get list of signals detected for each intent."""
    signals: dict[str, list[str]] = {
        "informational": [],
        "navigational": [],
        "transactional": [],
        "commercial": [],
    }
    keyword_lower = keyword.lower()

    for signal in INFORMATIONAL_SIGNALS:
        if signal in keyword_lower:
            signals["informational"].append(f"Contains '{signal}'")

    for signal in NAVIGATIONAL_SIGNALS:
        if signal in keyword_lower:
            signals["navigational"].append(f"Contains '{signal}'")

    for signal in TRANSACTIONAL_SIGNALS:
        if signal in keyword_lower:
            signals["transactional"].append(f"Contains '{signal}'")

    for signal in COMMERCIAL_SIGNALS:
        if signal in keyword_lower:
            signals["commercial"].append(f"Contains '{signal}'")

    # Remove empty lists
    return {k: v for k, v in signals.items() if v}


def analyze_intent(keyword: str) -> IntentResult:
    """
    Analyze search intent for a keyword.

    Args:
        keyword: Search query to analyze

    Returns:
        IntentResult with classification and recommendations
    """
    # Calculate intent scores
    scores = _analyze_keyword_patterns(keyword)

    # Normalize scores to percentages
    total = sum(scores.values())
    if total > 0:
        confidence = {
            intent.value: round(score / total * 100, 1)
            for intent, score in scores.items()
        }
    else:
        # Default to informational if no signals
        confidence = {
            SearchIntent.INFORMATIONAL.value: 40.0,
            SearchIntent.NAVIGATIONAL.value: 20.0,
            SearchIntent.TRANSACTIONAL.value: 20.0,
            SearchIntent.COMMERCIAL.value: 20.0,
        }

    # Primary intent is highest scoring
    primary_intent = max(scores.items(), key=lambda x: x[1])[0]

    # Secondary intent if within 15% of primary
    sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    secondary_intent = None
    if len(sorted_scores) > 1 and sorted_scores[0][1] > 0:
        primary_pct = confidence[sorted_scores[0][0].value]
        secondary_pct = confidence[sorted_scores[1][0].value]
        if primary_pct - secondary_pct < 15:
            secondary_intent = sorted_scores[1][0]

    # Get recommendations
    recommendations = list(INTENT_RECOMMENDATIONS[primary_intent])
    if secondary_intent:
        recommendations.append(
            f"Secondary intent is {secondary_intent.value} - consider blending approaches"
        )

    return IntentResult(
        keyword=keyword,
        primary_intent=primary_intent,
        secondary_intent=secondary_intent,
        confidence=confidence,
        signals_detected=_get_detected_signals(keyword),
        recommendations=recommendations,
    )
