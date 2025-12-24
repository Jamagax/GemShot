import os
import yaml
import logging

CONFIG_FILE = "config.yaml"

# Theme System
THEMES = {
    "LIGHT": {
        "bg": "#F9FAFB",
        "panel": "#FFFFFF",
        "text": "#1F2937",
        "text_dim": "#6B7280",
        "border": "#E5E7EB",
        "primary": "#3B82F6",
        "success": "#10B981",
        "accent": "#6366F1",
        "danger": "#EF4444",
        "canvas_bg": "#F3F4F6",
        "ctk_mode": "light"
    },
    "DARK": {
        "bg": "#111827",
        "panel": "#1F2937",
        "text": "#F9FAFB",
        "text_dim": "#9CA3AF",
        "border": "#374151",
        "primary": "#60A5FA",
        "success": "#34D399",
        "accent": "#818CF8",
        "danger": "#F87171",
        "canvas_bg": "#111827",
        "ctk_mode": "dark"
    },
    "CYBER": {
        "bg": "#0D1117",
        "panel": "#161B22",
        "text": "#58A6FF",
        "text_dim": "#8B949E",
        "border": "#30363D",
        "primary": "#00E0FF",
        "success": "#7EE787",
        "accent": "#F778BA",
        "danger": "#FF7B72",
        "canvas_bg": "#010409",
        "ctk_mode": "dark"
    }
}

class ConfigManager:
    @staticmethod
    def load():
        if os.path.exists(CONFIG_FILE):
            try:
                with open(CONFIG_FILE, 'r') as f:
                    return yaml.safe_load(f) or {}
            except Exception as e:
                logging.error(f"Error loading config: {e}")
        return {}

    @staticmethod
    def get_theme_name():
        return ConfigManager.load().get('theme', 'LIGHT')

    @staticmethod
    def get_colors():
        theme_name = ConfigManager.get_theme_name()
        return THEMES.get(theme_name, THEMES["LIGHT"])

    @staticmethod
    def save(data):
        try:
            existing = ConfigManager.load()
            existing.update(data)
            with open(CONFIG_FILE, 'w') as f:
                yaml.dump(existing, f)
        except Exception as e:
            logging.error(f"Error saving config: {e}")

    @staticmethod
    def get_dynamic_paths():
        cfg = ConfigManager.load()
        # Portable default root: "GemShot_Vault" inside the app directory
        default_root = os.path.abspath("GemShot_Vault")
            
        root = cfg.get('vault_root', default_root)
        
        # Priority: Specific roots -> Derivation from vault_root
        uni_root = cfg.get('universes_root') or os.path.join(root, "0_TZOL", "10_Areas")
        proj_root = cfg.get('projects_root') or os.path.join(root, "0_TZOL", "20_Projects")
        
        return {
            "root": root,
            "universes": uni_root,
            "projects": proj_root
        }

    @staticmethod
    def set_vault_root(new_root):
        data = {"vault_root": new_root}
        ConfigManager.save(data)

# Global dynamic accessors
COLORS = ConfigManager.get_colors()


# AI Configuration
GEMINI_MODEL = "gemini-2.0-flash-lite"

# Initial Load
PATHS = ConfigManager.get_dynamic_paths()
