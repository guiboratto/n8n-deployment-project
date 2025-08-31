#!/usr/bin/env python3
"""
File Reader Module
==================

Handles reading and processing of various file types including:
- Python scripts (.py)
- Markdown files (.md)
- Configuration files (.yaml, .json)
- Text files (.txt)

Features:
- Metadata extraction
- Content validation
- Encoding detection
- Error handling
"""

import os
import sys
import logging
import mimetypes
import chardet
from pathlib import Path
from typing import Dict, List, Optional, Union
import yaml
import json

class FileReader:
    """File reading and processing utility"""
    
    def __init__(self, config: Dict):
        """Initialize file reader with configuration"""
        self.config = config
        self.logger = logging.getLogger(__name__)
        
        # Supported file types
        self.supported_extensions = {
            '.py': 'python',
            '.md': 'markdown',
            '.txt': 'text',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.json': 'json',
            '.sh': 'shell',
            '.conf': 'config',
            '.cfg': 'config'
        }
    
    def detect_encoding(self, file_path: str) -> str:
        """Detect file encoding"""
        try:
            with open(file_path, 'rb') as file:
                raw_data = file.read()
                result = chardet.detect(raw_data)
                return result['encoding'] or 'utf-8'
        except Exception as e:
            self.logger.warning(f"Could not detect encoding for {file_path}: {e}")
            return 'utf-8'
    
    def get_file_metadata(self, file_path: str) -> Dict:
        """Extract file metadata"""
        try:
            path_obj = Path(file_path)
            stat = path_obj.stat()
            
            metadata = {
                'name': path_obj.name,
                'extension': path_obj.suffix,
                'size': stat.st_size,
                'created': stat.st_ctime,
                'modified': stat.st_mtime,
                'is_executable': os.access(file_path, os.X_OK),
                'mime_type': mimetypes.guess_type(file_path)[0],
                'encoding': self.detect_encoding(file_path)
            }
            
            # Determine file type
            metadata['file_type'] = self.supported_extensions.get(
                path_obj.suffix.lower(), 'unknown'
            )
            
            return metadata
            
        except Exception as e:
            self.logger.error(f"Error getting metadata for {file_path}: {e}")
            return {}
    
    def read_text_file(self, file_path: str, encoding: str = None) -> str:
        """Read a text file with proper encoding"""
        if not encoding:
            encoding = self.detect_encoding(file_path)
        
        try:
            with open(file_path, 'r', encoding=encoding) as file:
                return file.read()
        except UnicodeDecodeError:
            # Fallback to utf-8 with error handling
            try:
                with open(file_path, 'r', encoding='utf-8', errors='replace') as file:
                    return file.read()
            except Exception as e:
                self.logger.error(f"Could not read {file_path}: {e}")
                return ""
        except Exception as e:
            self.logger.error(f"Error reading {file_path}: {e}")
            return ""
    
    def parse_python_file(self, content: str) -> Dict:
        """Parse Python file and extract information"""
        info = {
            'docstring': None,
            'imports': [],
            'functions': [],
            'classes': [],
            'variables': [],
            'line_count': len(content.splitlines())
        }
        
        lines = content.splitlines()
        
        # Extract docstring (first triple-quoted string)
        in_docstring = False
        docstring_lines = []
        quote_type = None
        
        for line in lines:
            stripped = line.strip()
            
            if not in_docstring:
                if stripped.startswith('"""') or stripped.startswith("'''"):
                    quote_type = stripped[:3]
                    in_docstring = True
                    docstring_lines.append(stripped[3:])
                    if stripped.endswith(quote_type) and len(stripped) > 6:
                        # Single line docstring
                        info['docstring'] = stripped[3:-3].strip()
                        break
                elif stripped.startswith('import ') or stripped.startswith('from '):
                    info['imports'].append(stripped)
                elif stripped.startswith('def '):
                    func_name = stripped.split('(')[0].replace('def ', '').strip()
                    info['functions'].append(func_name)
                elif stripped.startswith('class '):
                    class_name = stripped.split('(')[0].replace('class ', '').strip(':')
                    info['classes'].append(class_name)
            else:
                if stripped.endswith(quote_type):
                    docstring_lines.append(stripped[:-3])
                    info['docstring'] = '\n'.join(docstring_lines).strip()
                    break
                else:
                    docstring_lines.append(line)
        
        return info
    
    def parse_markdown_file(self, content: str) -> Dict:
        """Parse Markdown file and extract structure"""
        info = {
            'title': None,
            'headings': [],
            'links': [],
            'images': [],
            'code_blocks': [],
            'line_count': len(content.splitlines())
        }
        
        lines = content.splitlines()
        in_code_block = False
        
        for line in lines:
            stripped = line.strip()
            
            # Extract title (first # heading)
            if stripped.startswith('# ') and not info['title']:
                info['title'] = stripped[2:].strip()
            
            # Extract all headings
            if stripped.startswith('#'):
                level = len(stripped) - len(stripped.lstrip('#'))
                heading_text = stripped.lstrip('#').strip()
                info['headings'].append({
                    'level': level,
                    'text': heading_text
                })
            
            # Extract links
            if '[' in stripped and '](' in stripped:
                # Simple regex-like extraction
                start = stripped.find('[')
                while start != -1:
                    end = stripped.find('](', start)
                    if end != -1:
                        link_end = stripped.find(')', end)
                        if link_end != -1:
                            link_text = stripped[start+1:end]
                            link_url = stripped[end+2:link_end]
                            info['links'].append({
                                'text': link_text,
                                'url': link_url
                            })
                    start = stripped.find('[', start + 1)
            
            # Extract code blocks
            if stripped.startswith('```'):
                if not in_code_block:
                    in_code_block = True
                    language = stripped[3:].strip()
                    info['code_blocks'].append({
                        'language': language,
                        'content': []
                    })
                else:
                    in_code_block = False
            elif in_code_block and info['code_blocks']:
                info['code_blocks'][-1]['content'].append(line)
        
        return info
    
    def parse_yaml_file(self, content: str) -> Dict:
        """Parse YAML file"""
        try:
            data = yaml.safe_load(content)
            return {
                'valid': True,
                'data': data,
                'keys': list(data.keys()) if isinstance(data, dict) else [],
                'type': type(data).__name__
            }
        except yaml.YAMLError as e:
            return {
                'valid': False,
                'error': str(e),
                'data': None
            }
    
    def parse_json_file(self, content: str) -> Dict:
        """Parse JSON file"""
        try:
            data = json.loads(content)
            return {
                'valid': True,
                'data': data,
                'keys': list(data.keys()) if isinstance(data, dict) else [],
                'type': type(data).__name__
            }
        except json.JSONDecodeError as e:
            return {
                'valid': False,
                'error': str(e),
                'data': None
            }
    
    def read_file(self, file_path: str) -> Dict:
        """Read and process a file"""
        if not os.path.exists(file_path):
            self.logger.warning(f"File not found: {file_path}")
            return {}
        
        # Get file metadata
        metadata = self.get_file_metadata(file_path)
        
        # Read file content
        content = self.read_text_file(file_path, metadata.get('encoding'))
        
        if not content:
            return {
                'metadata': metadata,
                'content': '',
                'parsed': {}
            }
        
        # Parse content based on file type
        parsed_info = {}
        file_type = metadata.get('file_type', 'unknown')
        
        if file_type == 'python':
            parsed_info = self.parse_python_file(content)
        elif file_type == 'markdown':
            parsed_info = self.parse_markdown_file(content)
        elif file_type == 'yaml':
            parsed_info = self.parse_yaml_file(content)
        elif file_type == 'json':
            parsed_info = self.parse_json_file(content)
        
        result = {
            'metadata': metadata,
            'content': content,
            'parsed': parsed_info
        }
        
        self.logger.info(f"Successfully processed {file_path} ({file_type})")
        return result
    
    def read_multiple_files(self, file_paths: List[str]) -> Dict[str, Dict]:
        """Read multiple files and return results"""
        results = {}
        
        for file_path in file_paths:
            try:
                result = self.read_file(file_path)
                if result:
                    results[file_path] = result
            except Exception as e:
                self.logger.error(f"Error processing {file_path}: {e}")
                results[file_path] = {
                    'error': str(e),
                    'metadata': {},
                    'content': '',
                    'parsed': {}
                }
        
        return results
    
    def find_files_by_pattern(self, pattern: str, directory: str = '.') -> List[str]:
        """Find files matching a pattern"""
        from pathlib import Path
        
        path_obj = Path(directory)
        files = []
        
        try:
            for file_path in path_obj.rglob(pattern):
                if file_path.is_file():
                    files.append(str(file_path))
        except Exception as e:
            self.logger.error(f"Error finding files with pattern {pattern}: {e}")
        
        return files
    
    def get_project_files(self, directory: str = '.') -> Dict[str, List[str]]:
        """Get all project files organized by type"""
        files_by_type = {
            'python': [],
            'markdown': [],
            'config': [],
            'text': [],
            'other': []
        }
        
        for ext, file_type in self.supported_extensions.items():
            pattern = f"*{ext}"
            found_files = self.find_files_by_pattern(pattern, directory)
            
            if file_type in files_by_type:
                files_by_type[file_type].extend(found_files)
            else:
                files_by_type['other'].extend(found_files)
        
        return files_by_type

# Example usage and testing
if __name__ == "__main__":
    # Test the file reader
    config = {'logging': {'level': 'INFO'}}
    reader = FileReader(config)
    
    # Test reading current file
    result = reader.read_file(__file__)
    print(f"Read file: {__file__}")
    print(f"File type: {result['metadata']['file_type']}")
    print(f"Size: {result['metadata']['size']} bytes")
    print(f"Functions found: {result['parsed'].get('functions', [])}")