import tkinter as tk
from tkinter import filedialog
from .support.options_window import OptionsWindow
from py3dic import __version__ as py3dic_version

import logging
class DICViewerMVCView(tk.Frame):
    def __init__(self, parent):
        super().__init__(master=parent)
        self.controller = None

        self.master.title(f"DIC Viewer v{py3dic_version}")

        self.main_frame = tk.Frame(self)
        self.main_frame.grid(row=0, column=0, columnspan=2, padx=20, pady=20, sticky="nsew")

        # Options  frame ================================================
        self.options_frame = OptionsWindow(self.main_frame)
        self.options_frame.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")
        self.options_frame.set_state(tk.DISABLED)  # Initially disable

        # Image Range Frame
        ## create and set a label frame for the image range (e.g. start, end, step)
        label_frame_image_range = tk.LabelFrame(self.main_frame, text="Image Range (not implemented)")
        label_frame_image_range.grid(row=0, column=2, padx=10, pady=10, sticky="nsew")
        
        lbl_image_range_start = tk.Label(label_frame_image_range, text="Start:")
        lbl_image_range_start.grid(row=0, column=0, padx=5, pady=5, sticky="w")
        self.image_range_start = tk.Entry(label_frame_image_range)
        self.image_range_start.grid(row=0, column=1, padx=5, pady=5, sticky="ew")

        lbl_image_range_end = tk.Label(label_frame_image_range, text="End:")
        lbl_image_range_end.grid(row=1, column=0, padx=5, pady=5, sticky="w")
        self.image_range_end = tk.Entry(label_frame_image_range)
        self.image_range_end.grid(row=1, column=1, padx=5, pady=5, sticky="ew")

        lbl_image_range_step = tk.Label(label_frame_image_range, text="Step:")
        lbl_image_range_step.grid(row=2, column=0, padx=5, pady=5, sticky="w")
        self.image_range_step = tk.Entry(label_frame_image_range)
        self.image_range_step.grid(row=2, column=1, padx=5, pady=5, sticky="ew")
        self.image_range_start.insert(0, "0")
        self.image_range_end.insert(0, "100")
        self.image_range_step.insert(0, "1")
        # self.columnconfigure(2, weight=1)


        # Action frame ================================================
        labframe_actions = tk.LabelFrame(self.main_frame, text="Actions")
        labframe_actions.grid(row=0, column=1, padx=10, pady=10, sticky="nsew")

        self.browse_button = tk.Button(labframe_actions, text="Browse JSON", command=self.browse_json)
        self.browse_button.grid(row=0, column=0, padx=10, pady=10, sticky="nsew")

        self.display_button = tk.Button(labframe_actions, text="Display JSON Data", command=self.display_json_data, state=tk.DISABLED)
        self.display_button.grid(row=1, column=0, padx=10, pady=10, sticky="nsew")

        self.validate_button = tk.Button(labframe_actions, text="Validate input", command=self.dry_run, state=tk.DISABLED)
        self.validate_button.grid(row=2, column=0, padx=10, pady=10, sticky="nsew")

        self.generate_button = tk.Button(labframe_actions, text="Generate Images", command=self.generate_images, state=tk.DISABLED)
        self.generate_button.grid(row=3, column=0, padx=10, pady=10, sticky="nsew")

        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)

    def set_controller(self, controller):
        self.controller = controller
        self.options_frame.set_controller(controller)

    def browse_json(self):
        file_path = filedialog.askopenfilename(filetypes=[("JSON files", "*.json")])
        if file_path:
            self.controller.load_json(file_path)

    def display_json_data(self):
        self.controller.display_json_data()

    def dry_run(self):
        self.controller.dry_run()

    def generate_images(self):
        print("View: Generating images")
        self.controller.generate_images()

    def enable_controls(self):
        # buttons 
        self.display_button.config(state=tk.NORMAL)
        self.validate_button.config(state=tk.NORMAL)
        self.generate_button.config(state=tk.NORMAL)
        # Options frame
        self.options_frame.set_state(tk.NORMAL)
