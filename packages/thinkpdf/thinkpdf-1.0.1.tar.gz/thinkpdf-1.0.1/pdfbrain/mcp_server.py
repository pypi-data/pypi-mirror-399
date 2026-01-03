"""
thinkpdf MCP Server v2 - Production-ready MCP server for IDE integration.

Uses Docling (IBM) for maximum quality PDF to Markdown conversion.

Tools:
- convert_pdf: Convert PDF/DOCX/PPTX to Markdown
- read_pdf: Convert and return content directly (best for IAs)
- get_document_info: Get metadata about a document
"""

from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any, Dict, Optional

from .engine import thinkpdfEngine, HAS_DOCLING, HAS_PDFMD


class thinkpdfMCPServer:
    """
    MCP Server for thinkpdf v2.
    
    Allows Cursor, Antigravity, and other MCP-compatible tools to
    convert and read PDFs directly.
    """
    
    def __init__(self):
        self.engine = thinkpdfEngine()
    
    def handle_request(self, request: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Handle an incoming MCP request."""
        method = request.get("method", "")
        params = request.get("params", {})
        request_id = request.get("id")
        
        # Notifications (no id) don't get responses
        is_notification = request_id is None
        
        try:
            if method == "initialize":
                result = self._handle_initialize(params)
            elif method == "initialized":
                # This is a notification, no response needed
                return None
            elif method == "notifications/initialized":
                # This is a notification, no response needed
                return None
            elif method == "tools/list":
                result = self._handle_list_tools()
            elif method == "tools/call":
                result = self._handle_tool_call(params)
            elif method == "ping":
                result = {}
            elif method == "resources/list":
                result = {"resources": []}
            elif method == "prompts/list":
                result = {"prompts": []}
            else:
                if is_notification:
                    return None
                return self._error_response(request_id, -32601, f"Method not found: {method}")
            
            # Notifications don't get responses
            if is_notification:
                return None
            
            return {
                "jsonrpc": "2.0",
                "id": request_id,
                "result": result,
            }
            
        except Exception as e:
            if is_notification:
                return None
            return self._error_response(request_id, -32603, str(e))
    
    def _handle_initialize(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle initialization request."""
        engine_info = "Docling (IBM)" if HAS_DOCLING else "pdfmd"
        
        return {
            "protocolVersion": "2024-11-05",
            "capabilities": {
                "tools": {},
            },
            "serverInfo": {
                "name": "thinkpdf",
                "version": "2.0.0",
                "description": f"PDF to Markdown converter powered by {engine_info}",
            },
        }
    
    def _handle_list_tools(self) -> Dict[str, Any]:
        """Return list of available tools."""
        return {
            "tools": [
                {
                    "name": "read_pdf",
                    "description": "Read a PDF file and return its content as Markdown. Best for reading documents in chat.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Absolute path to the PDF file",
                            },
                            "engine": {
                                "type": "string",
                                "description": "Conversion engine: 'auto' (default), 'docling' (high quality, slow), or 'pdfmd' (fast)",
                                "enum": ["auto", "docling", "pdfmd"],
                            },
                        },
                        "required": ["path"],
                    },
                },
                {
                    "name": "convert_pdf",
                    "description": "Convert a PDF file to Markdown and save to disk.",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Absolute path to the PDF file",
                            },
                            "output": {
                                "type": "string",
                                "description": "Output path for markdown file (optional)",
                            },
                            "engine": {
                                "type": "string",
                                "description": "Conversion engine: 'auto' (default), 'docling' (high quality, slow), or 'pdfmd' (fast)",
                                "enum": ["auto", "docling", "pdfmd"],
                            },
                        },
                        "required": ["path"],
                    },
                },
                {
                    "name": "get_document_info",
                    "description": "Get information about a document (page count, size, etc.)",
                    "inputSchema": {
                        "type": "object",
                        "properties": {
                            "path": {
                                "type": "string",
                                "description": "Absolute path to the document",
                            },
                        },
                        "required": ["path"],
                    },
                },
            ],
        }
    
    def _handle_tool_call(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle a tool call."""
        tool_name = params.get("name", "")
        arguments = params.get("arguments", {})
        
        if tool_name == "read_pdf":
            return self._tool_read_pdf(arguments)
        elif tool_name == "convert_pdf":
            return self._tool_convert_pdf(arguments)
        elif tool_name == "get_document_info":
            return self._tool_get_document_info(arguments)
        else:
            raise ValueError(f"Unknown tool: {tool_name}")
    
    def _tool_read_pdf(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Read a PDF and return content as markdown."""
        path = args.get("path")
        engine_choice = args.get("engine", "auto")
        if not path:
            raise ValueError("path is required")
        
        pdf_path = Path(path)
        if not pdf_path.exists():
            raise ValueError(f"File not found: {path}")
        
        # Convert using engine
        # We need to re-instantiate engine if a specific one is requested different from default
        # Or just pass it if convert accepted it. convert() doesn't take engine arg, engine is set on init.
        # So we create a temporary engine instance with the requested type.
        
        temp_engine = thinkpdfEngine(engine=engine_choice)
        markdown = temp_engine.convert(pdf_path)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"# Content from: {pdf_path.name}\n\n{markdown}",
                },
            ],
            "isError": False,
        }
    
    def _tool_convert_pdf(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Convert PDF to markdown file."""
        path = args.get("path")
        engine_choice = args.get("engine", "auto")
        if not path:
            raise ValueError("path is required")
        
        pdf_path = Path(path)
        if not pdf_path.exists():
            raise ValueError(f"File not found: {path}")
        
        # Determine output path
        output = args.get("output")
        if output:
            output_path = Path(output)
        else:
            output_path = pdf_path.with_suffix(".md")
        
        # Convert
        temp_engine = thinkpdfEngine(engine=engine_choice)
        markdown = temp_engine.convert(pdf_path, output_path)
        word_count = len(markdown.split())
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": f"Converted {pdf_path.name} to {output_path.name}\n"
                            f"Words: {word_count}\n"
                            f"Output: {output_path}",
                },
            ],
            "isError": False,
        }
    
    def _tool_get_document_info(self, args: Dict[str, Any]) -> Dict[str, Any]:
        """Get document information."""
        path = args.get("path")
        if not path:
            raise ValueError("path is required")
        
        doc_path = Path(path)
        if not doc_path.exists():
            raise ValueError(f"File not found: {path}")
        
        info = self.engine.get_document_info(doc_path)
        
        return {
            "content": [
                {
                    "type": "text",
                    "text": json.dumps(info, indent=2),
                },
            ],
            "isError": False,
        }
    
    def _error_response(self, request_id: Any, code: int, message: str) -> Dict[str, Any]:
        """Create an error response."""
        return {
            "jsonrpc": "2.0",
            "id": request_id,
            "error": {
                "code": code,
                "message": message,
            },
        }
    
    def run_stdio(self):
        """Run the server on stdio."""
        import io
        
        # Redirect stderr to avoid polluting stdout
        sys.stderr = io.StringIO()
        
        # Set stdout to binary mode for clean output
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', newline='\n')
        
        while True:
            try:
                line = sys.stdin.readline()
                if not line:
                    break
                
                line = line.strip()
                if not line:
                    continue
                
                request = json.loads(line)
                response = self.handle_request(request)
                
                # Only send response if there is one (notifications return None)
                if response is not None:
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                
            except json.JSONDecodeError:
                continue
            except KeyboardInterrupt:
                break
            except Exception:
                # Silently ignore errors to avoid corrupting protocol
                continue


def main():
    """Entry point for MCP server."""
    server = thinkpdfMCPServer()
    server.run_stdio()


if __name__ == "__main__":
    main()
