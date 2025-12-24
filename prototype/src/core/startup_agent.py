import os
import tkinter as tk
from tkinter import filedialog, messagebox
import logging
from src.core.config import ConfigManager, PATHS, GEMINI_MODEL
from logger_agent import log_agent

class StartupDiagnostics:
    """Performs first‑run checks and ensures the vault directory is set.

    - Detects missing or incomplete ``config.yaml``.
    - If ``vault_root`` is not defined, shows a simple GUI dialog asking the user to select a folder.
    - Creates required sub‑folders (output, attachments, logs, universes, projects).
    - Validates that the Gemini API key is present.
    """

    def __init__(self):
        self.config = ConfigManager.load()
        self.root_path = None

    def _prompt_vault_path(self):
        """Show a dialog to let the user choose the vault location.
        Returns the chosen absolute path or ``None`` if cancelled.
        """
        try:
            # Use a hidden root window to avoid extra UI
            hidden_root = tk.Tk()
            hidden_root.withdraw()
            hidden_root.update()
            default_path = os.path.abspath("GemShot_Vault")
            messagebox.showinfo(
                "Configuración inicial",
                "Selecciona la carpeta donde se guardará la bóveda de GemShot.\n" 
                f"Se sugiere: {default_path}",
            )
            chosen = filedialog.askdirectory(initialdir=default_path, title="Seleccionar carpeta de la bóveda")
            hidden_root.destroy()
            if chosen:
                return os.path.abspath(chosen)
        except Exception as e:
            logging.error(f"Error in vault path wizard: {e}")
        return None

    def _ensure_directories(self, root_path):
        """Create the standard directory tree under ``root_path``.
        ``output`` and its ``attachments`` sub‑folder are always created.
        """
        required = [
            root_path,
            os.path.join(root_path, "output"),
            os.path.join(root_path, "output", "attachments"),
            os.path.join(root_path, "logs"),
            os.path.join(root_path, "universes"),
            os.path.join(root_path, "projects"),
        ]
        for p in required:
            try:
                os.makedirs(p, exist_ok=True)
            except Exception as e:
                logging.error(f"Failed to create directory {p}: {e}")
                raise

    def _check_api_key(self):
        """Make sure a Gemini API key is present in the config.
        If missing, warn the user but do not abort – the app can still run
        without AI features.
        """
        api_key = self.config.get("gemini_api_key")
        if not api_key:
            messagebox.showwarning(
                "Clave API faltante",
                "No se encontró una clave Gemini API en config.yaml.\n"
                "Algunas funciones de IA estarán desactivadas.",
            )
            log_agent.log_event("WARNING", "Gemini API key missing in config")
        else:
            log_agent.log_event("SYSTEM", "Gemini API key loaded")

    def run(self):
        """Execute the full startup diagnostic flow.
        Returns ``True`` if everything is ready, ``False`` otherwise.
        """
        # 1. Detect missing config or missing vault_root
        vault_root = self.config.get("vault_root")
        if not vault_root:
            chosen = self._prompt_vault_path()
            if not chosen:
                messagebox.showerror(
                    "Instalación abortada",
                    "No se seleccionó una carpeta para la bóveda. La aplicación se cerrará.",
                )
                return False
            ConfigManager.set_vault_root(chosen)
            self.config = ConfigManager.load()
            vault_root = chosen
        self.root_path = os.path.abspath(vault_root)
        # 2. Ensure directory structure exists
        try:
            self._ensure_directories(self.root_path)
        except Exception:
            messagebox.showerror(
                "Error de configuración",
                f"No se pudieron crear las carpetas necesarias en {self.root_path}",
            )
            return False
        # 3. Verify API key (non‑blocking)
        self._check_api_key()
        # 4. Log success
        log_agent.log_event("SYSTEM", f"Startup diagnostics completed. Vault root: {self.root_path}")
        return True
