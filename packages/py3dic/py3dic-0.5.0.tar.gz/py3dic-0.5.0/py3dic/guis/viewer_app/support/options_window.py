import tkinter as tk
from .parameter_window import GridParameterWindow, MarkerParameterWindow, GenericFallbackParameterWindow

class OptionsWindow(tk.LabelFrame):
    param_windows = {
        "grid": GridParameterWindow,
        "marker": MarkerParameterWindow,
        "displacement": GenericFallbackParameterWindow,
        "displacement_hsv": GenericFallbackParameterWindow,
        "strainmap_xx": GenericFallbackParameterWindow,
        "strainmap_yy": GenericFallbackParameterWindow,
        "strainmap_xy": GenericFallbackParameterWindow
        # Add other mappings for specific parameter windows
    }

    def __init__(self, parent):
        super().__init__(parent, text="Options")
        self.controller = None
        self.model = None

        self.checkbox_vars = {
            "grid": tk.BooleanVar(),
            "marker": tk.BooleanVar(),
            "displacement": tk.BooleanVar(),
            "displacement_hsv": tk.BooleanVar(),
            "strainmap_xx": tk.BooleanVar(),
            "strainmap_yy": tk.BooleanVar(),
            "strainmap_xy": tk.BooleanVar()
        }

        self.checkbuttons = {}  # To store references to checkbuttons
        self.create_widgets()

    def set_controller(self, controller):
        """Set the MVC controller for this options window.
        This method is called by the main view to link the controller to this options window.
        Args:
            controller: The controller instance that manages the application logic.
        """
        self.controller = controller
        self.model = controller.model
        self.update_checkboxes()
        self.initialize_default_params()

    def create_widgets(self):
        """Create the checkboxes and their associated parameter windows."""
        for key in self.checkbox_vars:
            cb = tk.Checkbutton(self, text=key.replace("_", " ").title(), variable=self.checkbox_vars[key], command=lambda k=key: self.on_checkbox_select(k), state=tk.DISABLED)
            cb.pack(anchor="w")
            self.checkbuttons[key] = cb

    def update_checkboxes(self):
        for key, var in self.checkbox_vars.items():
            var.set(self.model.selected_plots[key])

    def initialize_default_params(self):
        for key in self.checkbox_vars:
            self.set_default_params(key)

    def set_default_params(self, key):
        """	
        Set default parameters for the given plot type.
        """ 

        if key in self.param_windows:
            param_window_class = self.param_windows[key]
            self.model.update_plot_params(key, param_window_class.default_params.copy())

    def on_checkbox_select(self, key):
        """Eventy that is triggered when a checkbox is selected

        Args:
            key (_type_): _description_
        """
        is_checked = self.checkbox_vars[key].get()
        if is_checked:
            self.open_param_window(key)
            self.model.selected_plots[key] = True
        else:
            self.model.selected_plots[key] = False
        

    def open_param_window(self, key):

        if key in self.param_windows:
            param_window = self.param_windows[key](
                self, 
                self.model.plot_params[key],
                lambda params: self.update_plot_params(key, params)
            )
            param_window.deiconify()

    def update_plot_params(self, plot_type, params):
        self.model.update_plot_params(plot_type, params)
        self.model.selected_plots[plot_type] = True

    def set_state(self, state):
        """Set the state (enabled/Disabled) for the controls

        Args:
            state (_type_): _description_
        """
        for cb in self.checkbuttons.values():
            cb.config(state=state)
