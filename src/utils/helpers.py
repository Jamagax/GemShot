from ctypes import windll, create_unicode_buffer
import math

def get_active_window_title():
    try:
        hWnd = windll.user32.GetForegroundWindow()
        length = windll.user32.GetWindowTextLengthW(hWnd)
        buf = create_unicode_buffer(length + 1)
        windll.user32.GetWindowTextW(hWnd, buf, length + 1)
        return buf.value
    except:
        return "Unknown"

def draw_arrow_pil(draw_ctx, x1, y1, x2, y2, color, width=3):
    """Draws an arrow on a PIL ImageDraw context."""
    # Draw the main line
    draw_ctx.line([x1, y1, x2, y2], fill=color, width=width)
    
    # Calculate angle
    angle = math.atan2(y2 - y1, x2 - x1)
    
    # Arrowhead size
    size = 15
    arrow_angle = math.pi / 6 # 30 degrees
    
    # Calculate vertices
    x3 = x2 - size * math.cos(angle - arrow_angle)
    y3 = y2 - size * math.sin(angle - arrow_angle)
    x4 = x2 - size * math.cos(angle + arrow_angle)
    y4 = y2 - size * math.sin(angle + arrow_angle)
    
    # Draw arrowhead triangle
    draw_ctx.polygon([x2, y2, x3, y3, x4, y4], fill=color)
