import customtkinter as ctk
import keyboard
import os
import time
import datetime
import mss
from PIL import Image

# Modular Imports
import shutil # <--- New Import for moving files
import threading
from src.utils.platform_utils import minimize_console, is_keyboard_hit, get_key
from src.core.config import ConfigManager, PATHS, GEMINI_MODEL # <--- Import PATHS & MODEL
from src.utils.helpers import get_active_window_title
from src.ui.snipping_overlay import SnippingOverlay
from src.ui.editor_window import EditorWindow
from src.ui.dashboard import DashboardWindow
from src.core.tray import SystemTrayIcon 
from src.core.data_manager import data_manager
from logger_agent import log_agent
from src.utils.animations import print_lifeos_intro
import sys

# Constants
OUTPUT_DIR = "output"
ATTACHMENTS_DIR = os.path.join(OUTPUT_DIR, "attachments")
HOTKEY = "ctrl+alt+s"
VERSION = "v3.8.0 (Visual Dashboard)"

from src.utils.singleton import ensure_single_instance

class LifeOSUltimateApp:
    def __init__(self):
        # Run startup diagnostics (first‑run wizard & directory checks)
        from src.core.startup_agent import StartupDiagnostics
        if not StartupDiagnostics().run():
            # Abort application if diagnostics fail
            sys.exit(1)
        # Tron Intro FIRST to clear any previous noise
        self.current_paths = ConfigManager.get_dynamic_paths()
        colors = ConfigManager.get_colors()
        ctk.set_appearance_mode(colors.get('ctk_mode', 'light'))
        print_lifeos_intro(VERSION, GEMINI_MODEL, self.current_paths['root'], os.getcwd())
        
        print_lifeos_intro(VERSION, GEMINI_MODEL, self.current_paths['root'], os.getcwd())
        
        self.root = ctk.CTk()
        self.root.withdraw()
        self.is_capturing = False
        
        # Ensure directories
        os.makedirs(ATTACHMENTS_DIR, exist_ok=True)
        
        # Init System Tray
        self.tray = SystemTrayIcon(self.trigger_capture_tray, self.trigger_dashboard, self.quit_app)
        self.tray.run()
        
        log_agent.log_event("SYSTEM", f"LifeOS Capture Ultimate Started. Hotkey: {HOTKEY}")
        
        keyboard.add_hotkey(HOTKEY, self.trigger_capture)
        keyboard.add_hotkey("ctrl+alt+d", self.trigger_dashboard)
        
        # Start Console Listener
        self.listener_thread = threading.Thread(target=self._console_listener, daemon=True)
        self.listener_thread.start()
        
        self.root.mainloop()

    def _console_listener(self):
        while True:
            try:
                if is_keyboard_hit():
                    ch = get_key()
                    if ch.lower() == b's':
                        print("\n" + "="*40)
                        print(" [CONFIG] CHANGE VAULT ROOT")
                        print("="*40)
                        print(f"Current: {self.current_paths['root']}")
                        new_path = input(">>> Enter new Vault Root Path (or ENTER to cancel): ").strip()
                        
                        if new_path:
                            # Remove quotes if user dragged and dropped folder
                            new_path = new_path.replace('"', '').replace("'", "")
                            
                            if os.path.exists(new_path):
                                ConfigManager.set_vault_root(new_path)
                                self.current_paths = ConfigManager.get_dynamic_paths()
                                print(f"✅ Vault Root updated to: {new_path}")
                                log_agent.log_event("CONFIG", f"Vault Root changed to {new_path}")
                            else:
                                print(f"❌ Path does not exist: {new_path}")
                        else:
                            print("Cancelled.")
                        
                        print("\nResuming... Press 's' to configure or 'd' for Dashboard.")
                    elif ch.lower() == b'd':
                        print("\n🚀 Launching Dashboard...")
                        self.trigger_dashboard()
            except Exception as e:
                pass
            time.sleep(0.1)

    def trigger_capture(self):
        # Triggered by Hotkey (keyboard thread)
        self.root.after(0, self._start_capture_flow)

    def trigger_capture_tray(self):
        # Triggered by Tray (tray thread)
        self.root.after(0, self._start_capture_flow)

    def _start_capture_flow(self):
        if self.is_capturing: return
        minimize_console()
        self.is_capturing = True
        self.source = get_active_window_title()
        log_agent.log_event("CAPTURE_START", f"Capture triggered on: {self.source}")
        self.start()

    def trigger_dashboard(self):
        # Triggered by Hotkey or Tray
        self.root.after(0, self.show_dashboard)

    def show_dashboard(self):
        # Open or focus dashboard
        if not hasattr(self, 'dashboard_win') or not self.dashboard_win.winfo_exists():
            self.dashboard_win = DashboardWindow(self.root)
        else:
            self.dashboard_win.focus()
            self.dashboard_win.deiconify()

    def start(self):
        SnippingOverlay(self.root, self.on_capture, self.reset)

    def quit_app(self):
        log_agent.log_event("SYSTEM", "Application Exiting via Tray")
        self.root.quit()
        sys.exit(0)

    def reset(self):
        self.is_capturing = False

    def on_capture(self, region):
        with mss.mss() as sct:
            img = sct.grab(region)
            pil_img = Image.frombytes("RGB", img.size, img.bgra, "raw", "BGRX")
            path = os.path.join(ATTACHMENTS_DIR, f"temp_{int(time.time())}.png")
            pil_img.save(path)
            EditorWindow(self.root, path, region, self.finish_save, self.reset, source=self.source)

    def finish_save(self, data, img_path):
        safe_title = "".join(x for x in data['title'] if x.isalnum() or x in " -_").strip() or "Untitled"
        final_name = f"{safe_title}_{int(time.time())}.png"
        md_name = f"{safe_title}.md"

        # --- SMART ROUTING LOGIC ---
        target_dir = OUTPUT_DIR # Default fallback
        is_routed = False

        # 0. Manual Override
        if data.get('target_override'):
             target_dir = data['target_override']
             is_routed = True

        # 1. Try Project Routing
        # Update paths dynamically in case they changed
        current_paths = ConfigManager.get_dynamic_paths()
        
        if not is_routed and data['project']:
            proj_path = os.path.join(current_paths['projects'], data['project'])
            if os.path.exists(proj_path):
                target_dir = proj_path
                is_routed = True
        
        # 2. Try Universe Routing (if not routed to project)
        if not is_routed and data['universe']:
            univ_path = os.path.join(current_paths['universes'], data['universe'])
            if os.path.exists(univ_path):
                target_dir = univ_path
                is_routed = True

        # Setup Paths
        attachments_dir = os.path.join(target_dir, "attachments")
        md_path = os.path.join(target_dir, md_name)
        
        save_img = data.get('save_image', True)
        final_img_path = ""

        if save_img:
            os.makedirs(attachments_dir, exist_ok=True)
            final_img_path = os.path.join(attachments_dir, final_name)
            
            # Move Image
            try:
                shutil.move(img_path, final_img_path)
            except Exception as e:
                print(f"Error moving image: {e}")
                # Fallback copy if move fails (e.g. cross-drive)
                shutil.copy(img_path, final_img_path)
        
        # Build image markdown only if saved
        img_md = f"![Screenshot](attachments/{final_name})" if save_img else ""

        # Write Markdown
        content = f"""---
created: {datetime.datetime.now()}
type: {data['type']}
universe: {data['universe']}
project: {data['project']}
tags: [{data['tags']}]
source: {data['source']}
software: {data.get('software', '')}
deadline: {data.get('deadline', '')}
related_file: {data.get('related_file', '')}
---
# {data['title']}
{img_md}

## My Notes
{data['notes']}

## AI Analysis
{data.get('ai_analysis', '')}
"""
        with open(md_path, "w", encoding="utf-8") as f:
            f.write(content)
        
        # --- INDEX IN REGISTRY (Final Paths) ---
        data_manager.add_task_entry({
            "title": data['title'],
            "type": data['type'],
            "universe": data['universe'],
            "project": data['project'],
            "client": data['client'],
            "role": data.get('role', ''),
            "tags": data['tags'],
            "notes": data['notes'],
            "ai_analysis": data.get('ai_analysis', ''),
            "file_path": final_img_path,
            "md_path": md_path
        })
        
        log_agent.log_event("SAVE", f"Saved to {target_dir}", path=md_path, universe=data['universe'])
        print(f"Saved successfully to: {md_path}")
            
        self.is_capturing = False

if __name__ == "__main__":
    ensure_single_instance()
    LifeOSUltimateApp()
