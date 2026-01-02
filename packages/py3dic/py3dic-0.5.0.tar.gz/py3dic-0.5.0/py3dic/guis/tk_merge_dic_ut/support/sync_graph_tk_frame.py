import tkinter as tk
from tkinter import ttk
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

# from .dual_slider_widget import DualSlider 

MAX_UT_DATAPOINTS = 1000

def plot_synced_norm_graph_with_diff(time_offset, dic_df:pd.DataFrame, ut_df:pd.DataFrame, axs:list[plt.axis]=None):
    """Plots the DIC and tensile data to see if they correlate well.

    Args:
        time_offset (float): The time offset between the two datasets
        dic_df (pd.DataFrame): DIC dataset  
        ut_df (pd.DataFrame): Universal Tensile machine dataset
        axs (list[plt.axis], optional): List of matplotlib axis. Defaults to None

    Returns:
        list[plt.axis]: List of matplotlib axis

    TODO this function and the TkFrSyncGraph._plot_synced_graph function are similar. Reduce repetition.
    """
    ts_ut = ut_df.time_s
    Fs_ut = ut_df.force_N
    ts_dic = dic_df["time_synced"]
    exx_dic = dic_df.e_xx
    if axs is None:
        fig, axs = plt.subplots(ncols=1, nrows=2, sharex=True)

    axs[0].plot(ts_ut, Fs_ut / Fs_ut.max(), '.', label="Normalised Force")
    axs[0].plot(ts_dic.iloc[:-1], exx_dic.iloc[:-1] / exx_dic.iloc[:-1].max(), '.', label="Normalised strain")
    axs[0].set_title(f"Normalised Forces (from Imada) and Strains (from dic)\n Used to determine time offset: {time_offset} (s)")
    axs[1].set_ylabel("Norm. Force and Strain")
    axs[0].legend()

    axs[1].plot(ts_ut.iloc[:-1], np.abs(np.diff(Fs_ut)) / np.abs(np.diff(Fs_ut)).max(), label="Norm. force diff")
    axs[1].plot(ts_dic.iloc[:-1], np.abs(np.diff(exx_dic)) / np.abs(np.diff(exx_dic)).max(), label="Norm. strain diff")
    axs[1].set_xlabel("Time (s)")
    axs[1].set_ylabel("Force and strain \n norm. diffs")
    axs[1].legend()
    return axs

class TkFrSyncGraph(tk.Frame):
    _callback_func: callable = None
    _time_resolution: float = 0.1
    _max_time_diff: float = 10
    offset_value = 0

    def __init__(self, parent
                 ,*args, **kwargs):
        """Constructor function

        Initializes the UT and DIC datasets, creates the tkinter GUI components, and sets up the plot.

        Args:
            parent (tk.Widget): The parent widget or window
            df_ut (pd.DataFrame): Universal Tensile machine dataset
            df_dic (pd.DataFrame): DIC dataset
            max_time_diff (float, optional): maximum time difference. Defaults to 10s.
            callback_func ([type], optional): callback function (this is used to update the GUI value). Defaults to None.
        """
        super().__init__(parent, *args, **kwargs)

        # Initialize the Tkinter components
        self._init_tk_components()
        # self._plot_synced_graph(0)

    def _init_tk_components(self):
        max_time_diff = self._max_time_diff
        time_resolution = self._time_resolution
        
        self.fig, self.axs = plt.subplots(ncols=1, nrows=2, sharex=True, figsize=(5, 4), dpi=100)

        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.draw()
        self.canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")

        self.slider = tk.Scale(self, from_=-max_time_diff, to=max_time_diff, 
                               resolution=time_resolution, orient=tk.HORIZONTAL,
                               command=self.on_slider_changed)
        self.slider.grid(row=1, column=0, sticky="ew")
        
        # dual slider for setting the limits 
        # self.dslider_time_limits = DualSlider(self, title="Time Limits (not implemented)", min_value=-max_time_diff, max_value=max_time_diff, start_value=-max_time_diff, stop_value=max_time_diff)
        # self.dslider_time_limits.grid(row=2, column=0, sticky="ew", padx=20)
        

    def _plot_synced_graph(self, offset):
        """Plots the DIC and tensile data to visually correlate the data from both datasets."""
        ts_ut = self.df_ut.time_s.copy()
        Fs_ut = self.df_ut.force_N.copy()
        
        Fs_ut_max = np.abs(Fs_ut).max()# This was added for compression tests
        # TODO: add a switch to inverse the force values if needed (ie. compression or tension). 
        # Currently it is done based on the median value of the force see below
        if Fs_ut.median() < 0:
            Fs_ut = -Fs_ut
            logging.warning("Force values are negative. Inverting the force values to increase offset selection.")

        ts_dic = self.df_dic.loc[:, "time(s)"].copy() - offset
        exx_dic = self.df_dic.e_xx.copy()

        # Ensure the time series are aligned
        self.axs[0].clear()
        self.axs[1].clear()

        self.axs[0].plot(ts_ut, Fs_ut / Fs_ut_max, '.', label="Normalized Force")
        self.axs[0].plot(ts_dic.iloc[:-1], exx_dic.iloc[:-1] / exx_dic.iloc[:-1].max(), '.', label="Normalized strain")
        self.axs[0].set_title(f"Normalized Forces (from Imada) and Strains (from dic)\n Used to determine time offset: {offset} (s)")
        self.axs[0].set_ylabel("Norm. Force and Strain")
        self.axs[0].legend()

        self.axs[1].plot(ts_ut.iloc[:-1], np.abs(np.diff(Fs_ut)) / np.abs(np.diff(Fs_ut)).max(), label="force diff")
        self.axs[1].plot(ts_dic.iloc[:-1], np.abs(np.diff(exx_dic)) / np.abs(np.diff(exx_dic)).max(), label="strain diff")
        self.axs[1].set_xlabel("Time (s)")
        self.axs[1].set_ylabel("Force and Strain diff")
        self.axs[1].legend()

        self.canvas.draw()

    def on_slider_changed(self, val):
        """Callback method when the slider in the GUI is adjusted."""
        offset = float(val)
        self._plot_synced_graph(offset=offset)
        self._model_callback(offset)

    def get_offset_value(self):
        """Returns the current offset value."""
        return self.slider.get()
    
    def set_callback_func(self, callback_func: callable):
        """Sets the callback function for the GUI component."""
        self._callback_func = callback_func
    
    def set_model_callback(self, callback_func: callable):
        """Sets the callback function for the model component."""
        self._model_callback = callback_func

    def set_dfs(self, df_ut: pd.DataFrame, df_dic: pd.DataFrame):
        """Sets the UT and DIC datasets."""
        self.df_ut = df_ut.copy()
        self.df_dic = df_dic.copy()

        # Reduce UT data if there are too many points (this is to make the plot more responsive)
        if self.df_ut.shape[0] > MAX_UT_DATAPOINTS:
            DEC_FACTOR = self.df_ut.shape[0] // MAX_UT_DATAPOINTS
            self.df_ut = self.df_ut.iloc[::DEC_FACTOR, :]

        self._plot_synced_graph(0)


    def _set_one_subplot(self):
        """Set the figure to use one subplot.

        This functions currently is not used but it can be used to change between one or two subplots
        
        """
        self.fig.clear()
        self.axs = [self.fig.add_subplot(111)]
        self.canvas.draw()

    def _set_two_subplots(self):
        """Set the figure to use two subplots.
        
        This functions currently is not used but it can be used to change between one or two subplots
        """
        self.fig.clear()
        self.axs = self.fig.subplots(ncols=1, nrows=2, sharex=True)
        self.canvas.draw()


# Usage example
if __name__ == "__main__":
    root = tk.Tk()
    root.title("DIC Offset Selector")

    # Example data
    df_ut = pd.DataFrame({
        'time_s': np.linspace(0, 100, 500),
        'force_N': np.random.random(500)
    })
    df_dic = pd.DataFrame({
        'time(s)': np.linspace(0, 100, 500),
        'e_xx': np.random.random(500)
    })

    def callback(offset):
        print(f"Offset selected: {offset}")

    frame = TkFrSyncGraph(root)
    frame.pack(fill=tk.BOTH, expand=True)
    frame.set_dfs(df_ut, df_dic)
    frame.set_callback_func(callback)

    root.mainloop()