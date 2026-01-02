import tkinter as tk

class ParameterWindow(tk.Toplevel):
    """Creates a template class for a window to edit parameters
    
    """
    def __init__(self, parent, title, param_dict, update_callback):
        super().__init__(parent)
        self.title(title)
        self.param_dict = param_dict
        self.update_callback = update_callback

        self.on_current_image_var = tk.BooleanVar(value=param_dict.get("on_current_image", True))
        self.text_var = tk.StringVar(value=param_dict.get("text", ""))
        self.scale_var = tk.DoubleVar(value=param_dict.get("scale", 1.0))
        self.save_memory_var = tk.BooleanVar(value=param_dict.get("save_memory", True))

        self.create_widgets()

    def create_widgets(self):
        tk.Checkbutton(self, text="On Current Image", variable=self.on_current_image_var).pack(anchor="w")
        tk.Label(self, text="Text:").pack(anchor="w")
        tk.Entry(self, textvariable=self.text_var).pack(anchor="w")
        tk.Label(self, text="Scale:").pack(anchor="w")
        tk.Entry(self, textvariable=self.scale_var).pack(anchor="w")
        tk.Checkbutton(self, text="Save Memory", variable=self.save_memory_var).pack(anchor="w")

        tk.Button(self, text="Close", command=self.hide).pack(pady=10)

    def hide(self):
        self.param_dict["on_current_image"] = self.on_current_image_var.get()
        text = None if self.text_var.get() == "" else self.text_var.get()
        self.param_dict["text"] = text
        self.param_dict["scale"] = self.scale_var.get()
        self.param_dict["save_memory"] = self.save_memory_var.get()
        self.update_callback(self.param_dict)
        self.withdraw()



class GenericFallbackParameterWindow(ParameterWindow):
    default_params = {
        "on_current_image": True,
        "text": "",
        "scale": 1.0,
        "p_color": (1.0, 1.0, 0.0),  # Example specific parameter
        "save_memory": True,
        # Add other specific default parameters for Marker
    }

    def __init__(self, parent, param_dict, update_callback):
        param_dict.update(MarkerParameterWindow.default_params)
        super().__init__(parent, "Generic Parameters", param_dict, update_callback)


class GridParameterWindow(ParameterWindow):
    default_params = {
        "on_current_image": True,
        "text": "",
        "scale": 1.0,
        "save_memory": True,
        # Add other specific default parameters for Grid
    }

    def __init__(self, parent, param_dict, update_callback):
        param_dict.update(GridParameterWindow.default_params)
        super().__init__(parent, "Grid Parameters", param_dict, update_callback)


class MarkerParameterWindow(ParameterWindow):
    default_params = {
        "on_current_image": True,
        "text": "",
        "scale": 1.0,
        "p_color": (1.0, 1.0, 0.0),  # Example specific parameter
        "save_memory": True,
        # Add other specific default parameters for Marker
    }

    def __init__(self, parent, param_dict, update_callback):
        param_dict.update(MarkerParameterWindow.default_params)
        super().__init__(parent, "Marker Parameters", param_dict, update_callback)

# Add other specific parameter windows similarly
