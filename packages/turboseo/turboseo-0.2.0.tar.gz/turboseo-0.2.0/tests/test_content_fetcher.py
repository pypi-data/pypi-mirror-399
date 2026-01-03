"""Tests for content fetcher."""

import pytest

from turboseo.analyzers.content_fetcher import (
    FetchedContent,
    parse_html,
)


class TestParseHtml:
    """Tests for HTML parsing."""

    def test_extracts_title(self):
        """Should extract page title."""
        html = "<html><head><title>Test Page</title></head><body></body></html>"
        result = parse_html(html, "https://example.com")
        assert result.title == "Test Page"

    def test_extracts_meta_description(self):
        """Should extract meta description."""
        html = '''
        <html>
        <head>
            <meta name="description" content="This is a test description">
        </head>
        <body></body>
        </html>
        '''
        result = parse_html(html, "https://example.com")
        assert result.meta_description == "This is a test description"

    def test_extracts_meta_description_content_first(self):
        """Should extract meta description with content attr first."""
        html = '''
        <html>
        <head>
            <meta content="Content first description" name="description">
        </head>
        <body></body>
        </html>
        '''
        result = parse_html(html, "https://example.com")
        assert result.meta_description == "Content first description"

    def test_extracts_h1(self):
        """Should extract H1 heading."""
        html = "<html><body><h1>Main Heading</h1></body></html>"
        result = parse_html(html, "https://example.com")
        assert result.h1 == "Main Heading"

    def test_extracts_multiple_h2s(self):
        """Should extract all H2 headings."""
        html = """
        <html><body>
            <h2>Section One</h2>
            <h2>Section Two</h2>
            <h2>Section Three</h2>
        </body></html>
        """
        result = parse_html(html, "https://example.com")
        assert len(result.h2s) == 3
        assert "Section One" in result.h2s
        assert "Section Two" in result.h2s

    def test_extracts_content_text(self):
        """Should extract readable text content."""
        html = """
        <html><body>
            <p>This is a paragraph.</p>
            <p>This is another paragraph.</p>
        </body></html>
        """
        result = parse_html(html, "https://example.com")
        assert "This is a paragraph" in result.content
        assert "This is another paragraph" in result.content

    def test_removes_scripts(self):
        """Should remove script content."""
        html = """
        <html><body>
            <p>Visible text</p>
            <script>var x = 'invisible';</script>
        </body></html>
        """
        result = parse_html(html, "https://example.com")
        assert "Visible text" in result.content
        assert "invisible" not in result.content

    def test_removes_styles(self):
        """Should remove style content."""
        html = """
        <html><body>
            <p>Visible text</p>
            <style>.hidden { display: none; }</style>
        </body></html>
        """
        result = parse_html(html, "https://example.com")
        assert "Visible text" in result.content
        assert "hidden" not in result.content

    def test_counts_words(self):
        """Should count words in content."""
        html = "<html><body><p>One two three four five</p></body></html>"
        result = parse_html(html, "https://example.com")
        assert result.word_count >= 5

    def test_extracts_internal_links(self):
        """Should identify internal links."""
        html = '''
        <html><body>
            <a href="/about">About</a>
            <a href="https://example.com/contact">Contact</a>
        </body></html>
        '''
        result = parse_html(html, "https://example.com")
        assert "/about" in result.internal_links
        assert "https://example.com/contact" in result.internal_links

    def test_extracts_external_links(self):
        """Should identify external links."""
        html = '''
        <html><body>
            <a href="https://other-site.com/page">External</a>
        </body></html>
        '''
        result = parse_html(html, "https://example.com")
        assert "https://other-site.com/page" in result.external_links

    def test_ignores_anchor_links(self):
        """Should ignore anchor links."""
        html = '''
        <html><body>
            <a href="#section">Anchor</a>
        </body></html>
        '''
        result = parse_html(html, "https://example.com")
        assert "#section" not in result.internal_links
        assert "#section" not in result.external_links

    def test_ignores_javascript_links(self):
        """Should ignore javascript links."""
        html = '''
        <html><body>
            <a href="javascript:void(0)">Click</a>
        </body></html>
        '''
        result = parse_html(html, "https://example.com")
        assert len(result.internal_links) == 0
        assert len(result.external_links) == 0

    def test_extracts_images(self):
        """Should extract images with alt text."""
        html = '''
        <html><body>
            <img src="/images/photo.jpg" alt="A photo">
        </body></html>
        '''
        result = parse_html(html, "https://example.com")
        assert len(result.images) == 1
        assert result.images[0]["src"] == "/images/photo.jpg"
        assert result.images[0]["alt"] == "A photo"

    def test_extracts_images_without_alt(self):
        """Should extract images even without alt text."""
        html = '''
        <html><body>
            <img src="/images/photo.jpg">
        </body></html>
        '''
        result = parse_html(html, "https://example.com")
        assert len(result.images) == 1
        assert result.images[0]["alt"] == ""

    def test_decodes_html_entities(self):
        """Should decode common HTML entities."""
        html = "<html><body><p>Rock &amp; Roll &mdash; forever</p></body></html>"
        result = parse_html(html, "https://example.com")
        assert "Rock & Roll" in result.content
        assert "—" in result.content

    def test_returns_fetched_content_model(self):
        """Should return FetchedContent model."""
        html = "<html><body></body></html>"
        result = parse_html(html, "https://example.com")
        assert isinstance(result, FetchedContent)
        assert result.url == "https://example.com"

    def test_handles_empty_html(self):
        """Should handle empty HTML."""
        result = parse_html("", "https://example.com")
        assert result.word_count == 0

    def test_cleans_heading_html(self):
        """Should clean HTML from heading content."""
        html = "<html><body><h2><span>Styled</span> Heading</h2></body></html>"
        result = parse_html(html, "https://example.com")
        assert "Styled Heading" in result.h2s

    def test_removes_nav_content(self):
        """Should remove navigation content."""
        html = """
        <html><body>
            <nav><a href="/">Home</a><a href="/about">About</a></nav>
            <p>Main content here</p>
        </body></html>
        """
        result = parse_html(html, "https://example.com")
        # Nav links shouldn't appear in main content
        assert "Main content here" in result.content


class TestFetchedContentModel:
    """Tests for FetchedContent model."""

    def test_default_values(self):
        """Should have sensible defaults."""
        content = FetchedContent(url="https://example.com")
        assert content.url == "https://example.com"
        assert content.title is None
        assert content.h2s == []
        assert content.word_count == 0
        assert content.error is None

    def test_error_field(self):
        """Should support error field."""
        content = FetchedContent(
            url="https://example.com",
            error="Connection failed"
        )
        assert content.error == "Connection failed"
