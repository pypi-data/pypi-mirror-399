import pathlib
import tkinter as tk
import logging
import sys

from .dic_viewer_controller import DICViewerController
from .dic_viewer_mvc_view import DICViewerMVCView

logging.basicConfig(level=logging.DEBUG)

def tk_viewer_app_launcher():
    if len(sys.argv) > 1:
        script_dir = pathlib.Path(sys.argv[1]).resolve()
    else:
        script_dir = pathlib.Path(__file__).resolve().parent

    print(f"Starting directory: {script_dir}")

    root = tk.Tk()
    root.title("DIC Analysis Viewer")

    main_view = DICViewerMVCView(root)
    main_view.pack(fill="both", expand=True)

    controller = DICViewerController(main_view, starting_dir=script_dir)
    main_view.set_controller(controller)

    root.mainloop()

if __name__ == "__main__":
    tk_viewer_app_launcher()
