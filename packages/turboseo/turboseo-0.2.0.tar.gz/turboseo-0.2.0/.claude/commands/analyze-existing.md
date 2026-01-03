# /analyze-existing

Analyze an existing web page or local file for SEO and human writing quality.

## Instructions

1. Determine if the input is a URL or file path:
   - URLs start with `http://` or `https://`
   - Otherwise treat as a local file path

2. For URLs, fetch and analyze the content:
   ```bash
   # First, check if requests is installed
   pip show requests || pip install requests
   ```

   Then use Python to fetch and analyze:
   ```python
   from turboseo.analyzers import fetch_url, analyze_seo, analyze_writing_standards

   content = fetch_url("$ARGUMENTS")
   if content.error:
       print(f"Error: {content.error}")
   else:
       # Analyze the fetched content
       print(f"Title: {content.title}")
       print(f"Word count: {content.word_count}")
   ```

3. For local files, run the standard analysis:
   ```bash
   turboseo analyze $ARGUMENTS
   turboseo check $ARGUMENTS
   ```

4. Create a comprehensive analysis report including:
   - Content health score (0-100)
   - Human writing score
   - SEO score breakdown
   - Quick wins (immediate improvements)
   - Strategic improvements
   - Rewrite priority and scope

5. Save the analysis to `research/analysis-{topic}-{date}.md`

## Analysis Report Format

```markdown
# Content Analysis: {title or filename}

**URL/File:** {source}
**Date:** {YYYY-MM-DD}
**Word Count:** {count}

## Content Health Score

**Overall:** {X}/100

| Category | Score | Status |
|----------|-------|--------|
| Human Writing | {X} | {OK/Needs Work} |
| SEO | {X} | {OK/Needs Work} |
| Readability | {X} | {OK/Needs Work} |
| Structure | {X} | {OK/Needs Work} |

## Quick Wins (Fix Now)

1. {Immediate improvement with specific action}
2. {Another quick fix}

## Strategic Improvements

1. {Larger improvement with explanation}
2. {Content gap to fill}

## Rewrite Recommendation

**Priority:** High/Medium/Low
**Scope:** Light update / Moderate revision / Full rewrite
**Reason:** {Why this level of effort}

## Next Steps

1. {Specific action}
2. {Specific action}
```

## Example Usage

```
/analyze-existing https://example.com/blog/seo-guide
/analyze-existing drafts/old-article.md
/analyze-existing published/product-page.md
```
