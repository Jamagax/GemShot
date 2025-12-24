import customtkinter as ctk
import tkinter as tk
from PIL import Image, ImageTk
import os
import datetime
from src.core.config import ConfigManager, COLORS
from src.core.data_manager import data_manager
from src.utils.platform_utils import open_folder

class CaptureCard(ctk.CTkFrame):
    def __init__(self, parent, entry, on_click):
        super().__init__(parent, fg_color=COLORS["panel"], corner_radius=15, border_width=1, border_color=COLORS["border"])
        self.entry = entry
        self.on_click = on_click

        self.setup_ui()
        
    def setup_ui(self):
        # --- PATH RECOVERY (Auto-Healing) ---
        img_path = self.entry.get('file_path', '')
        
        # Ensure path is absolute if it exists as relative
        if img_path and not os.path.isabs(img_path):
            img_path = os.path.abspath(img_path)

        # If path is dead, try to reconstruct it logically
        if not img_path or not os.path.exists(img_path):
            print(f"[DASHBOARD] Image missing: {img_path}. Attempting recovery...")
            recovered_path = self._try_recover_path(img_path)
            if recovered_path:
                img_path = recovered_path
                print(f"[DASHBOARD] ✅ Found at: {recovered_path}")
                # Update the entry for this session
                self.entry['file_path'] = recovered_path
            else:
                print(f"[DASHBOARD] ❌ Failed to recover: {self.entry.get('title')}")

        # Thumbnail
        if img_path and os.path.exists(img_path):
            try:
                pil_img = Image.open(img_path)
                pil_img.thumbnail((320, 200)) # Better quality
                self.thumb_img = ctk.CTkImage(pil_img, size=(280, 150))
                self.lbl_thumb = ctk.CTkLabel(self, image=self.thumb_img, text="", corner_radius=10)
                self.lbl_thumb.pack(padx=8, pady=(8, 4))
                
                # Click on image to view detail
                self.lbl_thumb.bind("<Button-1>", lambda e: self.on_click(self.entry))
            except:
                self.lbl_thumb = ctk.CTkLabel(self, text="⚠️ Image Error", height=150, fg_color=COLORS["bg"], corner_radius=10)
                self.lbl_thumb.pack(padx=8, pady=(8, 4), fill="x")
        else:
            self.lbl_thumb = ctk.CTkLabel(self, text="📝 Entry Only", height=150, fg_color=COLORS["bg"], corner_radius=10, text_color=COLORS["text_dim"])
            self.lbl_thumb.pack(padx=8, pady=(8, 4), fill="x")

        # Info
        info_frame = ctk.CTkFrame(self, fg_color="transparent")
        info_frame.pack(fill="x", padx=10, pady=(2, 8))
        
        title = self.entry.get('title', 'Untitled') or "Untitled Capture"
        if len(title) > 35: title = title[:32] + "..."
        
        lbl_title = ctk.CTkLabel(info_frame, text=title, font=("Inter", 12, "bold"), text_color=COLORS["text"], anchor="w")
        lbl_title.pack(fill="x")
        
        meta = f"{self.entry.get('universe', 'No Area')} / {self.entry.get('project', 'No Project')}"
        ctk.CTkLabel(info_frame, text=meta, font=("Inter", 10), text_color=COLORS["text_dim"], anchor="w").pack(fill="x")
        
        # Footer Actions (More compact)
        btn_row = ctk.CTkFrame(self, fg_color="transparent")
        btn_row.pack(fill="x", padx=10, pady=(0, 10))
        
        ctk.CTkButton(btn_row, text="View Detail", height=28, font=("Inter", 10, "bold"), fg_color=COLORS["primary"], corner_radius=8, command=lambda: self.on_click(self.entry)).pack(side="left", fill="x", expand=True, padx=(0, 4))
        ctk.CTkButton(btn_row, text="📂", width=35, height=28, fg_color="transparent", border_width=1, border_color=COLORS["border"], text_color=COLORS["text"], corner_radius=8, command=self.open_dir).pack(side="right")

    def _try_recover_path(self, old_path):
        """Attempts to find the image in PARA structure if moved."""
        title = self.entry.get('title', '').strip()
        uni = self.entry.get('universe', '').strip()
        proj = self.entry.get('project', '').strip()
        
        # Priority: Extract timestamp from old path if possible (it's the most unique key)
        timestamp = None
        if old_path:
            # Extract numbers from temp_XXXXXXXXXX.png
            import re
            match = re.search(r'(\d{10})', os.path.basename(old_path))
            if match:
                timestamp = match.group(1)

        # Build search directories
        paths = ConfigManager.get_dynamic_paths()
        search_dirs = []
        
        # 1. Broad PARA Project Attachment search
        if proj:
            search_dirs.append(os.path.join(paths['projects'], proj, "attachments"))
            search_dirs.append(os.path.join(paths['projects'], proj)) # Sibling search
        
        # 2. Broad PARA Universe Attachment search
        if uni:
            search_dirs.append(os.path.join(paths['universes'], uni, "attachments"))
            search_dirs.append(os.path.join(paths['universes'], uni)) # Sibling search
            
        # 3. Local output
        search_dirs.append(os.path.abspath(os.path.join("output", "attachments")))
        
        # 4. DEEP SCAN Roots (Last Resort)
        search_dirs.append(paths['projects'])
        search_dirs.append(paths['universes'])

        filename_part = "".join(x for x in title if x.isalnum() or x in " -_").strip()
        
        for s_dir in search_dirs:
            if not os.path.exists(s_dir): continue
            
            try:
                # For root folders, look only 1 level deep in subfolders
                is_root = s_dir in [paths['projects'], paths['universes']]
                
                if is_root:
                    # Scan subfolders attachments
                    for sub in os.listdir(s_dir):
                        sub_path = os.path.join(s_dir, sub, "attachments")
                        if os.path.exists(sub_path):
                            res = self._scan_dir_for_match(sub_path, timestamp, filename_part)
                            if res: return res
                else:
                    res = self._scan_dir_for_match(s_dir, timestamp, filename_part)
                    if res: return res
            except:
                continue
                
        return None

    def _scan_dir_for_match(self, directory, timestamp, filename_part):
        try:
            for f in os.listdir(directory):
                # Priority 1: Timestamp (ID)
                if timestamp and timestamp in f:
                    return os.path.abspath(os.path.join(directory, f))
                # Priority 2: Title match
                if filename_part and len(filename_part) > 5:
                    if filename_part.lower() in f.lower() and f.lower().endswith(".png"):
                        return os.path.abspath(os.path.join(directory, f))
        except:
            pass
        return None

    def open_dir(self):
        path = self.entry.get('file_path', '')
        if path:
            open_folder(os.path.dirname(path))

class DashboardWindow(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("GemShot Dashboard - Visual Knowledge Base")
        self.geometry("1400x900")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=COLORS["bg"])
        
        self.entries = data_manager._load_json(os.path.join("data", "tasks.json"))
        self.filtered_entries = self.entries
        
        self.setup_ui()
        self.refresh_grid()

    def setup_ui(self):
        # --- TOP NAVIGATION ---
        self.top_nav = ctk.CTkFrame(self, fg_color=COLORS["panel"], height=80, corner_radius=0)
        self.top_nav.pack(side="top", fill="x")
        self.top_nav.pack_propagate(False)
        
        ctk.CTkLabel(self.top_nav, text="💎 GEMSHOT DASHBOARD", font=("Inter", 20, "bold"), text_color=COLORS["primary"]).pack(side="left", padx=30)
        
        # Search
        self.search_var = tk.StringVar()
        self.search_var.trace_add("write", self.filter_data)
        self.search_entry = ctk.CTkEntry(self.top_nav, placeholder_text="Search in Knowledge Base...", width=400, height=40, font=("Inter", 12), fg_color=COLORS["bg"], border_color=COLORS["border"], textvariable=self.search_var)
        self.search_entry.pack(side="left", padx=20)
        
        # Stats
        stats_text = f"Total Captures: {len(self.entries)}"
        ctk.CTkLabel(self.top_nav, text=stats_text, font=("Inter", 12), text_color=COLORS["text_dim"]).pack(side="right", padx=30)

        # --- SIDEBAR ---
        self.sidebar = ctk.CTkFrame(self, fg_color=COLORS["bg"], width=250, corner_radius=0)
        self.sidebar.pack(side="left", fill="y", padx=10, pady=10)
        
        ctk.CTkLabel(self.sidebar, text="CATEGORIES", font=("Inter", 12, "bold"), text_color=COLORS["text_dim"]).pack(anchor="w", padx=20, pady=(20, 10))
        
        self.btn_all = self.add_sidebar_btn("📚 All Entries", "ALL")
        self.btn_tasks = self.add_sidebar_btn("✅ Tasks", "Task")
        self.btn_notes = self.add_sidebar_btn("📝 Notes", "Nota")
        self.btn_screens = self.add_sidebar_btn("🖥️ Screenshots", "Screen")
        
        ctk.set_appearance_mode(ConfigManager.get_colors().get('ctk_mode', 'dark'))

        # --- MAIN CONTENT ---
        self.main_content = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.main_content.pack(side="right", fill="both", expand=True, padx=10, pady=10)
        
        # Grid config
        self.main_content.grid_columnconfigure((0,1,2,3), weight=1)

    def add_sidebar_btn(self, text, filter_val):
        btn = ctk.CTkButton(self.sidebar, text=text, anchor="w", fg_color="transparent", text_color=COLORS["text"], hover_color=COLORS["panel"], height=40, font=("Inter", 12), command=lambda: self.set_category_filter(filter_val))
        btn.pack(fill="x", padx=10, pady=2)
        return btn

    def set_category_filter(self, cat):
        self.current_cat = cat
        self.filter_data()

    def filter_data(self, *args):
        query = self.search_var.get().lower()
        cat = getattr(self, 'current_cat', 'ALL')
        
        self.filtered_entries = []
        for e in self.entries:
            # Search filter
            match_query = query in e.get('title', '').lower() or query in e.get('tags', '').lower() or query in e.get('notes', '').lower()
            # Category filter
            match_cat = (cat == 'ALL' or e.get('type') == cat)
            
            if match_query and match_cat:
                self.filtered_entries.append(e)
                
        self.refresh_grid()

    def refresh_grid(self):
        # Clear existing
        for widget in self.main_content.winfo_children():
            widget.destroy()
            
        columns = 4
        for i, entry in enumerate(self.filtered_entries):
            r, c = divmod(i, columns)
            card = CaptureCard(self.main_content, entry, self.view_detail)
            card.grid(row=r, column=c, padx=10, pady=10, sticky="nsew")

    def view_detail(self, entry):
        md_path = entry.get('md_path')
        img_path = self.entry['file_path'] if hasattr(self, 'entry') else entry.get('file_path')
        title = entry.get('title', '').strip()
        
        # --- MD RECOVERY ---
        if not md_path or not os.path.exists(md_path):
            recovered_md = self._try_recover_md(entry)
            if recovered_md:
                md_path = recovered_md
        
        # Priority: Open Markdown Note (Obsidian context)
        if md_path and os.path.exists(md_path):
            os.startfile(md_path)
            self.show_toast(f"Opening Note: {title}")
        elif img_path and os.path.exists(img_path):
            os.startfile(img_path)
            self.show_toast(f"Opening Image: {title}")
        else:
            self.show_toast("⚠️ File not found in Vault.")

    def _try_recover_md(self, entry):
        """Finds the .md note if it was moved to PARA."""
        title = entry.get('title', '').strip()
        uni = entry.get('universe', '').strip()
        proj = entry.get('project', '').strip()
        if not title: return None
        
        paths = ConfigManager.get_dynamic_paths()
        search_dirs = []
        if proj: search_dirs.append(os.path.join(paths['projects'], proj))
        if uni: search_dirs.append(os.path.join(paths['universes'], uni))
        
        filename_part = "".join(x for x in title if x.isalnum() or x in " -_").strip()
        
        for s_dir in search_dirs:
            if not os.path.exists(s_dir): continue
            try:
                for f in os.listdir(s_dir):
                    if filename_part.lower() in f.lower() and f.lower().endswith(".md"):
                        return os.path.abspath(os.path.join(s_dir, f))
            except: continue
        return None

    def show_toast(self, message):
        print(f"[DASHBOARD] {message}")

