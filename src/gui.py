"""
Enhanced Modern GUI for Trello Sprint Generator using tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
import time
from typing import Optional, Dict, List
from .config import ConfigManager, ConfigError
from .trello_client import TrelloClient, TrelloAPIError
from .markdown_parser import MarkdownParser, MarkdownParseError
from .sprint_generator import SprintGenerator, SprintGeneratorError


class ModernTrelloGUI:
    """Enhanced Modern GUI application for Trello Sprint Generator"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.setup_variables()
        self.create_widgets()
        self.setup_tooltips()
        self.config = None
        self.trello_client = None
        self.sprint_data = None
        self.theme = "light"  # Default theme
        self.animation_running = False
        
    def setup_window(self):
        """Setup the main window with optimized dimensions"""
        self.root.title("🎯 Trello Sprint Generator")
        self.root.geometry("900x600")
        self.root.minsize(800, 550)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"900x600+{x}+{y}")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
            
        # Configure window behavior
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
    def setup_variables(self):
        """Setup tkinter variables"""
        self.api_key_var = tk.StringVar()
        self.token_var = tk.StringVar()
        self.board_id_var = tk.StringVar()
        self.file_path_var = tk.StringVar()
        self.list_name_var = tk.StringVar(value="Backlog")
        self.config_status_var = tk.StringVar(value="Not configured")
        self.file_status_var = tk.StringVar(value="No file selected")
        self.status_var = tk.StringVar(value="Ready")
        self.progress_var = tk.DoubleVar()
        
    def on_closing(self):
        """Handle window closing"""
        if self.animation_running:
            if messagebox.askokcancel("Quit", "Operation in progress. Are you sure you want to quit?"):
                self.root.destroy()
        else:
            self.root.destroy()
            
    def setup_styles(self):
        """Setup enhanced modern styles with themes"""
        self.style = ttk.Style()
        
        # Configure modern theme
        self.style.theme_use('clam')
        
        # Enhanced color schemes
        self.colors = {
            'light': {
                'bg': '#ffffff',
                'fg': '#2c3e50',
                'accent': '#3498db',
                'success': '#27ae60',
                'error': '#e74c3c',
                'warning': '#f39c12',
                'info': '#7f8c8d',
                'card_bg': '#f8f9fa',
                'border': '#dee2e6'
            },
            'dark': {
                'bg': '#2c3e50',
                'fg': '#ecf0f1',
                'accent': '#3498db',
                'success': '#27ae60',
                'error': '#e74c3c',
                'warning': '#f39c12',
                'info': '#95a5a6',
                'card_bg': '#34495e',
                'border': '#4a5f7a'
            }
        }
        
        self.apply_theme('light')
        
    def apply_theme(self, theme_name):
        """Apply theme colors"""
        self.theme = theme_name
        colors = self.colors[theme_name]
        
        # Configure colors
        self.style.configure('Title.TLabel', 
                            font=('Segoe UI', 18, 'bold'), 
                            foreground=colors['fg'],
                            background=colors['bg'])
        self.style.configure('Subtitle.TLabel', 
                            font=('Segoe UI', 12, 'bold'), 
                            foreground=colors['fg'],
                            background=colors['bg'])
        self.style.configure('Info.TLabel', 
                            font=('Segoe UI', 10), 
                            foreground=colors['info'],
                            background=colors['bg'])
        self.style.configure('Success.TLabel', 
                            font=('Segoe UI', 10, 'bold'), 
                            foreground=colors['success'],
                            background=colors['bg'])
        self.style.configure('Error.TLabel', 
                            font=('Segoe UI', 10, 'bold'), 
                            foreground=colors['error'],
                            background=colors['bg'])
        self.style.configure('Warning.TLabel', 
                            font=('Segoe UI', 10, 'bold'), 
                            foreground=colors['warning'],
                            background=colors['bg'])
        
        # Configure buttons with enhanced styling
        self.style.configure('Primary.TButton', 
                            font=('Segoe UI', 11, 'bold'),
                            foreground='white',
                            background=colors['accent'],
                            borderwidth=0,
                            focuscolor='none')
        self.style.map('Primary.TButton',
                      background=[('active', colors['accent']),
                                ('pressed', colors['accent'])])
        
        self.style.configure('Secondary.TButton', 
                            font=('Segoe UI', 10),
                            foreground=colors['fg'],
                            background=colors['card_bg'],
                            borderwidth=1,
                            focuscolor='none')
        
        self.style.configure('Success.TButton', 
                            font=('Segoe UI', 10, 'bold'),
                            foreground='white',
                            background=colors['success'],
                            borderwidth=0,
                            focuscolor='none')
        
        # Configure frames
        self.style.configure('Card.TFrame', 
                           relief='solid', 
                           borderwidth=1,
                           background=colors['card_bg'])
        
        # Configure entry fields
        self.style.configure('Modern.TEntry',
                           fieldbackground=colors['bg'],
                           foreground=colors['fg'],
                           borderwidth=1,
                           focuscolor=colors['accent'])
        
        # Configure combobox
        self.style.configure('Modern.TCombobox',
                           fieldbackground=colors['bg'],
                           foreground=colors['fg'],
                           borderwidth=1,
                           focuscolor=colors['accent'])
        
        # Set root background
        self.root.configure(bg=colors['bg'])
        
    def setup_tooltips(self):
        """Setup tooltip functionality"""
        self.tooltips = {}
        
    def create_tooltip(self, widget, text):
        """Create a tooltip for a widget"""
        def show_tooltip(event):
            tooltip = tk.Toplevel()
            tooltip.wm_overrideredirect(True)
            tooltip.wm_geometry(f"+{event.x_root+10}+{event.y_root+10}")
            
            label = tk.Label(tooltip, text=text, 
                           background="#ffffe0", 
                           foreground="#000000",
                           font=('Segoe UI', 9),
                           relief="solid", 
                           borderwidth=1,
                           padx=5, pady=3)
            label.pack()
            
            self.tooltips[widget] = tooltip
            
        def hide_tooltip(event):
            if widget in self.tooltips:
                self.tooltips[widget].destroy()
                del self.tooltips[widget]
                
        widget.bind("<Enter>", show_tooltip)
        widget.bind("<Leave>", hide_tooltip)
        
    def animate_progress(self, target_value, duration=1.0):
        """Animate progress bar smoothly"""
        self.animation_running = True
        start_value = self.progress_var.get()
        steps = 30
        step_delay = duration / steps
        step_size = (target_value - start_value) / steps
        
        def animate_step(step):
            if step <= steps:
                current_value = start_value + (step_size * step)
                self.progress_var.set(current_value)
                self.root.after(int(step_delay * 1000), lambda: animate_step(step + 1))
            else:
                self.animation_running = False
                
        animate_step(0)
        
    def create_widgets(self):
        """Create optimized GUI widgets with compact layout"""
        # Main container with compact styling
        main_frame = ttk.Frame(self.root, padding="15")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Header with theme toggle
        self.create_header(main_frame, row=0)
        
        # Configuration Section
        self.create_config_section(main_frame, row=1)
        
        # File Selection Section
        self.create_file_section(main_frame, row=2)
        
        # Preview Section
        self.create_preview_section(main_frame, row=3)
        
        # Action Section
        self.create_action_section(main_frame, row=4)
        
        # Status Section
        self.create_status_section(main_frame, row=5)
        
    def create_header(self, parent, row):
        """Create compact header with theme toggle"""
        header_frame = ttk.Frame(parent)
        header_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        header_frame.columnconfigure(0, weight=1)
        
        # Title with compact styling
        title_label = ttk.Label(header_frame, text="🎯 Trello Sprint Generator", style='Title.TLabel')
        title_label.grid(row=0, column=0, sticky=tk.W)
        
        # Theme toggle button
        theme_text = "🌙 Dark" if self.theme == "light" else "☀️ Light"
        self.theme_button = ttk.Button(header_frame, text=theme_text, 
                                      command=self.toggle_theme, 
                                      style='Secondary.TButton')
        self.theme_button.grid(row=0, column=1, sticky=tk.E, padx=(10, 0))
        
        # Add tooltip
        self.create_tooltip(self.theme_button, "Toggle between light and dark themes")
        
    def toggle_theme(self):
        """Toggle between light and dark themes"""
        new_theme = "dark" if self.theme == "light" else "light"
        self.apply_theme(new_theme)
        
        # Update theme button text
        theme_text = "🌙 Dark" if new_theme == "light" else "☀️ Light"
        self.theme_button.configure(text=theme_text)
        
        # Recreate widgets to apply new theme
        self.root.after(100, self.refresh_widgets)
        
    def create_config_section(self, parent, row):
        """Create compact configuration section"""
        # Config frame with compact styling
        config_frame = ttk.LabelFrame(parent, text="🔧 Configuration", padding="12", style='Card.TFrame')
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        config_frame.columnconfigure(1, weight=1)
        
        # API Key with compact styling
        api_key_label = ttk.Label(config_frame, text="🔑 API Key:", style='Subtitle.TLabel')
        api_key_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, 
                                     show="*", style='Modern.TEntry', width=35)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        
        # Add tooltip for API Key
        self.create_tooltip(self.api_key_entry, "Your Trello API key from https://trello.com/app-key")
        
        # Token with compact styling
        token_label = ttk.Label(config_frame, text="🎫 Token:", style='Subtitle.TLabel')
        token_label.grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.token_entry = ttk.Entry(config_frame, textvariable=self.token_var, 
                                   show="*", style='Modern.TEntry', width=35)
        self.token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        
        # Add tooltip for Token
        self.create_tooltip(self.token_entry, "Your Trello token with read/write permissions")
        
        # Board ID with compact styling
        board_label = ttk.Label(config_frame, text="📋 Board ID:", style='Subtitle.TLabel')
        board_label.grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.board_id_entry = ttk.Entry(config_frame, textvariable=self.board_id_var, 
                                      style='Modern.TEntry', width=35)
        self.board_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        
        # Add tooltip for Board ID
        self.create_tooltip(self.board_id_entry, "The ID of your Trello board (found in the URL)")
        
        # Compact button layout
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(8, 0))
        
        # Test connection button with compact styling
        self.test_button = ttk.Button(button_frame, text="🔍 Test", 
                                    command=self.test_connection, style='Success.TButton')
        self.test_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.test_button, "Test your API credentials")
        
        # Load config button
        self.load_button = ttk.Button(button_frame, text="📂 Load", 
                                    command=self.load_config, style='Secondary.TButton')
        self.load_button.pack(side=tk.LEFT, padx=(0, 8))
        self.create_tooltip(self.load_button, "Load saved configuration")
        
        # Save config button
        self.save_button = ttk.Button(button_frame, text="💾 Save", 
                                    command=self.save_config, style='Secondary.TButton')
        self.save_button.pack(side=tk.LEFT)
        self.create_tooltip(self.save_button, "Save current configuration")
        
        # Compact status with icon
        status_frame = ttk.Frame(config_frame)
        status_frame.grid(row=4, column=0, columnspan=2, pady=(8, 0))
        
        self.config_status_label = ttk.Label(status_frame, textvariable=self.config_status_var, 
                                           style='Info.TLabel')
        self.config_status_label.pack(side=tk.LEFT)
        
        # Add help button
        help_button = ttk.Button(status_frame, text="❓", 
                               command=self.show_config_help, style='Secondary.TButton')
        help_button.pack(side=tk.RIGHT)
        self.create_tooltip(help_button, "Get help with configuration")
        
    def show_config_help(self):
        """Show configuration help dialog"""
        help_text = """🔧 Configuration Help

🔑 API Key:
• Go to https://trello.com/app-key
• Copy your API key
• Paste it in the API Key field

🎫 Token:
• Click "Allow" on the token generation page
• Copy the generated token
• Paste it in the Token field

📋 Board ID:
• Open your Trello board
• Copy the ID from the URL (the part after /b/)
• Paste it in the Board ID field

💡 Tips:
• Use "Save Config" to remember your settings
• Use "Load Config" to restore saved settings
• Test connection before generating cards"""
        
        messagebox.showinfo("Configuration Help", help_text)
        
    def refresh_widgets(self):
        """Refresh widgets after theme change"""
        # Update preview text colors if it exists
        if hasattr(self, 'preview_text'):
            colors = self.colors[self.theme]
            self.preview_text.configure(
                bg=colors['card_bg'],
                fg=colors['fg'],
                selectbackground=colors['accent']
            )
        
    def create_file_section(self, parent, row):
        """Create compact file selection section"""
        # File frame with compact styling
        file_frame = ttk.LabelFrame(parent, text="📁 Sprint File", padding="12", style='Card.TFrame')
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        file_frame.columnconfigure(1, weight=1)
        
        # File selection with compact styling
        file_label = ttk.Label(file_frame, text="📄 Sprint File:", style='Subtitle.TLabel')
        file_label.grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        file_select_frame.columnconfigure(0, weight=1)
        
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, 
                                  state='readonly', style='Modern.TEntry', width=30)
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 8))
        
        browse_button = ttk.Button(file_select_frame, text="📂 Browse", 
                                 command=self.browse_file, style='Secondary.TButton')
        browse_button.grid(row=0, column=1)
        self.create_tooltip(browse_button, "Select a markdown sprint file")
        
        # Compact parse button
        parse_button = ttk.Button(file_frame, text="📋 Parse Sprint", 
                                command=self.parse_sprint, style='Primary.TButton')
        parse_button.grid(row=1, column=0, columnspan=2, pady=(8, 0))
        self.create_tooltip(parse_button, "Parse the selected sprint file")
        
        # Compact file status
        status_frame = ttk.Frame(file_frame)
        status_frame.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
        self.file_status_label = ttk.Label(status_frame, textvariable=self.file_status_var, 
                                         style='Info.TLabel')
        self.file_status_label.pack(side=tk.LEFT)
        
        # Add example button
        example_button = ttk.Button(status_frame, text="📝 Example", 
                                  command=self.load_example, style='Secondary.TButton')
        example_button.pack(side=tk.RIGHT)
        self.create_tooltip(example_button, "Load example sprint file")
        
    def load_example(self):
        """Load example sprint file"""
        example_path = "examples/example_sprint.md"
        if os.path.exists(example_path):
            self.file_path_var.set(example_path)
            self.file_status_var.set(f"✅ Example loaded: {os.path.basename(example_path)}")
            self.file_status_label.configure(style='Success.TLabel')
        else:
            messagebox.showwarning("Example Not Found", 
                                 "Example file not found. Please select a sprint file manually.")
        
    def create_preview_section(self, parent, row):
        """Create compact preview section"""
        # Preview frame with compact styling
        preview_frame = ttk.LabelFrame(parent, text="👀 Sprint Preview", padding="12", style='Card.TFrame')
        preview_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 12))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(1, weight=1)
        
        # Compact preview header
        header_frame = ttk.Frame(preview_frame)
        header_frame.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        header_frame.columnconfigure(1, weight=1)
        
        preview_label = ttk.Label(header_frame, text="📊 Sprint Overview:", style='Subtitle.TLabel')
        preview_label.grid(row=0, column=0, sticky=tk.W)
        
        # Clear preview button
        clear_button = ttk.Button(header_frame, text="🗑️ Clear", 
                                command=self.clear_preview, style='Secondary.TButton')
        clear_button.grid(row=0, column=1, sticky=tk.E)
        self.create_tooltip(clear_button, "Clear the preview")
        
        # Compact preview text with overflow protection
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=6, wrap=tk.WORD, 
                                                    state='disabled', font=('Consolas', 8),
                                                    width=70)
        self.preview_text.grid(row=1, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Add initial message
        self.preview_text.config(state='normal')
        self.preview_text.insert(1.0, "No sprint data loaded. Please select and parse a sprint file to see the preview.")
        self.preview_text.config(state='disabled')
        
    def clear_preview(self):
        """Clear the preview text"""
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, "Preview cleared. Parse a sprint file to see the preview.")
        self.preview_text.config(state='disabled')
        
    def create_action_section(self, parent, row):
        """Create compact action section"""
        # Action frame with compact styling
        action_frame = ttk.LabelFrame(parent, text="🚀 Actions", padding="12", style='Card.TFrame')
        action_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 12))
        action_frame.columnconfigure(1, weight=1)
        
        # Compact list selection
        list_frame = ttk.Frame(action_frame)
        list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 8))
        list_frame.columnconfigure(1, weight=1)
        
        list_label = ttk.Label(list_frame, text="📋 Target List:", style='Subtitle.TLabel')
        list_label.grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        
        self.list_combo = ttk.Combobox(list_frame, textvariable=self.list_name_var, 
                                     style='Modern.TCombobox', width=25)
        self.list_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 8))
        self.create_tooltip(self.list_combo, "Select the Trello list where cards will be created")
        
        refresh_button = ttk.Button(list_frame, text="🔄 Refresh", 
                                   command=self.refresh_lists, style='Secondary.TButton')
        refresh_button.grid(row=0, column=2)
        self.create_tooltip(refresh_button, "Refresh available lists from Trello")
        
        # Compact action buttons
        button_frame = ttk.Frame(action_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(8, 0))
        
        preview_button = ttk.Button(button_frame, text="🔍 Preview", 
                                   command=self.preview_cards, style='Secondary.TButton')
        preview_button.pack(side=tk.LEFT, padx=(0, 10))
        self.create_tooltip(preview_button, "Preview cards that will be created")
        
        generate_button = ttk.Button(button_frame, text="🎯 Generate", 
                                   command=self.generate_cards, style='Primary.TButton')
        generate_button.pack(side=tk.LEFT)
        self.create_tooltip(generate_button, "Generate all cards in Trello")
        
    def create_status_section(self, parent, row):
        """Create compact status section"""
        # Status frame with compact styling
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # Compact progress bar
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, 
                                          mode='determinate', length=300)
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status text with icon
        status_text_frame = ttk.Frame(status_frame)
        status_text_frame.grid(row=1, column=0, sticky=(tk.W, tk.E))
        status_text_frame.columnconfigure(1, weight=1)
        
        self.status_icon = ttk.Label(status_text_frame, text="ℹ️", style='Info.TLabel')
        self.status_icon.grid(row=0, column=0, sticky=tk.W, padx=(0, 5))
        
        self.status_label = ttk.Label(status_text_frame, textvariable=self.status_var, 
                                     style='Info.TLabel')
        self.status_label.grid(row=0, column=1, sticky=tk.W)
        
    def truncate_text(self, text, max_length=60):
        """Truncate text to prevent overflow"""
        if len(text) <= max_length:
            return text
        return text[:max_length-3] + "..."
    
    def update_status(self, message, status_type="info"):
        """Update status with icon and color, preventing overflow"""
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "error": "❌",
            "warning": "⚠️",
            "loading": "⏳"
        }
        
        # Truncate message to prevent overflow
        truncated_message = self.truncate_text(message, 80)
        
        self.status_icon.configure(text=icons.get(status_type, "ℹ️"))
        self.status_var.set(truncated_message)
        
        # Update status label style based on type
        if status_type == "success":
            self.status_label.configure(style='Success.TLabel')
        elif status_type == "error":
            self.status_label.configure(style='Error.TLabel')
        elif status_type == "warning":
            self.status_label.configure(style='Warning.TLabel')
        else:
            self.status_label.configure(style='Info.TLabel')
        
    def browse_file(self):
        """Browse for sprint file with enhanced dialog"""
        file_path = filedialog.askopenfilename(
            title="📁 Select Sprint File",
            filetypes=[("Markdown files", "*.md"), ("Text files", "*.txt"), ("All files", "*.*")],
            initialdir="examples"
        )
        if file_path:
            filename = os.path.basename(file_path)
            truncated_filename = self.truncate_text(filename, 30)
            self.file_path_var.set(file_path)
            self.file_status_var.set(f"✅ Selected: {truncated_filename}")
            self.file_status_label.configure(style='Success.TLabel')
            self.update_status(f"File selected: {truncated_filename}", "success")
            
    def load_config(self):
        """Load configuration from file with enhanced feedback"""
        try:
            self.config = ConfigManager.load_config()
            self.api_key_var.set(self.config.api_key)
            self.token_var.set(self.config.token)
            self.config_status_var.set("✅ Configuration loaded")
            self.config_status_label.configure(style='Success.TLabel')
            self.update_status("Configuration loaded successfully", "success")
        except ConfigError as e:
            messagebox.showerror("Configuration Error", str(e))
            self.config_status_var.set("❌ Configuration error")
            self.config_status_label.configure(style='Error.TLabel')
            self.update_status(f"Configuration error: {e}", "error")
            
    def save_config(self):
        """Save configuration to file with enhanced feedback"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs('config', exist_ok=True)
            
            # Save to secrets.env
            with open('config/secrets.env', 'w') as f:
                f.write(f"TRELLO_API_KEY={self.api_key_var.get()}\n")
                f.write(f"TRELLO_TOKEN={self.token_var.get()}\n")
                
            self.config_status_var.set("✅ Configuration saved")
            self.config_status_label.configure(style='Success.TLabel')
            self.update_status("Configuration saved successfully", "success")
            messagebox.showinfo("Success", "Configuration saved to config/secrets.env")
        except Exception as e:
            self.update_status(f"Save error: {e}", "error")
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
            
    def test_connection(self):
        """Test Trello API connection with enhanced feedback"""
        def test_thread():
            try:
                self.update_status("Testing connection...", "loading")
                self.animate_progress(50, 0.5)
                
                # Create config from current values
                api_key = self.api_key_var.get()
                token = self.token_var.get()
                
                if not api_key or not token:
                    raise ConfigError("Please enter API Key and Token")
                    
                from .models import TrelloConfig
                config = TrelloConfig(api_key=api_key, token=token)
                
                # Test connection
                client = TrelloClient(config)
                if client.test_connection():
                    self.config_status_var.set("✅ Connection successful")
                    self.config_status_label.configure(style='Success.TLabel')
                    self.update_status("Connection test passed", "success")
                    self.animate_progress(100, 0.3)
                else:
                    raise TrelloAPIError("Connection failed")
                    
            except Exception as e:
                self.config_status_var.set("❌ Connection failed")
                self.config_status_label.configure(style='Error.TLabel')
                self.update_status(f"Connection failed: {e}", "error")
                messagebox.showerror("Connection Error", str(e))
            finally:
                self.animate_progress(0, 0.3)
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def parse_sprint(self):
        """Parse the selected sprint file with enhanced feedback"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("No File", "Please select a sprint file first")
            return
            
        def parse_thread():
            try:
                self.update_status("Parsing sprint file...", "loading")
                self.animate_progress(25, 0.5)
                
                # Parse the sprint
                parser = MarkdownParser(file_path)
                self.sprint_data = parser.parse_sprint()
                
                # Update preview
                self.update_preview()
                
                self.file_status_var.set(f"✅ Parsed: {self.sprint_data.title}")
                self.file_status_label.configure(style='Success.TLabel')
                self.update_status("Sprint parsed successfully", "success")
                self.animate_progress(100, 0.3)
                
            except Exception as e:
                self.file_status_var.set("❌ Parse failed")
                self.file_status_label.configure(style='Error.TLabel')
                self.update_status(f"Parse failed: {e}", "error")
                messagebox.showerror("Parse Error", str(e))
            finally:
                self.animate_progress(0, 0.3)
                
        threading.Thread(target=parse_thread, daemon=True).start()
        
    def update_preview(self):
        """Update the preview text with enhanced formatting and overflow protection"""
        if not self.sprint_data:
            return
            
        # Truncate long titles to prevent overflow
        title = self.truncate_text(self.sprint_data.title, 50)
        focus = self.truncate_text(self.sprint_data.focus, 40)
        dependencies = self.truncate_text(self.sprint_data.dependencies, 40)
        
        preview_text = f"""🎯 SPRINT OVERVIEW
{'='*50}
📋 Title: {title}
📅 Duration: {self.sprint_data.duration}
🎯 Focus: {focus}
⚡ Priority: {self.sprint_data.priority}
🔗 Dependencies: {dependencies}

📊 MILESTONES ({len(self.sprint_data.milestones)})
{'='*50}
"""
        
        total_tasks = 0
        for i, milestone in enumerate(self.sprint_data.milestones, 1):
            milestone_title = self.truncate_text(milestone.title, 45)
            preview_text += f"\n{i}. 🎯 {milestone_title}\n"
            preview_text += f"   📅 Duration: {milestone.duration}\n"
            preview_text += f"   ⚡ Priority: {milestone.priority}\n"
            preview_text += f"   📋 Tasks: {len(milestone.tasks)}\n"
            
            for j, task in enumerate(milestone.tasks, 1):
                task_title = self.truncate_text(task.title, 40)
                preview_text += f"      {j}. 📋 {task_title} ({task.estimated_time})\n"
                
            total_tasks += len(milestone.tasks)
            preview_text += "\n"
                
        preview_text += f"""📈 SUMMARY
{'='*50}
• Total Milestones: {len(self.sprint_data.milestones)}
• Total Tasks: {total_tasks}
• Estimated Cards: {1 + len(self.sprint_data.milestones) + total_tasks}
"""
        
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state='disabled')
        
    def refresh_lists(self):
        """Refresh available lists from Trello with enhanced feedback"""
        if not self.config:
            messagebox.showwarning("No Config", "Please configure and test connection first")
            return
            
        def refresh_thread():
            try:
                self.update_status("Refreshing lists...", "loading")
                self.animate_progress(50, 0.5)
                
                # Get lists
                client = TrelloClient(self.config)
                board_id = self.board_id_var.get()
                
                if not board_id:
                    raise ValueError("Please enter Board ID")
                    
                lists = client.get_board_lists(board_id)
                
                # Update combo box
                list_names = [list_info['name'] for list_info in lists]
                self.list_combo['values'] = list_names
                
                if list_names and not self.list_name_var.get():
                    self.list_name_var.set(list_names[0])
                    
                self.update_status(f"Found {len(list_names)} lists", "success")
                self.animate_progress(100, 0.3)
                
            except Exception as e:
                self.update_status(f"Failed to refresh lists: {e}", "error")
                messagebox.showerror("Refresh Error", str(e))
            finally:
                self.animate_progress(0, 0.3)
                
        threading.Thread(target=refresh_thread, daemon=True).start()
        
    def preview_cards(self):
        """Preview cards that will be created with enhanced formatting"""
        if not self.sprint_data:
            messagebox.showwarning("No Sprint", "Please parse a sprint file first")
            return
            
        preview_text = f"""🎯 CARDS TO BE CREATED
{'='*50}

📋 SPRINT CARD
• {self.sprint_data.title}

🎯 MILESTONE CARDS ({len(self.sprint_data.milestones)})
"""
        
        total_tasks = 0
        for i, milestone in enumerate(self.sprint_data.milestones, 1):
            preview_text += f"\n{i}. 🎯 {milestone.title}"
            total_tasks += len(milestone.tasks)
            
        preview_text += f"\n\n📝 TASK CARDS ({total_tasks})"
        
        task_num = 1
        for milestone in self.sprint_data.milestones:
            for task in milestone.tasks:
                preview_text += f"\n{task_num}. 📋 {task.title}"
                task_num += 1
                
        preview_text += f"""

📊 SUMMARY
{'='*50}
• Sprint Card: 1
• Milestone Cards: {len(self.sprint_data.milestones)}
• Task Cards: {total_tasks}
• TOTAL: {1 + len(self.sprint_data.milestones) + total_tasks} cards"""
        
        messagebox.showinfo("Card Preview", preview_text)
        
    def generate_cards(self):
        """Generate Trello cards with enhanced feedback"""
        if not self.sprint_data:
            messagebox.showwarning("No Sprint", "Please parse a sprint file first")
            return
            
        if not self.config:
            messagebox.showwarning("No Config", "Please configure API credentials first")
            return
            
        board_id = self.board_id_var.get()
        if not board_id:
            messagebox.showwarning("No Board", "Please enter Board ID")
            return
            
        def generate_thread():
            try:
                self.update_status("Generating cards...", "loading")
                self.animate_progress(10, 0.3)
                
                # Create client and generator
                client = TrelloClient(self.config)
                generator = SprintGenerator(client)
                
                self.animate_progress(30, 0.3)
                
                # Generate cards
                result = generator.generate_cards(
                    self.sprint_data, 
                    board_id, 
                    self.list_name_var.get()
                )
                
                self.animate_progress(100, 0.5)
                
                # Show success message
                success_msg = f"""✅ CARDS GENERATED SUCCESSFULLY!

📋 Sprint Card: {result['sprint_card']['name']}
🎯 Milestone Cards: {len(result['milestone_cards'])}
📝 Task Cards: {len(result['task_cards'])}
🏷️ Labels Created: {len(result['created_labels'])}

📊 TOTAL: {1 + len(result['milestone_cards']) + len(result['task_cards'])} cards created!

🎉 Your Trello board has been updated with the sprint data!"""
                
                self.update_status("Cards generated successfully!", "success")
                messagebox.showinfo("Success", success_msg)
                
            except Exception as e:
                self.update_status(f"Generation failed: {e}", "error")
                messagebox.showerror("Generation Error", str(e))
            finally:
                self.animate_progress(0, 0.3)
                
        threading.Thread(target=generate_thread, daemon=True).start()
        
    def run(self):
        """Run the enhanced GUI application"""
        # Load initial configuration if available
        try:
            self.load_config()
        except:
            pass
            
        # Set initial status
        self.update_status("Ready to generate Trello cards", "info")
        
        # Start the main loop
        self.root.mainloop()


def main():
    """Main entry point for GUI"""
    app = ModernTrelloGUI()
    app.run()


if __name__ == "__main__":
    main()
