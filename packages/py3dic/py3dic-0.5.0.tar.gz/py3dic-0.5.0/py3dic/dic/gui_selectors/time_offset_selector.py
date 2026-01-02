#%%[markdown]
# # offset_selector.py
#
# This script contains a class for a GUI tool used to visually synchronise data from two different sources:
# a universal tensile machine (UT) and a digital image correlation (DIC) device. This is achieved by applying 
# a time offset to one of the datasets and plotting them together.
#
# ## Classes
#
# - `DICOffsetSelectorClass`: 
# 
# Methods:
#   - `__init__(self, df_ut, df_dic, max_time_diff:float=10)`: The constructor initialises the UT and DIC datasets, creates the tkinter GUI components, and sets up the plot.
#
#   - `plot_synced_graph(self, offset)`:  This method plots the UT and DIC data with the specified offset.
#
#   - `plot_data(self, offset)`: plots the time series data for both the UT and (offset) DIC datasets, 
#
#   - `on_slider_changed(self, val)`: reads the new slider value, converts it to a float, and re-plots the data using the new offset.
#
#   - `on_closing(self)`: This method is called when the GUI window is closed. It retrieves the final offset value from 
#     the slider and destroys the tkinter root window.
#
#   - `run(self)`: This method starts the tkinter main loop, which displays the GUI and begins listening for events.
#
# ## Functions
# ### `plot_synced_graph`
#
# This function creates two plots, intended to visually assess the synchronization between DIC and tensile testing data.
# The plots display the normalized forces and strains, allowing to estimate the time offset.
#
#%%
import tkinter as tk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

MAX_UT_DATAPOINTS = 1000

class DICOffsetSelectorClass:
    """
    This class creates a GUI using tkinter that allows a user to adjust the offset between the time series 
    of a UT dataset and a DIC dataset. This offset can be adjusted with a slider. 

    This is the amount of seconds that the dic data is shifted in order to coincide with the UT Data:

    - Positive values of offset means that the DIC data is delayed, 
    - negative values means that the DIC data is ahead of the UT data

    The class plots the normalized UT force and DIC strain data to aid in the selection of the offset.

    This class is used:
    - main_dic_class scirpt
    - merge_dic_ut gui app

    FIX: The fact that the window is open and closed is probably causing a problem when exiting from the gui app. 
    """
    def __init__(self, df_ut:pd.DataFrame, df_dic:pd.DataFrame,
                 time_resolution:float = 0.1,  
                 max_time_diff:float=10,
                 callback_func:callable = None):
        """constructor function 
        
        Initialises the UT and DIC datasets, creates the tkinter GUI components, and sets up the plot.

        Args:
            df_ut (pd.DataFrame): Universal Tensile machine dataset
            df_dic (pd.DataFrame): DIC dataset
            max_time_diff (float, optional): maximum time difference. Defaults to 10s.
            callback_func ([type], optional): callback function (this is used to update the gui value). Defaults to None.
        """
        self.df_ut = df_ut.copy()
        self._callback_func = callback_func
        self._time_resolution = time_resolution
        self._max_time_diff = max_time_diff
        # Reduce UT data if there are too many points (this is to make more responsive the plot)
        if self.df_ut.shape[0]>MAX_UT_DATAPOINTS :
            DEC_FACTOR = self.df_ut.shape[0]//MAX_UT_DATAPOINTS 
            self.df_ut = self.df_ut.iloc[::DEC_FACTOR,:]

        self.df_dico = df_dic.copy()
        self.offset_value = 0
        self._init_tk_window()

    def _init_tk_window(self):
        max_time_diff = self._max_time_diff
        time_resolution = self._time_resolution
        # tk code. 
        self.root = tk.Tk()
        self.root.title("Data Series Offset")

        # self.fig = Figure(figsize=(5, 4), dpi=100)
        # self.ax = self.fig.add_subplot(111)
        self.fig, self.axs = plt.subplots(ncols=1,nrows=2,sharex=True,figsize=(5, 4), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self.root)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(side=tk.TOP, fill=tk.BOTH, expand=True)

        self.slider = tk.Scale(self.root, from_=-max_time_diff, to=max_time_diff, 
                               resolution=time_resolution, orient=tk.HORIZONTAL,
                               command=self.on_slider_changed)
        self.slider.pack(side=tk.BOTTOM, fill=tk.X)

        # self.plot_data(0)
        self._plot_synced_graph(0)
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)


    def _plot_synced_graph(self, offset):
        """plots the dic and tensile data to visually correlate the data from both datasets.
        
        Two plots are made:
        - one plot with the normalised force and the normalised strain
        - plot:
            - the force diff normalised wrt abs(max(force diff)
            - the strain diff normalised wrt abs(max(strain diff))

        TODO: I could use cross-correlation but this would require similar timestep. 
            
        Args:
            offset (float): Time offset in s (used only for the plot). 
            dic_df (pd.DataFrame): dataframe obtained from dic
            ut_df (pd.DataFrame): dataframe obtained from imada
        """    
        # # this was commented out because the offset occurs outside 
        # dfCopy  = dic_df.copy()
        # dic_df.loc[:,"time_synced"] = dfCopy.loc[:,"time(s)"]-time_offset
        # axs = [axs]
        ts_ut = self.df_ut.time_s.copy()
        Fs_ut = self.df_ut.force_N.copy()
        ts_dic = self.df_dico.loc[:,"time(s)"].copy()-offset
        exx_dic = self.df_dico.e_xx.copy()
        # fig, axs = plt.subplots(ncols=1,nrows=2,sharex=True)
        self.axs[0].clear()
        self.axs[1].clear()
        # plot 1
        self.axs[0].plot(ts_ut, Fs_ut/Fs_ut.max(), '.', label ="Normalised Force")
        self.axs[0].plot(ts_dic.iloc[:-1], exx_dic.iloc[:-1]/exx_dic.iloc[:-1].max(), '.',label ="Normalised strain ")
        self.axs[0].set_title(f"Normalised Forces (from Imada) and Strains (from dic)\n Used to determine time offset: {offset} (s)")
        self.axs[0].set_ylabel("Norm. Force and Strain")
        self.axs[0].legend()

        # plot 2 with normalised diffs 
        self.axs[1].plot(ts_ut.iloc[:-1],np.abs(np.diff(Fs_ut))/np.abs(np.diff(Fs_ut)).max(), label ="force diff")
        self.axs[1].plot(ts_dic.iloc[:-1], np.abs(np.diff(exx_dic))/np.abs(np.diff(exx_dic)).max(),label ="strain diff ")
        self.axs[1].set_xlabel("Time (s)")
        self.axs[1].set_ylabel("Force and Strain diff")
        self.axs[1].legend()
        self.canvas.draw()

    def plot_data(self, offset:float):
        """#     This method plots the time series data for both the UT and DIC datasets, 
            applying the specified offset to the DIC data.

        Args:
            offset (float): time offset in seconds
        """        
        # self.ax.clear()
        # self.ax.scatter(self.df_ut["time_s"], self.df_ut["force_N"], label="df_ut (time_s, force_N)")
        # self.ax.scatter(self.df_dico["time(s)"]+ offset, self.df_dico["e_xx"] , label="df_dico (time(s), e_xx + offset)")
        # self.ax.set_xlabel("Time")
        # self.ax.set_ylabel("Value")
        # self.ax.legend(loc='upper right')
        self.axs[0].clear()
        self.axs[1].clear()
        self.df_dico.loc[:,"time_synced"] = self.df_dico.loc[:,"time(s)"].copy()-offset
        self.axs[0].plot(self.df_ut.time_s,self.df_ut.force_N, '.', label ="Normalised Force")
        self.axs[1].plot(self.df_dico["time_synced"][:-1], self.df_dico.e_xx[:-1], '.',label ="Normalised strain ")
        self.axs[1].set_xlabel("Time (s)")
        self.axs[1].set_ylabel("$e_{xx}$ ()")
        self.axs[0].set_ylabel("Force (N)")
        self.canvas.draw()

    def on_slider_changed(self, val):
        """ Callback method when the slider in the GUI is adjusted. 

        It reads the new slider value, converts it to a float, and re-plots the data using the new offset.

        Args:
            val (float): value from slider.
        """
        offset = float(val)
        # self.plot_data(offset)
        self._plot_synced_graph(offset=offset)

    def on_closing(self):
        """Callback  method when the GUI window is closed. 
        
        It retrieves the final offset value from the slider and destroys the tkinter root window.
        """        
        self.offset_value = self.slider.get()
        if self._callback_func is not None:
            self._callback_func(self.offset_value)
        self.root.destroy()

    def run(self):
        """Method starts the tkinter main loop, which displays the GUI and begins listening for events.
        """        
        self.root.mainloop()

    @staticmethod
    def plot_synced_norm_graph_with_diff(time_offset, dic_df:pd.DataFrame, ut_df:pd.DataFrame):
        """plots the dic and tensile data to see if they correlate well
        
        Two plots are made:
        - one plot with the normalised force and the normalised strain
        - plot:
            - the force diff normalised wrt abs(max(force diff)
            - the strain diff normalised wrt abs(max(strain diff))

        # TODO see if its possible to use to implement _plot_synced_data

        Args:
            time_offset (float): Time offset in s (used only for the plot)
            dic_df (pd.DataFrame): dataframe obtained from dic
            ut_df (pd.DataFrame): dataframe obtained from imada
        """    
        # # this was commented out because the offset occurs outside 
        # dfCopy  = dic_df.copy()
        # dic_df.loc[:,"time_synced"] = dfCopy.loc[:,"time(s)"]-time_offset
        # axs = [axs]
        ts_ut = ut_df.time_s
        Fs_ut = ut_df.force_N
        ts_dic = dic_df["time_synced"]
        exx_dic = dic_df.e_xx
        fig, axs = plt.subplots(ncols=1,nrows=2,sharex=True)

        # plot 1
        axs[0].plot(ts_ut, Fs_ut/Fs_ut.max(), '.', label ="Normalised Force")
        axs[0].plot(ts_dic.iloc[:-1], exx_dic.iloc[:-1]/exx_dic.iloc[:-1].max(), '.',label ="Normalised strain ")
        axs[0].set_title(f"Normalised Forces (from Imada) and Strains (from dic)\n Used to determine time offset: {time_offset} (s)")
        axs[1].set_ylabel("Norm. Force and Strain")
        axs[0].legend()

        # plot 2 with normalised diffs (the  )
        axs[1].plot(ts_ut.iloc[:-1],np.abs(np.diff(Fs_ut))/np.abs(np.diff(Fs_ut)).max(), label ="Norm. force diff")
        axs[1].plot(ts_dic.iloc[:-1], np.abs(np.diff(exx_dic))/np.abs(np.diff(exx_dic)).max(),label ="Norm. strain diff")
        axs[1].set_xlabel("Time (s)")
        axs[1].set_ylabel("Force and strain \n norm. diffs")
        axs[1].legend()

# %%
