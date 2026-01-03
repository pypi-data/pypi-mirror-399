# Published

Final versions of content ready for publication.

## Naming Convention

```
{topic-slug}-{YYYY-MM-DD}.md
```

Keep the same name as the draft for traceability.

## Required Metadata

All published content should have:

```markdown
---
title: "Article Title"
meta_title: "SEO Title | Brand"
meta_description: "150-160 character description"
keyword: "primary keyword"
published: YYYY-MM-DD
url: /blog/article-slug
---
```

## Quality Standards

All content here must meet:

| Metric | Requirement |
|--------|-------------|
| Human Score | 80+ |
| SEO Score | 75+ |
| Word Count | 2000+ |
| Readability | Grade 8-10 |

## Post-Publication

After publishing:
1. Add URL to metadata
2. Update `context/internal-links-map.md`
3. Note any content to update with links to this piece

## Updating Published Content

When updating:
1. Use `/analyze-existing [file]` to assess
2. Create new version in `rewrites/`
3. After approval, update this file
4. Note update date in metadata
