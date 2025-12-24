import os
import sys
import subprocess
import platform
import logging

def get_platform():
    return platform.system()

def open_folder(path):
    """Opens a folder in the system's file explorer."""
    path = os.path.abspath(path)
    if not os.path.exists(path):
        return
        
    system = get_platform()
    if system == "Windows":
        os.startfile(path)
    elif system == "Darwin": # macOS
        subprocess.run(["open", path])
    else: # Linux
        subprocess.run(["xdg-open", path])

def minimize_console():
    """Minimizes the console window if running on Windows."""
    system = get_platform()
    if system == "Windows":
        try:
            import ctypes
            kernel32 = ctypes.WinDLL('kernel32')
            user32 = ctypes.WinDLL('user32')
            hWnd = kernel32.GetConsoleWindow()
            if hWnd:
                user32.ShowWindow(hWnd, 6) # SW_MINIMIZE = 6
        except Exception as e:
            logging.error(f"Failed to minimize console on Windows: {e}")
    # On macOS/Linux, there isn't a standard way to minimize the active terminal 
    # without specific terminal emulators or complex AppleScript.

def copy_image_to_clipboard(image):
    """Copies a PIL Image to the system clipboard."""
    system = get_platform()
    
    if system == "Windows":
        try:
            import win32clipboard
            from io import BytesIO
            
            output = BytesIO()
            image.convert("RGB").save(output, "BMP")
            data = output.getvalue()[14:] # Remove BMP header
            output.close()
            
            win32clipboard.OpenClipboard()
            win32clipboard.EmptyClipboard()
            win32clipboard.SetClipboardData(win32clipboard.CF_DIB, data)
            win32clipboard.CloseClipboard()
            return True
        except Exception as e:
            logging.error(f"Windows Clipboard Error: {e}")
            return False
            
    elif system == "Darwin": # macOS
        try:
            from io import BytesIO
            temp_img = "temp_clipboard.png"
            image.save(temp_img, "PNG")
            
            # AppleScript to copy image to clipboard
            script = f'set the clipboard to (read (POSIX file "{os.path.abspath(temp_img)}") as «class PNGf»)'
            subprocess.run(["osascript", "-e", script])
            
            if os.path.exists(temp_img):
                os.remove(temp_img)
            return True
        except Exception as e:
            logging.error(f"macOS Clipboard Error: {e}")
            return False
            
    else:
        logging.warning("Clipboard image copy not supported on this platform yet.")
        return False

def is_keyboard_hit():
    """Cross-platform check for keyboard hit (non-blocking)."""
    system = get_platform()
    if system == "Windows":
        import msvcrt
        return msvcrt.kbhit()
    else:
        # On Mac/Linux, this is much more complex without third-party libs
        # For now, we return False to avoid blocking or errors
        return False

def get_key():
    """Cross-platform get key."""
    system = get_platform()
    if system == "Windows":
        import msvcrt
        return msvcrt.getch()
    else:
        return b''
