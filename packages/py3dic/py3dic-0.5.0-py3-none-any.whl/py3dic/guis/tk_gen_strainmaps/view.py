from __future__ import annotations

import re
import tkinter as tk
from tkinter import filedialog, messagebox


from .widgets.strain_component_widget import StrainComponentWidget
from .widgets.simple_tooltip import SimpleTooltip

from .model import STRAIN_COMPONENTS, StrainGeneratorModel
from .controller import StrainGeneratorController



class StrainGeneratorView(tk.Frame):
    """
    Tk view for the strain map generator.

    Keeps all Tk-specific concerns here; talks to the controller via its
    public methods only.
    """

    def __init__(self, master: tk.Tk, model: StrainGeneratorModel) -> None:
        super().__init__(master=master)
        self.model = model
        self.controller = StrainGeneratorController(model, self)

        self._status_var = tk.StringVar(value="Load an analysis JSON to begin.")
        self._cpu_var = tk.StringVar()
        self._frame_pattern_var = tk.StringVar(value=self.model.frame_pattern)
        self._alpha_var = tk.StringVar(value=str(self.model.global_alpha))

        # Info about loaded frames/images
        self._num_images_var = tk.StringVar(value="Images: -")
        self._last_image_var = tk.StringVar(value="Last image: -")
        self._lbl_num_images: tk.Label | None = None
        self._lbl_last_image: tk.Label | None = None
        self._frame_info_tooltip: SimpleTooltip | None = None

        # Per-component widgets keyed by component name
        self._component_widgets: dict[str, StrainComponentWidget] = {}

        self._build_ui()

    # ----- UI construction -------------------------------------------------
    def _build_ui(self) -> None:
        self.master.title("Tk Strain Map Generator")

        main = tk.Frame(self)
        main.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        # Actions frame
        act = tk.LabelFrame(main, text="Analysis")
        act.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")

        btn_browse = tk.Button(act, text="Browse JSON", command=self._on_browse_json)
        btn_browse.grid(row=0, column=0, padx=5, pady=5, sticky="ew")

        tk.Label(act, text="CPUs (blank = default):").grid(
            row=1, column=0, padx=5, pady=2, sticky="w"
        )
        cpu_entry = tk.Entry(act, textvariable=self._cpu_var, width=8)
        cpu_entry.grid(row=2, column=0, padx=5, pady=2, sticky="w")

        # Frame selection
        frame_sel = tk.LabelFrame(main, text="Frame Selection")
        frame_sel.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")

        tk.Label(frame_sel, text="Pattern (e.g. 1-10,20,30-50:2):").grid(
            row=0, column=0, padx=5, pady=2, sticky="w"
        )
        entry_pattern = tk.Entry(frame_sel, textvariable=self._frame_pattern_var, width=30)
        entry_pattern.grid(row=1, column=0, padx=5, pady=2, sticky="ew")

        help_btn = tk.Button(
            frame_sel,
            text="?",
            width=2,
            command=self._show_frame_pattern_help,
        )
        help_btn.grid(row=1, column=1, padx=2, pady=2, sticky="w")

        # Information labels about the loaded image set
        self._lbl_num_images = tk.Label(frame_sel, textvariable=self._num_images_var, anchor="w")
        self._lbl_num_images.grid(row=2, column=0, padx=5, pady=2, sticky="w", columnspan=2)

        self._lbl_last_image = tk.Label(frame_sel, textvariable=self._last_image_var, anchor="w")
        self._lbl_last_image.grid(row=3, column=0, padx=5, pady=2, sticky="w", columnspan=2)

        # Tooltip attached to last image label to report potential issues
        self._frame_info_tooltip = SimpleTooltip(self._lbl_last_image, text="")

        # Global options
        global_frame = tk.LabelFrame(main, text="Global Options")
        global_frame.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")

        tk.Label(global_frame, text="Alpha (0–1):").grid(
            row=0, column=0, padx=5, pady=2, sticky="w"
        )
        entry_alpha = tk.Entry(global_frame, textvariable=self._alpha_var, width=8)
        entry_alpha.grid(row=0, column=1, padx=5, pady=2, sticky="w")

        # Per-component options
        comp_frame = tk.LabelFrame(main, text="Strain Components")
        comp_frame.grid(row=0, column=1, rowspan=3, padx=5, pady=5, sticky="nsew")

        for r, name in enumerate(STRAIN_COMPONENTS):
            pretty = {
                "strain_xx": "ε_xx",
                "strain_yy": "ε_yy",
                "strain_xy": "ε_xy",
            }[name]

            widget = StrainComponentWidget(
                comp_frame,
                name=name,
                pretty_label=pretty,
                on_change=self._on_component_widget_change,
            )
            widget.grid(row=r, column=0, padx=5, pady=5, sticky="nsew")
            self._component_widgets[name] = widget

            # Initialize widget from current model config
            cfg = self.model.components[name]
            widget.set_from_config(cfg)

        # Actions at bottom
        btn_frame = tk.Frame(main)
        btn_frame.grid(row=3, column=0, columnspan=2, padx=5, pady=5, sticky="ew")

        btn_dry = tk.Button(btn_frame, text="Validate (dry run)", command=self._on_dry_run)
        btn_dry.grid(row=0, column=0, padx=5, pady=2)

        btn_gen = tk.Button(btn_frame, text="Generate Images", command=self._on_generate)
        btn_gen.grid(row=0, column=1, padx=5, pady=2)

        # Status bar
        status = tk.Label(self, textvariable=self._status_var, anchor="w")
        status.grid(row=1, column=0, padx=5, pady=5, sticky="ew")

        self.columnconfigure(0, weight=1)
        self.rowconfigure(0, weight=1)

    # ----- Callbacks from controller --------------------------------------
    def on_analysis_loaded(self) -> None:
        self.report_status("Analysis JSON loaded.")
        self._update_zlim_fields_from_model()
        self._update_frame_info_from_model()

    def report_status(self, msg: str) -> None:
        self._status_var.set(msg)
        self.update_idletasks()
    
    def _update_zlim_fields_from_model(self) -> None:
        """
        Update the zmin and zmax fields in the view based on the model's component configs.
        This is called after analysis is loaded and zlims are initialized.
        """
        for comp_name in STRAIN_COMPONENTS:
            if comp_name in self.model.components and comp_name in self._component_widgets:
                cfg = self.model.components[comp_name]
                if cfg.zlim is not None:
                    zmin, zmax = cfg.zlim
                    self._component_widgets[comp_name].set_zlims(zmin, zmax)

    def _update_frame_info_from_model(self) -> None:
        """
        Update informational labels about the number of images and the last image
        name based on the currently loaded analysis/container.
        """
        try:
            container = self.model.container
        except Exception:
            # Analysis not loaded yet
            self._num_images_var.set("Images: -")
            self._last_image_var.set("Last image: -")
            self._set_frame_info_style(ok=None, detail="")
            return

        image_list = getattr(container, "image_flist", None)
        if not image_list:
            self._num_images_var.set("Images: 0")
            self._last_image_var.set("Last image: -")
            self._set_frame_info_style(ok=None, detail="")
            return

        num_images = len(image_list)
        # Use sorted names to determine the "last" image by name
        sorted_names = sorted(str(p.name) for p in image_list)
        last_name = sorted_names[-1]

        self._num_images_var.set(f"Images: {num_images}")
        self._last_image_var.set(f"Last image: {last_name}")

        # Validate sequence consistency based on filename pattern:
        # expected pattern: <string>_00005.png (5-digit zero-padded index)
        m = re.match(r"^(.+)_([0-9]{5})\.png$", last_name)
        if not m:
            # Pattern not recognized; keep neutral color but offer a hint.
            self._set_frame_info_style(
                ok=None,
                detail=(
                    "Filename pattern not recognized as '<name>_00000.png'; "
                    "sequence consistency could not be checked."
                ),
            )
            return

        last_index_zero_based = int(m.group(2))
        expected_count = last_index_zero_based + 1

        if expected_count != num_images:
            detail = (
                f"Detected {num_images} image files, but last filename index is "
                f"{last_index_zero_based:05d} (expected {expected_count}). "
                "Some images may be missing; please verify the data."
            )
            self._set_frame_info_style(ok=False, detail=detail)
        else:
            self._set_frame_info_style(ok=True, detail="")

    def _set_frame_info_style(self, ok: bool | None, detail: str) -> None:
        """
        Adjust color and tooltip based on whether the frame sequence looks valid.
        ok=True  -> black text, no warning tooltip
        ok=False -> red text, warning tooltip
        ok=None  -> neutral (black) text, optional informational tooltip
        """
        if ok is True:
            fg_color = "black"
            tooltip_text = ""
        elif ok is False:
            fg_color = "red"
            tooltip_text = detail
        else:
            fg_color = "black"
            tooltip_text = detail

        if self._lbl_num_images is not None:
            self._lbl_num_images.configure(fg=fg_color)
        if self._lbl_last_image is not None:
            self._lbl_last_image.configure(fg=fg_color)
        if self._frame_info_tooltip is not None:
            self._frame_info_tooltip.set_text(tooltip_text)

    # ----- Help / tooltips ------------------------------------------------
    def _show_frame_pattern_help(self) -> None:
        """
        Show a small help dialog explaining the frame pattern syntax.
        """
        msg = (
            "Frame selection pattern syntax (1-based indices):\n\n"
            "  - '-1'               : all available frames\n"
            "  - 'N'                : single frame N\n"
            "  - 'A-B'              : all frames A, A+1, ..., B\n"
            "  - 'A-B:S'            : frames A, A+S, A+2S, ... ≤ B\n"
            "  - Comma-separated    : e.g. '1,2,5,10-20,30-50:2'\n\n"
            "Indices outside the available range are ignored; duplicates are removed."
        )
        messagebox.showinfo("Frame pattern help", msg)

    # ----- Internal event handlers ----------------------------------------
    def _on_browse_json(self) -> None:
        path = filedialog.askopenfilename(
            filetypes=[("JSON files", "*.json"), ("All files", "*.*")]
        )
        if not path:
            return

        cpus = self._parse_int(self._cpu_var.get())
        if cpus is not None and cpus <= 0:
            messagebox.showerror("Invalid CPUs", "CPUs must be a positive integer.")
            return

        self.controller.set_cpus(cpus)

        try:
            self.controller.load_json(path)
        except Exception as exc:  # pragma: no cover - user feedback
            messagebox.showerror("Error", f"Failed to load JSON:\n{exc}")

    def _on_component_widget_change(self, name: str) -> None:
        """
        Called whenever a StrainComponentWidget changes; pushes state to the model
        via the controller.
        """
        widget = self._component_widgets[name]
        cfg_args = widget.export_config_args()
        self.controller.update_component_config(name, **cfg_args)

    def _on_dry_run(self) -> None:
        self._push_basic_options_to_controller()
        summary = self.controller.dry_run()
        messagebox.showinfo("Dry run", f"{summary}")

    def _on_generate(self) -> None:
        self._push_basic_options_to_controller()
        try:
            self.controller.generate_images()
        except Exception as exc:  # pragma: no cover - user feedback
            messagebox.showerror("Error", f"Generation failed:\n{exc}")

    def _push_basic_options_to_controller(self) -> None:
        self.controller.set_frame_pattern(self._frame_pattern_var.get())

        alpha = self._parse_float(self._alpha_var.get())
        if alpha is None or not (0.0 <= alpha <= 1.0):
            messagebox.showerror("Invalid alpha", "Alpha must be a number between 0 and 1.")
            raise RuntimeError("Invalid alpha")
        self.controller.set_global_alpha(alpha)

    # ----- Parsing helpers -------------------------------------------------
    @staticmethod
    def _parse_int(text: str) -> int | None:
        text = text.strip()
        if not text:
            return None
        return int(text)

    @staticmethod
    def _parse_float(text: str) -> float | None:
        text = text.strip()
        if not text:
            return None
        return float(text)



