import pathlib

import numpy as np
import matplotlib.pyplot as plt
from matplotlib.widgets import Slider

class DIC2DContourInteractivePlot:
    """
    A class for generating and updating interactive 2D contour plots with adjustable color scales.

    This class is intended for internal use within this module only

    Attributes:
        image (np.ndarray): Image on which to overlay the contour plot.
        grid_x (np.ndarray): X grid values.
        grid_y (np.ndarray): Y grid values.
        data (np.ndarray): Z values to contour plot.
        title (str): Plot title.
    """
        
    def __init__(self, image, grid, data:np.ndarray, title:str):
        """
        Constructs all the necessary attributes for the plot object.

        Args:
            image (np.ndarray): Image on which to overlay the contour plot.
            grid (DIC_Grid): DIC_Grid object containing X and Y grid arrays.
            data (np.ndarray): Z values to contour plot.
            title (str): Plot title.
        """
        self.data = np.ma.masked_invalid(data)
        self.data_copy = np.copy(self.data)
        self.grid_x = grid.grid_x
        self.grid_y = grid.grid_y
        self.data = np.ma.array(self.data, mask=self.data == np.nan)
        self.title = title
        self.image = image

        self.fig = plt.figure()
        self.ax = self.fig.add_subplot(111)
        self.fig.subplots_adjust(left=0.25, bottom=0.25)

        self.ax.imshow(image, cmap=plt.cm.binary)
        #ax.contour(grid_x, grid_y, g, 10, linewidths=0.5, colors='k', alpha=0.7)

        
        self.im = self.ax.contourf(grid.grid_x, grid.grid_y, self.data, 10, cmap=plt.cm.rainbow,
                        vmax=self.data.max(), vmin=self.data.min(), alpha=0.7)
        self.contour_axis = plt.gca()

        self.ax.set_title(title)
        self.cb = self.fig.colorbar(self.im)

        axmin = self.fig.add_axes([0.25, 0.1, 0.65, 0.03])
        axmax = self.fig.add_axes([0.25, 0.15, 0.65, 0.03])
        self.smin = Slider(axmin, 'set min value', self.data.min(), self.data.max(), valinit=self.data.min(),valfmt='%1.6f')
        self.smax = Slider(axmax, 'set max value', self.data.min(), self.data.max(), valinit=self.data.max(),valfmt='%1.6f')
        
        self.smax.on_changed(self.update)
        self.smin.on_changed(self.update)
        

    def update(self, val):
        """
        Updates the contour plot based on slider values.

        Args:
            val (float): Value from slider used to adjust the color scale.
        """
        self.contour_axis.clear()
        self.ax.imshow(self.image, cmap=plt.cm.binary)
        self.data = np.copy(self.data_copy)
        self.data = np.ma.masked_where(self.data > self.smax.val, self.data)
        self.data = np.ma.masked_where(self.data < self.smin.val, self.data)
        self.data = np.ma.masked_invalid(self.data)

        self.im = self.contour_axis.contourf(self.grid_x, self.grid_y, self.data, 10, cmap=plt.cm.rainbow, alpha=0.7)

        # self.cb.update_normal(self.im)
        self.cb.update_normal(self.im)
        # self.cb.set_clim(self.smin.val, self.smax.val) # clim does not work
        self.cb.set_ticks(np.linspace(self.smin.val, self.smax.val, num=10))
        plt.pause(0.002)

        # # self.cb = self.figure.colorbar(self.im)
        # self.cb.set_clim(self.smin.val, self.smax.val)
        # self.cb.on_mappable_changed(self.im)
        # self.cb.draw_all() 
        # self.cb.update_normal(self.im)
        # self.cb.update_bruteforce(self.im)
        # plt.colorbar(self.im)
