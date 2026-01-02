# grid_interpolator.py
import numpy as np
import scipy.interpolate
import logging
from scipy.interpolate import griddata
from .grid_size import GridSize

class GridInterpolator:
    def __init__(self, grid_x, grid_y):
        self.grid_x = grid_x
        self.grid_y = grid_y
        self.disp_x = np.zeros_like(grid_x)
        self.disp_y = np.zeros_like(grid_y)

    def interpolate_displacement(self, point: np.ndarray, disp: np.ndarray, method='linear'):
        """Interpolate the displacement field.

        It allows to:
        (i) construct the displacement grid and to 
        (ii) smooth the displacement field thanks to the chosen method (raw, linear, spline, etc.)

        Args:
            point (np.ndarray): Original position (rows x 2 columns)
            disp (np.ndarray): New position (rows x 2 columns)
            method (str): Interpolation method
        """
        assert point.shape[1] ==2, "bad shape"
        assert disp.shape[1] ==2, "bad shape"
        x = np.array([p[0] for p in point], dtype=np.float64)
        y = np.array([p[1] for p in point], dtype=np.float64)
        dx = np.array([d[0] for d in disp], dtype=np.float64)
        dy = np.array([d[1] for d in disp], dtype=np.float64)

        logging.info('Interpolate displacement with %s method.', method)
        #TODO enumerate interpolation method
        if method == 'delaunay':
            inter_x = scipy.interpolate.LinearNDInterpolator(point, dx)
            inter_y = scipy.interpolate.LinearNDInterpolator(point, dy)
            self.disp_x = inter_x(self.grid_x, self.grid_y)
            self.disp_y = inter_y(self.grid_x, self.grid_y)
        elif method == 'raw':
            # need debugging
            self.disp_x = self.grid_x.copy()
            self.disp_y = self.grid_y.copy()

            assert self.disp_x.shape[0] == self.disp_y.shape[0], "bad shape"
            assert self.disp_x.shape[1] == self.disp_y.shape[1], "bad shape"
            assert len(dx) == len(dy), "bad shape"
            assert self.disp_x.shape[1] * self.disp_x.shape[0] == len(dx), "bad shape"
            count = 0
            for i in range(self.disp_x.shape[0]):
                for j in range(self.disp_x.shape[1]):
                    self.disp_x[i, j] = dx[count]
                    self.disp_y[i, j] = dy[count]
                    count += 1
        elif method == 'spline':
            # x displacement
            tck_x = scipy.interpolate.bisplrep(self.grid_x, self.grid_y, dx, kx=5, ky=5)
            self.disp_x = scipy.interpolate.bisplev(self.grid_x[:, 0], self.grid_y[0, :], tck_x)
            # y displacement
            tck_y = scipy.interpolate.bisplrep(self.grid_x, self.grid_y, dy, kx=5, ky=5)
            self.disp_y = scipy.interpolate.bisplev(self.grid_x[:, 0], self.grid_y[0, :], tck_y)
        else:
            # unstructured grid
            # ensure grid coordinates are float64
            xi = (self.grid_x.astype(np.float64), self.grid_y.astype(np.float64))
            self.disp_x = griddata((x, y), dx, xi, method=method)
            self.disp_y = griddata((x, y), dy, xi, method=method)
        return self.disp_x, self.disp_y
    
    @classmethod
    def from_grid(cls, grid: GridSize):
        """create a GridInterpolator from a GridSize object

        Args:
            grid (GridSize): _description_

        Returns:
            GridInterpolator: an object that is used to interpolate displacement fields.
        """
        grid.prepare_gridXY() # prepare grid_x and grid_y
        # could add some assertions here to make sure that the grid is valid. 
        return cls(grid.grid_x, grid.grid_y)
    