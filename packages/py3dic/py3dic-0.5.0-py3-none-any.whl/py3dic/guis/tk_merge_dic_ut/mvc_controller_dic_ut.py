#%%
import json

import pandas as pd
import logging
import pathlib
import tkinter as tk
from datetime import datetime
from tkinter import filedialog, messagebox

# from py3dic.testing_machine.imada import read_imada_csv

from py3dic.dic.merge_dic_ut import MergeDICandUTdfs

from ...tktools import show_warning_message

import logging
# Set up logging
logger = logging.getLogger(__name__)
#%%


logger = logging.getLogger(__name__)


from .mvc_model_dic_ut import Model_DIC_UT_merge
from .mvc_view_dic_ut import ViewMergeDicUT

INTERPOLATION_TIME_RESOLUTION_S= 0.1 #TODO PUT THIS IN THE VIEW FOR THE USER TO BE ABLE TO CHANGE



class tkapp_DIC_UT_merge_Controller:
    # TODO make these isnance variables
    experiment_state = False
    IMADA_DECIMATION_DEFAULT = 1 # TODO remove this. Imada Specific
    
    def __init__(self, master, starting_dir):
        self.master = master
        
        self.model = Model_DIC_UT_merge(starting_dir = starting_dir)
        self.view = ViewMergeDicUT(master, model=self.model)

        #region callbacks and event handlers-----------------------
        # self.view.dic_parameters_frame.btn_toggle_roi_window.config(command=self.view.toggle_select_ROI_window)
        self.view.btn_check_analysis_params.config(command=self.check_analysis_parameters)
        self.view.btn_start_analysis.config(command=self.start_merging)

        # browse buttons
        self.view.dic_parameters_frame.dic_entry.set_browse_command(self.browse_dic_xlsx)
        self.view.dic_parameters_frame.metadata_entry.set_browse_command(self.browse_metadata_file)
        self.view.dic_parameters_frame.ut_entry.set_browse_command(self.browse_ut_file)
           
        self.view.sync_plot_frame.set_model_callback( lambda x:self.model._tkvar_time_offset.set(x))
        #endregion

        
    def check_analysis_parameters(self):
        logging.info(f"FILE LOCATIONS")
        logging.info(f"   --> DIC Results        : {self.model.dic_xlsx_fname}")
        # logging.info(f"   --> Number of Images   : {self.model.num_images}")
        logging.info(f"   --> metadata  file     : {self.model.metadata_fname}")
        logging.info(f"   --> tensile datafile   : {self.model.ut_fname}")
        logging.info(f"   --> output directory   : {self.model.pp_dic_analysis_result_folder}")
        logging.info(f"Sync ")
        logging.info(f"   --> time offset [s]    : {self.model.time_offset}"  )
        logging.info(f"   --> time offset [s] (view)   : {self.view.sync_plot_frame.get_offset_value()}"  )

    
    def start_merging(self):
        self.check_analysis_parameters()
        # timestamp_as_str = self.model.analysis_time_stamp_str()
        # dic_analysis_result_folder = pathlib.Path(self.model.results_directory)/ f"res-{timestamp_as_str}" 
        # dic_analysis_result_folder.mkdir(parents=True, exist_ok=True)
        # DIC_ANALYSIS_OUTPUT = dic_analysis_result_folder /f'result.dic'
        # self.model.dic_analysis_result_folder = dic_analysis_result_folder

        df_dic = self.model.df_dic.copy()
        df_ut = self.model.df_ut.copy()

        self.model.merge_dicut = MergeDICandUTdfs(
            df_dic_wt=df_dic,
            df_ut_data=df_ut,
            pp_output_dir=self.model.pp_dic_analysis_result_folder,
            offset_value=self.model.time_offset)
        
        logging.info("asking for user to sync")
          
        def callback(x):
            """callback function to update the time offset in the GUI"""
            logging.debug(f"GUI callback started calling with {x}")
            self.model._tkvar_time_offset.set(x)
            self.view.dic_parameters_frame.txt_Time_offset.delete(0, tk.END)
            self.view.dic_parameters_frame.txt_Time_offset.insert(0, str(x))
            logging.debug(f"GUI callback finished with {x}")


        df_dic= self.model.merge_dicut.calculate_offset()
        
        logging.info(f"Final offset value: {self.model.merge_dicut.time_offset_s}")
        self.model._tkvar_time_offset.set(self.model.merge_dicut.time_offset_s)

        # plot synced graph
        self.model.merge_dicut.plot_synced_normed_graph()

        #TODO add this to the model. It a way of finding the analysis timestamp from the file name. 
        analysis_timestamp = self.model.dic_xlsx_fname.split("_")[-1]
        analysis_timestamp = analysis_timestamp.split(".")[0]
        
        # create final merged and save# # save dic results to file (save the time offset in the filename)
        df_fin = self.model.merge_dicut.resample_data(time_resolution_s=INTERPOLATION_TIME_RESOLUTION_S,
                                                      save_flag=True, 
                                                      fname_prefix=f"dicMerged_{self.model.time_offset}s")
        
        #TODO plot this in a window
        self.view.f_vs_exx_plot_frame.plot(x=df_fin['e_xx'], y=df_fin['force_N'])        
        self.view.f_vs_exx_plot_frame.axs[0].set_title(f"Force vs Strain (DIC)| time offset ={self.model.time_offset}s")
        self.view.f_vs_exx_plot_frame.axs[0].set_xlabel("Strain ($e_{xx}$)")
        self.view.f_vs_exx_plot_frame.axs[0].set_ylabel("Force (N)")
            
        # # df_dic_img_no = self.dic_proc.obtain_strain_curve(func=None)
        # PP_MERGED_FILE = self.model.pp_dic_analysis_result_folder/f"dicMerged.xlsx"
        # df_fin.to_excel(PP_MERGED_FILE)
        # df_fin.to_csv(PP_MERGED_FILE.with_suffix(".csv"))
        # # save metadata file
        # self.save_analysis_metadata()


    def save_analysis_metadata(self):
        #TODO save the offset value
        pass
        # metadata ={
        #     # "material": MATERIAL,
        #     # "orientation": ORIENTATION,
        #     # "specimen_no": SPECIMEN_NO,
        #     "Image Folder": self.model.image_directory,
        #     "ExperimentFolderName" : pathlib.Path(self.model.image_directory).absolute().parents[0].stem,
        #     "Number of Images"   : self.model.num_images,
        #     "metadata  file"     : self.model.metadata_file,
        #     # "Experiment Date": ExperimentDate,
        #     # "Experiment Time": ExperimentTime,
        #     "analysis timestamp":  self.model.analysis_time_stamp_str(),
        #     "ROI Selection"      : self.model.area_of_interest,
        #     "correl_window_size" : self.model.correl_wind_size,
        #     "correl_grid_size"   : self.model.correl_grid_size,
        #     "interpolation"   :  self.model.interpolation,
        #     "strain type"   :  self.model.strain_type,
        #     "remove translation" : self.model.remove_rigid_translation,
        #     "scale_disp"         : self.model.scale_disp,
        #     "scale_grid"         :  self.model.scale_grid,
        #     "Save Image"         : self.model.save_images
        #     # "time_offset": self.time_offset,
        #     # "Strain_Force_file": str(RESULT_XLSX_FNAME),
        # }

        # [print(f"{k} =  {v}") for k,v in metadata.items()]
        # with open(self.model.dic_analysis_result_folder/f'metadata-{self.model.analysis_time_stamp_str()}.json', 'w', encoding='utf-8') as f:
        #     json.dump(metadata, f, ensure_ascii=False, indent=4)

    #region Definition of Callbacks and Event Handlers ==============================
    def browse_dic_xlsx(self):
        """Function that selects the dic analysis.

        if autoselect is pressed the it tries to autoselect the other filenames 

        This function also performs the following actions:
        - selects a metadata file (and updates the model)
        - calculate the number of images in the folder (and updates the model)
        - sets the results direcotry (and updates the model). The result directory is set by default
                <img_dir>/../results
            This assumes that each experiment has a img_folder and also a results folder

        """
        # select results xlsx file
        dic_xslx_fname_str = filedialog.askopenfilename(
                initialdir=self.model.pp_dic_analysis_result_folder,
                title="Select the xlsx file with the DIC analysis",
                filetypes=[("DIC analysis", "*.xlsx")]
                )
        p_dic_fname = pathlib.Path(dic_xslx_fname_str)
        self.model._tkvar_dic_xlsx.set(dic_xslx_fname_str)
        logging.info(f"selected dic xlsx: {str(p_dic_fname)}")

        self.model.pp_dic_analysis_result_folder = p_dic_fname.parent
        # Attempt to find no of images
        # self.num_images = len(list(p_dic_fname.glob('*.jpg')) + list(p_dic_fname.glob('*.png')))

        if self.model._tk_auto_select_files.get():
            # metadata file
            p_experiment_folder = p_dic_fname.parents[2]
            try:
                # select images metadata file
                possible_matches = list(p_experiment_folder.rglob("_meta*.txt"))
                assert len(possible_matches)==1, "Zero or more than one matching names to '_meta*.txt' signature"
                p_metadata_file = possible_matches[0]
                self.model._tkvar_metadata_file.set(str(p_metadata_file))
            except:
                logging.info("could not find metadata_file")
            # automatically select ut_file
            try:
                # ut_possible_matches = list( (p_experiment_folder/"data_tensile/").rglob("*.csv"))
                ut_possible_matches = list( (p_experiment_folder/"data_tensile/").rglob("*.autd"))
                assert len(ut_possible_matches)==1, "Zero or more than one matching names to 'data_tensile/*.csv' ut file signature"
                p_ut_file = ut_possible_matches[0]
                self.model._tkvar_ut_file.set(str(p_ut_file))
            except:
                logging.info("could not find ut_file")

            # set merged file
            self.model._tkvar_merged_xlsx.set(str(self.model.pp_dic_analysis_result_folder/"DIC_merged.xlsx"))
        
        #region load data and update the sync graph -----------------------------------------------------
        # self.model.df_ut = read_imada_csv(fname= self.model.ut_fname, decimation=self.IMADA_DECIMATION_DEFAULT)
        self.model.df_ut = pd.read_csv( self.model.ut_fname, sep="\t",
                                       usecols=["force_N", "disp_mm", "time_s"],
                                       dtype={"force_N": float, "disp_mm": float, "time_s": float})
        
        # DICO_COLUMNS = MergeDICandUT.DF_DIC_REQ_COLS  #TODO One source of truth (consider putting it into core)
        DICO_COLUMNS = ['e_xx', 'e_xx_std', 'e_yy', 'e_yy_std', 'e_xy', 'e_xy_std', 'time(s)', 'id']
        
        # df_dico_file = dic_df_strains_time.loc[:,DICO_COLUMNS].set_index('id')
        logging.info("Reading DIC file: %s ", self.model.dic_xlsx_fname)
        self.model.df_dico = pd.read_excel(self.model.dic_xlsx_fname, index_col=0, usecols="B,D:I,J")        
        #TODO Clarity/efficiency use cols above is cryptic. It would be betterto use the DICO_COLUMNS to select the columns

        # Sometimes the time is too long and you need to remove data
        # Select subset for dic-analysis
        index_start = 0
        index_end = -1
        self.model.df_dic = self.model.df_dico.iloc[index_start:index_end].copy()
        # df_dic.tail()
        logging.info(self.model.df_ut.columns)
        self.view.sync_plot_frame.set_dfs(df_ut=self.model.df_ut, df_dic=self.model.df_dic)
        #endregion

    def browse_metadata_file(self):
        #TODO Complete implementation
        show_warning_message("What you are about to do is not recommended\n (FOR SAFETY IT IS NOT IMPLEMENTED)", 
                             callback=self._change_metadata_file)
        logging.warning(" WARNING: A metadata file was set arbitrarily!")
    
    def _change_metadata_file(self):
        """Changes the metadata File location.

        This is not a function that should be used without caution for the end user (i.e. the user should be warned before using it)
        The reason is that the metadata file should match the experiment. 
        #TODO DOES NOT WORK 
        """
        try:
            str_experiment_folder = str(self.model.pp_dic_analysis_result_folder.parents[1])
        except:
            str_experiment_folder = "" 
        logging.debug("User about to start selection: %s", str_experiment_folder)
        metadata_file = filedialog.askopenfilename(
                initialdir=str_experiment_folder, 
                filetypes=[("metadata file", "*.txt"),
                           ("default metadata file", self.model.DEFAULT_METADATA_FNAME)],
                title="Select the dic metadata file ")
        logging.warning("User finished selection. Metadata file: %s", metadata_file)
        # TODO: proprely handle what happens when a user cancels.
        assert metadata_file, "User Canceled"
        assert pathlib.Path(metadata_file).exists(), "Selected metadata file does NOT exist"

        self.model._tkvar_metadata_file.set(metadata_file)



    def browse_ut_file(self):
        """this is a function that allows the user to select the UT file. However, the recommended procedure is to place the file inside
        the 'data_tensile' folder located in the experiment directory.

        This is the reason this function displays a warning message to the user.

        Normally the user would select a json file from a results folder and the ut file (currently an agnostic file since version 0.5)
         would be selected automatically along with the metadata file for the images (See function browse_dic_xlsx).

        """
        show_warning_message("What you are about to do is not recommended", 
                             callback=self._change_ut_file)
        logging.warning(" WARNING: A Universal Tensile (UT) data file was set arbitrarily!: %s", self.model._tkvar_ut_file.get())
        


    def _change_ut_file(self):
        logging.debug("User about to start selection")
        try:
            str_UT_DATA_FOLDER = str(self.model.pp_dic_analysis_result_folder.parents[1] / "data_tensile")
        except:
            str_UT_DATA_FOLDER = ""
        ut_fname = filedialog.askopenfilename(
                initialdir=str_UT_DATA_FOLDER,
                filetypes=[("tensile data file", "*.csv")],
                title="Select the universal tensile file ")
        logging.debug("User finished selection")
        # TODO: proprely handle what happens when a user cancels.
        assert ut_fname, "User Canceled"
        assert pathlib.Path(ut_fname).exists(), "Selected tensile machine data file does NOT exist"

        self.model._tkvar_ut_file.set(ut_fname)

    #endregion

if __name__ == "__main__":
    script_dir = pathlib.Path(__file__).resolve().parent
    print(script_dir)
    root = tk.Tk()
    app = tkapp_DIC_UT_merge_Controller(root, starting_dir=script_dir)
    root.mainloop()
