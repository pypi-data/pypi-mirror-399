import tkinter as tk


class SimpleTooltip:
    """
    Very small tooltip helper for Tk widgets.
    Shows a small window with text when the mouse hovers over the widget.
    """

    def __init__(self, widget: tk.Widget, text: str = "") -> None:
        self.widget = widget
        self.text = text
        self._tipwindow: tk.Toplevel | None = None

        self.widget.bind("<Enter>", self._on_enter)
        self.widget.bind("<Leave>", self._on_leave)

    def set_text(self, text: str) -> None:
        self.text = text

    def _on_enter(self, event=None) -> None:  # type: ignore[override]
        if not self.text:
            return
        if self._tipwindow is not None:
            return
        x = self.widget.winfo_rootx() + 20
        y = self.widget.winfo_rooty() + self.widget.winfo_height() + 10
        self._tipwindow = tw = tk.Toplevel(self.widget)
        tw.wm_overrideredirect(True)
        tw.wm_geometry(f"+{x}+{y}")
        label = tk.Label(
            tw,
            text=self.text,
            justify="left",
            background="#ffffe0",
            relief="solid",
            borderwidth=1,
            padx=4,
            pady=2,
        )
        label.pack(ipadx=1)

    def _on_leave(self, event=None) -> None:  # type: ignore[override]
        if self._tipwindow is not None:
            self._tipwindow.destroy()
            self._tipwindow = None
