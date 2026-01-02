#%%
import logging
import pathlib
from tkinter import filedialog, messagebox
from typing import Tuple

import numpy as np
import tkinter as tk
# from PIL import Image, ImageTk

from py3dic.dic import EnumInterpolation, EnumStrainType, LocationMeasuresDict
from py3dic.misc.array_processing_plugins import ArrayProcessingPlugin

from py3dic.misc.array_processing_plugins import EnumDataSelection,PluginFactory

logger = logging.getLogger(__name__)
# Assuming the Camera and ImageCapturingExperiment classes are defined elsewhere

def show_warning_message(message, callback):
    """ This is a generic method that displays a message 
    """
    if messagebox.askokcancel("Warning", message):
        try:
            callback()
        except Exception as e:
            logging.debug(str(e))
    else:
        logging.debug("User aborted. Keeping default option")

#%%


class Model:
    """class to hold the MVC model
    """
    # TODO make this instance attributes
    DEFAULT_METADATA_FNAME = "_meta-data.txt"
    DEFAULT_RESULTS_FOLDER = "results/"
    pp_dic_analysis_result_folder = None

    def __init__(self, starting_dir:pathlib.Path=None):
        self._tkapp_dir = starting_dir

        # self.image_directory = None
        self._tkvar_image_directory = tk.StringVar()
        self._tkvar_image_directory.trace_add('write', lambda var, index, mode:print(f"image directory changed :{self._tkvar_image_directory.get()}"))
        self._tkvar_results_directory = tk.StringVar()
        self._tkvar_results_directory.trace_add('write', callback=self.checks_for_results_dir)
        self._tkvar_num_images = tk.IntVar(value = 0)
        self._tkvar_metadata_file = tk.StringVar()
        
        self._tkvar_correl_grid_size_x = tk.IntVar(value=20)
        self._tkvar_correl_grid_size_y = tk.IntVar(value=20)
        self._tkvar_correl_wind_size_x = tk.IntVar(value=80)
        self._tkvar_correl_wind_size_y = tk.IntVar(value=80)

        # strain map
        self._tkvar_remove_rigid_translation_var = tk.BooleanVar(value=True)
        self._tkvar_Interpolation = tk.StringVar(value=EnumInterpolation.SPLINE.value)
        self._tkvar_Strain_type = tk.StringVar(value=EnumStrainType.GREEN_LAGRANGE.value)
        self._tkvar_DataSelection = tk.StringVar(value=EnumDataSelection.REMOVE_BORDER.value)
        self.plugin_factory = PluginFactory()
        self._tkvar_LocationMeasure = tk.StringVar(value="mean")

        # Presentation parameters for graphs
        self._tkvar_scale_disp = tk.DoubleVar(value=1.0)
        self._tkvar_scale_grid = tk.DoubleVar(value=1.0)
        
        self._tkvar_save_images = tk.BooleanVar(value=True)

        # example  [(307, 114), (596, 189)]
        self.area_of_interest = None
        self.analysis_time_stamp = None

        #TODO Complete Verbosity level and add log window
        self.verbosity_level = 1

    def analysis_time_stamp_str(self, fmt:str= '%Y%m%d-%H%M')->str:
        return self.analysis_time_stamp.strftime(fmt)
    
    @property
    def correl_wind_size(self)->Tuple[int,int]:
        return (self._tkvar_correl_wind_size_x.get(), self._tkvar_correl_wind_size_y.get())
    
    @property
    def correl_grid_size(self)->Tuple[int,int]:
        return (self._tkvar_correl_grid_size_x.get(), self._tkvar_correl_grid_size_y.get())
    
    @property
    def image_directory(self)->str:
        p_directory = pathlib.Path(self._tkvar_image_directory.get())
        assert p_directory.exists(), "directory does not exist"
        return self._tkvar_image_directory.get()
    
    
    @property
    def metadata_file(self)->str:
        return self._tkvar_metadata_file.get()

    @property
    def remove_rigid_translation(self)->bool:
        return self._tkvar_remove_rigid_translation_var.get()

    @property
    def interpolation(self)->str:
        return self._tkvar_Interpolation.get()

    @property
    def strain_type(self)->str:
        return self._tkvar_Strain_type.get()
    
    @property
    def data_selection(self):
        return self._tkvar_DataSelection.get()

    @data_selection.setter
    def data_selection(self, value):
        self._tkvar_DataSelection.set(value)
    
    def get_selection_plugin(self):
        plugin_name = self.data_selection
        return self.plugin_factory.get_plugin(plugin_name)

    @property
    def location_measure(self):
        return self._tkvar_LocationMeasure.get()

    @location_measure.setter
    def location_measure(self, value):
        self._tkvar_LocationMeasure.set(value)

    @property
    def results_directory(self)->str:
        return self._tkvar_results_directory.get()
    
    @property
    def scale_disp(self)->float:
        return self._tkvar_scale_disp.get()
    
    @property
    def scale_grid(self)->float:
        return self._tkvar_scale_grid.get()

    @property
    def save_images(self)->bool:
        return self._tkvar_save_images.get()

    def get_starting_dir(self):
        """returns the starting dir

        Returns:
            _type_: _description_
        """        
        return self._tkapp_dir
    
    def checks_for_results_dir(self, *args):
        """this function performs checks before creating a results dir
        """        
        # check if image directory exists
        if pathlib.Path(self.image_directory).exists():
            logging.info("image directory exists. making sure that results also exists")
            pathlib.Path(self.results_directory).mkdir(parents=True, exist_ok=True)
        else:
            messagebox.showerror('Image directory does not exist. Aborting creation of results')

    def select_first_image_in_dir(self):
        p_directory = pathlib.Path(self.image_directory)
        img_list = list(p_directory.glob('*.jpg')) + list(p_directory.glob('*.png'))
        logging.debug(img_list[0])
        return str(img_list[0])

    def browse_image_directory(self):
        """Function that selects image directory. 

        This function also performs the following actions:
        - selects a metadata file (and updates the model)
        - calculate the number of images in the folder (and updates the model)
        - sets the results direcotry (and updates the model). The result directory is set by default
                <img_dir>/../results
            This assumes that each experiment has a img_folder and also a results folder

        """

        directory = filedialog.askdirectory(
                initialdir=self.image_directory,
                title="Select a directory with images for DIC analysis")
        p_directory = pathlib.Path(directory)
        self._tkvar_image_directory.set(str(p_directory))
        logging.info(f"selected image directory : {str(p_directory)}")
        self._auto_update_based_on_img_dir()

    def _auto_update_based_on_img_dir(self):
        """function that auto updates results directory and metadata based on image directory
        """        
        p_directory = pathlib.Path(self._tkvar_image_directory.get())

        self.num_images = len(list(p_directory.glob('*.jpg')) + list(p_directory.glob('*.png')))

        p_metadata_file =  p_directory/ self.DEFAULT_METADATA_FNAME
        if p_metadata_file.exists():
            logging.info("metadata file exists in image folder. Selecting by default")    
            self._tkvar_metadata_file.set(str(p_metadata_file))
            self._tkvar_results_directory.set(str(p_directory.parent/self.DEFAULT_RESULTS_FOLDER))
        else:
            messagebox.showwarning("MetaData File does not exist", "Please select the metadata file.")

        # logging.critical("Implementation not completed")


    def browse_results_directory(self):
        show_warning_message("What you are about to do is not recommended", 
                             callback=self._change_results_directory)
        logging.info(f"selected results directory : {self._tkvar_results_directory.get()}")


    def _change_results_directory(self):
        res_directory = filedialog.askdirectory(
                initialdir=self.image_directory,
                title="Select a directory where DIC analysis should reside")
        assert pathlib.Path(res_directory).exists(), "Selected result directory does NOT exist"
        self._tkvar_results_directory.set(res_directory)
        
    def browse_metadata_file(self):
        show_warning_message("What you are about to do is not recommended", 
                             callback=self._change_metadata_file)
        logging.info(f" new metadata file: {self._tkvar_metadata_file.get()}")

    def _change_metadata_file(self):
        logging.debug("User about to start selection")
        metadata_file = filedialog.askopenfile(
                initialdir=self.image_directory, 
                filetypes=[("metadata file", "*.txt"),
                           ("default metadata file", self.DEFAULT_METADATA_FNAME)],
                title="Select a metadata")
        logging.debug("User finished selection")
        assert metadata_file, "User Canceled"
        assert pathlib.Path(metadata_file).exists(), "Selected metadata file does NOT exist"

        self._tkvar_metadata_file.set(metadata_file)
