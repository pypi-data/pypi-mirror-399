# Drafts

Work-in-progress articles live here.

## Naming Convention

```
{topic-slug}-{YYYY-MM-DD}.md
```

Examples:
- `podcast-monetization-guide-2024-12-23.md`
- `best-interview-tips-2024-12-20.md`

## Draft Status

Track status in the frontmatter:

```markdown
---
title: "Article Title"
status: draft | review | ready
keyword: "primary keyword"
created: YYYY-MM-DD
updated: YYYY-MM-DD
---
```

## Quality Checklist

Before moving to `published/`:

### Human Writing
- [ ] Human score 80+
- [ ] No AI vocabulary flagged
- [ ] No puffery patterns

### SEO
- [ ] Keyword in H1
- [ ] Keyword in first 100 words
- [ ] Keyword in 2-3 H2s
- [ ] Keyword in conclusion
- [ ] 1-2% keyword density

### Content
- [ ] 2000+ words
- [ ] 4+ H2 sections
- [ ] Specific examples included
- [ ] Sources cited

### Meta
- [ ] Title 50-60 characters
- [ ] Description 150-160 characters

## Workflow

1. `/write [topic]` creates draft here
2. Run `/optimize [draft]` for final check
3. Make edits based on feedback
4. Move to `published/` when ready
