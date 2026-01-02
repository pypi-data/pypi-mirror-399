import pathlib
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

# from .gui_selectors.time_offset_selector import DICOffsetSelectorClass
from .io_utils import resample_dic_df, resample_ut

import logging

class MergeDICandUTdfs:
    #TODO Tests
    DF_DIC_REQ_COLS: list[str] = ['e_xx', 'e_xx_std', 'e_yy', 'e_yy_std','e_xy', 'e_xy_std', 'time(s)']
    #    'id', 'file', 'force(N)'] This are additional columns but not required
    # Consider filtering when inserting
    #TODO this should be the same as AGNOSTIC_COLNAMES `from py3dic.testing_machine import AGNOSTIC_COLNAMES`
    DF_UT_REQ_COLS: list[str] = ['force_N', 'disp_mm', 'time_s']

    time_offset_s:float=None

    def __init__(self, df_dic_wt:pd.DataFrame, 
                 df_ut_data:pd.DataFrame, 
                 pp_output_dir:pathlib.Path, 
                 offset_value:float = None):
        # copy to avoid unpredictable changes in the original datasets
        self.df_dic_wt = df_dic_wt.copy()
        self.df_ut = df_ut_data.copy()

        self._perform_df_assertions()

        self.pp_analysis_res_dir = pp_output_dir

        # initialisation 
        self.time_offset_s:float = offset_value

    def _perform_df_assertions(self):
        """This is to check that the files have the necessary columns
        """
        #TODO add test
        assert set(self.DF_UT_REQ_COLS).issubset(set(self.df_ut.columns)), f"Missing columns in UT Dataframe: {set(self.DF_UT_REQ_COLS) - set(self.df_ut.columns)}" 
        assert set(self.DF_DIC_REQ_COLS).issubset(set(self.df_dic_wt.columns)), f"Missing columns in DIC Dataframe: {set(self.DF_DIC_REQ_COLS) - set(self.df_dic_wt.columns)}" 
    

    def calculate_offset(self) -> pd.DataFrame:
        self.df_dic_wt.loc[:,"time_synced"] = self.df_dic_wt.loc[:,"time(s)"].copy()-self.time_offset_s
        return self.df_dic_wt


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
            self.calculate_offset()

            ut_df = self.df_ut.copy()
            dic_df = self.df_dic_wt.copy()

            ts_ut = ut_df.time_s
            Fs_ut = ut_df.force_N
            ts_dic = dic_df["time_synced"]
            exx_dic = dic_df.e_xx

            fig, axs = plt.subplots(ncols=1,nrows=2,sharex=True)

            # plot 1
            axs[0].plot(ts_ut, Fs_ut/Fs_ut.max(), '.', label ="Normalised Force")
            axs[0].plot(ts_dic.iloc[:-1], exx_dic.iloc[:-1]/exx_dic.iloc[:-1].max(), '.',label ="Normalised strain ")
            axs[0].set_title(f"Normalised Forces (from Imada) and Strains (from dic)\n Used to determine time offset: {self.time_offset_s} (s)")
            axs[1].set_ylabel("Norm. Force and Strain")
            axs[0].legend()

            # plot 2 with normalised diffs (the  )
            axs[1].plot(ts_ut.iloc[:-1],np.abs(np.diff(Fs_ut))/np.abs(np.diff(Fs_ut)).max(), label ="Norm. force diff")
            axs[1].plot(ts_dic.iloc[:-1], np.abs(np.diff(exx_dic))/np.abs(np.diff(exx_dic)).max(),label ="Norm. strain diff")
            axs[1].set_xlabel("Time (s)")
            axs[1].set_ylabel("Force and strain \n norm. diffs")
            axs[1].legend()
