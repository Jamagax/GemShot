import customtkinter as ctk
import tkinter as tk
from tkinter import messagebox, colorchooser
from PIL import Image, ImageTk, ImageDraw, ImageFont
import datetime
import os
import math
import json

# Imports from our new modular structure
from src.core.config import ConfigManager, COLORS, PATHS
from src.core.ai import AIService
from src.core.data_manager import data_manager
from src.utils.helpers import draw_arrow_pil
from src.utils.platform_utils import copy_image_to_clipboard
from logger_agent import log_agent # Import logger

class EditorWindow(ctk.CTkToplevel):
    def __init__(self, parent, screenshot_path, region, on_save, on_cancel, source=""):
        # Dynamic Path Loading
        self.paths = ConfigManager.get_dynamic_paths()
        self.UNIVERSES_ROOT = self.paths["universes"]
        self.PROJECTS_ROOT = self.paths["projects"]

        super().__init__(parent)
        self.title("LifeOS Capture Station")
        self.geometry("1400x900")
        self.after(0, lambda: self.state("zoomed"))
        self.configure(fg_color=COLORS["bg"])
        
        self.screenshot_path = screenshot_path
        self.on_save_cb = on_save
        self.on_cancel_cb = on_cancel
        self.source = source
        self.config = ConfigManager.load()
        self.ai_service = AIService(api_key=self.config.get('gemini_api_key'))

        # Canvas State
        self.tool = "pen"
        self.color = "red"
        self.is_drawing = False
        self.current_shape = None
        self.draw_color_hex = "#F92672" # Default Monokai Pink
        
        self.complexity_level = self.config.get('complexity_level', 'Zen')
        self.form_groups = {'basic': [], 'standard': [], 'pro': []}
        self.detected_software = "" 
        self.image_active = True 
        self.custom_target_path = self.config.get('last_target_override')

        self.setup_ui()
        self.load_image()
        
        # Delayed initial target update
        self.after(100, self.update_target_path)
        self.after(600, lambda: self.apply_complexity(self.complexity_level))
        
        # Binds
        self.bind("<Escape>", lambda e: self.close_window())

    # ... (setup_ui and other methods)

    # ... Drawing logic starts here (setup_ui) ...


    def setup_ui(self):
        # Configure Grid: Row 0 is Header, Row 1 is Main 
        self.grid_columnconfigure(0, weight=7)
        self.grid_columnconfigure(1, weight=3)
        self.grid_rowconfigure(0, weight=0) # Header
        self.grid_rowconfigure(1, weight=1) # Main Content

        # --- GLOBAL HEADER BAR (Top of everything) ---
        self.header_bar = ctk.CTkFrame(self, fg_color=COLORS["panel"], height=40, corner_radius=0, border_width=0)
        self.header_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.header_bar.pack_propagate(False)

        # Left: App Name / Status
        ctk.CTkLabel(self.header_bar, text="💎 LifeOS Capture Station", font=("Inter", 12, "bold"), text_color=COLORS["primary"]).pack(side="left", padx=20)

        # Center: EDITABLE PATH
        path_frame = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        path_frame.pack(side="left", fill="x", expand=True, padx=20)
        
        self.target_path_var = tk.StringVar(value="Calculating...")
        self.path_entry = ctk.CTkEntry(path_frame, textvariable=self.target_path_var, height=28, 
                                       fg_color=COLORS["bg"], border_color=COLORS["border"], 
                                       text_color=COLORS["primary"], font=("Inter", 10), corner_radius=14)
        self.path_entry.pack(side="left", fill="x", expand=True)
        
        ctk.CTkButton(path_frame, text="📂", width=30, height=28, fg_color="transparent", 
                      text_color=COLORS["text_dim"], hover_color=COLORS["border"], 
                      command=self.change_target_path).pack(side="right", padx=(5, 0))

        # Right: Global Toggles
        self.right_header_toggles = ctk.CTkFrame(self.header_bar, fg_color="transparent")
        self.right_header_toggles.pack(side="right", padx=10)

        # Complexity
        self.complexity_var = ctk.StringVar(value=self.complexity_level)
        self.seg_complexity = ctk.CTkSegmentedButton(self.right_header_toggles, values=["Zen", "Med", "PRO"], 
                                                     variable=self.complexity_var, command=self.apply_complexity,
                                                     height=24, font=("Inter", 9, "bold"),
                                                     selected_color=COLORS["primary"], selected_hover_color=COLORS["accent"])
        self.seg_complexity.pack(side="left", padx=5)

        # Theme
        current_theme = ConfigManager.get_theme_name()
        self.theme_var = ctk.StringVar(value=current_theme)
        self.seg_theme = ctk.CTkSegmentedButton(self.right_header_toggles, values=["LIGHT", "DARK", "CYBER"], 
                                                variable=self.theme_var, command=self.change_theme,
                                                height=24, font=("Inter", 8),
                                                selected_color=COLORS["primary"], selected_hover_color=COLORS["accent"])
        self.seg_theme.pack(side="left", padx=5)

        # --- MAIN PANELS (Row 1) ---

        # --- LEFT PANEL: CANVAS ---
        self.left_panel = ctk.CTkFrame(self, fg_color=COLORS["bg"], corner_radius=0)
        self.left_panel.grid(row=1, column=0, sticky="nsew")
        self.left_panel.grid_columnconfigure(0, weight=1)
        
        self.left_panel.grid_rowconfigure(0, weight=0)
        self.left_panel.grid_rowconfigure(1, weight=1) 
        self.left_panel.grid_rowconfigure(2, weight=0)

        # Header / Toolbar (Type Selectors + Drawing)
        self.top_panel = ctk.CTkFrame(self.left_panel, fg_color=COLORS["panel"], corner_radius=0)
        self.top_panel.grid(row=0, column=0, sticky="ew")
        self.top_panel.grid_columnconfigure(1, weight=1) 

        # --- LEFT SECTION: Type Selectors ---
        left_header = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        left_header.grid(row=0, column=0, sticky="nw", padx=20, pady=5)
        
        ctk.CTkLabel(left_header, text="TIPO DE ENTRADA", font=("Inter", 11, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 2))

        type_frame_grid = ctk.CTkFrame(left_header, fg_color="transparent")
        type_frame_grid.pack(anchor="w")

        types = [("📝", "Nota"), ("🖥️", "Screen"), ("📄", "Minuta"), ("📁", "Archivo"), ("✅", "Task"), ("💎", "Hito")]
        self.type_var = tk.StringVar(value="Task")
        
        for i, (icon, label) in enumerate(types):
             r, c = divmod(i, 3)
             ctk.CTkRadioButton(type_frame_grid, text=f"{icon} {label}", variable=self.type_var, value=label, 
                                font=("Inter", 10), fg_color=COLORS["primary"], text_color=COLORS["text"],
                                width=60, height=18, radiobutton_width=12, radiobutton_height=12
                               ).grid(row=r, column=c, padx=(0, 8), pady=1, sticky="w")

        # --- CENTER SECTION: Toolbar ---
        toolbar_frame_container = ctk.CTkFrame(self.top_panel, fg_color="transparent")
        toolbar_frame_container.grid(row=0, column=1, sticky="n", pady=5)
        
        toolbar_frame = ctk.CTkFrame(toolbar_frame_container, fg_color=COLORS["panel"], height=40, corner_radius=20, border_width=1, border_color=COLORS["border"])
        toolbar_frame.pack()

        # Tools
        tools = [("🖱️", "pointer"), ("⬜", "rect"), ("↗️", "arrow"), ("✏️", "pen"), ("T", "text")]
        self.tool_btns = {}
        for txt, mode in tools:
            btn = ctk.CTkButton(toolbar_frame, text=txt, width=34, height=32, fg_color="transparent", text_color=COLORS["text"], hover_color=COLORS["border"], command=lambda m=mode: self.set_tool(m))
            btn.pack(side="left", padx=1, pady=1)
            self.tool_btns[mode] = btn
        
        # Colors (Monokai Palette)
        ctk.CTkFrame(toolbar_frame, width=1, height=16, fg_color=COLORS["border"]).pack(side="left", padx=5)
        mono_colors = [("#F92672", "pink"), ("#A6E22E", "green"), ("#66D9EF", "cyan"), ("#FD971F", "orange"), ("#AE81FF", "purple")]
        for hex_code, name in mono_colors:
            ctk.CTkButton(toolbar_frame, text="", width=16, height=16, corner_radius=8, 
                          fg_color=hex_code, hover_color=hex_code, 
                          command=lambda c=hex_code: self.set_color(c)).pack(side="left", padx=3)
        
        self.btn_picker = ctk.CTkButton(toolbar_frame, text="🌈", width=28, height=28, corner_radius=14,
                                        fg_color="transparent", text_color=COLORS["text"], hover_color=COLORS["border"],
                                        font=("Inter", 12), command=self.choose_color)
        self.btn_picker.pack(side="left", padx=5)

        self.btn_zoom = ctk.CTkButton(toolbar_frame, text="🔍 Fit", width=45, height=28, fg_color=COLORS["primary"], font=("Inter", 10), command=self.toggle_zoom)
        self.btn_zoom.pack(side="left", padx=5)

        # IA / Action Row
        center_bottom_row = ctk.CTkFrame(toolbar_frame_container, fg_color="transparent")
        center_bottom_row.pack(pady=(5, 0), fill="x", padx=10)

        self.btn_toggle_img = ctk.CTkButton(center_bottom_row, text="🗑️ Remove Image", width=120, height=24, fg_color="transparent", border_width=1, border_color=COLORS["danger"], text_color=COLORS["danger"], hover_color="#FEE2E2", font=("Inter", 10), command=self.toggle_image_mode)
        self.btn_toggle_img.pack(side="left", padx=(0, 5))
        
        self.ai_instruction_entry = ctk.CTkEntry(center_bottom_row, placeholder_text="Instrucciones para la IA (Opcional)...", width=250, height=24, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"], font=("Inter", 9))
        self.ai_instruction_entry.pack(side="left", fill="x", expand=True)

        self.btn_run_instruct = ctk.CTkButton(center_bottom_row, text="▶", width=30, height=24, fg_color=COLORS["accent"], hover_color="#4F46E5", command=self.run_instruction_analysis)
        self.btn_run_instruct.pack(side="left", padx=(2, 0))

        # Version tag in corner
        ctk.CTkLabel(self.top_panel, text="v3.8.0", text_color=COLORS["text_dim"], font=("Inter", 9)).grid(row=0, column=2, sticky="ne", padx=5, pady=5)



        # Canvas Area (Row 1 - Expands)
        self.canvas_container = ctk.CTkFrame(self.left_panel, fg_color="transparent")
        self.canvas_container.grid(row=1, column=0, sticky="nsew", padx=20, pady=10)
        self.canvas_container.grid_rowconfigure(0, weight=1)
        self.canvas_container.grid_columnconfigure(0, weight=1)

        # Scrollbars
        self.v_scroll = tk.Scrollbar(self.canvas_container, orient="vertical")
        self.h_scroll = tk.Scrollbar(self.canvas_container, orient="horizontal")

        self.canvas = tk.Canvas(self.canvas_container, bg=COLORS["canvas_bg"], highlightthickness=0,
                                xscrollcommand=self.h_scroll.set, yscrollcommand=self.v_scroll.set)
        
        self.v_scroll.config(command=self.canvas.yview)
        self.h_scroll.config(command=self.canvas.xview)
        
        self.canvas.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        self.h_scroll.grid(row=1, column=0, sticky="ew")

        self.canvas.bind("<ButtonPress-1>", self.start_draw)
        self.canvas.bind("<B1-Motion>", self.draw)
        self.canvas.bind("<ButtonRelease-1>", self.stop_draw)
        self.canvas.bind("<MouseWheel>", self._on_mousewheel)
        self.canvas.bind("<Configure>", self.on_canvas_resize)


        # --- NOTES AREA (Below Canvas) ---
        self.notes_frame = ctk.CTkFrame(self.left_panel, fg_color=COLORS["panel"], height=200, corner_radius=0)
        self.notes_frame.grid(row=2, column=0, sticky="ew", padx=0, pady=0)
        self.notes_frame.pack_propagate(False) 
        
        # Split into 2 columns
        self.notes_frame.grid_columnconfigure(0, weight=1)
        self.notes_frame.grid_columnconfigure(1, weight=1)
        self.notes_frame.grid_rowconfigure(0, weight=1)

        # Left: Personal Notes
        left_note_frame = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        left_note_frame.grid(row=0, column=0, sticky="nsew", padx=(20, 10), pady=10)
        
        ctk.CTkLabel(left_note_frame, text="NOTAS PERSONALES", font=("Inter", 12, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 5))
        self.notes_personal = ctk.CTkTextbox(left_note_frame, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"], border_width=1)
        self.notes_personal.pack(fill="both", expand=True)

        # Right: AI Analysis
        right_note_frame = ctk.CTkFrame(self.notes_frame, fg_color="transparent")
        right_note_frame.grid(row=0, column=1, sticky="nsew", padx=(10, 20), pady=10)

        ctk.CTkLabel(right_note_frame, text="ANÁLISIS IA", font=("Inter", 12, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(0, 5))
        self.ai_text = ctk.CTkTextbox(right_note_frame, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"], border_width=1)
        self.ai_text.pack(fill="both", expand=True)


        # --- RIGHT PANEL: SIDEBAR ---
        self.right_panel = ctk.CTkFrame(self, fg_color=COLORS["panel"], corner_radius=0, width=350)
        self.right_panel.grid(row=1, column=1, sticky="nsew")
        self.right_panel.grid_propagate(False)

        # 1. Pack Footer FIRST (at the bottom) to guarantee visibility
        footer_internal = ctk.CTkFrame(self.right_panel, fg_color=COLORS["panel"], height=140)
        footer_internal.pack(side="bottom", fill="x", padx=10, pady=10)

        self.btn_discard = ctk.CTkButton(footer_internal, text="Discard", fg_color=COLORS["bg"], text_color=COLORS["danger"], hover_color="#FEE2E2", command=self.close_window)
        self.btn_discard.pack(fill="x", pady=2)
        
        self.btn_autofill = ctk.CTkButton(footer_internal, text="🪄 Auto-Fill Content", fg_color="#8B5CF6", hover_color="#7C3AED", command=self.autofill_content)
        self.btn_autofill.pack(fill="x", pady=2)

        self.btn_ai = ctk.CTkButton(footer_internal, text="✨ Analyze with Gemini", fg_color=COLORS["accent"], hover_color="#4F46E5", command=self.analyze_image)
        self.btn_ai.pack(fill="x", pady=2)

        self.btn_save = ctk.CTkButton(footer_internal, text="Save", fg_color=COLORS["success"], hover_color="#059669", command=self.save)
        self.btn_save.pack(fill="x", pady=5)

        # 2. Pack Content Scroll SECOND (fill remaining space above footer)
        self.sidebar_scroll = ctk.CTkScrollableFrame(self.right_panel, fg_color="transparent")
        self.sidebar_scroll.pack(side="top", fill="both", expand=True, padx=10, pady=10)

        ctk.CTkLabel(self.sidebar_scroll, text="DETALLES DE CAPTURA", font=("Inter", 12, "bold"), text_color=COLORS["text"]).pack(anchor="w", pady=(10, 20))

        # --- Group: PRO ---
        self.group_pro = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.group_pro.pack(fill="x")
        
        self.add_label("ARCHIVO RELACIONADO", self.group_pro)
        file_frame = ctk.CTkFrame(self.group_pro, fg_color="transparent")
        file_frame.pack(fill="x", pady=(0, 10))
        self.file_entry = ctk.CTkEntry(file_frame, height=35, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.file_entry.pack(side="left", fill="x", expand=True, padx=(0, 5))
        btn_browse = ctk.CTkButton(file_frame, text="📂", width=40, height=35, fg_color=COLORS["primary"], command=self.browse_file)
        btn_browse.pack(side="right")

        # --- Group: BASIC ---
        self.group_basic = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.group_basic.pack(fill="x")

        self.add_label("TÍTULO", self.group_basic)
        self.title_entry = ctk.CTkEntry(self.group_basic, height=35, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.title_entry.pack(fill="x", pady=(0, 10))

        self.add_label("TAGS (Separados por coma)", self.group_basic)
        self.tags_entry = ctk.CTkEntry(self.group_basic, height=35, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.tags_entry.pack(fill="x", pady=(0, 10))

        # --- Group: MED ---
        self.group_med = ctk.CTkFrame(self.sidebar_scroll, fg_color="transparent")
        self.group_med.pack(fill="x")

        self.univ_combo = self.add_select("UNIVERSO", self.load_universes(), "last_universe", self.group_med)
        self.proj_combo = self.add_select("PROYECTO", self.load_projects(), "last_project", self.group_med)
        self.client_combo = self.add_select("CLIENTE", data_manager.get_clients(), "last_client", self.group_med)

        # --- Back to Group: PRO ---
        # Add role to pro group
        self.role_combo = self.add_select("ROLE / AREA", data_manager.get_roles(), "last_role", self.group_pro)
        
        self.add_label("FECHA LÍMITE", self.group_pro)
        self.date_entry = ctk.CTkEntry(self.group_pro, height=35, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"])
        self.date_entry.insert(0, datetime.datetime.now().strftime("%Y-%m-%d"))
        self.date_entry.pack(fill="x", pady=(0, 10))



    def add_label(self, text, parent=None):
        target = parent or self.sidebar_scroll
        ctk.CTkLabel(target, text=text, font=("Inter", 10, "bold"), text_color=COLORS["text_dim"]).pack(anchor="w", pady=(5, 2))

    def add_select(self, label, values, config_key, parent=None):
        target = parent or self.sidebar_scroll
        self.add_label(label, target)
        if isinstance(values, list):
            values.sort()
        combo = ctk.CTkComboBox(target, values=values, height=35, fg_color=COLORS["bg"], border_color=COLORS["border"], text_color=COLORS["text"], button_color=COLORS["border"], command=lambda e: self.update_target_path())
        combo.pack(fill="x", pady=(0, 10))
        last_val = self.config.get(config_key, "")
        if last_val:
            combo.set(last_val)
        return combo

    def load_universes(self):
        return data_manager.get_universes()

    def load_projects(self):
        return data_manager.get_projects()

    # --- CANVAS & ZOOM LOGIC ---
    def load_image(self):
        self.original_image = Image.open(self.screenshot_path)
        self.drawing_layer = Image.new("RGBA", self.original_image.size, (255, 255, 255, 0))
        self.draw_ctx = ImageDraw.Draw(self.drawing_layer)
        
        self.scale = 1.0
        self.zoom_mode = "fit" # 'fit' or '100%'
        
        # Initial draw will happen in on_canvas_resize or manually
        self.after(100, self.update_image_display)

    def on_canvas_resize(self, event):
        if self.zoom_mode == "fit":
            self.update_image_display()

    def toggle_zoom(self):
        self.zoom_mode = "100%" if self.zoom_mode == "fit" else "fit"
        self.btn_zoom.configure(text="🔍 100%" if self.zoom_mode == "fit" else "🔍 Fit")
        self.update_image_display()

    def update_image_display(self):
        cw = self.canvas.winfo_width()
        ch = self.canvas.winfo_height()
        iw, ih = self.original_image.size

        if cw <= 1 or ch <= 1: return # Not ready

        if self.zoom_mode == "fit":
            self.scale = min(cw/iw, ch/ih)
            # Avoid upscaling if image is smaller than canvas
            if self.scale > 1: self.scale = 1.0
        else:
            self.scale = 1.0

        new_size = (int(iw * self.scale), int(ih * self.scale))
        
        # Composite Original + Drawing Layer for Display
        combined = Image.alpha_composite(self.original_image.convert("RGBA"), self.drawing_layer)
        
        # Resize safely
        if new_size[0] > 0 and new_size[1] > 0:
            resized = combined.resize(new_size, Image.Resampling.LANCZOS)
            self.tk_image = ImageTk.PhotoImage(resized)
            self.canvas.create_image(0, 0, image=self.tk_image, anchor="nw")
            self.canvas.config(scrollregion=(0, 0, new_size[0], new_size[1]))

    def get_img_coords(self, event_x, event_y):
        cx = self.canvas.canvasx(event_x)
        cy = self.canvas.canvasy(event_y)
        return cx / self.scale, cy / self.scale

    def set_tool(self, tool):
        self.tool = tool
        for t, btn in self.tool_btns.items():
            is_active = (t == tool)
            btn.configure(
                fg_color=COLORS["primary"] if is_active else "transparent", 
                text_color="white" if is_active else COLORS["text"]
            )

    def set_color(self, hex_color):
        self.draw_color_hex = hex_color
        # Update picker icon color to show selection
        self.btn_picker.configure(text_color=hex_color if hex_color != COLORS["text"] else COLORS["text"])

    def choose_color(self):
        color = colorchooser.askcolor(title="Choose Stroke Color", initialcolor=getattr(self, "draw_color_hex", "#F92672"))
        if color[1]:
            self.set_color(color[1])

    def start_draw(self, event):
        ix, iy = self.get_img_coords(event.x, event.y)
        
        if self.tool == "text":
            self.add_text_annotation(ix, iy)
            return
            
        self.is_drawing = True
        self.start_x, self.start_y = ix, iy # Image Coords
        self.last_x, self.last_y = ix, iy
        
    def draw(self, event):
        if not self.is_drawing: return
        
        ix, iy = self.get_img_coords(event.x, event.y)       # Image Coords
        cx, cy = self.canvas.canvasx(event.x), self.canvas.canvasy(event.y) # Canvas Coords
        
        hex_col = getattr(self, "draw_color_hex", "#EF4444")
        
        if self.tool == "pen":
            # Determine previous canvas coordinates based on stored image coordinates
            lcx, lcy = self.last_x * self.scale, self.last_y * self.scale
            
            # Draw on Canvas (Visual Feedback)
            self.canvas.create_line(lcx, lcy, cx, cy, width=3, fill=hex_col, capstyle=tk.ROUND, smooth=True)
            
            # Draw on Pillow Layer (Real resolution)
            line_width = int(3 / self.scale) if self.scale < 1 else 3
            if line_width < 1: line_width = 1
            self.draw_ctx.line([self.last_x, self.last_y, ix, iy], fill=hex_col, width=line_width)
            self.last_x, self.last_y = ix, iy
            
        elif self.tool in ["rect", "arrow"]:
            if self.current_shape: self.canvas.delete(self.current_shape)
            
            # Preview on Canvas uses Scaled Coords (Origin was stored as Image coord, convert back)
            scx, scy = self.start_x * self.scale, self.start_y * self.scale
            
            if self.tool == "rect":
                self.current_shape = self.canvas.create_rectangle(scx, scy, cx, cy, outline=hex_col, width=2)
            elif self.tool == "arrow":
                self.current_shape = self.canvas.create_line(scx, scy, cx, cy, arrow=tk.LAST, fill=hex_col, width=2)

    def stop_draw(self, event):
        if not self.is_drawing: return
        self.is_drawing = False
        
        ix, iy = self.get_img_coords(event.x, event.y)
        hex_col = getattr(self, "draw_color_hex", "#EF4444")

        # Commit to Pillow Layer
        if self.tool == "rect":
            self.draw_ctx.rectangle([self.start_x, self.start_y, ix, iy], outline=hex_col, width=3)
        elif self.tool == "arrow":
            draw_arrow_pil(self.draw_ctx, self.start_x, self.start_y, ix, iy, hex_col)
            
        self.current_shape = None
        
        # Refresh display to burn in the drawing at correct resolution
        self.update_image_display()

    def add_text_annotation(self, ix, iy):
        # ix, iy are Image Coordinates
        dialog = ctk.CTkInputDialog(title="Add Text", text="Enter annotation text:")
        text = dialog.get_input()
        if text:
            hex_col = getattr(self, "draw_color_hex", "#F92672")
            try:
                font = ImageFont.truetype("arial.ttf", 24)
            except:
                font = ImageFont.load_default()
            self.draw_ctx.text((ix, iy), text, fill=hex_col, font=font)
            
            # Refresh Display
            self.update_image_display()

    def run_instruction_analysis(self):
        instruct = self.ai_instruction_entry.get().strip()
        if not instruct:
            self.show_toast("⚠️ Escribe una instrucción primero")
            return
            
        self.btn_run_instruct.configure(state="disabled", fg_color="#9CA3AF")
        self.analyze_image(custom_instruct=instruct)

    def analyze_image(self, custom_instruct=None):
        # Allow passing custom instructions directly
        instruct = custom_instruct or self.ai_instruction_entry.get().strip()
        
        self.btn_ai.configure(text="Analyzing...", state="disabled")
        
        def on_success(text, is_custom):
            header = f"--- 🤖 AI Output (Custom Instruction) ---\nNOTE: {instruct}\n" if is_custom else "--- 🤖 AI Analysis (Auto) ---\n"
            
            # Prepend (Newest on Top)
            full_block = header + text + "\n\n" + ("-"*40) + "\n\n"
            self.ai_text.insert("1.0", full_block)
            self.ai_text.see("1.0") # Scroll to top
            
            self.after(0, lambda: self.btn_ai.configure(text="✨ Analyze with Gemini", state="normal"))
            self.after(0, lambda: self.btn_run_instruct.configure(state="normal", fg_color=COLORS["accent"]))
            
        def on_error(err):
            messagebox.showerror("AI Error", err)
            self.after(0, lambda: self.btn_ai.configure(text="Error", state="normal"))
            self.after(0, lambda: self.btn_run_instruct.configure(state="normal", fg_color=COLORS["accent"]))
            
        self.ai_service.analyze_image(self.original_image, on_success, on_error, instructions=instruct)

    def autofill_content(self):
        self.btn_autofill.configure(text="🪄 Filling...", state="disabled")
        
        user_instruct = self.ai_instruction_entry.get().strip()

        def on_success(json_text):
            try:
                # Basic cleanup if model wraps in code blocks
                clean_json = json_text.replace("```json", "").replace("```", "").strip()
                data = json.loads(clean_json)
                
                # Fill Fields
                if data.get("title"):
                    self.title_entry.delete(0, "end")
                    self.title_entry.insert(0, data["title"])
                
                if data.get("tags"):
                    tags_val = data["tags"]
                    if data.get("software"):
                         self.detected_software = data['software'] # Store for metadata
                         tags_val = f"{data['software']}, {tags_val}"
                    self.tags_entry.delete(0, "end")
                    self.tags_entry.insert(0, tags_val)
                
                if data.get("summary"):
                    self.ai_text.delete("1.0", "end")
                    self.ai_text.insert("end", data["summary"])

                if data.get("deadline"):
                     self.date_entry.delete(0, "end")
                     self.date_entry.insert(0, data["deadline"])

                if data.get("type"):
                     self.type_var.set(data["type"])

                if data.get("file_path"):
                     self.file_entry.delete(0, "end")
                     self.file_entry.insert(0, data["file_path"].replace("\\", "/"))
                
            except Exception as e:
                print(f"JSON Parse Error: {e}")
                messagebox.showerror("Auto-Fill Failed", f"Could not parse AI response.\n{e}")
                
            self.after(0, lambda: self.btn_autofill.configure(text="🪄 Auto-Fill Content", state="normal"))
            
        def on_error(err):
            messagebox.showerror("Autofill Error", err)
            self.after(0, lambda: self.btn_autofill.configure(text="Error", state="normal"))
            
        self.ai_service.smart_fill_analysis(self.original_image, on_success, on_error, instructions=user_instruct)

    def toggle_image_mode(self):
        self.image_active = not self.image_active
        
        if self.image_active:
            self.canvas_container.grid() # Restore
            self.btn_toggle_img.configure(text="🗑️ Remove Image", fg_color="transparent", text_color=COLORS["danger"])
        else:
            self.canvas_container.grid_remove() # Hide
            self.btn_toggle_img.configure(text="🖼️ Restore Image", fg_color=COLORS["bg"], text_color=COLORS["primary"])

    def browse_file(self):
        filename = ctk.filedialog.askopenfilename()
        if filename:
            self.file_entry.delete(0, "end")
            self.file_entry.insert(0, filename)

    def change_target_path(self, event=None):
        path = ctk.filedialog.askdirectory(initialdir=self.PROJECTS_ROOT)
        if path:
            self.custom_target_path = path
            self.target_path_var.set(f"📂 Saving to: .../{os.path.basename(path)}")
            self.lbl_target.configure(text_color=COLORS["primary"]) # Highlight change

    def update_target_path(self):
        root_path = getattr(self, 'custom_target_path', None)
        
        if root_path:
             self.target_path_var.set(root_path)
             return

        uni_val = self.univ_combo.get().strip()
        proj_val = self.proj_combo.get().strip()
        
        path_display = self.paths['root']
        
        if proj_val:
             path_display = os.path.join(self.PROJECTS_ROOT, proj_val)
        elif uni_val:
             path_display = os.path.join(self.UNIVERSES_ROOT, uni_val)
        
        self.target_path_var.set(path_display)

    def save(self):
        # Data Gathering
        uni_val = self.univ_combo.get().strip()
        proj_val = self.proj_combo.get().strip()
        cli_val = self.client_combo.get().strip()
        role_val = self.role_combo.get().strip()
        tags_val = self.tags_entry.get().strip()
        
        if not tags_val:
            tags_val = "Untitled"
        
        save_image = self.image_active
        
        # Gather Data EARLY (before any UI updates/saves)
        data = {
            'title': self.title_entry.get().strip(),
            'universe': uni_val,
            'project': proj_val,
            'client': cli_val,
            'role': role_val,
            'tags': tags_val,
            'notes': self.notes_personal.get("1.0", "end"),
            'ai_analysis': self.ai_text.get("1.0", "end"),
            'type': self.type_var.get(),
            'deadline': self.date_entry.get().strip(),
            'related_file': self.file_entry.get().strip(),
            'target_override': getattr(self, 'custom_target_path', None),
            'software': getattr(self, 'detected_software', ''),
            'source': self.source,
            'save_image': save_image,
            'last_universe': uni_val,
            'last_project': proj_val,
            'last_client': cli_val,
            'last_role': role_val,
            'last_tags': tags_val
        }
        
        if save_image:
            final = Image.alpha_composite(self.original_image.convert("RGBA"), self.drawing_layer).convert("RGB")
            final.save(self.screenshot_path)
            
            # Copy to Clipboard
            if copy_image_to_clipboard(final):
                self.show_toast("📋 Imagen copiada al portapapeles")
            else:
                log_agent.log_event("WARNING", "Clipboard Copy Failed")
        else:
            # If not saving image, skip physical save
            pass

        # --- AUTO-CREATE LOGIC (FOLDERS + JSON DB) ---
        # 1. UNIVERSE
        if uni_val:
            data_manager.add_universe(uni_val) # Add to JSON
            if os.path.exists(self.UNIVERSES_ROOT):
                uni_path = os.path.join(self.UNIVERSES_ROOT, uni_val)
                if not os.path.exists(uni_path):
                    try:
                        os.makedirs(uni_path)
                        log_agent.log_event("SYSTEM", f"NEW UNIVERSE FOLDER: {uni_path}")
                    except Exception as e:
                        log_agent.error(f"Failed to create Universe folder {uni_val}", e)

        # 2. PROJECT
        if proj_val:
            data_manager.add_project(proj_val) # Add to JSON
            if os.path.exists(self.PROJECTS_ROOT):
                proj_path = os.path.join(self.PROJECTS_ROOT, proj_val)
                if not os.path.exists(proj_path):
                    try:
                        os.makedirs(proj_path)
                        log_agent.log_event("SYSTEM", f"NEW PROJECT FOLDER: {proj_path}")
                    except Exception as e:
                        log_agent.error(f"Failed to create Project folder {proj_val}", e)
        
        # 3. ROLE
        if role_val:
            data_manager.add_role(role_val) # Add to JSON

        # 4. CLIENT
        if cli_val:
            data_manager.add_client(cli_val) # Add to JSON

        # Save only User Preferences to Config

        ConfigManager.save({
            'last_universe': uni_val,
            'last_project': proj_val,
            'last_client': cli_val,
            'last_role': role_val,
            'last_target_override': data.get('target_override'),
            'complexity_level': self.complexity_level
        })
        
        self.on_save_cb(data, self.screenshot_path)
        self.destroy()

    def apply_complexity(self, level):
        self.complexity_level = level
        
        # Hide All first
        self.group_pro.pack_forget()
        self.group_med.pack_forget()
        self.group_basic.pack_forget()

        if level == "Zen":
            # Zen: Only Basic
            self.group_basic.pack(fill="x", pady=5)
        elif level == "Med":
            # Med: Basic + Standard (Med)
            self.group_basic.pack(fill="x", pady=5)
            self.group_med.pack(fill="x", pady=5)
        else:
            # PRO: Everything
            self.group_pro.pack(fill="x", pady=5)
            self.group_basic.pack(fill="x", pady=5)
            self.group_med.pack(fill="x", pady=5)

        # Persistence: Save the last used state
        ConfigManager.save({'complexity_level': self.complexity_level})
        
        self.show_toast(f"Modo {level} activado")

    def show_toast(self, message, duration=1500):
        try:
            # Parent to master so it survives self.destroy()
            toast = ctk.CTkToplevel(self.master)
            toast.overrideredirect(True)
            toast.attributes("-topmost", True)
            
            # Calculate Position (Bottom Center)
            sw = self.winfo_screenwidth()
            sh = self.winfo_screenheight()
            w, h = 320, 50
            x = (sw - w) // 2
            y = sh - 150 
            
            toast.geometry(f"{w}x{h}+{x}+{y}")
            
            # Style
            # Green bg for success
            frame = ctk.CTkFrame(toast, fg_color="#10B981", corner_radius=20, border_color="white", border_width=1)
            frame.pack(fill="both", expand=True)
            
            label = ctk.CTkLabel(frame, text=message, text_color="white", font=("Inter", 13, "bold"))
            label.pack(expand=True, padx=20, pady=10)
            
            # Self Destruct
            toast.after(duration, toast.destroy)
            
            # Force update to show immediately before main thread gets busy
            toast.update()
        except Exception as e:
            print(f"Toast Error: {e}")

    def change_theme(self, new_theme):
        ConfigManager.save({'theme': new_theme})
        colors = ConfigManager.get_colors()
        ctk.set_appearance_mode(colors.get('ctk_mode', 'light'))
        self.show_toast(f"Tema {new_theme} aplicado. (Reinicia para cambios totales)")

    def _on_mousewheel(self, event):
        self.canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def close_window(self):
        self.on_cancel_cb()
        self.destroy()
