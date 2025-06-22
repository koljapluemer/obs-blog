#!/usr/bin/env python3
"""
Obsidian to HTML Converter

This script reads Obsidian markdown files from the input directory specified in obs-blog.yaml
and converts them to HTML files in the output directory, preserving the directory structure.
"""

import os
import re
import yaml
import shutil
from pathlib import Path
from typing import List, Tuple
import markdown
from markdown.extensions import codehilite, fenced_code


class ObsidianConverter:
    def __init__(self, config_file: str = "obs-blog.yaml"):
        """Initialize the converter with configuration from YAML file."""
        self.config = self._load_config(config_file)
        self.input_path = Path(self.config['input']).expanduser()
        self.output_path = Path(self.config['output'])
        
        # Initialize markdown converter with extensions
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.tables',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br'
            ]
        )
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{config_file}' not found")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
    def _process_obsidian_content(self, content: str) -> str:
        """Process Obsidian-specific markdown features."""
        # Remove frontmatter (YAML metadata at the top)
        content = self._remove_frontmatter(content)
        
        # Convert internal links to plaintext
        content = self._convert_internal_links(content)
        
        # Convert tags to plaintext
        content = self._convert_tags(content)
        
        # Process callouts
        content = self._process_callouts(content)
        
        return content
    
    def _remove_frontmatter(self, content: str) -> str:
        """Remove YAML frontmatter from the beginning of the file."""
        # Pattern to match YAML frontmatter between --- markers
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        if match:
            return content[match.end():]
        return content
    
    def _convert_internal_links(self, content: str) -> str:
        """Convert Obsidian internal links to plaintext."""
        # Convert [[link]] to link
        content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
        
        # Convert [[link|display text]] to display text
        content = re.sub(r'\[\[([^|]+)\|([^\]]+)\]\]', r'\2', content)
        
        # Convert regular markdown links to plaintext
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        return content
    
    def _convert_tags(self, content: str) -> str:
        """Convert Obsidian tags to plaintext."""
        # Convert #tag to tag
        content = re.sub(r'(?<!\w)#(\w+)', r'\1', content)
        
        return content
    
    def _process_callouts(self, content: str) -> str:
        """Process Obsidian callouts and convert them to HTML."""
        # Pattern to match callouts: > [!type] title\n> content
        callout_pattern = r'>\s*\[!(\w+)\]\s*(.*?)\n((?:>.*?\n)*)'
        
        def replace_callout(match):
            callout_type = match.group(1).lower()
            title = match.group(2).strip()
            content_lines = match.group(3).strip().split('\n')
            
            # Remove the '> ' prefix from each line
            content_text = '\n'.join([line[2:] if line.startswith('> ') else line for line in content_lines])
            
            # Convert the content to HTML
            content_html = self.md.convert(content_text)
            
            # Create callout HTML structure
            callout_html = f'<div class="callout callout-{callout_type}">'
            if title:
                callout_html += f'<div class="callout-title">{title}</div>'
            callout_html += f'<div class="callout-content">{content_html}</div>'
            callout_html += '</div>'
            
            return callout_html
        
        return re.sub(callout_pattern, replace_callout, content, flags=re.MULTILINE | re.DOTALL)
    
    def _convert_markdown_to_html(self, content: str) -> str:
        """Convert markdown content to HTML."""
        # Process Obsidian-specific features first
        processed_content = self._process_obsidian_content(content)
        
        # Convert to HTML
        html_content = self.md.convert(processed_content)
        
        # Reset the markdown converter for next use
        self.md.reset()
        
        return html_content
    
    def _create_html_document(self, html_content: str, title: str = "") -> str:
        """Wrap HTML content in a complete HTML document."""
        if not title:
            title = "Document"
        
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
</head>
<body>
{html_content}
</body>
</html>"""
    
    def _get_relative_path(self, file_path: Path) -> Path:
        """Get the relative path from input directory."""
        try:
            return file_path.relative_to(self.input_path)
        except ValueError:
            return file_path
    
    def convert_file(self, input_file: Path) -> None:
        """Convert a single markdown file to HTML."""
        try:
            # Read the markdown content
            with open(input_file, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Convert to HTML
            html_content = self._convert_markdown_to_html(content)
            
            # Create output file path
            relative_path = self._get_relative_path(input_file)
            output_file = self.output_path / relative_path.with_suffix('.html')
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create HTML document with title
            title = input_file.stem
            full_html = self._create_html_document(html_content, title)
            
            # Write HTML file
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(full_html)
            
            print(f"Converted: {input_file} -> {output_file}")
            
        except Exception as e:
            print(f"Error converting {input_file}: {e}")
    
    def copy_non_markdown_file(self, input_file: Path) -> None:
        """Copy non-markdown files as-is to the output directory."""
        try:
            relative_path = self._get_relative_path(input_file)
            output_file = self.output_path / relative_path
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Copy the file
            shutil.copy2(input_file, output_file)
            print(f"Copied: {input_file} -> {output_file}")
            
        except Exception as e:
            print(f"Error copying {input_file}: {e}")
    
    def convert_directory(self) -> None:
        """Convert all files in the input directory."""
        if not self.input_path.exists():
            raise FileNotFoundError(f"Input directory '{self.input_path}' does not exist")
        
        # Create output directory if it doesn't exist
        self.output_path.mkdir(parents=True, exist_ok=True)
        
        # Walk through all files in the input directory
        for root, dirs, files in os.walk(self.input_path):
            root_path = Path(root)
            
            for file in files:
                file_path = root_path / file
                
                # Convert markdown files
                if file_path.suffix.lower() == '.md':
                    self.convert_file(file_path)
                else:
                    # Copy non-markdown files as-is
                    self.copy_non_markdown_file(file_path)
        
        print(f"\nConversion complete! Output directory: {self.output_path}")


def main():
    """Main function to run the converter."""
    try:
        converter = ObsidianConverter()
        converter.convert_directory()
    except Exception as e:
        print(f"Error: {e}")
        return 1
    
    return 0


if __name__ == "__main__":
    exit(main())
