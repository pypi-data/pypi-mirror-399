import logging
import pathlib
import tkinter as tk
import tkinter.font as tkfont
from tkinter import filedialog, messagebox, ttk
import numpy as np


import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg


class TLMatplotlibGraph(tk.Toplevel):
    """top level window to display a graph

    can maximize window without border (in windows)

    Args:

    """    
    fullScreen = False

    def __init__(self, parent, 
            figsize:tuple=(8,8), 
            title:str = "Plot Window",
            width:int=800, height:int=800, 
            **kwargs):
        super().__init__(parent)

        self.__kwargs = kwargs
        self._window_title = title
        self._figsize = figsize


        self.protocol('WM_DELETE_WINDOW', self.withdraw)
        # windows only (remove the minimize/maximize button)
        self.attributes('-toolwindow', True)
        self.resizable(1, 1)

        self.title(f'{self._window_title} (F11:maximize, Esc: Emergency Stop)')
        # self.geometry(f'{width}x{height}')
        self.geometry('500x500')

        # layout on the root window
        # self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)
        self.rowconfigure(0, weight=1)
        # self.columnconfigure(2, weight=1)

        self.__create_widgets()

    def __create_widgets(self):
        # create the input frame
        # input_frame = InputFrame(self)
        # input_frame.grid(column=0, row=1)

        # set bindings
        self.bind("<F11>", func=self.toggleFullScreen)
        self.bind("<Alt-Return>", func=self.toggleFullScreen)
        self.bind("<Escape>", func=self.activateEmergencyStop)


        self.fig=plt.figure(figsize=self._figsize)
        self._ax=self.fig.add_axes([0.1,0.1,0.8,0.8],polar=False)
        self.canvas = FigureCanvasTkAgg(self.fig, master=self)
        self.canvas.get_tk_widget().grid(row=0,column=1)
        # self.columnconfigure(index=1, weight=1)
        # self.rowconfigure(index=1, weight=1)
        self.canvas.draw()


    @property
    def ax(self):
        """returns the main plotting axes (default to the first in the subplot grid)

        Returns:
            _type_: _description_
        """        
        return self._ax


    def toggleFullScreen(self, event):
        if self.fullScreen:
            self.deactivateFullscreen()
        else:
            self.activateFullscreen()

    def activateFullscreen(self):
        self.fullScreen = True

        # Store geometry for reset
        self._geometry_old = self.geometry()

        # Hides borders and make truly fullscreen
        self.overrideredirect(True)

        # Maximize window (Windows only). Optionally set screen geometry if you have it
        self.state("zoomed")

        # # code for linux 
        # self.geometry = self.geometry()
        # # Hides borders and make truly fullscreen
        # self.overrideredirect(True)
        # # Maximize window (Windows only). Optionally set screen geometry if you have it
        # if sys.platform.startswith('linux'):
        #     # this should work on linux
        #     self.attributes('-zoomed', True)
        # else:
        #     # this should work on macos and windows
        #     self.state("zoomed")

    def deactivateFullscreen(self):
        self.fullScreen = False
        self.state("normal")
        self.geometry(self._geometry_old)
        self.overrideredirect(False)

        # code for linux compatibility
        # if sys.platform.startswith('linux'):
        #     # this should work on linux
        #     self.root.attributes('-zoomed', False)
        # else:
        #     # this should work on macos and windows
        #     self.root.state("normal")
        
        # self.root.geometry(self.geometry)
        # self.root.overrideredirect(False)

    def activateEmergencyStop(self,event):
        """activates the emergency stop
        """        
        logging.debug('Emergency stop Activated from Image Projection window')
        self.master.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    root.withdraw()
    tlmg = TLMatplotlibGraph(parent=root)
    x = np.linspace(0, np.pi*2 ,100)
    y = np.sin(x)
    tlmg.ax.plot(x,y)
    tlmg.mainloop()
