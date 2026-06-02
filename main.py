import tkinter as tk

from gui.app import App
from gui.theme import get_dpi_scale, init_dpi_before_tk, setup_theme


def main():
    init_dpi_before_tk()
    root = tk.Tk()
    scale = get_dpi_scale(root)
    root.tk.call('tk', 'scaling', scale)
    fonts = setup_theme(root, scale)
    App(root, fonts)
    root.mainloop()


if __name__ == '__main__':
    main()
