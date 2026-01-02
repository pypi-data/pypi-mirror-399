import pathlib
import tkinter as tk
from tkinter import filedialog, messagebox

import cv2
from PIL import Image, ImageTk

import logging


logger = logging.getLogger(__name__)

from .mvc_model_dic import Model
from .support.tkf_dic_parameters import TKDICParameters
from .support.tktl_roi_image_window import ROIImageWindow
from ...tktools.tk_collapsible_pane import CollapsiblePane
from .support.tktp_browse_results import TLBrowseImageWindow
# code for integrating Merge Tool
from ..tk_merge_dic_ut.mvc_controller_dic_ut import tkapp_DIC_UT_merge_Controller

from py3dic import __version__ as p3dic_version
#TODO Add log window 
class ViewDicAnalysis:
    def __init__(self, master:tk.Tk, model:Model, full_interface:bool=False):
        self.master = master
        self._full_interface = full_interface
        self.model = model
        self._tk_app_dir = self.model.get_starting_dir()

        self.create_widgets()

        self.master.after(ms=50, func=self.create_widgets_with_delay)
    
    def create_widgets(self):
        self.master.title(f"DIC Analysis v{p3dic_version}")
        # self.master.geometry("800x600")
        self.master.configure(bg="lightgrey")

        # DIC parameters =================================================
        self.dic_parameters_frame = TKDICParameters(self.master, model=self.model)
        self.dic_parameters_frame.grid(row=0, column=0, padx=10, pady=10, columnspan=3)
        # callbacks
        self.dic_parameters_frame.btn_area_of_interest.configure(command=self.select_area_of_interest)
        self.dic_parameters_frame.btn_toggle_roi_window.configure(command=self.toggle_select_ROI_window)

        # BUTTONS        =================================================
        # Button to start the DIC analysis
        self.__frm_actions = tk.LabelFrame(self.master, text="Actions")
        self.__frm_actions.grid(row=0, column=4, columnspan=3, padx=10, pady=10)

        self.btn_check_analysis_params = tk.Button(self.__frm_actions, 
                text="Check Analysis\nParameters")
        self.btn_check_analysis_params.grid(row=2, column=0, padx=10, pady=10)

        # Button to start the DIC analysis
        self.btn_start_analysis = tk.Button(self.__frm_actions, 
                text="Start Analysis",font=("Helvetica",16,'bold')
                )
        self.btn_start_analysis.grid(row=2, column=1, padx=10, pady=10)

        # Button to view results of DIC analysis
        self.btn_view_results = tk.Button(self.__frm_actions, 
                text="View Results",font=("Helvetica",14, 'normal')
                )
        self.btn_view_results.grid(row=3, column=0, columnspan=2, padx=10, pady=10)
        self.btn_view_results.configure(command=self.toggle_tl_results_window)




        # Collapsible Pane for Merged data ==============================================
        # this section should be entirely modular. 
        # i.e. if I comment out the following line, the code will still work without any errors
        # TODO use an option in the model to determine if the merge tool is available
        # this will enable adding a different entry point in setup.py
        if self._full_interface:
            self._create_merge_collapsible_pane()
        
    def _create_merge_collapsible_pane(self):
        # ==============================================CollapsibleFrame for Merged data
        self.__cpMerged = CollapsiblePane(parent=self.__frm_actions, 
                title="Merging Tool options", expanded=False
                # TODO only allow expansion if analysis is performed.? 
                # there might be a use case where its not suitable (i.e. If I want to perfom analysis on already performed analysis)
                # Use a flag that is set to false when analysis commences, and true when the analysis is finished
                # and check for this flag before allowing expansion
                )
        self._frm_merge = self.__cpMerged.content_frame
        self.__cpMerged.grid(row=4, column=0, columnspan=3, padx=10, pady=10)

        #region code for integrating Merge Tool
        # create the Toplevel window for the merge tool, and the merge tool
        self._tltk_merge = tk.Toplevel(self.master)
        # change the top leven window close protocol for the view of cntr_merge to withdraw instead of destroy
        self._tltk_merge.protocol("WM_DELETE_WINDOW", self._tltk_merge.withdraw)
        self._tltk_merge.withdraw()

        self.cntr_merge = tkapp_DIC_UT_merge_Controller(master=self._tltk_merge,  starting_dir=self._tk_app_dir)
        
        # button for merging with UT
        self.btn_merge_with_UT = tk.Button(self.__cpMerged.content_frame, 
                text="Toggle Merge window"#,font=("Helvetica",14, 'normal')
                )
        self.btn_merge_with_UT.grid(row=1, column=0, columnspan=3, padx=10, pady=10)
        self.btn_merge_with_UT.configure(command= self.toggle_tl_factory(self._tltk_merge))

        #TODO Add logic in the controllor

        #endregion


    def create_widgets_with_delay(self):
        """This creates widgets with a delay 
        (to allow the gui window to be properly created)
        This should include other MDI window
        """        
        # Placeholder for the image window
        self.tlw_select_ROI = ROIImageWindow(master=self.master, image_path=None) 
        self.tlw_select_ROI.withdraw()

        # Placeholder for the browse results window
        self.tlw_browse_results = TLBrowseImageWindow(master=self.master, results_folder=None, standalone=True)
        self.tlw_browse_results.withdraw()


    def select_area_of_interest(self):
        
        self.tlw_select_ROI.set_image(image_path= self.model.select_first_image_in_dir())
        self.tlw_select_ROI.deiconify()
        
        #TODO implement logic that saves the region of interest 
        # (covert window to modal) This is ONLY SUGGESTION



    def toggle_tl_results_window(self):
        #consider this alternatively
        if self.tlw_browse_results.winfo_viewable():
            self.tlw_browse_results.withdraw()
        else:
            self.tlw_browse_results.deiconify()
            self.tlw_browse_results.change_type()
    
    def toggle_select_ROI_window(self):
        #consider this alternatively
        if self.tlw_select_ROI.winfo_viewable():
            self.tlw_select_ROI.withdraw()
        else:
            self.tlw_select_ROI.deiconify()

    def toggle_tl_merge_window(self):
        #consider this alternatively
        if self._tltk_merge.winfo_viewable():
            self._tltk_merge.withdraw()
        else:
            self._tltk_merge.deiconify() # if is withdrawn, it will be shown

    def toggle_tl_factory(self, window:tk.Toplevel):
        def toggle_tl_factory(self, window: tk.Toplevel):
            """
            Returns a function that toggles the visibility of the given Toplevel window.
            Parameters:
            - window (tk.Toplevel): The Toplevel window to toggle.
            Returns:
            - function: A function that toggles the visibility of the given Toplevel window.
            """

        def func():
            #consider this alternatively
            if window.winfo_viewable():
                window.withdraw()
            else:
                window.deiconify()
        return func