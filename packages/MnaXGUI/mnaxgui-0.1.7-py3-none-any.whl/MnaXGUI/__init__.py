# PyGUI.py
import tkinter as tk

# -----------------------
# Window
# -----------------------

class Window:
    def __init__(self):
        self.root = tk.Tk()
        self.visible = True

    def title(self, text):
        self.root.title(text)
        return self

    def size(self, size):
        self.root.geometry(size)
        return self

    def show(self):
        if not self.visible:
            self.root.deiconify()
            self.visible = True
        self.root.mainloop()
        return self

    def hide(self):
        self.root.withdraw()
        self.visible = False
        return self


window = Window()


# -----------------------
# Base Widget
# -----------------------

class BaseWidget:
    def __init__(self):
        self.widget = None
        self.x = 0
        self.y = 0
        self.w = None
        self.h = None
        self.visible = False

    def pos(self, x, y):
        self.x = x
        self.y = y
        return self

    def size(self, w, h):
        self.w = w
        self.h = h
        return self

    def show(self):
        if self.widget:
            self.widget.place(x=self.x, y=self.y, width=self.w, height=self.h)
            self.visible = True
        return self

    def hide(self):
        if self.widget:
            self.widget.place_forget()
            self.visible = False
        return self


# -----------------------
# Text
# -----------------------

class Text(BaseWidget):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.color_value = "black"
        self.outline_value = False

    def color(self, color):
        self.color_value = color
        return self

    def outline(self, yes):
        self.outline_value = yes
        return self

    def show(self):
        if self.widget is None:
            self.widget = tk.Label(
                window.root,
                text=self.text,
                fg=self.color_value,
                bd=2 if self.outline_value else 0,
                relief="solid" if self.outline_value else "flat"
            )
        return super().show()


# -----------------------
# Button
# -----------------------

class Button(BaseWidget):
    def __init__(self, text):
        super().__init__()
        self.text = text
        self.color_value = "lightgray"
        self.command_func = None

    def color(self, color):
        self.color_value = color
        return self

    def on_click(self, func):
        self.command_func = func
        return self

    def show(self):
        if self.widget is None:
            self.widget = tk.Button(
                window.root,
                text=self.text,
                bg=self.color_value,
                command=self.command_func
            )
        return super().show()


# -----------------------
# Input
# -----------------------

class Input(BaseWidget):
    def __init__(self, placeholder=""):
        super().__init__()
        self.placeholder = placeholder

    def show(self):
        if self.widget is None:
            self.widget = tk.Entry(window.root)
            if self.placeholder:
                self.widget.insert(0, self.placeholder)
        return super().show()

    def get(self):
        if self.widget:
            return self.widget.get()
        return ""


# -----------------------
# Public API
# -----------------------

__all__ = [
    "window",
    "Text",
    "Button",
    "Input"
]
