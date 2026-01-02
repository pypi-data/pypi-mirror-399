#%%
import tkinter as tk
import matplotlib.pyplot as plt
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class TkMatplotlibPlotFrame(tk.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self._init_tk_components()
    
    def _init_tk_components(self):
        # initialize the figure and axis
        self._fig = plt.figure()
        self._axs = [self._fig.add_subplot(111)]

        # initialize the canvas  to add the plot
        self._canvas = FigureCanvasTkAgg(self._fig, master=self)
        self._canvas.draw()
        # use grid 
        self._canvas.get_tk_widget().grid(row=0, column=0, sticky="nsew")
        
    @property
    def axs(self):
        return self._axs
    
    def plot(self, x, y, ax_idx=0):
        self.axs[ax_idx].plot(x, y, 'o--')
        self.axs[ax_idx].grid()
        self._canvas.draw()
    

if __name__ == "__main__":
    root = tk.Tk()
    frame = TkMatplotlibPlotFrame(root)
    frame.pack(expand=True, fill="both")
    import numpy as np
    x = np.arange(100)
    
    y = np.sin(x/3)
    frame.plot(x, y)
    root.mainloop()
        
    