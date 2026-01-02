#%%
import logging
import pathlib
from tkinter import filedialog, messagebox
import tkinter as tk
import pandas as pd
from py3dic.dic.merge_dic_ut import MergeDICandUTdfs


logger = logging.getLogger(__name__)



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
class Model_DIC_UT_merge:
    """class to hold the MVC model
    """
    # TODO make these isnance variables
    DEFAULT_METADATA_FNAME = "_meta-data.txt"
    DEFAULT_RESULTS_FOLDER = "results/"
    _tkapp_dir:pathlib.Path = None 
    dic_analysis_result_folder = None
    merge_dicut:MergeDICandUTdfs = None
    time_offset = None
    df_ut:pd.DataFrame = None
    df_dic:pd.DataFrame = None
    df_dico:pd.DataFrame = None # original data frame.
    verbosity_level:int = 1

    def __init__(self, starting_dir:pathlib.Path=None):
        """
        Initializes the MVC Model DIC UT object.
        Parameters:
        - starting_dir (pathlib.Path, optional): The starting directory path. Defaults to None.
        
        Attributes:
        - _tkapp_dir (pathlib.Path): The starting directory path.
        - pp_dic_analysis_result_folder (pathlib.Path): The starting directory path.
        - _tkvar_dic_xlsx (tk.StringVar): The tkinter string variable for DIC xlsx filename.
        - _tkvar_metadata_file (tk.StringVar): The tkinter string variable for metadata file.
        - _tkvar_ut_file (tk.StringVar): The tkinter string variable for UT file.
        - _tkvar_num_images (tk.IntVar): The tkinter integer variable for number of images.
        - _tk_auto_select_files (tk.BooleanVar): The tkinter boolean variable for auto selecting files.
        - _tkvar_merged_xlsx (tk.StringVar): The tkinter string variable for merged xlsx filename.
        - _tkvar_time_offset (tk.DoubleVar): The tkinter double variable for time offset.
        - analysis_time_stamp (None): The analysis time stamp (not used).
        - verbosity_level (int): The verbosity level (Higher values for more verbosity).
        Returns:
        - None
        """

        self._tkapp_dir = starting_dir
        self.pp_dic_analysis_result_folder = starting_dir

        #region Variables========================================================
        # self.image_directory = None
        self._tkvar_dic_xlsx = tk.StringVar()
        self._tkvar_dic_xlsx.trace_add('write', lambda var, index, mode:print(f"dic xlsx fname changed :{self._tkvar_dic_xlsx.get()}"))
        
        self._tkvar_metadata_file = tk.StringVar()

        self._tkvar_ut_file = tk.StringVar()
        self._tkvar_ut_file.trace_add('write', callback=self.checks_for_ut_file)

        self._tkvar_num_images = tk.IntVar(value = 0)
        
        self._tk_auto_select_files = tk.BooleanVar(value=True)
        self._tkvar_merged_xlsx = tk.StringVar()

        # Synchronisation parameters
        self._tkvar_time_offset = tk.DoubleVar(value=0.0)
        #endregion

        #TODO this is never used
        self.analysis_time_stamp = None

        #TODO
        self.verbosity_level = 1

    def analysis_time_stamp_str(self, fmt:str= '%Y%m%d-%H%M')->str:
        return self.analysis_time_stamp.strftime(fmt)
    
    #region Properties========================================================
    @property
    def dic_xlsx_fname(self)->str:
        return self._tkvar_dic_xlsx.get()

   
    @property
    def metadata_fname(self)->str:
        return self._tkvar_metadata_file.get()
    
    @property
    def ut_fname(self)->str:
        return self._tkvar_ut_file.get()
    

    @property
    def time_offset(self)->float:
        return self._tkvar_time_offset.get()

    #endregion

    def get_starting_dir(self):
        """returns the starting dir

        Returns:
            _type_: _description_
        """        
        return self._tkapp_dir
    
    def checks_for_ut_file(self, *args):
        """this function performs checks for ut file to verify it is a valid imada file

        TODO this assumes that the file uses a IMADA format. Change this to a more generic format.
        """        
        # check if image directory exists

        pp_ut_fname = pathlib.Path(self._tkvar_ut_file.get())

        if pp_ut_fname.exists():
            logging.info(f"ut file: {str(pp_ut_fname)} exists. ")
        else:
            messagebox.showerror('UT file does not exist. Aborting creation of results')
            raise NotImplemented("This needs to perform checks that the ut file has the right columns")

        valid_ut_File = False

        assert pp_ut_fname.suffix =='.autd'  , f"expected UT file should have a .autd extension. Got {pp_ut_fname.suffix}"

        
        with open(pp_ut_fname, "r") as file:
            # the first line of the autd should contain 'force_N	disp_mm	time_s'
            first_line = file.readline().strip()
            expected_columns = ["force_N", "disp_mm", "time_s"]
            if all(col in first_line for col in expected_columns):
                valid_ut_File = True
            else:
                messagebox.showerror('UT file does not have the expected columns. Aborting creation of results')
                raise NotImplemented("This needs to perform checks that the ut file has the right columns")
        
        # TODO: The check should change and the file that will be loaded should 
        # have the following columns. 
        # as it is currently the file 
        # - force_N	
        # - disp_mm
        # - time_s
        # 
        # Assuming you have a DataFrame named 'df'
        # expected_columns = ["force_N", "disp_mm", "time_s"]

        # assert set(expected_columns).issubset(df.columns), "DataFrame does not have expected columns."
  
        



