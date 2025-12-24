import customtkinter as ctk
import tkinter as tk
import mss

class SnippingOverlay(ctk.CTkToplevel):
    def __init__(self, parent, callback, on_cancel):
        super().__init__(parent)
        self.callback = callback
        self.on_cancel = on_cancel
        
        with mss.mss() as sct:
            # Multi-monitor support handled by using the virtual screen (index 0 usually covers union, but mss behavior varies. 
            # Using index 1 first monitor simply for safety or 0 for 'all' if supported correctly on platform).
            # For Windows, monitor[0] is strictly 'all monitors combined' in MSS.
            monitor = sct.monitors[0]
            self.geometry(f"{monitor['width']}x{monitor['height']}+{monitor['left']}+{monitor['top']}")
            self.virtual_left = monitor["left"]
            self.virtual_top = monitor["top"]

        self.overrideredirect(True) 
        self.attributes("-topmost", True) 
        self.attributes("-alpha", 0.3) 
        self.configure(fg_color="black")
        
        self.canvas = tk.Canvas(self, cursor="cross", bg="black", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)
        
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<B1-Motion>", self.on_drag)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)
        self.canvas.bind("<Escape>", lambda e: self.close())
        self.canvas.bind("<Button-3>", lambda e: self.close()) 

        self.start_x = None
        self.start_y = None
        self.rect = None
        self.lift()
        self.focus_force()

    def on_press(self, event):
        self.start_x = self.canvas.canvasx(event.x)
        self.start_y = self.canvas.canvasy(event.y)
        self.rect = self.canvas.create_rectangle(self.start_x, self.start_y, self.start_x, self.start_y, outline='#00ff00', width=2, fill="white", stipple="gray25")

    def on_drag(self, event):
        cur_x, cur_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        self.canvas.coords(self.rect, self.start_x, self.start_y, cur_x, cur_y)

    def on_release(self, event):
        end_x, end_y = (self.canvas.canvasx(event.x), self.canvas.canvasy(event.y))
        left, top = min(self.start_x, end_x), min(self.start_y, end_y)
        width, height = abs(end_x - self.start_x), abs(end_y - self.start_y)
        self.destroy()
        
        if width > 5 and height > 5:
            self.callback({
                'top': int(top) + self.virtual_top, 
                'left': int(left) + self.virtual_left, 
                'width': int(width), 
                'height': int(height)
            })
        else:
            self.on_cancel()

    def close(self):
        self.on_cancel()
        self.destroy()
