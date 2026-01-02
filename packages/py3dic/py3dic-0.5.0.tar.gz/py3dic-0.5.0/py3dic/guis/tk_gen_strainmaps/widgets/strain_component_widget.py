import tkinter as tk

from .simple_tooltip import SimpleTooltip

DEFAULT_BG = "Cur"  # Change this for changing the default background selection
# Select one of "Ref", "Cur", "Both"
# NOTE: the default behavior is determined by StrainComponentConfig class.


class StrainComponentWidget(tk.LabelFrame):
    """
    Composite widget encapsulating all options for a single strain component.

    Responsibilities:
    - Manage Tk variables for:
        * enabled (generate images)
        * background mode (Ref / Cur / Both)
        * auto z-lim flag
        * manual z-min / z-max
    - Provide helpers to synchronize with the model / controller.
    """

    def __init__(self, master, name: str, pretty_label: str, on_change) -> None:
        super().__init__(master, text=pretty_label, borderwidth=2, relief="groove")

        self._name = name
        self._on_change = on_change # callback when any setting changes

        # Main enable checkbox
        self.enabled_var = tk.BooleanVar(value=True)
        self._chk_enabled = tk.Checkbutton(
            self,
            text="Generate",
            variable=self.enabled_var,
            command=self._on_any_change,
        )
        self._chk_enabled.grid(row=0, column=0, padx=5, pady=2, sticky="w")

        # Background dropdown: Ref / Cur / Both
        tk.Label(self, text="Background:").grid(
            row=0, column=1, padx=5, pady=2, sticky="e"
        )
        self.bg_var = tk.StringVar(value=DEFAULT_BG)
        self._bg_menu = tk.OptionMenu(
            self,
            self.bg_var,
            "Ref",
            "Cur",
            "Both",
            command=lambda _value: self._on_any_change(),
        )
        self._bg_menu.grid(row=0, column=2, padx=5, pady=2, sticky="w")

        # Auto z-lim
        self.auto_zlim_var = tk.BooleanVar(value=True)
        self._chk_auto = tk.Checkbutton(
            self,
            text="Auto z-lim",
            variable=self.auto_zlim_var,
            command=self._on_any_change,
        )
        self._chk_auto.grid(row=1, column=0, columnspan=2, padx=5, pady=2, sticky="w")

        # Manual z-lim
        tk.Label(self, text="zmin:").grid(
            row=2, column=0, padx=5, pady=1, sticky="e"
        )
        self.zmin_var = tk.StringVar()
        self._entry_zmin = tk.Entry(self, textvariable=self.zmin_var, width=8)
        self._entry_zmin.grid(row=2, column=1, padx=2, pady=1, sticky="w")

        tk.Label(self, text="zmax:").grid(
            row=2, column=2, padx=5, pady=1, sticky="e"
        )
        self.zmax_var = tk.StringVar()
        self._entry_zmax = tk.Entry(self, textvariable=self.zmax_var, width=8)
        self._entry_zmax.grid(row=2, column=3, padx=2, pady=1, sticky="w")

        # Initial enabled state sync
        self._refresh_enabled_state()

    # ----- Internal helpers -------------------------------------------------
    def _on_any_change(self) -> None:
        """
        Callback whenever any user-facing control changes.
        """
        self._refresh_enabled_state()
        if self._on_change is not None:
            self._on_change(self._name)

    def _refresh_enabled_state(self) -> None:
        """
        Enable/disable child widgets based on the main enabled checkbox.
        Note: this only affects user interaction; programmatic updates to
        the StringVars still work.
        """
        state = "normal" if self.enabled_var.get() else "disabled"

        # Background dropdown is disabled/enabled via its associated menubutton
        self._bg_menu.configure(state=state)
        self._chk_auto.configure(state=state)
        self._entry_zmin.configure(state=state)
        self._entry_zmax.configure(state=state)

    # ----- Public API used by the view/controller --------------------------
    def set_from_config(self, cfg) -> None:
        """
        Initialize widget state from a StrainComponentConfig.
        """
        self.enabled_var.set(cfg.enabled)

        # Map booleans to dropdown text
        if cfg.use_ref_background and cfg.use_cur_background:
            self.bg_var.set("Both")
        elif cfg.use_ref_background and not cfg.use_cur_background:
            self.bg_var.set("Ref")
        elif cfg.use_cur_background and not cfg.use_ref_background:
            self.bg_var.set("Cur")
        else:
            # Fallback to default if nothing is selected
            self.bg_var.set(DEFAULT_BG)

        self.auto_zlim_var.set(cfg.use_auto_zlim)

        if cfg.zlim is not None:
            zmin, zmax = cfg.zlim
            self.zmin_var.set(str(zmin))
            self.zmax_var.set(str(zmax))

        self._refresh_enabled_state()

    def export_config_args(self) -> dict:
        """
        Export keyword arguments for StrainGeneratorController.update_component_config.
        """
        enabled = self.enabled_var.get()

        bg_value = self.bg_var.get()
        if bg_value == "Both":
            use_ref_background = True
            use_cur_background = True
        elif bg_value == "Cur":
            use_ref_background = False
            use_cur_background = True
        else:  # "Ref" or anything unexpected
            use_ref_background = True
            use_cur_background = False

        use_auto_zlim = self.auto_zlim_var.get()

        manual_zlim = None
        if not use_auto_zlim:
            try:
                zmin = float(self.zmin_var.get())
                zmax = float(self.zmax_var.get())
                manual_zlim = (zmin, zmax)
            except ValueError:
                manual_zlim = None

        return {
            "enabled": enabled,
            "use_ref_background": use_ref_background,
            "use_cur_background": use_cur_background,
            "use_auto_zlim": use_auto_zlim,
            "manual_zlim": manual_zlim,
        }

    def set_zlims(self, zmin: float, zmax: float) -> None:
        """
        Programmatically update the zmin/zmax fields, regardless of enabled state.
        """
        self.zmin_var.set(str(zmin))
        self.zmax_var.set(str(zmax))

    def set_enabled_state(self, enabled: bool) -> None:
        """
        Explicitly set the enabled state and refresh the widget.
        """
        self.enabled_var.set(enabled)
        self._refresh_enabled_state()
