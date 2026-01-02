import copy

import numpy as np
import pandas as pd

from matplotlib import pyplot as plt
# from matplotlib.widgets import Button, RadioButtons, Slider
import matplotlib.tri as tri
from scipy.interpolate import Rbf#, griddata


class GridSize():
    """The GridSize class is used to define the grid size for DIC analysis.
    """
    
    def __init__(self, xmin:int = None
                 ,xmax:int = None
                 ,xnum:int = None 
                 , win_size_x:int= None
                 , ymin:int= None
                , ymax:int= None
                ,ynum:int= None
                ,win_size_y:int= None):
        self.xmin = xmin
        self.xmax = xmax
        self.xnum = xnum
        self.win_size_x = win_size_x

        self.ymin = ymin
        self.ymax = ymax
        self.ynum = ynum
        self.win_size_y = win_size_y

        # calculate the grid size
        # TODO: check if the grid size is integer
        # this is the grid size in pixels
        # TODO check if this is used in the code
        self.x_grid_size = int((self.xmax - self.xmin)/(self.xnum - 1))
        self.y_grid_size = int((self.ymax - self.ymin)/(self.ynum - 1))

    @property
    def shape(self) -> list[int]:
        """Returns the shape of the grid as a tuple (ynum, xnum)."""	
        return [self.ynum, self.xnum]
        
    
    def get_winsize(self) ->tuple[int]:
        """
        Returns the size of the DIC correlation window as a tuple (win_size_x, win_size_y).

        higher number means
         - wider area to check for tracking
         - greater confidence in the tracking
         - slower tracking (more computaional effort)
        """
        return (self.win_size_x, self.win_size_y)

    def prepare_gridXY(self) -> tuple[np.ndarray]:
        """
        Prepare the grid for X and Y coordinates.

        Returns:
            A tuple containing the grid arrays for X and Y coordinates.
        """
        self.grid_x, self.grid_y = np.mgrid[self.xmin:self.xmax:int(self.xnum)*1j, self.ymin:self.ymax:int(self.ynum)*1j]
        return (self.grid_x.copy(), self.grid_y.copy())

    @classmethod
    def from_tuplesXY(cls, xtuple, ytuple):
        """Create a new instance of the class using two tuples for x and y coordinates.

        Args:
            cls: The class itself.
            xtuple: Tuple containing x coordinates.
            ytuple: Tuple containing y coordinates.

        Returns:
            An instance of the class with x and y coordinates initialized from the given tuples.
        """
        return cls(*xtuple, *ytuple)

    @classmethod
    def from_result_dic(cls, fname):
        """Create a GridSize object from a result DIC file.

        This is useful when reading a completed analysis
        
        Parameters:
        - fname (str): The path to the result.dic DIC file.

        Returns:
        - GridSize: The GridSize object created from the result DIC file.
        """
        with open(fname, 'r', encoding='utf-8') as f:
            lines = f.readlines()
            # Parse grid dimensions and window sizes
            (xmin, xmax, xnum, x_window_size) = [int(float(x)) for x in lines[0].split()]
            (ymin, ymax, ynum, y_window_size) = [int(float(x)) for x in lines[1].split()]
        return cls(xmin=xmin, xmax=xmax,
                   xnum=xnum, win_size_x=x_window_size,
                   ymin=ymin, ymax=ymax,
                   ynum=ynum, win_size_y=y_window_size)


    @classmethod
    def from_lines_list(cls, lines: list[str]=None):
        """Create a GridSize object from lines list (list of strings).
        
        Parameters:
        - fname (str): The path to the result.dic DIC file.

        Returns:
        - GridSize: The GridSize object created from the result DIC file.
        """
        # Parse grid dimensions and window sizes
        (xmin, xmax, xnum, x_window_size) = [int(float(x)) for x in lines[0].split()]
        (ymin, ymax, ynum, y_window_size) = [int(float(x)) for x in lines[1].split()]
        return cls(xmin=xmin, xmax=xmax,
                   xnum=xnum, win_size_x=x_window_size,
                   ymin=ymin, ymax=ymax,
                   ynum=ynum, win_size_y=y_window_size)

    @staticmethod
    def grid_to_flat_array(x_grid:np.ndarray, y_grid:np.ndarray):
        """
        Converts from grid (MxN) format to flat array format.

        Parameters:
        disp_x_grid (np.ndarray): 2D array of x displacements (size (MxN) ).
        disp_y_grid (np.ndarray): 2D array of y displacements (size (MxN) ).

        Returns:
        np.ndarray: 2D array of displacements in flat array format. Size ( MxN,2).
        """
        disp_x_flat = x_grid.ravel()
        disp_y_flat = y_grid.ravel()
        return np.column_stack((disp_x_flat, disp_y_flat))

    @staticmethod
    def flat_array_to_grid(flat_array:np.ndarray, grid_shape:list[int]|tuple[int],
                reverse_flag:bool=False) -> tuple[np.ndarray]:
        """
        Converts displacement fields from flat array format to grid format.

        Parameters:
        flat_array (np.ndarray): 2D array of displacements in flat array format.
        grid_shape (tuple): Shape of the grid (ynum, xnum).

        Returns:
        tuple: 2D arrays of x and y displacements in grid format.
        """
        if not isinstance(flat_array, np.ndarray) or flat_array.shape[1] != 2 or flat_array.shape[0] != grid_shape[0]*grid_shape[1]:
            raise ValueError("flat_array must be a numpy array with shape (n, 2), where n = xnum * ynum.")
        
        if reverse_flag:
            grid_shape = grid_shape[::-1]
        _x_grid = np.reshape(flat_array[:, 0], grid_shape)
        _y_grid = np.reshape(flat_array[:, 1], grid_shape)
        return _x_grid, _y_grid