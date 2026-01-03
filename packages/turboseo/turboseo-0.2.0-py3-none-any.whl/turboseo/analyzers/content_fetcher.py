"""
Content Fetcher

Fetches and parses web pages for SEO analysis.
Extracts text content, headings, meta tags, and structure.
"""

import re
from urllib.parse import urlparse

from pydantic import BaseModel


class FetchedContent(BaseModel):
    """Result of fetching and parsing a web page."""

    url: str
    title: str | None = None
    meta_description: str | None = None
    meta_keywords: str | None = None
    h1: str | None = None
    h2s: list[str] = []
    h3s: list[str] = []
    content: str = ""
    word_count: int = 0
    internal_links: list[str] = []
    external_links: list[str] = []
    images: list[dict[str, str]] = []
    error: str | None = None


def _extract_text_from_html(html: str) -> str:
    """Extract readable text from HTML, removing scripts and styles."""
    # Remove script and style elements
    html = re.sub(r"<script[^>]*>.*?</script>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<style[^>]*>.*?</style>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<noscript[^>]*>.*?</noscript>", "", html, flags=re.DOTALL | re.IGNORECASE)

    # Remove HTML comments
    html = re.sub(r"<!--.*?-->", "", html, flags=re.DOTALL)

    # Remove header and footer (common noise)
    html = re.sub(r"<header[^>]*>.*?</header>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<footer[^>]*>.*?</footer>", "", html, flags=re.DOTALL | re.IGNORECASE)
    html = re.sub(r"<nav[^>]*>.*?</nav>", "", html, flags=re.DOTALL | re.IGNORECASE)

    # Replace block elements with newlines
    html = re.sub(r"</(p|div|h[1-6]|li|br|tr)>", "\n", html, flags=re.IGNORECASE)
    html = re.sub(r"<br\s*/?>", "\n", html, flags=re.IGNORECASE)

    # Remove remaining tags
    html = re.sub(r"<[^>]+>", " ", html)

    # Decode common HTML entities
    html = html.replace("&nbsp;", " ")
    html = html.replace("&amp;", "&")
    html = html.replace("&lt;", "<")
    html = html.replace("&gt;", ">")
    html = html.replace("&quot;", '"')
    html = html.replace("&#39;", "'")
    html = html.replace("&rsquo;", "'")
    html = html.replace("&lsquo;", "'")
    html = html.replace("&rdquo;", '"')
    html = html.replace("&ldquo;", '"')
    html = html.replace("&mdash;", "—")
    html = html.replace("&ndash;", "–")

    # Clean up whitespace
    html = re.sub(r"[ \t]+", " ", html)
    html = re.sub(r"\n\s*\n", "\n\n", html)
    html = html.strip()

    return html


def _extract_meta_tag(html: str, name: str) -> str | None:
    """Extract content from a meta tag by name or property."""
    # Try name attribute
    match = re.search(
        rf'<meta\s+name=["\']?{name}["\']?\s+content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    # Try content before name
    match = re.search(
        rf'<meta\s+content=["\']([^"\']+)["\']\s+name=["\']?{name}["\']?',
        html,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    # Try property attribute (for Open Graph)
    match = re.search(
        rf'<meta\s+property=["\']?{name}["\']?\s+content=["\']([^"\']+)["\']',
        html,
        re.IGNORECASE,
    )
    if match:
        return match.group(1)

    return None


def _extract_title(html: str) -> str | None:
    """Extract the page title."""
    match = re.search(r"<title[^>]*>([^<]+)</title>", html, re.IGNORECASE)
    if match:
        return match.group(1).strip()
    return None


def _extract_headings(html: str, level: int) -> list[str]:
    """Extract all headings of a given level."""
    pattern = rf"<h{level}[^>]*>(.*?)</h{level}>"
    matches = re.findall(pattern, html, re.IGNORECASE | re.DOTALL)
    # Clean HTML from heading content
    headings = []
    for match in matches:
        clean = re.sub(r"<[^>]+>", "", match).strip()
        if clean:
            headings.append(clean)
    return headings


def _extract_links(html: str, base_url: str) -> tuple[list[str], list[str]]:
    """Extract internal and external links."""
    internal: list[str] = []
    external: list[str] = []

    parsed_base = urlparse(base_url)
    base_domain = parsed_base.netloc.lower()

    # Find all href attributes
    matches = re.findall(r'href=["\']([^"\']+)["\']', html, re.IGNORECASE)

    for href in matches:
        # Skip anchors, javascript, and mailto
        if href.startswith("#") or href.startswith("javascript:") or href.startswith("mailto:"):
            continue

        # Parse the URL
        parsed = urlparse(href)

        # Determine if internal or external
        if not parsed.netloc:
            # Relative URL = internal
            internal.append(href)
        elif parsed.netloc.lower() == base_domain:
            internal.append(href)
        else:
            external.append(href)

    return list(set(internal)), list(set(external))


def _extract_images(html: str) -> list[dict[str, str]]:
    """Extract images with their alt text."""
    images: list[dict[str, str]] = []

    # Find img tags
    img_matches = re.findall(r"<img[^>]+>", html, re.IGNORECASE)

    for img in img_matches:
        src_match = re.search(r'src=["\']([^"\']+)["\']', img)
        alt_match = re.search(r'alt=["\']([^"\']*)["\']', img)

        if src_match:
            images.append({
                "src": src_match.group(1),
                "alt": alt_match.group(1) if alt_match else "",
            })

    return images


def parse_html(html: str, url: str) -> FetchedContent:
    """
    Parse HTML content and extract SEO-relevant elements.

    Args:
        html: Raw HTML content
        url: The URL the content was fetched from

    Returns:
        FetchedContent with extracted elements
    """
    # Extract elements
    title = _extract_title(html)
    meta_description = _extract_meta_tag(html, "description")
    meta_keywords = _extract_meta_tag(html, "keywords")

    h1s = _extract_headings(html, 1)
    h2s = _extract_headings(html, 2)
    h3s = _extract_headings(html, 3)

    internal_links, external_links = _extract_links(html, url)
    images = _extract_images(html)

    # Extract main content
    content = _extract_text_from_html(html)
    word_count = len(content.split())

    return FetchedContent(
        url=url,
        title=title,
        meta_description=meta_description,
        meta_keywords=meta_keywords,
        h1=h1s[0] if h1s else None,
        h2s=h2s,
        h3s=h3s,
        content=content,
        word_count=word_count,
        internal_links=internal_links,
        external_links=external_links,
        images=images,
    )


def fetch_url(url: str) -> FetchedContent:
    """
    Fetch a URL and parse its content.

    Args:
        url: The URL to fetch

    Returns:
        FetchedContent with parsed content or error

    Note:
        This function requires the 'requests' library.
        If not available, returns an error.
    """
    try:
        import requests
    except ImportError:
        return FetchedContent(
            url=url,
            error="requests library not installed. Run: pip install requests",
        )

    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (compatible; TurboSEO/1.0; +https://github.com/turboseo)"
        }
        response = requests.get(url, headers=headers, timeout=30)
        response.raise_for_status()

        return parse_html(response.text, url)

    except requests.exceptions.RequestException as e:
        return FetchedContent(
            url=url,
            error=str(e),
        )
