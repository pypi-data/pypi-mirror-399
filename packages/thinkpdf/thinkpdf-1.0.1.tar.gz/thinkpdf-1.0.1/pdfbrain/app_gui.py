"""
thinkpdf GUI - Modern desktop application for PDF to Markdown conversion.

Features:
- Modern dark/light theme with CustomTkinter
- Drag and drop support
- Progress tracking
- Quality selection
- Batch processing
- Preview panel
"""

from __future__ import annotations

import os
import sys
import threading
from pathlib import Path
from typing import Optional, List
from tkinter import filedialog, messagebox
import tkinter as tk

try:
    import customtkinter as ctk
    HAS_CTK = True
except ImportError:
    HAS_CTK = False
    ctk = None

try:
    from PIL import Image
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Version
__version__ = "1.0.0"

from .core.converter import PDFConverter, ConversionOptions, ConversionResult
from .cache.cache_manager import CacheManager


# Color schemes
COLORS = {
    "dark": {
        "bg": "#1a1a2e",
        "fg": "#eaeaea",
        "accent": "#7c3aed",
        "accent_hover": "#8b5cf6",
        "secondary": "#2d2d44",
        "success": "#10b981",
        "error": "#ef4444",
        "border": "#3d3d5c",
    },
    "light": {
        "bg": "#f8fafc",
        "fg": "#1e293b",
        "accent": "#7c3aed",
        "accent_hover": "#8b5cf6",
        "secondary": "#e2e8f0",
        "success": "#10b981",
        "error": "#ef4444",
        "border": "#cbd5e1",
    },
}


class thinkpdfApp:
    """Main application window."""
    
    def __init__(self):
        if not HAS_CTK:
            self._run_fallback()
            return
        
        # Configure CustomTkinter
        ctk.set_appearance_mode("dark")
        ctk.set_default_color_theme("blue")
        
        # Create window
        self.root = ctk.CTk()
        self.root.title("thinkpdf - PDF to Markdown Converter")
        self.root.geometry("900x650")
        self.root.minsize(800, 600)
        
        # State
        self.input_files: List[Path] = []
        self.is_converting = False
        self.cache = CacheManager()
        
        # Build UI
        self._build_ui()
        
        # Enable drag and drop on Windows
        self._setup_dnd()
    
    def _run_fallback(self):
        """Run a simple fallback if CustomTkinter is not available."""
        root = tk.Tk()
        root.title("thinkpdf")
        root.geometry("500x300")
        
        label = tk.Label(
            root,
            text="thinkpdf requires CustomTkinter for the GUI.\n\n"
                 "Install it with:\n"
                 "pip install customtkinter\n\n"
                 "Or use the CLI:\n"
                 "thinkpdf input.pdf",
            font=("Arial", 12),
            padx=20,
            pady=20,
        )
        label.pack(expand=True)
        
        root.mainloop()
    
    def _build_ui(self):
        """Build the main UI."""
        # Main container
        main_frame = ctk.CTkFrame(self.root)
        main_frame.pack(fill="both", expand=True, padx=20, pady=20)
        
        # Header
        self._build_header(main_frame)
        
        # Drop zone
        self._build_drop_zone(main_frame)
        
        # Options
        self._build_options(main_frame)
        
        # File list
        self._build_file_list(main_frame)
        
        # Progress
        self._build_progress(main_frame)
        
        # Buttons
        self._build_buttons(main_frame)
        
        # Status bar
        self._build_status(main_frame)
    
    def _build_header(self, parent):
        """Build the header section."""
        header = ctk.CTkFrame(parent, fg_color="transparent")
        header.pack(fill="x", pady=(0, 15))
        
        # Logo + Title
        if HAS_PIL and HAS_CTK:
            logo_path = Path(__file__).parent.parent / "logo.png"
            if logo_path.exists():
                try:
                    logo_img = ctk.CTkImage(
                        light_image=Image.open(logo_path),
                        dark_image=Image.open(logo_path),
                        size=(40, 40)
                    )
                    logo_label = ctk.CTkLabel(header, image=logo_img, text="")
                    logo_label.pack(side="left", padx=(0, 10))
                except Exception:
                    pass
        
        # Title
        title = ctk.CTkLabel(
            header,
            text="thinkpdf",
            font=ctk.CTkFont(size=28, weight="bold"),
        )
        title.pack(side="left")
        
        # Theme toggle
        self.theme_var = ctk.StringVar(value="dark")
        theme_btn = ctk.CTkSegmentedButton(
            header,
            values=["☀️ Light", "🌙 Dark"],
            command=self._toggle_theme,
            width=150,
        )
        theme_btn.set("🌙 Dark")
        theme_btn.pack(side="right")
    
    def _build_drop_zone(self, parent):
        """Build the drag and drop zone."""
        self.drop_frame = ctk.CTkFrame(
            parent,
            height=120,
            corner_radius=15,
            border_width=2,
            border_color=COLORS["dark"]["accent"],
        )
        self.drop_frame.pack(fill="x", pady=(0, 15))
        self.drop_frame.pack_propagate(False)
        
        drop_label = ctk.CTkLabel(
            self.drop_frame,
            text="📁 Drag & Drop PDF files here\nor click to browse",
            font=ctk.CTkFont(size=16),
        )
        drop_label.pack(expand=True)
        
        # Make clickable
        self.drop_frame.bind("<Button-1>", self._browse_files)
        drop_label.bind("<Button-1>", self._browse_files)
    
    def _build_options(self, parent):
        """Build the options section."""
        options_frame = ctk.CTkFrame(parent, fg_color="transparent")
        options_frame.pack(fill="x", pady=(0, 15))
        
        # Quality selector
        quality_label = ctk.CTkLabel(options_frame, text="Quality:")
        quality_label.pack(side="left", padx=(0, 10))
        
        self.quality_var = ctk.StringVar(value="balanced")
        quality_menu = ctk.CTkSegmentedButton(
            options_frame,
            values=["⚡ Fast", "⚖️ Balanced", "🎯 Maximum"],
            command=self._on_quality_change,
            width=300,
        )
        quality_menu.set("⚖️ Balanced")
        quality_menu.pack(side="left", padx=(0, 20))
        
        # Options checkboxes
        self.use_cache_var = ctk.BooleanVar(value=True)
        cache_check = ctk.CTkCheckBox(
            options_frame,
            text="Use cache",
            variable=self.use_cache_var,
        )
        cache_check.pack(side="left", padx=(0, 15))
        
        self.export_images_var = ctk.BooleanVar(value=False)
        images_check = ctk.CTkCheckBox(
            options_frame,
            text="Export images",
            variable=self.export_images_var,
        )
        images_check.pack(side="left")
    
    def _build_file_list(self, parent):
        """Build the file list section."""
        list_frame = ctk.CTkFrame(parent)
        list_frame.pack(fill="both", expand=True, pady=(0, 15))
        
        # Header
        list_header = ctk.CTkFrame(list_frame, fg_color="transparent")
        list_header.pack(fill="x", padx=15, pady=(10, 5))
        
        ctk.CTkLabel(
            list_header,
            text="Files to Convert",
            font=ctk.CTkFont(size=14, weight="bold"),
        ).pack(side="left")
        
        clear_btn = ctk.CTkButton(
            list_header,
            text="Clear All",
            width=80,
            height=28,
            command=self._clear_files,
        )
        clear_btn.pack(side="right")
        
        # Scrollable file list
        self.file_list = ctk.CTkScrollableFrame(list_frame, height=150)
        self.file_list.pack(fill="both", expand=True, padx=10, pady=(5, 10))
        
        self.file_widgets: List[ctk.CTkFrame] = []
        
        # Empty state
        self.empty_label = ctk.CTkLabel(
            self.file_list,
            text="No files added yet",
            text_color="gray",
        )
        self.empty_label.pack(pady=30)
    
    def _build_progress(self, parent):
        """Build the progress section."""
        progress_frame = ctk.CTkFrame(parent, fg_color="transparent")
        progress_frame.pack(fill="x", pady=(0, 15))
        
        self.progress_label = ctk.CTkLabel(
            progress_frame,
            text="Ready to convert",
        )
        self.progress_label.pack(anchor="w")
        
        self.progress_bar = ctk.CTkProgressBar(progress_frame)
        self.progress_bar.pack(fill="x", pady=(5, 0))
        self.progress_bar.set(0)
    
    def _build_buttons(self, parent):
        """Build the action buttons."""
        btn_frame = ctk.CTkFrame(parent, fg_color="transparent")
        btn_frame.pack(fill="x")
        
        self.convert_btn = ctk.CTkButton(
            btn_frame,
            text="🚀 Convert All",
            font=ctk.CTkFont(size=16, weight="bold"),
            height=45,
            command=self._start_conversion,
        )
        self.convert_btn.pack(side="left", expand=True, fill="x", padx=(0, 10))
        
        self.open_folder_btn = ctk.CTkButton(
            btn_frame,
            text="📂 Open Output",
            height=45,
            width=150,
            fg_color="transparent",
            border_width=2,
            command=self._open_output_folder,
        )
        self.open_folder_btn.pack(side="right")
    
    def _build_status(self, parent):
        """Build the status bar."""
        status_frame = ctk.CTkFrame(parent, fg_color="transparent", height=30)
        status_frame.pack(fill="x", pady=(15, 0))
        
        self.status_label = ctk.CTkLabel(
            status_frame,
            text=f"thinkpdf v{__version__} | Ready",
            text_color="gray",
        )
        self.status_label.pack(side="left")
        
        cache_stats = self.cache.get_stats()
        cache_label = ctk.CTkLabel(
            status_frame,
            text=f"Cache: {cache_stats['entries']} files, {cache_stats['total_size_mb']:.1f} MB",
            text_color="gray",
        )
        cache_label.pack(side="right")
    
    def _setup_dnd(self):
        """Setup drag and drop (Windows)."""
        # For now, just use file browser
        # TODO: Add proper DnD with tkinterdnd2
        pass
    
    def _browse_files(self, event=None):
        """Open file browser to select PDFs."""
        files = filedialog.askopenfilenames(
            title="Select PDF files",
            filetypes=[("PDF files", "*.pdf"), ("All files", "*.*")],
        )
        
        if files:
            for f in files:
                self._add_file(Path(f))
    
    def _add_file(self, file_path: Path):
        """Add a file to the list."""
        if file_path in self.input_files:
            return
        
        self.input_files.append(file_path)
        
        # Hide empty label
        self.empty_label.pack_forget()
        
        # Create file widget
        file_frame = ctk.CTkFrame(self.file_list)
        file_frame.pack(fill="x", pady=2)
        
        # File icon and name
        ctk.CTkLabel(
            file_frame,
            text=f"📄 {file_path.name}",
            anchor="w",
        ).pack(side="left", padx=10, pady=8)
        
        # Size
        size_mb = file_path.stat().st_size / (1024 * 1024)
        ctk.CTkLabel(
            file_frame,
            text=f"{size_mb:.1f} MB",
            text_color="gray",
        ).pack(side="right", padx=10)
        
        self.file_widgets.append(file_frame)
        self._update_status()
    
    def _clear_files(self):
        """Clear all files from the list."""
        self.input_files.clear()
        
        for widget in self.file_widgets:
            widget.destroy()
        self.file_widgets.clear()
        
        self.empty_label.pack(pady=30)
        self._update_status()
    
    def _toggle_theme(self, value):
        """Toggle between light and dark theme."""
        if "Light" in value:
            ctk.set_appearance_mode("light")
        else:
            ctk.set_appearance_mode("dark")
    
    def _on_quality_change(self, value):
        """Handle quality change."""
        if "Fast" in value:
            self.quality_var.set("fast")
        elif "Maximum" in value:
            self.quality_var.set("maximum")
        else:
            self.quality_var.set("balanced")
    
    def _update_status(self):
        """Update the status label."""
        count = len(self.input_files)
        if count == 0:
            self.status_label.configure(text=f"thinkpdf v{__version__} | Ready")
        else:
            total_size = sum(f.stat().st_size for f in self.input_files) / (1024 * 1024)
            self.status_label.configure(
                text=f"thinkpdf v{__version__} | {count} files ({total_size:.1f} MB)"
            )
    
    def _start_conversion(self):
        """Start the conversion process."""
        if not self.input_files:
            messagebox.showwarning("No files", "Please add PDF files to convert.")
            return
        
        if self.is_converting:
            return
        
        self.is_converting = True
        self.convert_btn.configure(state="disabled", text="Converting...")
        
        # Run in thread
        thread = threading.Thread(target=self._convert_files)
        thread.start()
    
    def _convert_files(self):
        """Convert all files (runs in background thread)."""
        try:
            options = ConversionOptions(
                quality=self.quality_var.get(),
                export_images=self.export_images_var.get(),
            )
            
            total = len(self.input_files)
            success_count = 0
            
            for i, pdf_path in enumerate(self.input_files):
                # Update progress
                self.root.after(0, lambda p=i, t=total: self._update_progress(p, t, pdf_path.name))
                
                try:
                    converter = PDFConverter(options=options)
                    output_path = pdf_path.with_suffix(".md")
                    result = converter.convert(pdf_path, output_path=output_path)
                    
                    # Cache if enabled
                    if self.use_cache_var.get():
                        self.cache.cache(pdf_path, result.markdown)
                    
                    success_count += 1
                    
                except Exception as e:
                    print(f"Error converting {pdf_path.name}: {e}")
            
            # Done
            self.root.after(0, lambda: self._conversion_complete(success_count, total))
            
        except Exception as e:
            self.root.after(0, lambda: messagebox.showerror("Error", str(e)))
        
        finally:
            self.is_converting = False
            self.root.after(0, lambda: self.convert_btn.configure(
                state="normal",
                text="🚀 Convert All"
            ))
    
    def _update_progress(self, current: int, total: int, filename: str):
        """Update progress bar and label."""
        progress = (current + 1) / total
        self.progress_bar.set(progress)
        self.progress_label.configure(text=f"Converting: {filename} ({current + 1}/{total})")
    
    def _conversion_complete(self, success: int, total: int):
        """Handle conversion completion."""
        self.progress_bar.set(1.0)
        self.progress_label.configure(
            text=f"✅ Completed: {success}/{total} files converted successfully"
        )
        
        if success == total:
            messagebox.showinfo(
                "Conversion Complete",
                f"Successfully converted {total} files!"
            )
        else:
            messagebox.showwarning(
                "Conversion Complete",
                f"Converted {success}/{total} files.\n"
                f"{total - success} files had errors."
            )
    
    def _open_output_folder(self):
        """Open the output folder in file explorer."""
        if self.input_files:
            folder = self.input_files[0].parent
            os.startfile(str(folder))
    
    def run(self):
        """Start the application."""
        if HAS_CTK:
            self.root.mainloop()


def main():
    """Entry point for the GUI."""
    app = thinkpdfApp()
    app.run()


if __name__ == "__main__":
    main()
