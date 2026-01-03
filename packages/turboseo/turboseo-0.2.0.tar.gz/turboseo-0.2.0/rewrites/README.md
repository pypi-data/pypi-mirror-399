# Rewrites

Updated versions of existing content live here.

## When to Rewrite

Use `/analyze-existing` to assess if content needs:
- **Light update**: Fix issues, refresh stats (< 30% changed)
- **Moderate revision**: Add sections, improve SEO (30-60% changed)
- **Full rewrite**: Complete overhaul (> 60% changed)

## Naming Convention

```
{original-slug}-rewrite-{YYYY-MM-DD}.md
```

Example:
- Original: `published/podcast-tips-2024-01-15.md`
- Rewrite: `rewrites/podcast-tips-rewrite-2024-12-23.md`

## Rewrite Metadata

```markdown
---
title: "Updated Article Title"
original: published/original-file.md
original_url: /blog/original-url
rewrite_type: light | moderate | full
rewrite_date: YYYY-MM-DD
changes:
  - Updated statistics for 2024
  - Added new section on X
  - Improved human writing score from 65 to 88
---
```

## Workflow

1. Run `/analyze-existing [original]`
2. Review analysis in `research/analysis-*.md`
3. Run `/rewrite [topic]` to create new version
4. Compare with original
5. After approval, update `published/` version

## Change Tracking

Document what changed:

```markdown
## Changes Made

### Content Updates
- [Section]: Updated X to Y
- [Section]: Added new subsection on Z

### SEO Improvements
- Added keyword to H2: "..."
- Improved meta description

### Human Writing Fixes
- Replaced "delve" with "explore"
- Removed puffery in paragraph 3

### Metrics
| Metric | Before | After |
|--------|--------|-------|
| Human Score | 65 | 88 |
| Word Count | 1800 | 2400 |
```
