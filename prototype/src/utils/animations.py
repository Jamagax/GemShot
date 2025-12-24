import time
import sys
import os
from colorama import init, Fore, Style

# Initialize colorama
init()

def clear_console():
    os.system('cls' if os.name == 'nt' else 'clear')

def print_lifeos_intro(version, model, vault_path, script_path):
    # Cyan minimalist palette
    C_CYAN = Fore.CYAN
    C_WHITE = Fore.WHITE
    C_RESET = Style.RESET_ALL
    C_BRIGHT = Style.BRIGHT
    
    # ... (Animation frames unchanged)
    frames = ["[ . 0 . . ]", "[ . . 0 . ]", "[ . . . 0 ]", "[ . . 0 . ]", "[ . 0 . . ]", "[ 0 . . . ]"]

    for _ in range(2):
        for frame in frames:
            clear_console()
            print("\n\n")
            print(f"         {C_CYAN}/\\   *{C_RESET}")
            print(f"        {C_CYAN}/  \\{C_RESET}")
            print(f"        {C_CYAN}\\  /{C_RESET}")
            print(f"         {C_CYAN}\\/{C_RESET}\n")
            print(f"      {C_CYAN}{frame}{C_RESET}\n")
            print(f"   {C_CYAN}Loading - GemShot - LifeOS{C_RESET}")
            print(f"       {C_CYAN}Version: {version}{C_RESET}")
            time.sleep(0.12)
            
    # Final Dashboard State
    clear_console()
    dash = f"{C_CYAN}{'='*60}{C_RESET}"
    
    print(f"\n   {C_CYAN}GEMSHOT ULTIMATE - LifeOS Station {version}{C_RESET}")
    print(dash)
    
    # 1. SYSTEM PATHS
    print(f"   {C_CYAN}[ SYSTEM PATHS ]{C_RESET}")
    print(f"   > Script Source: {C_WHITE}{script_path}{C_RESET}")
    print(f"   > Obsidian Vault: {C_WHITE}{vault_path}{C_RESET}")
    print(f"   > AI Intel: {C_WHITE}{model}{C_RESET}")
    print(dash)
    
    # 2. SHORTCUTS
    print(f"   {C_CYAN}[ QUICK SHORTCUTS ]{C_RESET}")
    print(f"   > {C_WHITE}Ctrl + Alt + S{C_RESET} : Trigger NEW Capture")
    print(f"   > {C_WHITE}S (in console){C_RESET} : Force Save All & Info")
    print(f"   > {C_WHITE}ESC (in UI){C_RESET}     : Cancel / Discard")
    print(dash)
    
    # 3. HOW TO CHANGE PATH
    print(f"   {C_CYAN}[ SETTINGS / RECOVERY ]{C_RESET}")
    print(f"   GemShot es ahora {C_WHITE}Portátil{C_RESET}. La boveda se crea en su propia carpeta.")
    print(f"   Puedes cambiar la ruta del Vault directamente en el {C_WHITE}Header{C_RESET} del Editor")
    print(f"   o editando {C_WHITE}config.yaml -> vault_root{C_RESET}")
    print(dash)
    
    # 4. HOW TO USE
    print(f"   {C_CYAN}[ USER GUIDE / HOW TO USE ]{C_RESET}")
    print(f"   1. {C_WHITE}Captura:{C_RESET} Usa el hotkey o click derecho en el Tray.")
    print(f"   2. {C_WHITE}Edita:{C_RESET} Dibuja flechas o usa el Borrador para ocultar info.")
    print(f"   3. {C_WHITE}IA:{C_RESET} Escribe instrucciones arriba y dale a ▶ para analizar.")
    print(f"   4. {C_WHITE}Modos:{C_RESET} Alterna entre Zen/Med/Pro en la esquina superior.")
    print(f"   5. {C_WHITE}Guarda:{C_RESET} Clic en 'Save' (Copia img al portapapeles y genera nota Markdown).")
    print(dash)
    
    print(f"\n   {C_CYAN}>>> STATUS: SYSTEM ONLINE & WAITING...{C_RESET}\n")

def print_fractal_celebration():
    """Fractal Gem ASCII animation to celebrate success!"""
    C_CYAN = Fore.CYAN
    C_WHITE = Fore.WHITE
    C_RESET = Style.RESET_ALL
    
    frames = [
        # Frame 1: Core
        """
             .
            / \\
            \\ /
             '
        """,
        # Frame 2: Expanding
        """
             .
            / \\
           <   >
            \\ /
             '
        """,
        # Frame 3: Crystalline
        """
             .
           /   \\
          /  💎  \\
          \\     /
           \\   /
             '
        """,
        # Frame 4: Fractal Burst
        """
          .     .     .
           \\   /   /
            \\ /  /
          -- 💎 --
            / \\  \\
           /   \\   \\
          '     '     '
        """
    ]
    
    for _ in range(3):
        for f in frames:
            os.system('cls' if os.name == 'nt' else 'clear')
            print(f"\n\n{C_CYAN}{f}{C_RESET}")
            print(f"\n   {C_WHITE}MISSION COMPLETE: GEMSHOT v3.8.0 ONLINE{C_RESET}")
            time.sleep(0.15)

