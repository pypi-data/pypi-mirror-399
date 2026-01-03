# Templates

Template files for setting up your TurboSEO workspace.

## Usage

Copy these templates to your `context/` directory and fill them out:

```bash
cp templates/brand-voice.md context/brand-voice.md
cp templates/style-guide.md context/style-guide.md
cp templates/internal-links-map.md context/internal-links-map.md
cp templates/seo-guidelines.md context/seo-guidelines.md
```

Then edit each file with your specific information.

## Templates

| Template | Purpose |
|----------|---------|
| `brand-voice.md` | Define your brand's voice and tone |
| `style-guide.md` | Editorial and formatting standards |
| `internal-links-map.md` | Key pages for internal linking |
| `seo-guidelines.md` | SEO requirements and targets |

## Why Context Files?

When you run commands like `/write` or `/research`, Claude reads these context files to:
- Match your brand voice
- Follow your style conventions
- Include relevant internal links
- Meet your SEO requirements

Better context files = better content output.
