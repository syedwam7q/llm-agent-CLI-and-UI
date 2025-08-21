"""
File operation tools.
"""
import os
import json
import csv
from pathlib import Path
from typing import List, Dict, Any, Optional
import aiofiles
import pypdf
from docx import Document

import sys
from pathlib import Path

# Ensure proper path setup
current_dir = Path(__file__).parent
src_dir = current_dir.parent
sys.path.insert(0, str(src_dir))
sys.path.insert(0, str(current_dir))

from base import BaseTool, ToolResult, ToolCategory, register_tool
from config import settings


@register_tool
class FileReaderTool(BaseTool):
    """Read and analyze various file formats."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.FILE_OPERATIONS
        self.description = "Read and analyze files in various formats (txt, json, csv, pdf, docx)"
    
    async def execute(self, file_path: str, max_length: int = 5000) -> ToolResult:
        """Execute file reading."""
        if not settings.enable_file_operations:
            return ToolResult(
                success=False,
                error="File operations are disabled"
            )
        
        try:
            path = Path(file_path)
            
            # Security check - ensure file is within allowed directories
            if not path.is_absolute():
                # First try uploads directory, then project root
                upload_path = settings.data_dir / "uploads" / path
                project_path = settings.project_root / path
                if upload_path.exists():
                    path = upload_path
                elif project_path.exists():
                    path = project_path
                else:
                    # Try data directory as well
                    data_path = settings.data_dir / path
                    if data_path.exists():
                        path = data_path
                    else:
                        return ToolResult(
                            success=False,
                            error=f"File not found: {file_path} (checked uploads/, data/, and project root)"
                        )
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"File not found: {file_path}"
                )
            
            # Check file size
            file_size = path.stat().st_size
            max_size = settings.max_file_size_mb * 1024 * 1024
            if file_size > max_size:
                return ToolResult(
                    success=False,
                    error=f"File too large: {file_size} bytes (max: {max_size})"
                )
            
            file_extension = path.suffix.lower()
            
            if file_extension == '.txt':
                content = await self._read_text_file(path, max_length)
            elif file_extension == '.json':
                content = await self._read_json_file(path)
            elif file_extension == '.csv':
                content = await self._read_csv_file(path)
            elif file_extension == '.pdf':
                content = await self._read_pdf_file(path, max_length)
            elif file_extension == '.docx':
                content = await self._read_docx_file(path, max_length)
            else:
                # Try to read as text
                content = await self._read_text_file(path, max_length)
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(path),
                    "file_size": file_size,
                    "file_type": file_extension,
                    "content": content
                },
                metadata={"encoding": "utf-8"}
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"File reading failed: {str(e)}"
            )
    
    async def _read_text_file(self, path: Path, max_length: int) -> str:
        """Read a text file."""
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return content[:max_length] if len(content) > max_length else content
    
    async def _read_json_file(self, path: Path) -> Dict[str, Any]:
        """Read a JSON file."""
        async with aiofiles.open(path, 'r', encoding='utf-8') as f:
            content = await f.read()
            return json.loads(content)
    
    async def _read_csv_file(self, path: Path) -> Dict[str, Any]:
        """Read a CSV file."""
        rows = []
        with open(path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for i, row in enumerate(reader):
                if i >= 100:  # Limit rows
                    break
                rows.append(row)
        
        return {
            "headers": list(rows[0].keys()) if rows else [],
            "rows": rows,
            "total_rows": len(rows)
        }
    
    async def _read_pdf_file(self, path: Path, max_length: int) -> str:
        """Read a PDF file."""
        text = ""
        with open(path, 'rb') as f:
            reader = pypdf.PdfReader(f)
            for page in reader.pages:
                text += page.extract_text() + "\n"
                if len(text) > max_length:
                    break
        
        return text[:max_length] if len(text) > max_length else text
    
    async def _read_docx_file(self, path: Path, max_length: int) -> str:
        """Read a DOCX file."""
        doc = Document(path)
        text = ""
        for paragraph in doc.paragraphs:
            text += paragraph.text + "\n"
            if len(text) > max_length:
                break
        
        return text[:max_length] if len(text) > max_length else text


@register_tool
class FileWriterTool(BaseTool):
    """Write content to files in various formats."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.FILE_OPERATIONS
        self.description = "Write content to files in various formats"
    
    async def execute(self, file_path: str, content: str, format: str = "txt") -> ToolResult:
        """Execute file writing."""
        if not settings.enable_file_operations:
            return ToolResult(
                success=False,
                error="File operations are disabled"
            )
        
        try:
            path = Path(file_path)
            
            # Security check - ensure file is within allowed directories
            if not path.is_absolute():
                path = settings.data_dir / path
            
            # Create directory if it doesn't exist
            path.parent.mkdir(parents=True, exist_ok=True)
            
            if format.lower() == "json":
                # Try to parse content as JSON
                try:
                    data = json.loads(content)
                    async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                        await f.write(json.dumps(data, indent=2))
                except json.JSONDecodeError:
                    return ToolResult(
                        success=False,
                        error="Invalid JSON content"
                    )
            else:
                # Write as text
                async with aiofiles.open(path, 'w', encoding='utf-8') as f:
                    await f.write(content)
            
            return ToolResult(
                success=True,
                data={
                    "file_path": str(path),
                    "bytes_written": len(content.encode('utf-8')),
                    "format": format
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"File writing failed: {str(e)}"
            )


@register_tool
class DirectoryListTool(BaseTool):
    """List files and directories."""
    
    def __init__(self):
        super().__init__()
        self.category = ToolCategory.FILE_OPERATIONS
        self.description = "List files and directories in a given path"
    
    async def execute(self, directory_path: str = ".", include_hidden: bool = False) -> ToolResult:
        """Execute directory listing."""
        try:
            path = Path(directory_path)
            
            if not path.is_absolute():
                path = settings.project_root / path
            
            if not path.exists():
                return ToolResult(
                    success=False,
                    error=f"Directory not found: {directory_path}"
                )
            
            if not path.is_dir():
                return ToolResult(
                    success=False,
                    error=f"Path is not a directory: {directory_path}"
                )
            
            items = []
            for item in path.iterdir():
                if not include_hidden and item.name.startswith('.'):
                    continue
                
                item_info = {
                    "name": item.name,
                    "path": str(item),
                    "type": "directory" if item.is_dir() else "file",
                    "size": item.stat().st_size if item.is_file() else None
                }
                items.append(item_info)
            
            # Sort items: directories first, then files
            items.sort(key=lambda x: (x["type"] == "file", x["name"].lower()))
            
            return ToolResult(
                success=True,
                data={
                    "directory": str(path),
                    "items": items,
                    "total_items": len(items)
                }
            )
        
        except Exception as e:
            return ToolResult(
                success=False,
                error=f"Directory listing failed: {str(e)}"
            )