#!/usr/bin/env python3
"""
AI Studio Log Converter

Converts Google AI Studio exported logs into clean, human-readable Markdown format.
Parses the Python code structure to extract user prompts and model responses.
"""

import argparse
import re
import ast
from datetime import datetime
from pathlib import Path
from typing import List, Dict, Any


class AIStudioLogConverter:
    def __init__(self):
        self.conversations = []
        self.model_name = "MODEL"
    
    def parse_log_file(self, file_path: str) -> None:
        """Parse the AI Studio log file and extract conversations."""
        # Extract model name from filename
        self.model_name = self._extract_model_name_from_path(file_path)
        
        with open(file_path, 'r', encoding='utf-8') as file:
            content = file.read()
        
        # Extract the contents list from the Python code
        contents = self._extract_contents_from_code(content)
        
        if contents:
            self._parse_contents(contents)
        else:
            print("Warning: Could not find contents list in the log file")
    
    def _extract_model_name_from_path(self, file_path: str) -> str:
        """Extract a readable model name from the file path."""
        file_name = Path(file_path).stem  # Get filename without extension
        
        # Handle common naming patterns
        if file_name.lower() in ['sample_log', 'google_ai_studio_test', 'markdown_test']:
            return "MODEL"
        
        # Remove "_Test" suffix if present
        if file_name.endswith('_Test'):
            file_name = file_name[:-5]
        
        # Handle camelCase patterns first
        # e.g., "CTOAlex" -> "CTO Alex"
        import re
        name = re.sub(r'([A-Z]+)([A-Z][a-z])', r'\1 \2', file_name)
        name = re.sub(r'([a-z])([A-Z])', r'\1 \2', name)
        
        # Convert underscores to spaces and title case
        # e.g., "Coach_Martin" -> "Coach Martin"
        name = name.replace('_', ' ').title()
        
        return name
    
    def _extract_contents_from_code(self, code: str) -> List[Dict]:
        """Extract the contents list from the Python code using AST parsing."""
        try:
            # Parse the Python code
            tree = ast.parse(code)
            
            # Find the contents assignment
            for node in ast.walk(tree):
                if isinstance(node, ast.Assign):
                    for target in node.targets:
                        if isinstance(target, ast.Name) and target.id == 'contents':
                            # Convert the AST back to a Python object
                            return self._ast_to_python(node.value)
            
            # Fallback: try to find contents using regex
            return self._extract_contents_regex(code)
            
        except Exception as e:
            print(f"Error parsing with AST: {e}")
            return self._extract_contents_regex(code)
    
    def _extract_contents_regex(self, code: str) -> List[Dict]:
        """Fallback method to extract contents using regex."""
        try:
            # Find the contents list definition
            pattern = r'contents\s*=\s*\[(.*?)\]'
            match = re.search(pattern, code, re.DOTALL)
            
            if not match:
                return []
            
            contents_str = match.group(1)
            
            # Extract Content blocks
            content_pattern = r'types\.Content\(\s*role="(user|model)",\s*parts=\[(.*?)\],?\s*\)'
            content_matches = re.finditer(content_pattern, contents_str, re.DOTALL)
            
            contents = []
            for match in content_matches:
                role = match.group(1)
                parts_str = match.group(2)
                
                # Extract text parts
                text_pattern = r'types\.Part\.from_text\(text="""(.*?)"""\)'
                text_matches = re.findall(text_pattern, parts_str, re.DOTALL)
                
                if text_matches:
                    contents.append({
                        'role': role,
                        'parts': [{'text': text.strip()} for text in text_matches]
                    })
            
            return contents
            
        except Exception as e:
            print(f"Error with regex extraction: {e}")
            return []
    
    def _ast_to_python(self, node: ast.AST) -> Any:
        """Convert AST node to Python object (simplified version)."""
        if isinstance(node, ast.List):
            return [self._ast_to_python(item) for item in node.elts]
        elif isinstance(node, ast.Call):
            # Handle types.Content() calls
            if (isinstance(node.func, ast.Attribute) and 
                isinstance(node.func.value, ast.Name) and 
                node.func.value.id == 'types' and 
                node.func.attr == 'Content'):
                
                result = {}
                for keyword in node.keywords:
                    if keyword.arg == 'role':
                        result['role'] = self._ast_to_python(keyword.value)
                    elif keyword.arg == 'parts':
                        result['parts'] = self._ast_to_python(keyword.value)
                return result
            
            # Handle types.Part.from_text() calls
            elif (isinstance(node.func, ast.Attribute) and 
                  isinstance(node.func.value, ast.Attribute) and
                  isinstance(node.func.value.value, ast.Name) and
                  node.func.value.value.id == 'types' and
                  node.func.value.attr == 'Part' and
                  node.func.attr == 'from_text'):
                
                for keyword in node.keywords:
                    if keyword.arg == 'text':
                        return {'text': self._ast_to_python(keyword.value)}
                return {}
        elif isinstance(node, ast.Constant):
            return node.value
        elif isinstance(node, ast.Str):  # For older Python versions
            return node.s
        
        return None
    
    def _parse_contents(self, contents: List[Dict]) -> None:
        """Parse the extracted contents and organize into conversations."""
        for content in contents:
            if content is None:
                continue
                
            role = content.get('role', '')
            parts = content.get('parts', [])
            
            # Skip if it's the INSERT_INPUT_HERE placeholder
            if any('INSERT_INPUT_HERE' in part.get('text', '') for part in parts if part is not None):
                continue
            
            # Combine all text parts
            text_parts = []
            for part in parts:
                if part is not None and 'text' in part:
                    text = part['text'].strip()
                    if text:
                        text_parts.append(text)
            
            if text_parts:
                combined_text = '\n\n'.join(text_parts)
                
                # Filter out thinking parts (text starting with **)
                if role == 'model':
                    combined_text = self._filter_thinking_parts(combined_text)
                
                if combined_text.strip():
                    self.conversations.append({
                        'role': role,
                        'content': combined_text.strip()
                    })
    
    def _filter_thinking_parts(self, text: str) -> str:
        """Filter out thinking parts from model responses while preserving Markdown formatting."""
        # Split text into paragraphs
        paragraphs = text.split('\n\n')
        filtered_paragraphs = []
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            
            # Skip empty paragraphs
            if not paragraph:
                continue
            
            lines = paragraph.split('\n')
            first_line = lines[0].strip()
            
            # Check if it's a thinking block header (starts and ends with ** on the same line)
            # This is different from Markdown bold which would be **text** within content
            if (first_line.startswith('**') and first_line.endswith('**') and 
                len(first_line) > 4 and first_line.count('**') == 2):
                continue
            
            # Check if it contains AI thinking-like content patterns
            # These are specific to AI reasoning, not normal Markdown content
            thinking_patterns = [
                "I began by searching",
                "I've moved on to",
                "I've been examining", 
                "I've determined",
                "I confirm the test",
                "Analyzing the results",
                "My focus is on",
                "I'm now honing in",
                "I'm focusing on",
                "I'm carefully sifting",
                "I'm aiming to",
                "I'm currently assessing",
                "I need to understand",
                "I need to search"
            ]
            
            # Only filter if it's clearly AI thinking, not just content with Markdown
            is_thinking = any(pattern in paragraph for pattern in thinking_patterns)
            if is_thinking:
                continue
                
            filtered_paragraphs.append(paragraph)
        
        return '\n\n'.join(filtered_paragraphs).strip()
    
    def write_markdown(self, output_path: str) -> None:
        """Write the conversations to a Markdown file."""
        output_file = Path(output_path)
        output_file.parent.mkdir(parents=True, exist_ok=True)
        
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write("# AI Studio Chat History\n\n")
            
            for i, conv in enumerate(self.conversations):
                if conv['role'] == 'user':
                    file.write(f"---\n**USER:**\n")
                    file.write(f"{conv['content']}\n\n")
                elif conv['role'] == 'model':
                    file.write(f"---\n**{self.model_name.upper()}:**\n")
                    file.write(f"{conv['content']}\n\n")
        
        print(f"Successfully converted {len(self.conversations)} conversation turns to {output_path}")


def main():
    parser = argparse.ArgumentParser(
        description="Convert Google AI Studio logs to clean Markdown format"
    )
    parser.add_argument(
        "input_file", 
        help="Path to the input log file"
    )
    parser.add_argument(
        "output_file", 
        help="Path for the output Markdown file"
    )
    
    args = parser.parse_args()
    
    # Validate input file exists
    if not Path(args.input_file).exists():
        print(f"Error: Input file '{args.input_file}' does not exist")
        return 1
    
    try:
        converter = AIStudioLogConverter()
        converter.parse_log_file(args.input_file)
        converter.write_markdown(args.output_file)
        return 0
    except Exception as e:
        print(f"Error converting file: {e}")
        return 1


if __name__ == "__main__":
    exit(main())
