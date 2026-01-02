#%%
"""
Launcher for the Tk strain-map generator application.

start with

> python -m py3dic.guis.tk_gen_strainmaps

"""
#%%

from __future__ import annotations

import logging
import pathlib
import sys
import tkinter as tk

from .model import StrainGeneratorModel
from .view import StrainGeneratorView

#TODO: check what is the best way to enable logging for the whole package 
#     i.e. I realised that if there is basicCofing elsewhere it modifies the logging level for the whole package


def run_strainmap_generator() -> None:
    """
    Entry point for the Tk strain-map generator application.

    Usage (from CLI):
        python -m py3dic.guis.tk_gen_strainmaps.launcher [optional_json_path]
    """
    # # Set up logging with DEBUG level
    logging.basicConfig(
        level=logging.INFO, 
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        force=True
    )

    logging.debug("Starting Tk strain-map generator application")
    print("Starting Tk strain-map generator application")
    if len(sys.argv) > 1:
        start_dir = pathlib.Path(sys.argv[1]).resolve()
    else:
        start_dir = pathlib.Path(__file__).resolve().parent

    print(f"Starting directory: {start_dir}")

    root = tk.Tk()
    model = StrainGeneratorModel()
    view = StrainGeneratorView(root, model)
    view.pack(fill="both", expand=True)

    root.mainloop()


if __name__ == "__main__":
    run_strainmap_generator()



