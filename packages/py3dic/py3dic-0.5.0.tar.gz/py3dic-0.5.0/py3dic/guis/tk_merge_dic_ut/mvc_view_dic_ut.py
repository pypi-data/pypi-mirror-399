
import logging
import pathlib
import tkinter as tk
from tkinter import ttk
from tkinter import filedialog

import cv2
from PIL import Image, ImageTk

logger = logging.getLogger(__name__)

from ...tktools.tk_collapsible_pane import CollapsiblePane

from .support.merge_parameters_tk_frame import TKDIC_UT_mergeParameters
from .mvc_model_dic_ut import Model_DIC_UT_merge
from .support.sync_graph_tk_frame import TkFrSyncGraph
from .support.plot_frame import TkMatplotlibPlotFrame
from py3dic import __version__ as py3dic_version

#TODO Add log window 
class ViewMergeDicUT:
    def __init__(self, master:tk.Tk, model:Model_DIC_UT_merge):
        self.master = master
        self.model = model
        self._tk_app_dir = model.get_starting_dir()

        # Configure the grid to allow resizing
        self.master.grid_columnconfigure(0, weight=1)
        self.master.grid_rowconfigure(0, weight=1)

        self.create_widgets()
        self.master.after(ms=1, func=self.create_widgets_with_delay)
    
    def create_widgets(self):
        self.master.title(f"DIC and UT merging tool v{py3dic_version}")
        # self.master.geometry("800x600")
        # Set only the width of the master window and let the height be determined by the widgets
        self.master.minsize(800, 100)

        self.master.configure(bg="lightgrey")

        self.dic_parameters_frame = TKDIC_UT_mergeParameters(self.master, model=self.model)
        self.dic_parameters_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=3, sticky="nsew")
        # self.dic_parameters_frame.btn_area_of_interest.configure(command=self.select_area_of_interest)
        # self.dic_parameters_frame.btn_toggle_roi_window.configure(command=self.toggle_select_ROI_window)

        # Button to start the DIC analysis
        self.btn_check_analysis_params = tk.Button(self.master, 
                text="Check Analysis\nParameters")
        self.btn_check_analysis_params.grid(row=2, column=0, padx=10, pady=10)

        # Button to start the DIC analysis
        self.btn_start_analysis = tk.Button(self.master, 
                text="Start Analysis",font=("Helvetica",16,'bold')
                )
        self.btn_start_analysis.grid(row=2, column=1, padx=10, pady=10)

        # sync plot tk.fram
        self.__notebook = ttk.Notebook(self.master)
        self.__notebook.grid(row=0, column=3,rowspan=3, padx=10, pady=10, sticky="nsew") 
        self.sync_plot_frame = TkFrSyncGraph(self.__notebook)
        self.sync_plot_frame.grid(row=0, column=0,rowspan=3, padx=10, pady=10, sticky="nsew")
        
        self.f_vs_exx_plot_frame = TkMatplotlibPlotFrame(self.__notebook)
        self.f_vs_exx_plot_frame.grid(row=0, column=0,rowspan=3, padx=10, pady=10, sticky="nsew")

        self.__notebook.add(self.sync_plot_frame, text="Time Plot")
        self.__notebook.add(self.f_vs_exx_plot_frame, text="Force vs Strain (exx) Plot")



        # # CollapsibleFrame for Merged data
        # self.cpMerged = CollapsiblePane(parent=self.master, 
        #         title="Merging file", expanded=False
        #         # TODO only allow expansion if analysis is performed.? 
        #         # there might be a use case where its not suitable (i.e. If I want to perfom analysis on already performed analysis)
        #         )
        # self.cpMerged.grid(row=3, column=0, columnspan=3, padx=10, pady=10)

        # self.lblUTTest = tk.Label(self.cpMerged.content_frame, text="UT Test name")
        # self.lblUTTest.grid(row=0,column=0)
        # self.txtUTFname = tk.Entry(self.cpMerged.content_frame, text="", state='readonly')
        # self.txtUTFname.grid(row=0,column=1)


    def create_widgets_with_delay(self):
        """This creates widgets with a delay 
        (to allow the gui window to be properly created)
        This should include other MDI window
        """        
        # Placeholder for the browse results window
        self.tlw_browse_results = None 


