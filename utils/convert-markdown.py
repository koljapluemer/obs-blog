#!/usr/bin/env python3
"""
Markdown conversion utilities for Obsidian to HTML conversion.

This module handles the conversion of Obsidian-specific markdown features
to HTML, including callouts, internal links, tags, and frontmatter removal.
"""

import re
import markdown
from typing import Optional


class MarkdownConverter:
    """Handles conversion of Obsidian markdown to HTML."""
    
    def __init__(self):
        """Initialize the markdown converter with extensions."""
        self.md = markdown.Markdown(
            extensions=[
                'markdown.extensions.fenced_code',
                'markdown.extensions.codehilite',
                'markdown.extensions.tables',
                'markdown.extensions.toc',
                'markdown.extensions.nl2br'
            ]
        )
    
    def convert_obsidian_to_html(self, content: str) -> str:
        """
        Convert Obsidian markdown content to HTML.
        
        Args:
            content: Raw markdown content from Obsidian
            
        Returns:
            HTML string with Obsidian features processed
        """
        # Process Obsidian-specific features first
        processed_content = self._process_obsidian_content(content)
        
        # Convert to HTML
        html_content = self.md.convert(processed_content)
        
        # Reset the markdown converter for next use
        self.md.reset()
        
        return html_content
    
    def _process_obsidian_content(self, content: str) -> str:
        """
        Process Obsidian-specific markdown features.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Processed markdown content with Obsidian features converted
        """
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
        """
        Remove YAML frontmatter from the beginning of the file.
        
        Args:
            content: Raw markdown content
            
        Returns:
            Content with frontmatter removed
        """
        # Pattern to match YAML frontmatter between --- markers
        frontmatter_pattern = r'^---\s*\n(.*?)\n---\s*\n'
        match = re.match(frontmatter_pattern, content, re.DOTALL)
        if match:
            return content[match.end():]
        return content
    
    def _convert_internal_links(self, content: str) -> str:
        """
        Convert Obsidian internal links to plaintext.
        
        Args:
            content: Markdown content with internal links
            
        Returns:
            Content with internal links converted to plaintext
        """
        # Convert [[link]] to link
        content = re.sub(r'\[\[([^\]]+)\]\]', r'\1', content)
        
        # Convert [[link|display text]] to display text
        content = re.sub(r'\[\[([^|]+)\|([^\]]+)\]\]', r'\2', content)
        
        # Convert regular markdown links to plaintext
        content = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', content)
        
        return content
    
    def _convert_tags(self, content: str) -> str:
        """
        Convert Obsidian tags to plaintext.
        
        Args:
            content: Markdown content with tags
            
        Returns:
            Content with tags converted to plaintext
        """
        # Convert #tag to tag
        content = re.sub(r'(?<!\w)#(\w+)', r'\1', content)
        
        return content
    
    def _process_callouts(self, content: str) -> str:
        """
        Process Obsidian callouts and convert them to HTML.
        
        Args:
            content: Markdown content with callouts
            
        Returns:
            Content with callouts converted to HTML
        """
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
    
    def create_html_document(self, html_content: str, title: str = "") -> str:
        """
        Wrap HTML content in a complete HTML document.
        
        Args:
            html_content: The main HTML content
            title: Page title (optional)
            
        Returns:
            Complete HTML document
        """
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


def convert_markdown_to_html(content: str, title: Optional[str] = None) -> str:
    """
    Convenience function to convert markdown to HTML.
    
    Args:
        content: Raw markdown content
        title: Optional page title
        
    Returns:
        Complete HTML document
    """
    converter = MarkdownConverter()
    html_content = converter.convert_obsidian_to_html(content)
    return converter.create_html_document(html_content, title or "Document") 