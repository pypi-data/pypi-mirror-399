#%%

#%%
import logging
import json
import pathlib
import time
import tkinter as tk
from tkinter import filedialog, messagebox
from datetime import datetime
#%%
import cv2
from PIL import Image, ImageTk


# logging.basicConfig(level=logging.DEBUG)
# Assuming the Camera and ImageCapturingExperiment classes are defined elsewhere

from py3dic.dic.batch_image_marker_tracker import BatchImageMarkerTracker
from py3dic.dic.batch_dic_strain_processor import BatchDICStrainProcessor
from py3dic.misc.array_processing_plugins import ArrayProcessingPlugin

from .mvc_model_dic import Model
from .mvc_view_dic import ViewDicAnalysis 


class tkapp_DIC_Controller:
    __DEVELOPMENT_FLAG = False # comment this out for final version
    # __DEVELOPMENT_FLAG flag is a leftover from earlier development. It set the parameters automatically to the GUI for testing purposes
    # TODO remove this flag and the view function that uses it (__init_for_development__)

    # TODO make this isnance variables
    experiment_state = False
    model:Model = None
    def __init__(self, master, starting_dir, full_interface:bool=False):
        self.master = master
        self._full_interace = full_interface
        
        
        self.master.attributes("-topmost", True)

        self.model = Model(starting_dir = starting_dir)

        self.view = ViewDicAnalysis(master, model=self.model, full_interface=full_interface)

        # self.view.dic_parameters_frame.btn_toggle_roi_window.config(command=self.view.toggle_select_ROI_window)
        self.view.btn_check_analysis_params.config(command=self.check_analysis_parameters)
        self.view.btn_start_analysis.config(command=self.start_experiment)

        # remove at 
        try:
            if self.__DEVELOPMENT_FLAG:
                self.master.after(ms=100, func=self.__init_for_development__)
        except:
            pass

    def __init_for_development__(self):
        """ This function is used during developmnet to automatically set the parameters 
        for the gui (to minimize clicks)
        """ 
        try:
            working_dir = pathlib.Path.cwd()
            img_dir = working_dir/"examples/imada_ut/img_png/"
            self.model._tkvar_image_directory.set(img_dir)
            self.model._auto_update_based_on_img_dir()

            logging.debug(f"setting: dir to {img_dir}")
            self.model.area_of_interest = [(307, 114), (596, 189)]
            self.view.tlw_select_ROI.set_image(str(list(img_dir.glob("*.png"))[0]))  # resets params
            self.view.tlw_select_ROI.roi = [(307, 114), (596, 189)]  
            self.view.tlw_select_ROI._update_rectangle()
            logging.debug(f"setting: area of interest  {self.model.area_of_interest}")     
        except Exception as e:
            logging.error(f"Error in __init_for_development__ {e}: the image directory does not exist ")



        
    def check_analysis_parameters(self):
        # 
        self.model.area_of_interest = self.view.tlw_select_ROI.get_roi()
        if self.model.area_of_interest is None:
            messagebox.showinfo("ROI is not selected")
            return 
        self.model.analysis_time_stamp = datetime.now()
        timestamp_as_str = self.model.analysis_time_stamp_str()
        DIC_ANALYSIS_OUTPUT = pathlib.Path(self.model.results_directory)/ f"res-{timestamp_as_str}" /'result.dic'
        # Add timestamp
        logging.info(f"\n\nStarting analysis at {timestamp_as_str}"+ "*"*20)
        logging.info(f"PARAMETERS")
        logging.info(f"Generic parameters ")
        logging.info(f"   --> ROI Selection      : {self.model.area_of_interest}")
        logging.info(f"   --> correl_window_size : {self.model.correl_wind_size}")
        logging.info(f"   --> correl_grid_size   : {self.model.correl_grid_size}")
        logging.info(f"STRAIN Computation parameters ")
        logging.info(f"   |--> remove translation : {self.model.remove_rigid_translation}")
        logging.info(f"   |--> interpolation      : {self.model.interpolation}")
        logging.info(f"   |--> strain type        : {self.model.strain_type}")
        logging.info(f"   |--> selection type     : {self.model.strain_type}")
        logging.info(f"   |--> array selection    : {self.model.data_selection}")
        logging.info(f"   |--> measure location   : {self.model.location_measure}")
        logging.info(f"IMAGE SAVE  parameters ")
        logging.info(f"   |--> scale_disp         : {self.model.scale_disp}")
        logging.info(f"   --> scale_grid         : {self.model.scale_grid}")
        logging.info(f"   --> Save Image         : {self.model.save_images}")
        logging.info(f"FILE LOCATIONS")
        logging.info(f"   --> image directory    : {self.model.image_directory}")
        logging.info(f"   --> Number of Images   : {self.model.num_images}")
        logging.info(f"   --> metadata  file     : {self.model.metadata_file}")
        logging.info(f"   --> output directory   : {self.model.results_directory}")
        logging.info(f"ARGUMENTS ")
        logging.info(f"   --> image pattern      : {self.model.image_directory+'/*.png'}")
        logging.info(f"   --> VERBOSITY_LEVEL    : {self.model.verbosity_level}  -- NOT IMPLEMENTED")

    
    def start_experiment(self):
        # 
        self.check_analysis_parameters()
        timestamp_as_str = self.model.analysis_time_stamp_str()
        pp_dic_analysis_result_folder = pathlib.Path(self.model.results_directory)/ f"res-{timestamp_as_str}" 
        pp_dic_analysis_result_folder.mkdir(parents=True, exist_ok=True)
        DIC_ANALYSIS_OUTPUT = pp_dic_analysis_result_folder /f'result.dic'
        self.model.pp_dic_analysis_result_folder = pp_dic_analysis_result_folder
        
            
        # read image series and write a separated result file 
        self.idp = BatchImageMarkerTracker(
            image_pattern=self.model.image_directory+'/*.png', 
            win_size_px=self.model.correl_wind_size, 
            grid_size_px=self.model.correl_grid_size, 
            area_of_interest = self.model.area_of_interest ,
            result_file=DIC_ANALYSIS_OUTPUT,
            verbosity = self.model.verbosity_level,
            analysis_folder=pp_dic_analysis_result_folder)

        self.idp.compute_and_save_results()

        # loading the analysis result file and analysing

        self.dic_proc= BatchDICStrainProcessor(result_file=DIC_ANALYSIS_OUTPUT, 
                    unit_test_mode=False,
                    interpolation=self.model.interpolation, 
                    strain_type=self.model.strain_type, 
                    save_image=self.model.save_images, 
                    scale_disp=self.model.scale_disp, 
                    scale_grid=self.model.scale_disp, 
                    meta_info_file=self.model.metadata_file, 
                    analysis_folder=pp_dic_analysis_result_folder)

        self.dic_proc.process_data()

        plugin = self.model.plugin_factory.get_plugin(self.model.data_selection)
        assert isinstance(plugin, ArrayProcessingPlugin), "plugin must be an instance of ArrayProcessingPlugin"
        location_measure = self.model.location_measure
        # save dic results to file
        # df_dic_img_no = self.dic_proc.obtain_strain_curve(func=None)
        df_dic_img_no = self.dic_proc.get_df_with_time(plugin=plugin, loc_measure_method=location_measure, save_to_file=False)
        df_dic_img_no.to_excel(pp_dic_analysis_result_folder/f"dic_vs_img_no_{self.model.analysis_time_stamp_str()}.xlsx")
        df_dic_img_no.to_csv(pp_dic_analysis_result_folder/f"dic_vs_img_no_{self.model.analysis_time_stamp_str()}.csv")
        # save metadata file
        self.save_analysis_metadata()
        # set directory to view results
        self.view.tlw_browse_results.set_results_folder( path_to_folder=self.model.pp_dic_analysis_result_folder)

    def save_analysis_metadata(self):

        metadata ={
            # "material": MATERIAL,
            # "orientation": ORIENTATION,
            # "specimen_no": SPECIMEN_NO,
            "Image Folder": self.model.image_directory,
            "ExperimentFolderName" : str(pathlib.Path(self.model.image_directory).absolute()),
            "Number of Images"   : self.model.num_images,
            "metadata  file"     : self.model.metadata_file,
            # "Experiment Date": ExperimentDate,
            # "Experiment Time": ExperimentTime,
            "analysis timestamp":  self.model.analysis_time_stamp_str(),
            "ROI Selection"      : self.model.area_of_interest,
            "correl_window_size" : self.model.correl_wind_size,
            "correl_grid_size"   : self.model.correl_grid_size,
            "remove translation" : self.model.remove_rigid_translation,
            "interpolation"   :  self.model.interpolation,
            "strain type"   :  self.model.strain_type,
            "selection plugin" :self.model.data_selection,
            "location measure": self.model.location_measure,
            "scale_disp"         : self.model.scale_disp,
            "scale_grid"         :  self.model.scale_grid,
            "Save Image"         : self.model.save_images
            # "time_offset": self.time_offset,
            # "Strain_Force_file": str(RESULT_XLSX_FNAME),
        }

        [print(f"{k} =  {v}") for k,v in metadata.items()]
        with open(self.model.pp_dic_analysis_result_folder/f'metadata-{self.model.analysis_time_stamp_str()}.json', 'w', encoding='utf-8') as f:
            json.dump(metadata, f, ensure_ascii=False, indent=4)

if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).resolve().parent
    print(script_dir)
    root = tk.Tk()
    app = tkapp_DIC_Controller(root, starting_dir=script_dir)
    root.mainloop()
