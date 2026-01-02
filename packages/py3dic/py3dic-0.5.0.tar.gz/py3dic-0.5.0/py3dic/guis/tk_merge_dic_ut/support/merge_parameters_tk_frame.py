#TODO add button for verbosity level
# from ..mvc_model_dic_ut import Model_DIC_UT_merge
from .file_browser_entry import FileBrowseEntry


import tkinter as tk
from tkinter import messagebox


class TKDIC_UT_mergeParameters(tk.Frame):

    ENTRY_BOX_WIDTH = 6
    def __init__(self, master, 
                 model #:Model_DIC_UT_merge
                 ,**kwargs):
        super().__init__(master, **kwargs)
        self.model = model
        self._tk_app_dir = model.get_starting_dir()

        # Configure the grid to allow resizing
        self.grid_columnconfigure(0, weight=1)
        # self.grid_rowconfigure(0, weight=1)

        # =================== Input files Labelled frame ===================================
        lfInputFiles = tk.LabelFrame(self, text="Input Files")
        lfInputFiles.grid(row=0, column=0, padx=5, pady=5, sticky="nsew")
        lfInputFiles.grid_columnconfigure(0, weight=1)

        # Create FileBrowseEntry for DIC xlsx
        self.dic_entry = FileBrowseEntry(
                parent=lfInputFiles,
                label_text="DIC results:",
                button_text="Browse",
                browse_command=None,
                textvariable=self.model._tkvar_dic_xlsx)
        self.dic_entry.grid(row=0, column=0, sticky="nsew")

        self.chbx_auto_select = tk.Checkbutton(
                        master=lfInputFiles,
                        text="Auto-select",
                        variable=self.model._tk_auto_select_files)
        self.chbx_auto_select.grid(row=1, column=0, columnspan=3, sticky="nsew")
        #set command for the check box
        self.chbx_auto_select.config(command=self.auto_select_toggle)

        # Create FileBrowseEntry for metadata file
        self.metadata_entry = FileBrowseEntry(
                parent=lfInputFiles,
                label_text="Image\nMetadata File:",
                button_text="Browse",
                browse_command=None,
                textvariable=self.model._tkvar_metadata_file)
        self.metadata_entry.grid(row=2, column=0, sticky="nsew")
        self.metadata_entry.set_button_state("disabled")

        # Create FileBrowseEntry for ut file
        self.ut_entry = FileBrowseEntry(
            parent=lfInputFiles,
            label_text="Tensile Data:",
            button_text="Browse",
            browse_command=None,
            textvariable=self.model._tkvar_ut_file)
        self.ut_entry.grid(row=3,column=0,  sticky="nsew")
        self.ut_entry.set_button_state("disabled")


        # =================== Synchronisation Labelled frame ===================================
        lfSynchrosization = tk.LabelFrame(self, text="Synchronisation")
        lfSynchrosization.grid(row=1, column=0, padx=5, pady=5, sticky="nsew")
        lfSynchrosization.grid_columnconfigure(0, weight=1)

        self.lbl_timeOffset = tk.Label(
            master=lfSynchrosization,
            text="Time offset [s]"
        )
        self.lbl_timeOffset.grid(row=1,column=0, sticky="nsew")

        self.txt_Time_offset = tk.Entry(
            master = lfSynchrosization,
            textvariable=self.model._tkvar_time_offset
        )
        self.txt_Time_offset.grid(row=1,column=1, sticky="nsew")


        # =================== OUTPUT FILES Labeled frame ===================================
        lfOutPutFiles = tk.LabelFrame(self, text="Output Files")
        lfOutPutFiles.grid(row=2, column=0, padx=5, pady=5, sticky="nsew")
        lfOutPutFiles.grid_columnconfigure(0, weight=1)
        # Widgets for output parameters
        self.output_file_entry = FileBrowseEntry(
            parent = lfOutPutFiles,
            label_text= "Output file",
            button_text= "Browse",
            browse_command= lambda : messagebox.showinfo("Not implemented"),
            textvariable=self.model._tkvar_merged_xlsx
        )
        self.output_file_entry.grid(row=0,column=0, sticky="nsew")


    def auto_select_toggle(self):
        """Function that toggles the auto select files"""
        if self.model._tk_auto_select_files.get():
            # disable the metadata and ut file entries
            self.metadata_entry.set_button_state("disabled")
            self.ut_entry.set_button_state("disabled")
        else:
            # enable the metadata and ut file entries
            self.metadata_entry.set_button_state("normal")
            self.ut_entry.set_button_state("normal")