# Obsidian to HTML Converter

A Python script that converts Obsidian markdown files to HTML while preserving directory structure and handling Obsidian-specific features.

## Features

- **Directory Structure Preservation**: Maintains the exact same folder structure from input to output
- **Obsidian Feature Support**:
  - Converts internal links (`[[note]]`, `[[note|display text]]`) to plaintext
  - Converts tags (`#tag`) to plaintext
  - Renders callouts (`> [!note]` blocks) as HTML
  - Removes YAML frontmatter
  - Ignores images
- **Non-Markdown Files**: Copies non-markdown files as-is to the output directory
- **No Styling**: Generates clean, semantic HTML without CSS styling

## Installation

1. Install the required dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration

The script reads configuration from `obs-blog.yaml`:

```yaml
input: ~/MEGA/Obsidian/Zettelkasten/Blog
output: site
```

- `input`: Path to your Obsidian vault or blog directory
- `output`: Path where HTML files will be generated

## Usage

Run the converter:

```bash
python converter.py
```

The script will:
1. Read the configuration from `obs-blog.yaml`
2. Scan the input directory recursively
3. Convert all `.md` files to `.html` files
4. Copy non-markdown files as-is
5. Preserve the directory structure in the output

## Example

If you have:
```
~/MEGA/Obsidian/Zettelkasten/Blog/
├── post1.md
├── images/
│   └── image.png
└── subfolder/
    └── post2.md
```

The output will be:
```
site/
├── post1.html
├── images/
│   └── image.png
└── subfolder/
    └── post2.html
```

## Obsidian Features Handled

- **Internal Links**: `[[note]]` → `note`, `[[note|display]]` → `display`
- **Tags**: `#tag` → `tag`
- **Callouts**: `> [!note] Title\n> Content` → HTML callout structure
- **Frontmatter**: YAML metadata at the top of files is removed
- **Code Blocks**: Standard markdown code blocks are preserved
- **Images**: Image references are ignored (not converted to HTML)

## Requirements

- Python 3.6+
- `markdown` library
- `PyYAML` library
