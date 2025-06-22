#!/usr/bin/env python3
"""
Obsidian to HTML Converter

This script reads Obsidian markdown files from the input directory specified in obs-blog.yaml
and converts them to HTML files in the output directory, preserving the directory structure.
"""

import os
import yaml
import shutil
from pathlib import Path
from utils.convert_markdown import MarkdownConverter


class ObsidianConverter:
    def __init__(self, config_file: str = "obs-blog.yaml"):
        """Initialize the converter with configuration from YAML file."""
        self.config = self._load_config(config_file)
        self.input_path = Path(self.config['input']).expanduser()
        self.output_path = Path(self.config['output'])
        
        # Initialize markdown converter
        self.markdown_converter = MarkdownConverter()
    
    def _load_config(self, config_file: str) -> dict:
        """Load configuration from YAML file."""
        try:
            with open(config_file, 'r') as f:
                return yaml.safe_load(f)
        except FileNotFoundError:
            raise FileNotFoundError(f"Configuration file '{config_file}' not found")
        except yaml.YAMLError as e:
            raise ValueError(f"Error parsing YAML configuration: {e}")
    
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
            
            # Convert to HTML using the markdown converter
            html_content = self.markdown_converter.convert_obsidian_to_html(content)
            
            # Create output file path
            relative_path = self._get_relative_path(input_file)
            output_file = self.output_path / relative_path.with_suffix('.html')
            
            # Ensure output directory exists
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Create HTML document with title
            title = input_file.stem
            full_html = self.markdown_converter.create_html_document(html_content, title)
            
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
