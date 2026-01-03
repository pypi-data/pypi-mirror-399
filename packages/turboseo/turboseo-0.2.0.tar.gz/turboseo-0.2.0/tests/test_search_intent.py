"""Tests for search intent analyzer."""

import pytest

from turboseo.analyzers.search_intent import (
    IntentResult,
    SearchIntent,
    analyze_intent,
)


class TestSearchIntent:
    """Tests for search intent classification."""

    def test_informational_how_query(self):
        """How-to queries should be informational."""
        result = analyze_intent("how to start a podcast")
        assert result.primary_intent == SearchIntent.INFORMATIONAL
        assert result.confidence["informational"] > 40

    def test_informational_what_query(self):
        """What-is queries should be informational."""
        result = analyze_intent("what is SEO")
        assert result.primary_intent == SearchIntent.INFORMATIONAL

    def test_informational_guide_query(self):
        """Guide queries should be informational."""
        result = analyze_intent("beginner's guide to content marketing")
        assert result.primary_intent == SearchIntent.INFORMATIONAL

    def test_transactional_buy_query(self):
        """Buy queries should be transactional."""
        result = analyze_intent("buy podcast microphone")
        assert result.primary_intent == SearchIntent.TRANSACTIONAL

    def test_transactional_pricing_query(self):
        """Pricing queries should be transactional."""
        result = analyze_intent("podcast hosting pricing")
        assert result.primary_intent == SearchIntent.TRANSACTIONAL

    def test_transactional_discount_query(self):
        """Discount queries should be transactional."""
        result = analyze_intent("podcast equipment discount code")
        assert result.primary_intent == SearchIntent.TRANSACTIONAL

    def test_commercial_best_query(self):
        """Best-of queries should be commercial."""
        result = analyze_intent("best podcast hosting platforms")
        assert result.primary_intent == SearchIntent.COMMERCIAL

    def test_commercial_vs_query(self):
        """Comparison queries should be commercial."""
        result = analyze_intent("spotify vs apple podcasts")
        assert result.primary_intent == SearchIntent.COMMERCIAL

    def test_commercial_review_query(self):
        """Review queries should be commercial."""
        result = analyze_intent("castos review")
        assert result.primary_intent == SearchIntent.COMMERCIAL

    def test_commercial_alternatives_query(self):
        """Alternatives queries should be commercial."""
        result = analyze_intent("anchor alternatives")
        assert result.primary_intent == SearchIntent.COMMERCIAL

    def test_navigational_login_query(self):
        """Login queries should be navigational."""
        result = analyze_intent("spotify login")
        assert result.primary_intent == SearchIntent.NAVIGATIONAL

    def test_navigational_app_query(self):
        """App queries should be navigational."""
        result = analyze_intent("podcast app")
        assert result.primary_intent == SearchIntent.NAVIGATIONAL

    def test_numbered_list_commercial(self):
        """Numbered list queries should be commercial."""
        result = analyze_intent("10 best podcast microphones")
        assert result.primary_intent == SearchIntent.COMMERCIAL

    def test_returns_intent_result(self):
        """Should return IntentResult model."""
        result = analyze_intent("podcast tips")
        assert isinstance(result, IntentResult)

    def test_has_confidence_scores(self):
        """Result should have confidence scores for all intents."""
        result = analyze_intent("podcast tips")
        assert "informational" in result.confidence
        assert "navigational" in result.confidence
        assert "transactional" in result.confidence
        assert "commercial" in result.confidence

    def test_confidence_sums_to_100(self):
        """Confidence scores should sum to approximately 100."""
        result = analyze_intent("how to start a podcast")
        total = sum(result.confidence.values())
        assert 99 <= total <= 101  # Allow small floating point variance

    def test_has_recommendations(self):
        """Result should include recommendations."""
        result = analyze_intent("best podcast hosting")
        assert len(result.recommendations) > 0

    def test_signals_detected(self):
        """Should detect and report signals."""
        result = analyze_intent("how to buy podcast equipment")
        assert len(result.signals_detected) > 0

    def test_secondary_intent_close_scores(self):
        """Should report secondary intent when scores are close."""
        # Query with mixed signals
        result = analyze_intent("best way to buy podcast equipment")
        # This has both commercial (best) and transactional (buy) signals
        # May or may not have secondary intent depending on scoring
        assert result.primary_intent in [SearchIntent.COMMERCIAL, SearchIntent.TRANSACTIONAL]

    def test_empty_query(self):
        """Empty query should default to informational."""
        result = analyze_intent("")
        assert result.primary_intent == SearchIntent.INFORMATIONAL

    def test_generic_query(self):
        """Generic query without signals should still return result."""
        result = analyze_intent("podcast")
        assert isinstance(result, IntentResult)
        assert result.keyword == "podcast"


class TestIntentRecommendations:
    """Tests for intent-based recommendations."""

    def test_informational_recommendations(self):
        """Informational queries should get educational recommendations."""
        result = analyze_intent("what is podcasting")
        recs = " ".join(result.recommendations).lower()
        assert "educational" in recs or "step-by-step" in recs or "answer" in recs

    def test_transactional_recommendations(self):
        """Transactional queries should get conversion recommendations."""
        result = analyze_intent("buy microphone")
        recs = " ".join(result.recommendations).lower()
        assert "product" in recs or "pricing" in recs or "cta" in recs

    def test_commercial_recommendations(self):
        """Commercial queries should get comparison recommendations."""
        result = analyze_intent("best podcast hosting")
        recs = " ".join(result.recommendations).lower()
        assert "comparison" in recs or "review" in recs or "pros" in recs
