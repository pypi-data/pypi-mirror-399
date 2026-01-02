#TODO add button for verbosity level
from py3dic.guis.tk_dic_analysis.mvc_model_dic import EnumDataSelection, EnumInterpolation, EnumStrainType, Model


import tkinter as tk
from tkinter import ttk


class TKDICParameters(tk.Frame):

    ENTRY_BOX_WIDTH = 6
    def __init__(self, master, model:Model,**kwargs):
        super().__init__(master, **kwargs)
        self.model = model
        self._tk_app_dir = model.get_starting_dir()

        # =================== Input files Labelled frame ===================================
        lfInputFiles = tk.LabelFrame(self, text="Input Files")
        lfInputFiles.grid(row=0, column=0, padx=5, pady=5)

        # Widgets for image directory
        self.label_image_directory = tk.Label(lfInputFiles,
                text="Image Directory:")
        self.label_image_directory.grid(row=0, column=0)
        self.entry_image_directory = tk.Entry(lfInputFiles,
                state='readonly',
                textvariable=self.model._tkvar_image_directory)
        self.entry_image_directory.grid(row=0, column=1)
        self.button_image_directory = tk.Button(lfInputFiles,
                text="Browse",
                command=self.model.browse_image_directory)
        self.button_image_directory.grid(row=0, column=2)

        # Widgets for metadata file
        self.label_metadata_file = tk.Label(lfInputFiles,
                text="Metadata File:")
        self.label_metadata_file.grid(row=1, column=0)
        self.entry_metadata_file = tk.Entry(lfInputFiles,
                state='readonly',
                textvariable=self.model._tkvar_metadata_file)
        self.entry_metadata_file.grid(row=1, column=1)
        self.button_metadata_file = tk.Button(lfInputFiles,
                text="Browse",
                command=self.model.browse_metadata_file)
        self.button_metadata_file.grid(row=1, column=2)

        # =================== DIC Analysis Parameters Labelled frame ===================================
        lfDICAnalysisParams = tk.LabelFrame(self, text="DIC Analysis Parameters")
        lfDICAnalysisParams.grid(row=1, column=0, padx=5, pady=5)


        self.btn_area_of_interest = tk.Button(lfDICAnalysisParams,
                text="Select Area of Interest")
                #,command=self.select_area_of_interest)
        self.btn_area_of_interest.grid(row=0, column=0, columnspan=2)
        # Button to toggle the image window
        self.btn_toggle_roi_window = tk.Button(lfDICAnalysisParams,
                text="Toggle \nROI Window")
        self.btn_toggle_roi_window.grid(row=0, column=2)

        # Widgets for DIC analysis parameters
        label_correl_X = tk.Label(lfDICAnalysisParams, text="X")
        label_correl_X.grid(row=1, column=1)
        label_correl_Y = tk.Label(lfDICAnalysisParams, text="Y")
        label_correl_Y.grid(row=1, column=2)
        self.label_correl_wind_size_x = tk.Label(lfDICAnalysisParams, text="Correlation Window Size:")
        self.label_correl_wind_size_x.grid(row=2, column=0)
        self.entry_correl_wind_size_x = tk.Entry(lfDICAnalysisParams, width=self.ENTRY_BOX_WIDTH, justify=tk.CENTER,
                                                 textvariable=self.model._tkvar_correl_wind_size_x)
        self.entry_correl_wind_size_x.grid(row=2, column=1)
        self.entry_correl_wind_size_y = tk.Entry(lfDICAnalysisParams, width=self.ENTRY_BOX_WIDTH, justify=tk.CENTER,
                                                 textvariable=self.model._tkvar_correl_wind_size_y)
        self.entry_correl_wind_size_y.grid(row=2, column=2)

        self.label_correl_grid_size = tk.Label(lfDICAnalysisParams, text="Correlation Grid Size:")
        self.label_correl_grid_size.grid(row=3, column=0)
        self.entry_correl_grid_size_x = tk.Entry(lfDICAnalysisParams, width=self.ENTRY_BOX_WIDTH, justify=tk.CENTER,
                                                 textvariable=self.model._tkvar_correl_grid_size_x)
        self.entry_correl_grid_size_x.grid(row=3, column=1)
        self.entry_correl_grid_size_y = tk.Entry(lfDICAnalysisParams, width=self.ENTRY_BOX_WIDTH, justify=tk.CENTER,
                                                 textvariable=self.model._tkvar_correl_grid_size_y)
        self.entry_correl_grid_size_y.grid(row=3, column=2)

        # Widgets for strain map parameters
        self.checkbutton_remove_rigid_translation = tk.Checkbutton(lfDICAnalysisParams, text="Remove Rigid Translation",
                                            variable=self.model._tkvar_remove_rigid_translation_var)
        self.checkbutton_remove_rigid_translation.grid(row=5, column=0, columnspan=3)

        self.label_interpolation = tk.Label(lfDICAnalysisParams, text="Interpolation:")
        self.label_interpolation.grid(row=6, column=0)
        self.combobox_interpolation = ttk.Combobox(lfDICAnalysisParams,
            values=EnumInterpolation.to_list(),
            state="readonly",
            textvariable=self.model._tkvar_Interpolation)
        self.combobox_interpolation.grid(row=6, column=1, columnspan=2)
        self.combobox_interpolation.set(self.model.interpolation)

        self.label_strain_type = tk.Label(lfDICAnalysisParams, text="Strain Type:")
        self.label_strain_type.grid(row=7, column=0)
        self.combobox_strain_type = ttk.Combobox(lfDICAnalysisParams,
            values=EnumStrainType.to_list(),
            state="readonly", # to behave only as a dropbox list
            textvariable=self.model._tkvar_Strain_type)
        self.combobox_strain_type.grid(row=7, column=1, columnspan=2)
        self.combobox_strain_type.set(self.model.strain_type)

        # Data selection method (using plugins)
        self.label_data_selection = tk.Label(lfDICAnalysisParams, text="Data Selection:")
        self.label_data_selection.grid(row=8, column=0)
        self.combobox_data_selection = ttk.Combobox(lfDICAnalysisParams,
            values=EnumDataSelection.to_list(),
            state="readonly",
            textvariable=self.model._tkvar_DataSelection)
        self.combobox_data_selection.grid(row=8, column=1, columnspan=2)
        self.combobox_data_selection.set(self.model.data_selection)
        # Bind the combobox selection change event
        self.combobox_data_selection.bind("<<ComboboxSelected>>", self.on_data_selection_change)


        # Location of measure combobox
        self.label_location_measure = tk.Label(lfDICAnalysisParams, text="Location Measure:")
        self.label_location_measure.grid(row=9, column=0)
        self.combobox_location_measure = ttk.Combobox(lfDICAnalysisParams,
            values=["mean", "median"],
            state="readonly",
            textvariable=self.model._tkvar_LocationMeasure)
        self.combobox_location_measure.grid(row=9, column=1, columnspan=2)
        self.combobox_location_measure.set(self.model.location_measure)
        self.combobox_location_measure.bind("<<ComboboxSelected>>", self.on_location_measure_change)


        # =================== OUTPUT FILES Labelled frame ===================================
        lfOutPutFiles = tk.LabelFrame(self, text="Output Files")
        lfOutPutFiles.grid(row=2, column=0, padx=5, pady=5)
        # Widgets for output parameters
        self.label_results_directory = tk.Label(lfOutPutFiles, text="Results Directory:")
        self.label_results_directory.grid(row=8, column=0)
        self.entry_results_directory = tk.Entry(lfOutPutFiles,
                state='readonly',
                textvariable=self.model._tkvar_results_directory)
        self.entry_results_directory.grid(row=8, column=1)
        self.button_results_directory = tk.Button(lfOutPutFiles, text="Browse",
                 command=self.model.browse_results_directory)
        self.button_results_directory.grid(row=8, column=2)

        self.label_scale_disp = tk.Label(lfOutPutFiles, text="Scale Disp:")
        self.label_scale_disp.grid(row=9, column=0)
        self.entry_scale_disp = tk.Entry(lfOutPutFiles, justify=tk.CENTER,
                                         textvariable=self.model._tkvar_scale_disp)
        self.entry_scale_disp.grid(row=9, column=1)

        self.label_scale_grid = tk.Label(lfOutPutFiles, text="Scale Grid:")
        self.label_scale_grid.grid(row=10, column=0)
        self.entry_scale_grid = tk.Entry(lfOutPutFiles, justify=tk.CENTER,
                                         textvariable=self.model._tkvar_scale_grid)
        self.entry_scale_grid.grid(row=10, column=1)

        self.checkbutton_save_image = tk.Checkbutton(lfOutPutFiles, text="Save Image", variable=self.model._tkvar_save_images)
        self.checkbutton_save_image.grid(row=11, column=0)

    def on_data_selection_change(self, event):
        #TODO this might no be necessary (nothing is done with plugin)
        selected_value = self.combobox_data_selection.get()
        self.model.data_selection = selected_value
        # plugin = self.model.get_plugin()

    def on_location_measure_change(self, event):
        selected_value = self.combobox_location_measure.get()
        self.model.location_measure = selected_value