import pathlib
import numpy as np
import pandas as pd
from ..gui_selectors.time_offset_selector import DICOffsetSelectorClass
from ..io_utils import resample_dic_df, resample_ut

import logging

class MergeDICandUT_obsolete:
    
    DF_DIC_REQ_COLS: list[str] = ['e_xx', 'e_xx_std', 'e_yy', 'e_yy_std','e_xy', 'e_xy_std', 'time(s)']
    #    'id', 'file', 'force(N)'] This are additional columns but not required
    # Consider filtering when inserting
    DF_UT_REQ_COLS: list[str] = ['force_N', 'disp_mm', 'time_s']

    time_offset_s:float=None

    def __init__(self, df_dic_wt:pd.DataFrame, 
                 df_ut_data:pd.DataFrame, 
                 pp_output_dir:pathlib.Path, 
                 reset_params_flag:bool=False,
                 initial_offset_value:float = None):
        # copy to avoid unpredictable changes in the original datasets
        self.df_dic_wt = df_dic_wt.copy()
        self.df_ut = df_ut_data.copy()

        self._perform_df_assertions()

        self.pp_analysis_res_dir = pp_output_dir

        # initialisation 
        self.reset_params_flag = reset_params_flag
        self.time_offset_s:float = initial_offset_value

        # placeholder for offset selector (Lazy)
        self._offset_selector_plot = None
        

    def _perform_df_assertions(self):
        """This is to check that the files have the necessary columns
        """
        assert set(self.DF_UT_REQ_COLS).issubset(set(self.df_ut.columns)), f"Missing columns in UT Dataframe: {set(self.DF_UT_REQ_COLS) - set(self.df_ut.columns)}" 
        assert set(self.DF_DIC_REQ_COLS).issubset(set(self.df_dic_wt.columns)), f"Missing columns in DIC Dataframe: {set(self.DF_DIC_REQ_COLS) - set(self.df_dic_wt.columns)}" 
    
    def reset_offset(self):
        self.time_offset_s = None

    def calculate_offset(self, reset:bool=False, 
                         time_resolution:float=0.,
                         gui_call_back:callable=None
                         ) -> pd.DataFrame:
        
        def call_back_func(x):
            logging.debug(f"Merge DIC callback called with {x}")
            self.time_offset_s = x
            logging.debug(f"Merge DIC callback finished with {x}")

        if self.time_offset_s is None or self.reset_params_flag or reset:
            self._offset_selector_plot = DICOffsetSelectorClass(df_ut=self.df_ut, 
                        df_dic=self.df_dic_wt, 
                        time_resolution=time_resolution,
                        callback_func=call_back_func)
            
            # FIX:  I think this is what breaks the gui and the callback never returns. 
            self._offset_selector_plot.run()
            
            self.time_offset_s = self._offset_selector_plot.offset_value

        print(f"Final offset value: {self.time_offset_s}")

        if gui_call_back is not None:
            print(f"Calling GUI callback with {self.time_offset_s}")
            # call the gui callback function which updates the GUI
            gui_call_back(self.time_offset_s)
            print(f"GUI callback finished with {self.time_offset_s}")

        if self.time_offset_s is not None:
            # update the df_dic value if there is a valid final_offset_values
            self._update_df_dic()
            return self.df_dic_wt
        else:
            raise ValueError('Could not update the DIC DataFrame, because offset is none')
    
    def _update_df_dic(self):
        """this function updates the final offset value
        """        
        self.df_dic_wt.loc[:,"time_synced"] = self.df_dic_wt.loc[:,"time(s)"].copy()-self.time_offset_s


    def resample_data(self, time_resolution_s:float=0.1,  
                      save_flag:bool=True, fname_prefix:str='total_data'):
        """resamples data at a specified interval and creates the merged df

        Args:
            time_resolution_s (float, optional): resampling interval. Defaults to 0.1.
            save_flag (bool, optional): save the new file to disk. Defaults to True.
            fname_prefix (str, optional): Name of file. Defaults to 'total_data'.

        Returns:
            _type_: _description_
        """        
        
        df_dic:pd.DataFrame = self.df_dic_wt   
        df_ut:pd.DataFrame = self.df_ut
        ts = np.arange(0, df_dic['time_synced'].max(), step=time_resolution_s)
        df_dicrs = resample_dic_df(df_dic=df_dic, ts=ts)   # the DIC resampling
        df_utrs = resample_ut(df_ut=df_ut, ts=ts) # the UT resampling

        df_fin = pd.concat([df_utrs, df_dicrs],axis=1)
        if save_flag:
            if fname_prefix is None:
                fname_prefix = 'total_data'
            df_fin.to_excel(self.pp_analysis_res_dir / f'{fname_prefix }.xlsx')
            df_fin.to_csv(self.pp_analysis_res_dir / f'{fname_prefix }.csv')
        self.df_merged = df_fin
        return self.df_merged
    
    def plot_synced_normed_graph(self):
        if 'time_synced' in self.df_dic_wt.columns:
            self._update_df_dic()
            DICOffsetSelectorClass.plot_synced_norm_graph_with_diff(self.time_offset_s, dic_df=self.df_dic_wt, ut_df=self.df_ut)
