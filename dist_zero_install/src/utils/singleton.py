import os
import signal
import time
import atexit

PID_FILE = "gemshot.pid"

def ensure_single_instance():
    """
    Ensures that only one instance of the app is running.
    If a previous instance is found, it is terminated to let the new one take over.
    """
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                content = f.read().strip()
                if not content:
                    old_pid = None
                else:
                    old_pid = int(content)
            
            if old_pid and old_pid != os.getpid():
                print(f"[*] Found previous instance (PID: {old_pid}). Terminating...")
                if os.name == 'nt':
                    # Windows specific kill
                    os.system(f"taskkill /F /PID {old_pid} >nul 2>&1")
                else:
                    # Unix/Mac kill
                    os.kill(old_pid, signal.SIGKILL)
                
                # Wait a bit for the previous instance to release hotkeys/tray
                time.sleep(1.0)
        except Exception as e:
            # PID might be stale or invalid, ignore
            pass
            
    # Write current PID
    try:
        with open(PID_FILE, "w") as f:
            f.write(str(os.getpid()))
    except:
        pass

def cleanup_pid():
    """Removes the PID file on exit."""
    if os.path.exists(PID_FILE):
        try:
            with open(PID_FILE, "r") as f:
                stored_pid = int(f.read().strip())
                if stored_pid == os.getpid():
                    os.remove(PID_FILE)
        except:
            pass

# Register cleanup
atexit.register(cleanup_pid)
