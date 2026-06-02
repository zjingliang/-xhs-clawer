import sys
import ctypes

import tkinter as tk
from tkinter import ttk


def init_dpi_before_tk():
    if sys.platform != 'win32':
        return
    try:
        ctypes.windll.user32.SetProcessDpiAwarenessContext(ctypes.c_void_p(-4))
    except Exception:
        try:
            ctypes.windll.shcore.SetProcessDpiAwareness(2)
        except Exception:
            try:
                ctypes.windll.user32.SetProcessDPIAware()
            except Exception:
                pass


def get_dpi_scale(root):
    try:
        dpi = root.winfo_fpixels('1i')
        return max(1.0, dpi / 96.0)
    except Exception:
        return 1.0


def setup_theme(root, scale):
    base = max(13, round(13 * scale))
    title = max(18, round(18 * scale))
    small = max(12, round(12 * scale))
    log_size = max(12, round(12 * scale))

    fonts = {
        'title': ('Microsoft YaHei UI', title, 'bold'),
        'normal': ('Microsoft YaHei UI', base),
        'small': ('Microsoft YaHei UI', small),
        'log': ('Consolas', log_size),
    }

    style = ttk.Style(root)
    style.configure('.', font=fonts['normal'])
    style.configure('TLabel', font=fonts['normal'])
    style.configure('Title.TLabel', font=fonts['title'])
    style.configure('Sub.TLabel', font=fonts['small'])
    style.configure('TButton', font=fonts['normal'], padding=(14, 8))
    style.configure('TNotebook.Tab', font=fonts['normal'], padding=(18, 10))
    style.configure('TEntry', font=fonts['normal'])
    style.configure('TSpinbox', font=fonts['normal'])
    style.configure('TLabelframe.Label', font=fonts['normal'])
    return fonts
