import pystray
from PIL import Image, ImageDraw
import threading
import os
import sys
from src.utils.platform_utils import open_folder

class SystemTrayIcon:
    def __init__(self, on_capture, on_dashboard, on_exit):
        self.on_capture = on_capture
        self.on_dashboard = on_dashboard
        self.on_exit = on_exit
        self.icon = None

    def create_image(self):
        # Create a simple icon (Blue Diamond)
        width = 64
        height = 64
        image = Image.new('RGB', (width, height), (255, 255, 255))
        dc = ImageDraw.Draw(image)
        
        # Transparent background hack (not real transparency in systray usually without .ico, but visually okay for generated)
        dc.rectangle((0, 0, width, height), fill=(0, 0, 0)) # Black bg
        
        # Draw Diamond
        dc.polygon(
            [(width//2, 10), (width-10, height//2), (width//2, height-10), (10, height//2)],
            fill="#3B82F6", outline="#60A5FA"
        )
        return image

    def run(self):
        menu = (
            pystray.MenuItem('📊 Dashboard', self.action_dashboard),
            pystray.MenuItem('📸 Capture Now', self.action_capture, default=True),
            pystray.MenuItem('📂 Open Folder', self.action_open_folder),
            pystray.Menu.SEPARATOR,
            pystray.MenuItem('❌ Exit', self.action_exit)
        )
        
        self.icon = pystray.Icon("LifeOS", self.create_image(), "LifeOS Capture", menu)
        
        # Run in independent thread to not block main loop if needed, 
        # BUT pystray usually needs to be main thread on macOS/some Linux. 
        # On Windows, it's flexible but sticking to thread is valuable for GUI app integration.
        threading.Thread(target=self.icon.run, daemon=True).start()

    def action_capture(self, icon, item):
        self.on_capture()

    def action_dashboard(self, icon, item):
        self.on_dashboard()

    def action_open_folder(self, icon, item):
        path = os.path.abspath("output/attachments")
        open_folder(path)

    def action_exit(self, icon, item):
        self.icon.stop()
        self.on_exit()
