# Performance Review Command

Manual content audit and prioritization without external APIs.

## Usage

```
/performance-review [directory]
```

Default directory: `published/`

## What This Command Does

1. Scans content in the specified directory
2. Analyzes each file for quality metrics
3. Identifies improvement opportunities
4. Prioritizes content by optimization potential
5. Creates actionable task queue

## Process

### 1. Content Inventory

For each markdown file in the directory:

```bash
# Analyze all published content
for file in published/*.md; do
  turboseo analyze "$file"
  turboseo check "$file"
done
```

Or analyze specific files:
```bash
turboseo analyze published/article-1.md
turboseo analyze published/article-2.md
```

### 2. Categorize Content

Group content by quality score:

| Score | Category | Action |
|-------|----------|--------|
| 80+ | Healthy | Monitor, minor tweaks |
| 60-79 | Needs Work | Schedule optimization |
| <60 | Critical | Prioritize rewrite |

### 3. Identify Opportunities

**Quick Wins** (High impact, low effort):
- Human score 60-79 (few AI patterns to fix)
- Missing keyword in key locations
- Meta elements need minor updates

**Rewrites Needed** (Medium effort):
- Human score <60 (significant AI patterns)
- Outdated content (check dates in frontmatter)
- Thin content (<1500 words)

**New Content Gaps**:
- Topics mentioned but not covered
- Related topics to existing content
- Questions not fully answered

### 4. Prioritization Scoring

Score each opportunity (0-100):

```
Score = Impact (50%) + Effort (30%) + Urgency (20%)

Impact:
- High traffic potential = +40
- Strategic topic = +30
- Supports other content = +20

Effort:
- Quick fix (<1 hour) = +30
- Moderate (<4 hours) = +20
- Major (full rewrite) = +10

Urgency:
- Outdated info = +20
- Low human score = +15
- Missing SEO basics = +10
```

## Output Format

Create report at `research/performance-review-{date}.md`:

```markdown
# Content Performance Review

**Date:** YYYY-MM-DD
**Content Analyzed:** X files
**Directory:** published/

## Summary

| Category | Count | % of Total |
|----------|-------|------------|
| Healthy (80+) | X | X% |
| Needs Work (60-79) | X | X% |
| Critical (<60) | X | X% |

**Average Human Score:** X/100
**Average SEO Score:** X/100

## Priority Queue

### 🔥 Urgent (This Week)

1. **[Article Title]**
   - File: `published/filename.md`
   - Human Score: X/100
   - Issue: [Primary issue]
   - Action: [Specific action]
   - Effort: X hours
   - Priority Score: X/100

### ⚡ High Priority (This Month)

[Same format]

### 📋 Scheduled (Next Month)

[Same format]

## Content Health by File

| File | Human | SEO | Words | Issues | Priority |
|------|-------|-----|-------|--------|----------|
| article-1.md | 85 | 78 | 2400 | 2 | Low |
| article-2.md | 62 | 65 | 1800 | 5 | High |

## Quick Wins

Easy fixes that improve scores quickly:

1. **[Article]**: Add keyword to first 100 words
2. **[Article]**: Fix meta description length
3. **[Article]**: Replace 2 AI vocabulary words

## Recommended Actions

### Week 1
- [ ] [Action 1]
- [ ] [Action 2]

### Week 2
- [ ] [Action 1]
- [ ] [Action 2]

## Next Review

Schedule next review: [date + 30 days]
Focus areas: [based on findings]
```

## Without Analytics Data

This command works entirely with local content analysis. For traffic-based prioritization:

1. **Manual Traffic Input**: Add traffic data to frontmatter
   ```yaml
   ---
   monthly_pageviews: 5000
   monthly_clicks: 450
   ---
   ```

2. **Strategic Prioritization**: Prioritize by:
   - Business importance
   - Keyword competitiveness
   - Content freshness
   - Internal link opportunities

3. **Export/Import**: Export your analytics data to CSV and reference during review

## Example Workflow

```bash
# Run content audit
/performance-review published/

# Review the generated report
# research/performance-review-2024-12-23.md

# Act on top priorities
/analyze-existing published/low-score-article.md
/rewrite low-score-article

# Track changes
# Update the article, run analysis again
turboseo check published/low-score-article.md
```

## Best Practices

1. **Monthly Reviews**: Run at least monthly to catch issues early
2. **Track Changes**: Note what you changed and measure improvement
3. **80/20 Rule**: Focus 80% on improving existing content, 20% on new
4. **Quick Wins First**: Fix easy issues before major rewrites
5. **Document Progress**: Keep notes in the performance review file

## Integration with Other Commands

After identifying priorities:

| Finding | Next Command |
|---------|--------------|
| Low human score | `/rewrite [article]` |
| Missing SEO elements | `/optimize [article]` |
| Outdated content | `/analyze-existing [article]` then `/rewrite` |
| Content gap | `/research [topic]` then `/write` |
