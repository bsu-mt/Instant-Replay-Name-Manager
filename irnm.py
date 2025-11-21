import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
import re
import subprocess
import platform

try:
    from send2trash import send2trash
except ImportError:
    send2trash = None

# Config file path
CONFIG_FILE = "./config.json"

class VideoManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Instant Replay Name Manager")
        self.root.geometry("1100x750")
        self.root.configure(bg="#f0f2f5")  # Overall background color

        # --- SET ICON ---
        # Looks for icon.ico in the same folder. If found, sets it.
        if os.path.exists("icon.ico"):
            try:
                self.root.iconbitmap("icon.ico")
            except Exception:
                pass # Ignore icon errors
        
        # Initialize data
        self.current_folder = ""
        self.video_files = []
        # Default tags
        self.available_tags = ["3k", "4k", "ace", "clutch", "funny", "marshal", "airshot"] 
        self.selected_tags_vars = {}
        
        # Variables for search and Tab cycling
        self.filtered_tags = []      # List of tags matching current search
        self.tab_cycle_index = -1    # Current index for Tab cycling
        
        # Load configuration
        self.load_config()
        
        # --- Style Configuration ---
        self.setup_styles()
        
        # --- Build UI ---
        self.create_ui()
        
        # Auto-load previous folder
        if self.current_folder and os.path.exists(self.current_folder):
            self.refresh_file_list()
        else:
            self.current_folder = ""

    def setup_styles(self):
        """Configure styles (Unified font: Arial)"""
        self.style = ttk.Style()
        self.style.theme_use('clam')
        
        # Color definitions
        PRIMARY_COLOR = "#0078d4"    # Windows Blue
        DANGER_COLOR = "#d13438"     # Warning Red
        SUCCESS_COLOR = "#107c10"    # Success Green
        BG_COLOR = "#ffffff"
        
        # --- Font Configuration (Unified Arial) ---
        self.font_main = ("Arial", 11)
        self.font_bold = ("Arial", 11, "bold")
        self.font_large = ("Arial", 12, "bold")
        self.font_mono = ("Arial", 12)  # Used for lists, user requested Arial everywhere
        self.font_hint = ("Arial", 9)

        # General Frame
        self.style.configure("TFrame", background="#f0f2f5")
        self.style.configure("Card.TFrame", background=BG_COLOR, relief="flat")
        
        # Labelframe
        self.style.configure("Card.TLabelframe", background=BG_COLOR, relief="solid", borderwidth=1)
        self.style.configure("Card.TLabelframe.Label", background=BG_COLOR, foreground="#555", font=self.font_bold)

        # Label
        self.style.configure("TLabel", background="#f0f2f5", foreground="#333", font=self.font_main)
        self.style.configure("Card.TLabel", background=BG_COLOR, foreground="#333", font=self.font_main)
        
        # Special Label Styles
        self.style.configure("Title.TLabel", background=BG_COLOR, foreground="#000", font=("Arial", 14, "bold"))
        self.style.configure("Preview.TLabel", background=BG_COLOR, foreground=PRIMARY_COLOR, font=("Arial", 12, "bold"))
        self.style.configure("Hint.TLabel", background=BG_COLOR, foreground="#999999", font=self.font_hint)

        # Button (Normal)
        self.style.configure("TButton", font=self.font_main, padding=6, borderwidth=0)
        self.style.map("TButton", background=[('active', '#e1e1e1')])

        # Button (Primary - Blue)
        self.style.configure("Primary.TButton", background=PRIMARY_COLOR, foreground="white", font=self.font_bold, borderwidth=0)
        self.style.map("Primary.TButton", background=[('active', '#006cc1'), ('pressed', '#005a9e')])

        # Button (Danger - Red)
        self.style.configure("Danger.TButton", background=DANGER_COLOR, foreground="white", font=self.font_bold, borderwidth=0)
        self.style.map("Danger.TButton", background=[('active', '#b12b2e')])

        # Button (Success - Green)
        self.style.configure("Success.TButton", background=SUCCESS_COLOR, foreground="white", font=self.font_bold, borderwidth=0)
        self.style.map("Success.TButton", background=[('active', '#0e6f0e')])

        # Checkbox
        self.style.configure("TCheckbutton", background=BG_COLOR, font=self.font_main)

    def create_ui(self):
        # --- Header (Dark Background) ---
        header_frame = tk.Frame(self.root, bg="#2b2d30", height=60)
        header_frame.pack(fill=tk.X, side=tk.TOP)
        header_frame.pack_propagate(False) # Fixed height

        # Title
        tk.Label(header_frame, text="Instant Replay Name Manager", bg="#2b2d30", fg="#ff4655", font=("Arial", 16, "bold", "italic")).pack(side=tk.LEFT, padx=20)
        
        # Folder Path Display
        self.folder_label = tk.Label(header_frame, text=self.current_folder or "No folder selected", bg="#2b2d30", fg="#cccccc", font=("Arial", 11))
        self.folder_label.pack(side=tk.LEFT, padx=10)
        
        # Header Buttons
        btn_bar = tk.Frame(header_frame, bg="#2b2d30")
        btn_bar.pack(side=tk.RIGHT, padx=20)

        self.create_header_btn(btn_bar, "📂 Select Folder", self.select_folder)
        self.create_header_btn(btn_bar, "🔄 Refresh", self.refresh_file_list)
        
        # --- Main Container ---
        main_container = ttk.Frame(self.root, padding=15)
        main_container.pack(fill=tk.BOTH, expand=True)

        # Paned Window (Splitter)
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)

        # --- Left Panel: File List ---
        left_panel = ttk.Frame(paned, style="Card.TFrame")
        paned.add(left_panel, weight=1)

        # List Header
        list_header = tk.Frame(left_panel, bg="white", padx=10, pady=10)
        list_header.pack(fill=tk.X)
        ttk.Label(list_header, text="Video File List", font=self.font_large, style="Card.TLabel").pack(side=tk.LEFT)
        ttk.Label(list_header, text="(Time Descending)", foreground="gray", style="Card.TLabel").pack(side=tk.LEFT, padx=5)

        # Listbox Container
        list_frame = tk.Frame(left_panel, bg="white")
        list_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.file_listbox = tk.Listbox(
            list_frame, 
            yscrollcommand=scrollbar.set, 
            font=self.font_mono,
            selectmode=tk.SINGLE,
            bd=0,
            highlightthickness=0,
            activestyle='none',
            selectbackground="#e3f2fd",
            selectforeground="#000000",
            fg="#333",
            height=20
        )
        self.file_listbox.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Event Bindings
        self.file_listbox.bind('<<ListboxSelect>>', self.on_file_select)
        self.file_listbox.bind('<Double-1>', lambda event: self.open_video()) # Double click to open

        # --- NEW BINDINGS FOR DELETION ---
        self.file_listbox.bind('<Delete>', self.delete_to_recycle_bin)
        self.file_listbox.bind('<Shift-Delete>', self.delete_permanently)
        
        scrollbar.config(command=self.file_listbox.yview)

        # Batch Action Bar (Bottom Left)
        batch_action_frame = tk.Frame(left_panel, bg="#f8f9fa", height=50, padx=10)
        batch_action_frame.pack(fill=tk.X, side=tk.BOTTOM, pady=(1, 0))
        
        ttk.Button(batch_action_frame, text="⚠️ Batch Format (DVR -> Index)", command=self.batch_format_base_names, style="Danger.TButton").pack(side=tk.LEFT, pady=10, padx=5)
        ttk.Button(batch_action_frame, text="✂️ Replace Trimmed (Trim -> Orig)", command=self.replace_trimmed_files, style="Primary.TButton").pack(side=tk.RIGHT, pady=10, padx=5)

        # --- Right Panel: Details & Operations ---
        right_panel = ttk.Frame(paned, padding=(15, 0, 0, 0))
        paned.add(right_panel, weight=1)

        # Card 1: Currently Selected
        info_card = ttk.Labelframe(right_panel, text="Currently Selected", style="Card.TLabelframe", padding=15)
        info_card.pack(fill=tk.X, pady=(0, 15))
        
        self.current_file_label = ttk.Label(info_card, text="Select a video from the list...", wraplength=400, style="Title.TLabel")
        self.current_file_label.pack(anchor=tk.W, fill=tk.X)

        btn_row = ttk.Frame(info_card, style="Card.TFrame")
        btn_row.pack(fill=tk.X, pady=(15, 0))
        ttk.Button(btn_row, text="🎬 Open Player / Trim", command=self.open_video).pack(side=tk.LEFT)
        ttk.Label(btn_row, text="Tip: After saving a trim copy, click 'Replace Trimmed' below.", foreground="#888", style="Card.TLabel").pack(side=tk.LEFT, padx=10)

        # Card 2: Tag System
        tag_card = ttk.Labelframe(right_panel, text="Add Tags", style="Card.TLabelframe", padding=15)
        tag_card.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Search / New Tag Bar
        search_row = ttk.Frame(tag_card, style="Card.TFrame")
        search_row.pack(fill=tk.X, padx=10, pady=(10, 5))
        
        ttk.Label(search_row, text="🔍 Search or Create Tag:", style="Card.TLabel").pack(side=tk.LEFT)
        
        # Combobox for search
        self.new_tag_combobox = ttk.Combobox(search_row, font=("Arial", 11))
        self.new_tag_combobox.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=5)
        
        # Bindings
        self.new_tag_combobox.bind("<Return>", lambda event: self.add_or_select_tag())
        self.new_tag_combobox.bind("<KeyRelease>", self.on_tag_search_type) # Real-time filtering
        self.new_tag_combobox.bind("<Tab>", self.on_tab_cycle) # Tab cycling
        
        ttk.Button(search_row, text="+ Add/Select", command=self.add_or_select_tag).pack(side=tk.LEFT)

        # Tags Grid Area
        self.tags_frame = ttk.Frame(tag_card, style="Card.TFrame")
        self.tags_frame.pack(fill=tk.BOTH, expand=True, pady=5)
        
        # Hint text
        ttk.Label(tag_card, text="💡 Tip: Press Tab to cycle matches; Right-click tag to delete.", style="Hint.TLabel").pack(anchor=tk.W, padx=10, pady=(0, 5))

        # Card 3: Preview & Apply
        action_card = ttk.Labelframe(right_panel, text="Confirm Changes", style="Card.TLabelframe", padding=15)
        action_card.pack(fill=tk.X)

        ttk.Label(action_card, text="Filename Preview (Editable):", style="Card.TLabel").pack(anchor=tk.W)
        
        # Preview Entry (Arial)
        self.preview_entry = ttk.Entry(action_card, font=("Arial", 11))
        self.preview_entry.pack(anchor=tk.W, pady=5, fill=tk.X)

        ttk.Button(action_card, text="✅ Apply Rename", command=self.apply_rename, style="Success.TButton", width=20).pack(anchor=tk.E, pady=(10, 0))

    def create_header_btn(self, parent, text, command):
        """Create flat button for header"""
        btn = tk.Button(parent, text=text, command=command, 
                        bg="#404246", fg="white", 
                        activebackground="#505256", activeforeground="white",
                        bd=0, padx=15, pady=5, font=("Arial", 9))
        btn.pack(side=tk.LEFT, padx=2)

    # ---------------- Logic Section ----------------
    
    def load_config(self):
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    self.current_folder = data.get('last_folder', "")
                    saved_tags = data.get('tags', [])
                    if saved_tags:
                        self.available_tags = saved_tags
            except:
                pass

    def save_config(self):
        # Ensure directory exists
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        data = {
            'last_folder': self.current_folder,
            'tags': self.available_tags
        }
        with open(CONFIG_FILE, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=4)

    def select_folder(self):
        folder = filedialog.askdirectory()
        if folder:
            self.current_folder = folder
            self.folder_label.config(text=folder)
            self.save_config()
            self.refresh_file_list()

    def refresh_file_list(self):
        if not self.current_folder:
            return
        
        self.file_listbox.delete(0, tk.END)
        self.video_files = []
        
        try:
            files = os.listdir(self.current_folder)
            files = [f for f in files if f.lower().endswith('.mp4')]
            files.sort(reverse=True) 
            
            for f in files:
                self.file_listbox.insert(tk.END, f)
                self.video_files.append(f)
                
            self.current_file_label.config(text="Select a video from the list...")
            self.preview_entry.delete(0, tk.END)
            self.preview_entry.insert(0, "...")
            
            self.refresh_tags_ui()
            
        except Exception as e:
            messagebox.showerror("Error", f"Cannot read folder: {e}")

    def batch_format_base_names(self):
        if not self.current_folder:
            return

        files = [f for f in os.listdir(self.current_folder) if f.lower().endswith('.mp4')]
        
        pattern = re.compile(r"(.+ \d{4}\.\d{2}\.\d{2}) - .*DVR.*\.mp4", re.IGNORECASE)
        groups = {}
        
        for f in files:
            match = pattern.match(f)
            if match:
                date_prefix = match.group(1)
                if date_prefix not in groups:
                    groups[date_prefix] = []
                groups[date_prefix].append(f)
        
        count = 0
        for prefix, file_list in groups.items():
            file_list.sort(key=lambda x: os.path.getmtime(os.path.join(self.current_folder, x)))
            
            for idx, filename in enumerate(file_list):
                old_path = os.path.join(self.current_folder, filename)
                new_name = f"{prefix} - {idx + 1}.mp4"
                new_path = os.path.join(self.current_folder, new_name)
                
                if filename != new_name:
                    while os.path.exists(new_path):
                         break 
                    else:
                        try:
                            os.rename(old_path, new_path)
                            count += 1
                        except OSError as e:
                            print(f"Error renaming {filename}: {e}")

        messagebox.showinfo("Done", f"Formatted {count} video files.")
        self.refresh_file_list()

    def replace_trimmed_files(self):
        if not self.current_folder:
            return
            
        files = [f for f in os.listdir(self.current_folder) if f.lower().endswith('.mp4')]
        replaced_count = 0
        trim_pattern = re.compile(r"(.+?)(?:[\s_-]+Trim)\.mp4$", re.IGNORECASE)
        
        for filename in files:
            match = trim_pattern.match(filename)
            if match:
                base_name_no_ext = match.group(1)
                trimmed_file_path = os.path.join(self.current_folder, filename)
                original_filename = f"{base_name_no_ext}.mp4"
                original_file_path = os.path.join(self.current_folder, original_filename)
                
                if os.path.exists(original_file_path):
                    try:
                        os.remove(original_file_path)
                        os.rename(trimmed_file_path, original_file_path)
                        replaced_count += 1
                    except OSError as e:
                        messagebox.showerror("Error", f"Error replacing file:\n{e}")
                        return

        if replaced_count > 0:
            messagebox.showinfo("Done", f"Successfully replaced {replaced_count} trimmed videos.")
            self.refresh_file_list()
        else:
            messagebox.showinfo("Info", "No matching Trim files and originals found.\n(Filename must contain 'Trim' and original must exist)")

    def refresh_tags_ui(self):
        for widget in self.tags_frame.winfo_children():
            widget.destroy()
            
        self.selected_tags_vars = {}
        
        # Sort tags
        self.available_tags.sort()

        # Update Combobox values
        if hasattr(self, 'new_tag_combobox'):
            self.new_tag_combobox['values'] = self.available_tags
        
        # Grid layout for tags
        col_max = 8
        for i, tag in enumerate(self.available_tags):
            var = tk.BooleanVar()
            chk = ttk.Checkbutton(self.tags_frame, text=tag, variable=var, command=self.update_preview_name)
            
            row = i // col_max
            col = i % col_max
            chk.grid(row=row, column=col, sticky="w", padx=10, pady=5)
            
            self.selected_tags_vars[tag] = var
            
            # Right-click to delete binding
            chk.bind("<Button-3>", lambda event, t=tag: self.show_tag_context_menu(event, t))
            if platform.system() == 'Darwin':
                chk.bind("<Button-2>", lambda event, t=tag: self.show_tag_context_menu(event, t))

    def show_tag_context_menu(self, event, tag):
        menu = tk.Menu(self.root, tearoff=0)
        menu.add_command(label=f"🗑️ Delete tag '{tag}'", command=lambda: self.delete_custom_tag(tag))
        menu.post(event.x_root, event.y_root)

    def delete_custom_tag(self, tag):
        if messagebox.askyesno("Delete Confirmation", f"Permanently delete tag '{tag}'?"):
            if tag in self.available_tags:
                self.available_tags.remove(tag)
                if tag in self.selected_tags_vars:
                    del self.selected_tags_vars[tag]
                
                self.save_config()
                self.refresh_tags_ui()
                self.update_preview_name()

    def on_tag_search_type(self, event):
        """Filter logic for Combobox"""
        # Ignore navigation/control keys
        if event.keysym in ['Up', 'Down', 'Return', 'Tab']:
            return
            
        current_text = self.new_tag_combobox.get()
        
        # If empty, show all, reset cycle
        if current_text == '':
            self.new_tag_combobox['values'] = self.available_tags
            self.filtered_tags = self.available_tags
            self.tab_cycle_index = -1
        else:
            # Filter data
            self.filtered_tags = []
            for item in self.available_tags:
                if current_text.lower() in item.lower():
                    self.filtered_tags.append(item)
            
            # Update values
            self.new_tag_combobox['values'] = self.filtered_tags
            # Reset cycle index on input change
            self.tab_cycle_index = -1

    def on_tab_cycle(self, event):
        """Handle Tab key cycling"""
        if not self.filtered_tags:
            return # No items to cycle
        
        # Increment index and wrap around
        self.tab_cycle_index = (self.tab_cycle_index + 1) % len(self.filtered_tags)
        
        # Get next tag
        next_tag = self.filtered_tags[self.tab_cycle_index]
        
        # Update text
        self.new_tag_combobox.delete(0, tk.END)
        self.new_tag_combobox.insert(0, next_tag)
        
        # Prevent default focus change
        return 'break'

    def add_or_select_tag(self):
        """Smart add or select tag"""
        input_text = self.new_tag_combobox.get().strip()
        if not input_text:
            return
            
        # Check if exists (case-insensitive)
        existing_tag = None
        for tag in self.available_tags:
            if tag.lower() == input_text.lower():
                existing_tag = tag
                break
        
        if existing_tag:
            # Select existing
            if existing_tag in self.selected_tags_vars:
                self.selected_tags_vars[existing_tag].set(True)
                self.update_preview_name()
                self.new_tag_combobox.set('')
                # Restore full list
                self.new_tag_combobox['values'] = self.available_tags
                self.filtered_tags = self.available_tags
                self.tab_cycle_index = -1
        else:
            # Create new
            self.available_tags.append(input_text)
            self.save_config()
            self.refresh_tags_ui()
            
            # Select the new one
            if input_text in self.selected_tags_vars:
                self.selected_tags_vars[input_text].set(True)
            
            self.update_preview_name()
            self.new_tag_combobox.set('')
            self.filtered_tags = self.available_tags
            self.tab_cycle_index = -1

    def on_file_select(self, event):
        selection = self.file_listbox.curselection()
        if selection:
            filename = self.file_listbox.get(selection[0])
            self.current_file_label.config(text=filename)
            
            for var in self.selected_tags_vars.values():
                var.set(False)
            
            name_part = os.path.splitext(filename)[0]
            parts = name_part.split('-')
            if len(parts) > 2:
                potential_tags = parts[2:] 
                for t in potential_tags:
                    if t in self.selected_tags_vars:
                        self.selected_tags_vars[t].set(True)
                        
            self.update_preview_name()

    def update_preview_name(self):
        selection = self.file_listbox.curselection()
        if not selection:
            self.preview_entry.delete(0, tk.END)
            self.preview_entry.insert(0, "...")
            return
            
        original_name = self.file_listbox.get(selection[0])
        base, ext = os.path.splitext(original_name)
        
        # 修改: 通用化正则，匹配 "任意游戏名 日期 - 序号"
        match = re.match(r"(.+ \d{4}\.\d{2}\.\d{2} - \d+)", base)
        
        if match:
            core_name = match.group(1)
        else:
            core_name = base
            
        active_tags = [tag for tag, var in self.selected_tags_vars.items() if var.get()]
        
        if active_tags:
            new_suffix = "-" + "-".join(active_tags)
            new_name = f"{core_name}{new_suffix}{ext}"
        else:
            new_name = f"{core_name}{ext}"
            
        self.preview_entry.delete(0, tk.END)
        self.preview_entry.insert(0, new_name)

    def apply_rename(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
            
        old_name = self.file_listbox.get(selection[0])
        new_name = self.preview_entry.get().strip()
        
        if not new_name:
            messagebox.showwarning("Info", "Filename cannot be empty")
            return

        if old_name == new_name:
            return
            
        old_path = os.path.join(self.current_folder, old_name)
        new_path = os.path.join(self.current_folder, new_name)
        
        try:
            os.rename(old_path, new_path)
            index = selection[0]
            self.file_listbox.delete(index)
            self.file_listbox.insert(index, new_name)
            self.file_listbox.selection_set(index)
            self.current_file_label.config(text=new_name)
        except OSError as e:
            messagebox.showerror("Error", f"Rename failed (File might be in use):\n{e}")

    def open_video(self):
        selection = self.file_listbox.curselection()
        if not selection:
            return
        filename = self.file_listbox.get(selection[0])
        filepath = os.path.join(self.current_folder, filename)
        
        if platform.system() == 'Windows':
            os.startfile(filepath)
        elif platform.system() == 'Darwin': 
            subprocess.call(('open', filepath))
        else: 
            subprocess.call(('xdg-open', filepath))

    # ------------------------------------------------
    # NEW DELETE FUNCTIONS
    # ------------------------------------------------
    
    def delete_to_recycle_bin(self, event):
        """Delete key: Send to Recycle Bin"""
        if send2trash is None:
            messagebox.showerror("Missing Library", "Please run 'pip install send2trash' to use the Recycle Bin feature.")
            return

        selection = self.file_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        filename = self.file_listbox.get(index)
        filepath = os.path.join(self.current_folder, filename)

        # Optional: Confirmation for recycle bin (usually not needed, but safer)
        if not messagebox.askyesno("Move to Trash", f"Move '{filename}' to Recycle Bin?"):
            return

        try:
            send2trash(filepath)
            # Update UI
            self.file_listbox.delete(index)
            self.video_files.remove(filename)
            self.current_file_label.config(text="Select a video...")
            self.preview_entry.delete(0, tk.END)
            
            # Select the next item if available
            if self.file_listbox.size() > index:
                self.file_listbox.selection_set(index)
                self.file_listbox.event_generate("<<ListboxSelect>>")
            elif self.file_listbox.size() > 0:
                self.file_listbox.selection_set(tk.END)
                self.file_listbox.event_generate("<<ListboxSelect>>")

        except Exception as e:
            messagebox.showerror("Error", f"Could not move to trash:\n{e}")

    def delete_permanently(self, event):
        """Shift+Delete: Permanently Remove"""
        selection = self.file_listbox.curselection()
        if not selection:
            return

        index = selection[0]
        filename = self.file_listbox.get(index)
        filepath = os.path.join(self.current_folder, filename)

        # STRONG Confirmation
        if not messagebox.askyesno("Permanent Delete", f"⚠️ PERMANENTLY delete '{filename}'?\nThis cannot be undone!", icon='warning'):
            return

        try:
            os.remove(filepath)
            # Update UI
            self.file_listbox.delete(index)
            self.video_files.remove(filename)
            self.current_file_label.config(text="Select a video...")
            self.preview_entry.delete(0, tk.END)
            
            # Select the next item logic
            if self.file_listbox.size() > index:
                self.file_listbox.selection_set(index)
                self.file_listbox.event_generate("<<ListboxSelect>>")
            elif self.file_listbox.size() > 0:
                self.file_listbox.selection_set(tk.END)
                self.file_listbox.event_generate("<<ListboxSelect>>")
                
        except OSError as e:
            messagebox.showerror("Error", f"Could not delete file:\n{e}")
            
        # Return 'break' to prevent the standard Delete event from also firing
        return 'break'

if __name__ == "__main__":
    root = tk.Tk()
    app = VideoManagerApp(root)
    root.mainloop()