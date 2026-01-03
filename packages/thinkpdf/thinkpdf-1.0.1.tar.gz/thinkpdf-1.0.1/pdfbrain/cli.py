"""
thinkpdf CLI Pro - Uses the full pdfmd pipeline for best quality conversion.

This CLI uses the advanced modules from pdfmd for:
- Table detection and reconstruction
- Equation/LaTeX detection
- Header/footer removal
- Smart paragraph merging
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import List, Optional

# Use the pdfmd pipeline
from .core.pipeline import pdf_to_markdown
from .core.models import Options
from .cache.cache_manager import CacheManager


def create_parser() -> argparse.ArgumentParser:
    """Create the argument parser."""
    parser = argparse.ArgumentParser(
        prog="thinkpdf",
        description="thinkpdf Pro - The Ultimate PDF to Markdown Converter",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  thinkpdf document.pdf                    # Convert single file
  thinkpdf document.pdf -o output.md       # Specify output path
  thinkpdf folder/ --batch                 # Convert all PDFs in folder
        """,
    )
    
    parser.add_argument(
        "input",
        help="PDF file or folder to convert",
    )
    
    parser.add_argument(
        "-o", "--output",
        help="Output markdown file or folder",
        default=None,
    )
    
    parser.add_argument(
        "--batch",
        action="store_true",
        help="Batch convert all PDFs in a folder",
    )
    
    parser.add_argument(
        "--no-cache",
        action="store_true",
        help="Skip cache and force re-conversion",
    )
    
    parser.add_argument(
        "--ocr",
        choices=["off", "auto", "force"],
        default="auto",
        help="OCR mode (default: auto)",
    )
    
    parser.add_argument(
        "--export-images",
        action="store_true",
        help="Export images to _assets folder",
    )
    
    parser.add_argument(
        "--password",
        help="Password for encrypted PDFs",
        default=None,
    )
    
    parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Verbose output",
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="thinkpdf Pro 1.1.0",
    )
    
    return parser


def convert_single_file(
    input_path: Path,
    output_path: Optional[Path],
    options: Options,
    use_cache: bool,
    password: Optional[str],
    verbose: bool,
) -> bool:
    """Convert a single PDF file using the full pipeline."""
    
    def log(msg: str) -> None:
        if verbose:
            print(f"  {msg}")
    
    def progress(done: int, total: int) -> None:
        if verbose:
            pct = done * 100 // total
            print(f"  Progress: {pct}%", end="\r")
    
    # Determine output path
    if output_path is None:
        output_path = input_path.with_suffix(".md")
    
    print(f"[PDF] Converting: {input_path.name}")
    
    # Check cache
    cache = CacheManager() if use_cache else None
    
    if cache:
        cached = cache.get_cached(input_path)
        if cached:
            output_path.write_text(cached, encoding="utf-8")
            print(f"  [CACHE] Loaded from cache -> {output_path.name}")
            return True
    
    # Convert using pdfmd pipeline
    try:
        pdf_to_markdown(
            input_pdf=str(input_path),
            output_md=str(output_path),
            options=options,
            progress_cb=progress if verbose else None,
            log_cb=log,
            pdf_password=password,
        )
        
        # Read result for caching
        markdown = output_path.read_text(encoding="utf-8")
        
        # Cache result
        if cache:
            cache.cache(input_path, markdown)
        
        word_count = len(markdown.split())
        print(f"  [OK] Converted -> {output_path.name}")
        print(f"       {word_count} words")
        
        return True
        
    except Exception as e:
        print(f"  [ERROR] {e}")
        return False


def convert_batch(
    input_dir: Path,
    output_dir: Optional[Path],
    options: Options,
    use_cache: bool,
    password: Optional[str],
    verbose: bool,
) -> int:
    """Convert all PDFs in a folder."""
    
    pdf_files = list(input_dir.glob("*.pdf"))
    
    if not pdf_files:
        print(f"No PDF files found in: {input_dir}")
        return 0
    
    print(f"[BATCH] Converting {len(pdf_files)} files from: {input_dir}")
    
    if output_dir is None:
        output_dir = input_dir
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)
    
    success_count = 0
    
    for pdf_file in pdf_files:
        output_path = output_dir / pdf_file.with_suffix(".md").name
        
        if convert_single_file(
            pdf_file,
            output_path,
            options,
            use_cache,
            password,
            verbose,
        ):
            success_count += 1
    
    print(f"\n[DONE] Converted {success_count}/{len(pdf_files)} files")
    return success_count


def main(args: Optional[List[str]] = None) -> int:
    """Main entry point."""
    parser = create_parser()
    parsed = parser.parse_args(args)
    
    input_path = Path(parsed.input)
    
    if not input_path.exists():
        print(f"[ERROR] Input not found: {input_path}")
        return 1
    
    # Build options using pdfmd Options class
    options = Options(
        ocr_mode=parsed.ocr,
        export_images=parsed.export_images,
    )
    
    use_cache = not parsed.no_cache
    
    # Handle batch or single file
    if input_path.is_dir() or parsed.batch:
        if not input_path.is_dir():
            print(f"[ERROR] --batch requires a directory")
            return 1
        
        output_dir = Path(parsed.output) if parsed.output else None
        
        success = convert_batch(
            input_path,
            output_dir,
            options,
            use_cache,
            parsed.password,
            parsed.verbose,
        )
        
        return 0 if success > 0 else 1
    else:
        output_path = Path(parsed.output) if parsed.output else None
        
        success = convert_single_file(
            input_path,
            output_path,
            options,
            use_cache,
            parsed.password,
            parsed.verbose,
        )
        
        return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())
