import tkinter as tk
from tkinter import ttk

class DualSlider(ttk.LabelFrame):
    """
    A custom widget that represents a dual slider.
    UseCase: set the limits of a range. 

    Args:
        parent (tkinter.Tk | tkinter.Toplevel): The parent widget.
        title (str): The title of the widget.
        min_value (int, optional): The minimum value of the sliders. Defaults to 0.
        max_value (int, optional): The maximum value of the sliders. Defaults to 100.
        start_value (int, optional): The initial value of the start slider. Defaults to 20.
        stop_value (int, optional): The initial value of the stop slider. Defaults to 80.
    Attributes:
        min_value (int): The minimum value of the sliders.
        max_value (int): The maximum value of the sliders.
        start_value (tkinter.IntVar): The current value of the start slider.
        stop_value (tkinter.IntVar): The current value of the stop slider.
    Methods:
        update_start(value): Updates the start slider value and prevents crossing the stop slider.
        update_stop(value): Updates the stop slider value and prevents crossing the start slider.
        update_limits(min_value, max_value): Updates the minimum and maximum values of the sliders.
        update_start_label(*args): Updates the label text for the start slider.
        update_stop_label(*args): Updates the label text for the stop slider.
        get_range() -> list: Returns the current range of the sliders as a list.
    """
    def __init__(self, parent, title, min_value=0, max_value=100, start_value=20, stop_value=80, *args, **kwargs):
        super().__init__(parent, text=title, *args, **kwargs)

        self.min_value = min_value
        self.max_value = max_value
        self.start_value = tk.IntVar(value=start_value)
        self.stop_value = tk.IntVar(value=stop_value)

        # Start slider and label
        self.start_label = ttk.Label(self, text=f"Start ({self.start_value.get()}):")
        self.start_label.grid(row=0, column=0, padx=5, pady=5)
        self.start_slider = ttk.Scale(self, from_=min_value, to=max_value, orient='horizontal', variable=self.start_value, command=self.update_start)
        self.start_slider.grid(row=0, column=1, padx=10, pady=5, sticky="ew")

        # End slider and label
        self.stop_label = ttk.Label(self, text=f"End ({self.stop_value.get()}):")
        self.stop_label.grid(row=1, column=0, padx=5, pady=5)
        self.stop_slider = ttk.Scale(self, from_=min_value, to=max_value, orient='horizontal', variable=self.stop_value, command=self.update_stop)
        self.stop_slider.grid(row=1, column=1, padx=10, pady=5, sticky="ew")

        # Configure the grid to expand the slider when the window resizes
        self.columnconfigure(1, weight=1)

        # Update the label text when the slider values change using trace_add
        self.start_value.trace_add('write', self.update_start_label)
        self.stop_value.trace_add('write', self.update_stop_label)

    def update_start(self, value)->None:
        # Prevent crossing the stop slider
        if self.start_value.get() >= self.stop_value.get():
            self.start_value.set(self.stop_value.get() - 1)

    def update_stop(self, value)->None:
        # Prevent crossing the start slider
        if self.stop_value.get() <= self.start_value.get():
            self.stop_value.set(self.start_value.get() + 1)
            
    def update_limits(self, min_value, max_value)->None:
        self.min_value = min_value
        self.max_value = max_value
        self.start_slider.config(from_=min_value, to=max_value)
        self.stop_slider.config(from_=min_value, to=max_value)

    def update_start_label(self, *args)->None:
        self.start_label.config(text=f"Start ({self.start_value.get()}):")

    def update_stop_label(self, *args)->None:
        self.stop_label.config(text=f"End ({self.stop_value.get()}):")

    def get_range(self) -> list:
        return [self.start_value.get(), self.stop_value.get()]

if __name__ == "__main__":
    root = tk.Tk()
    root.title("Dual Slider Example")

    dual_slider = DualSlider(root, title="Time Limits", min_value=0, max_value=100, start_value=20, stop_value=80)
    dual_slider.pack(fill='both', expand=True, padx=10, pady=10)

    dual_slider2 = DualSlider(root, title="Force Limits", min_value=0, max_value=100, start_value=20, stop_value=80)
    dual_slider2.pack(fill='both', expand=True, padx=10, pady=10)
    root.mainloop()
