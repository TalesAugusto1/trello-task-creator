"""
Modern GUI for Trello Sprint Generator using tkinter.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import threading
import os
from typing import Optional
from .config import ConfigManager, ConfigError
from .trello_client import TrelloClient, TrelloAPIError
from .markdown_parser import MarkdownParser, MarkdownParseError
from .sprint_generator import SprintGenerator, SprintGeneratorError


class ModernTrelloGUI:
    """Modern GUI application for Trello Sprint Generator"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.setup_window()
        self.setup_styles()
        self.create_widgets()
        self.config = None
        self.trello_client = None
        self.sprint_data = None
        
    def setup_window(self):
        """Setup the main window"""
        self.root.title("Trello Sprint Generator")
        self.root.geometry("900x700")
        self.root.minsize(800, 600)
        
        # Center the window
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (900 // 2)
        y = (self.root.winfo_screenheight() // 2) - (700 // 2)
        self.root.geometry(f"900x700+{x}+{y}")
        
        # Set window icon (if available)
        try:
            self.root.iconbitmap("assets/icon.ico")
        except:
            pass
            
    def setup_styles(self):
        """Setup modern styles"""
        style = ttk.Style()
        
        # Configure modern theme
        style.theme_use('clam')
        
        # Configure colors
        style.configure('Title.TLabel', font=('Segoe UI', 16, 'bold'), foreground='#2c3e50')
        style.configure('Subtitle.TLabel', font=('Segoe UI', 12, 'bold'), foreground='#34495e')
        style.configure('Info.TLabel', font=('Segoe UI', 10), foreground='#7f8c8d')
        style.configure('Success.TLabel', font=('Segoe UI', 10), foreground='#27ae60')
        style.configure('Error.TLabel', font=('Segoe UI', 10), foreground='#e74c3c')
        
        # Configure buttons
        style.configure('Primary.TButton', font=('Segoe UI', 10, 'bold'))
        style.configure('Secondary.TButton', font=('Segoe UI', 10))
        
        # Configure frames
        style.configure('Card.TFrame', relief='solid', borderwidth=1)
        
    def create_widgets(self):
        """Create all GUI widgets"""
        # Main container
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configure grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Title
        title_label = ttk.Label(main_frame, text="🎯 Trello Sprint Generator", style='Title.TLabel')
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
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
        
    def create_config_section(self, parent, row):
        """Create configuration section"""
        # Config frame
        config_frame = ttk.LabelFrame(parent, text="🔧 Configuration", padding="15")
        config_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        config_frame.columnconfigure(1, weight=1)
        
        # API Key
        ttk.Label(config_frame, text="API Key:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        self.api_key_var = tk.StringVar()
        self.api_key_entry = ttk.Entry(config_frame, textvariable=self.api_key_var, show="*", width=50)
        self.api_key_entry.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        
        # Token
        ttk.Label(config_frame, text="Token:", style='Subtitle.TLabel').grid(row=1, column=0, sticky=tk.W, pady=(0, 5))
        self.token_var = tk.StringVar()
        self.token_entry = ttk.Entry(config_frame, textvariable=self.token_var, show="*", width=50)
        self.token_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        
        # Board ID
        ttk.Label(config_frame, text="Board ID:", style='Subtitle.TLabel').grid(row=2, column=0, sticky=tk.W, pady=(0, 5))
        self.board_id_var = tk.StringVar()
        self.board_id_entry = ttk.Entry(config_frame, textvariable=self.board_id_var, width=50)
        self.board_id_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        
        # Buttons
        button_frame = ttk.Frame(config_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔍 Test Connection", command=self.test_connection, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Load Config", command=self.load_config, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="💾 Save Config", command=self.save_config, style='Secondary.TButton').pack(side=tk.LEFT)
        
        # Status
        self.config_status_var = tk.StringVar(value="Not configured")
        self.config_status_label = ttk.Label(config_frame, textvariable=self.config_status_var, style='Info.TLabel')
        self.config_status_label.grid(row=4, column=0, columnspan=2, pady=(10, 0))
        
    def create_file_section(self, parent, row):
        """Create file selection section"""
        # File frame
        file_frame = ttk.LabelFrame(parent, text="📁 Sprint File", padding="15")
        file_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        file_frame.columnconfigure(1, weight=1)
        
        # File selection
        ttk.Label(file_frame, text="Sprint File:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, pady=(0, 5))
        
        file_select_frame = ttk.Frame(file_frame)
        file_select_frame.grid(row=0, column=1, sticky=(tk.W, tk.E), pady=(0, 5), padx=(10, 0))
        file_select_frame.columnconfigure(0, weight=1)
        
        self.file_path_var = tk.StringVar()
        self.file_entry = ttk.Entry(file_select_frame, textvariable=self.file_path_var, state='readonly')
        self.file_entry.grid(row=0, column=0, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(file_select_frame, text="📂 Browse", command=self.browse_file, style='Secondary.TButton').grid(row=0, column=1)
        
        # Parse button
        ttk.Button(file_frame, text="📋 Parse Sprint", command=self.parse_sprint, style='Primary.TButton').grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        # File status
        self.file_status_var = tk.StringVar(value="No file selected")
        self.file_status_label = ttk.Label(file_frame, textvariable=self.file_status_var, style='Info.TLabel')
        self.file_status_label.grid(row=2, column=0, columnspan=2, pady=(5, 0))
        
    def create_preview_section(self, parent, row):
        """Create preview section"""
        # Preview frame
        preview_frame = ttk.LabelFrame(parent, text="👀 Sprint Preview", padding="15")
        preview_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=(0, 15))
        preview_frame.columnconfigure(0, weight=1)
        preview_frame.rowconfigure(0, weight=1)
        
        # Preview text
        self.preview_text = scrolledtext.ScrolledText(preview_frame, height=8, wrap=tk.WORD, state='disabled')
        self.preview_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
    def create_action_section(self, parent, row):
        """Create action section"""
        # Action frame
        action_frame = ttk.LabelFrame(parent, text="🚀 Actions", padding="15")
        action_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 15))
        
        # List selection
        list_frame = ttk.Frame(action_frame)
        list_frame.grid(row=0, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 10))
        list_frame.columnconfigure(1, weight=1)
        
        ttk.Label(list_frame, text="Target List:", style='Subtitle.TLabel').grid(row=0, column=0, sticky=tk.W, padx=(0, 10))
        self.list_name_var = tk.StringVar(value="Backlog")
        self.list_combo = ttk.Combobox(list_frame, textvariable=self.list_name_var, width=30)
        self.list_combo.grid(row=0, column=1, sticky=(tk.W, tk.E), padx=(0, 10))
        
        ttk.Button(list_frame, text="🔄 Refresh Lists", command=self.refresh_lists, style='Secondary.TButton').grid(row=0, column=2)
        
        # Action buttons
        button_frame = ttk.Frame(action_frame)
        button_frame.grid(row=1, column=0, columnspan=2, pady=(10, 0))
        
        ttk.Button(button_frame, text="🔍 Preview Cards", command=self.preview_cards, style='Secondary.TButton').pack(side=tk.LEFT, padx=(0, 10))
        ttk.Button(button_frame, text="🎯 Generate Cards", command=self.generate_cards, style='Primary.TButton').pack(side=tk.LEFT)
        
    def create_status_section(self, parent, row):
        """Create status section"""
        # Status frame
        status_frame = ttk.Frame(parent)
        status_frame.grid(row=row, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        status_frame.columnconfigure(0, weight=1)
        
        # Progress bar
        self.progress_var = tk.DoubleVar()
        self.progress_bar = ttk.Progressbar(status_frame, variable=self.progress_var, mode='determinate')
        self.progress_bar.grid(row=0, column=0, sticky=(tk.W, tk.E), pady=(0, 5))
        
        # Status text
        self.status_var = tk.StringVar(value="Ready")
        self.status_label = ttk.Label(status_frame, textvariable=self.status_var, style='Info.TLabel')
        self.status_label.grid(row=1, column=0, sticky=tk.W)
        
    def browse_file(self):
        """Browse for sprint file"""
        file_path = filedialog.askopenfilename(
            title="Select Sprint File",
            filetypes=[("Markdown files", "*.md"), ("All files", "*.*")],
            initialdir="examples"
        )
        if file_path:
            self.file_path_var.set(file_path)
            self.file_status_var.set(f"Selected: {os.path.basename(file_path)}")
            
    def load_config(self):
        """Load configuration from file"""
        try:
            self.config = ConfigManager.load_config()
            self.api_key_var.set(self.config.api_key)
            self.token_var.set(self.config.token)
            self.config_status_var.set("✅ Configuration loaded")
            self.config_status_label.configure(style='Success.TLabel')
        except ConfigError as e:
            messagebox.showerror("Configuration Error", str(e))
            self.config_status_var.set("❌ Configuration error")
            self.config_status_label.configure(style='Error.TLabel')
            
    def save_config(self):
        """Save configuration to file"""
        try:
            # Create config directory if it doesn't exist
            os.makedirs('config', exist_ok=True)
            
            # Save to secrets.env
            with open('config/secrets.env', 'w') as f:
                f.write(f"TRELLO_API_KEY={self.api_key_var.get()}\n")
                f.write(f"TRELLO_TOKEN={self.token_var.get()}\n")
                
            self.config_status_var.set("✅ Configuration saved")
            self.config_status_label.configure(style='Success.TLabel')
            messagebox.showinfo("Success", "Configuration saved to config/secrets.env")
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save configuration: {e}")
            
    def test_connection(self):
        """Test Trello API connection"""
        def test_thread():
            try:
                self.status_var.set("Testing connection...")
                self.progress_var.set(50)
                
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
                    self.status_var.set("Connection test passed")
                else:
                    raise TrelloAPIError("Connection failed")
                    
            except Exception as e:
                self.config_status_var.set("❌ Connection failed")
                self.config_status_label.configure(style='Error.TLabel')
                self.status_var.set(f"Connection failed: {e}")
                messagebox.showerror("Connection Error", str(e))
            finally:
                self.progress_var.set(0)
                
        threading.Thread(target=test_thread, daemon=True).start()
        
    def parse_sprint(self):
        """Parse the selected sprint file"""
        file_path = self.file_path_var.get()
        if not file_path:
            messagebox.showwarning("No File", "Please select a sprint file first")
            return
            
        def parse_thread():
            try:
                self.status_var.set("Parsing sprint file...")
                self.progress_var.set(25)
                
                # Parse the sprint
                parser = MarkdownParser(file_path)
                self.sprint_data = parser.parse_sprint()
                
                # Update preview
                self.update_preview()
                
                self.file_status_var.set(f"✅ Parsed: {self.sprint_data.title}")
                self.status_var.set("Sprint parsed successfully")
                
            except Exception as e:
                self.file_status_var.set("❌ Parse failed")
                self.status_var.set(f"Parse failed: {e}")
                messagebox.showerror("Parse Error", str(e))
            finally:
                self.progress_var.set(0)
                
        threading.Thread(target=parse_thread, daemon=True).start()
        
    def update_preview(self):
        """Update the preview text"""
        if not self.sprint_data:
            return
            
        preview_text = f"""🎯 Sprint: {self.sprint_data.title}
📅 Duration: {self.sprint_data.duration}
🎯 Focus: {self.sprint_data.focus}
⚡ Priority: {self.sprint_data.priority}
🔗 Dependencies: {self.sprint_data.dependencies}

📊 Milestones ({len(self.sprint_data.milestones)}):
"""
        
        for milestone in self.sprint_data.milestones:
            preview_text += f"\n  🎯 {milestone.title}"
            preview_text += f"\n    Duration: {milestone.duration}"
            preview_text += f"\n    Priority: {milestone.priority}"
            preview_text += f"\n    Tasks: {len(milestone.tasks)}"
            
            for task in milestone.tasks:
                preview_text += f"\n      📋 {task.title} ({task.estimated_time})"
                
        preview_text += f"\n\n📈 Total Tasks: {sum(len(m.tasks) for m in self.sprint_data.milestones)}"
        
        self.preview_text.config(state='normal')
        self.preview_text.delete(1.0, tk.END)
        self.preview_text.insert(1.0, preview_text)
        self.preview_text.config(state='disabled')
        
    def refresh_lists(self):
        """Refresh available lists from Trello"""
        if not self.config:
            messagebox.showwarning("No Config", "Please configure and test connection first")
            return
            
        def refresh_thread():
            try:
                self.status_var.set("Refreshing lists...")
                self.progress_var.set(50)
                
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
                    
                self.status_var.set(f"Found {len(list_names)} lists")
                
            except Exception as e:
                self.status_var.set(f"Failed to refresh lists: {e}")
                messagebox.showerror("Refresh Error", str(e))
            finally:
                self.progress_var.set(0)
                
        threading.Thread(target=refresh_thread, daemon=True).start()
        
    def preview_cards(self):
        """Preview cards that will be created"""
        if not self.sprint_data:
            messagebox.showwarning("No Sprint", "Please parse a sprint file first")
            return
            
        preview_text = f"""🎯 Cards to be created:

📋 Sprint Card: {self.sprint_data.title}

🎯 Milestone Cards ({len(self.sprint_data.milestones)}):
"""
        
        total_tasks = 0
        for milestone in self.sprint_data.milestones:
            preview_text += f"\n  🎯 {milestone.title}"
            total_tasks += len(milestone.tasks)
            
        preview_text += f"\n📝 Task Cards ({total_tasks}):"
        
        for milestone in self.sprint_data.milestones:
            for task in milestone.tasks:
                preview_text += f"\n  📋 {task.title}"
                
        preview_text += f"\n\n📊 Total: {1 + len(self.sprint_data.milestones) + total_tasks} cards"
        
        messagebox.showinfo("Card Preview", preview_text)
        
    def generate_cards(self):
        """Generate Trello cards"""
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
                self.status_var.set("Generating cards...")
                self.progress_var.set(10)
                
                # Create client and generator
                client = TrelloClient(self.config)
                generator = SprintGenerator(client)
                
                self.progress_var.set(30)
                
                # Generate cards
                result = generator.generate_cards(
                    self.sprint_data, 
                    board_id, 
                    self.list_name_var.get()
                )
                
                self.progress_var.set(100)
                
                # Show success message
                success_msg = f"""✅ Cards generated successfully!

📋 Sprint card: {result['sprint_card']['name']}
🎯 Milestone cards: {len(result['milestone_cards'])}
📝 Task cards: {len(result['task_cards'])}
🏷️ Labels created: {len(result['created_labels'])}

Total: {1 + len(result['milestone_cards']) + len(result['task_cards'])} cards created!"""
                
                self.status_var.set("Cards generated successfully!")
                messagebox.showinfo("Success", success_msg)
                
            except Exception as e:
                self.status_var.set(f"Generation failed: {e}")
                messagebox.showerror("Generation Error", str(e))
            finally:
                self.progress_var.set(0)
                
        threading.Thread(target=generate_thread, daemon=True).start()
        
    def run(self):
        """Run the GUI application"""
        # Load initial configuration if available
        try:
            self.load_config()
        except:
            pass
            
        self.root.mainloop()


def main():
    """Main entry point for GUI"""
    app = ModernTrelloGUI()
    app.run()


if __name__ == "__main__":
    main()
