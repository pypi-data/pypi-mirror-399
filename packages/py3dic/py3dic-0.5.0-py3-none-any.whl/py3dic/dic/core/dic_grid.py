import pathlib
import copy

import numpy as np
import pandas as pd

from scipy.interpolate import Rbf, griddata

import logging

# from matplotlib.widgets import Button, RadioButtons, Slider

from .core_calcs import compute_disp_and_remove_rigid_transform, compute_displacement

# from .._obsolete.draw_opencv_v2 import draw_opencv_v2 #TODO the  import `draw_opencv_v2` should be removed
# from ..plotting.dic2d_contour_plot import DIC2DContourInteractivePlot
from .grid_size import GridSize

from ...misc.array_processing_plugins import ArrayProcessingPlugin, DefaultBorderRemovalPlugin
from .calc_grid_interpolator import GridInterpolator
from .calc_strain_calculator import StrainCalculator

class DICGrid:
    """The DIC_Grid class is the main class of pydic. This class embed a lot of usefull
    method to treat and post-treat results

    #TODO make the attribute names a bit more clear and consistent (i.e reference_image, image are filenames)
    #TODO clarify the type of each attribute (e.g. avoid str|pathlib.Path)
    """
    
    def __init__(self, grid_x:np.ndarray, grid_y:np.ndarray,
                size_x:int, size_y:int):
        """Construct a new DIC_Grid object with 

        Args:
            grid_x (np.ndarray): x coordinate (grid_x) for each marker
            grid_y (np.ndarray): y coordinate (grid_y) for each marker
            size_x (int): number of point along x (size_x)
            size_y (int): number of point along y (size_y)
        """
        # self._grid_x = grid_x
        # self._grid_y = grid_y
        # self._size_x = size_x
        # self._size_y = size_y
        xmin = np.min(grid_x)
        xmax = np.max(grid_x)
        ymin = np.min(grid_y)
        ymax = np.max(grid_y)
        self.grid_size = GridSize(xmin = xmin, xmax = xmax, 
                                  ymin = ymin, ymax = ymax, 
                                  xnum = size_x, ynum = size_y)
        self.grid_size.prepare_gridXY()

        # initilize instance attributes
        self.grid_interpolator: GridInterpolator = None
        self.reference_image:str = None  # filename of the reference image
        self.image:str|pathlib.Path = None # filename of the current image
        self.reference_point:np.ndarray = None # array (shape: n x 2) with xy coordinates for each point in the reference image
        self.correlated_point:np.ndarray = None # array (shape: n x 2) with xy coordinates for each point in the final image
        self.disp:np.ndarray = None # array (shape: n x 2) with the displacement for each point (with or without rigid body transform)
        self.meta_info:dict = None # dictionary with meta information


        self.disp_x =  self.grid_x.copy().fill(0.)
        self.disp_y =  self.grid_y.copy().fill(0.)
        self.strain_xx:np.ndarray = None
        self.strain_yy:np.ndarray = None
        self.strain_xy:np.ndarray = None

    #region **Properties**
    # the following properties are to ease the introductino of GridSize
    @property
    def grid_x(self)-> np.array:
        """property that returns a rectangular grid with x coordinates

        Returns:
            np.array: _description_
        """
        # return self._grid_x
        return self.grid_size.grid_x

    @property
    def grid_y(self)-> np.array:
        """ position that returns a rectangular grid with y coordinates
        returns the grid_y attribute of the GridSize object
        """
        # return self._grid_y
        return self.grid_size.grid_y

    @property
    def size_x(self) ->int:
        """property that returns the number of points in x direction

        Returns:
            int: number of points in x direction
        """
        return self.grid_size.xnum

    @property
    def size_y(self)->int:
        """property that returns the number of points in y direction	
        """
        return self.grid_size.ynum
    #endregion

    def add_meta_info(self, meta_info):
        """Save the related meta info into the current DIC_Grid object"""
        self.meta_info = meta_info

    def is_valid_number(self, i:int, j:int):
        """check if grid_x, grid_y, disp_x, and disp_y at i,j are nan

        Args:
            i (int): index in x direction
            j (int): index in y direction

        Returns:
            _type_: _description_
        """
        return  (not np.isnan(self.grid_x[i,j]) and
            not np.isnan(self.grid_y[i,j]) and
            not np.isnan(self.disp_x[i,j]) and
            not np.isnan(self.disp_y[i,j]))

    def prepare_saved_file(self, prefix, extension, analysis_folder=None):
        """prepares the filename in the form:

        <analysis_folder or image_folder>/pydic/<prefix>/<image_name>_<prefix>.<extension>

        Args:
            prefix (str): folder that the file will be saved in the pydic folder structure
            extension (str): File extension
            analysis_folder (str): the main folder where the image will be saved

        Returns:
            str: the prepared file path
        """
        if analysis_folder:
            folder = pathlib.Path(analysis_folder)
            if not folder.is_dir():
                raise ValueError(f"{analysis_folder} is not a valid directory.")
            folder = folder / prefix
        else:
            folder = pathlib.Path(self.image).parent / 'pydic' / prefix

        folder.mkdir(parents=True, exist_ok=True)
        base = pathlib.Path(self.image).stem
        name = folder / f"{base}_{prefix}.{extension}"
        print("saving", name, "file...")
        return str(name)

    def write_result(self,analysis_folder=None):
        """write a raw csv result file. 

        Indeed, you can use your favorite tool to post-treat this file
        """
        name = self.prepare_saved_file('result', 'csv',analysis_folder=analysis_folder)
        with open(name, 'w', encoding='utf-8') as f:
            f.write("index" + ',' + "index_x" + ',' + "index_y" + ',' +
                    "pos_x"     + ',' + "pos_y"     + ',' +
                    "disp_x"    + ',' + "disp_y"    + ',' + 
                    "strain_xx" + ',' + "strain_yy" + ',' + "strain_xy" + '\n')
            index = 0
            for i in range(self.size_x):
                for j in range(self.size_y):
                    f.write(str(index)   + ',' +
                        str(i)                   + ',' + str(j)                   + ',' +
                        str(self.grid_x[i,j])    + ',' + str(self.grid_y[i,j])    + ',' +
                        str(self.disp_x[i,j])    + ',' + str(self.disp_y[i,j])    + ',' +
                        str(self.strain_xx[i,j]) + ',' + str(self.strain_yy[i,j]) + ',' +
                        str(self.strain_xy[i,j]) + '\n')
                    index = index + 1
            f.close()


    def obtain_strains(self, 
                       plugin: ArrayProcessingPlugin=None, 
                       loc_measure_method:str='mean')->dict:
        """this is a function that calculates the strains xx, yy, xy  on this grid. 

        Returns:
            dict: dataframe that for this grid contains 
                    (e_xx, e_xx_std, e_yy, e_yy_std, e_xy, e_xy_std) 
        """

        if plugin is None:
            plugin = DefaultBorderRemovalPlugin()
        assert isinstance(plugin, ArrayProcessingPlugin), "plugin must be an instance of ArrayProcessingPlugin"

        portion_xx = plugin.process(self.strain_xx) 
        portion_yy = plugin.process(self.strain_yy)
        portion_xy = plugin.process(self.strain_xy)
        loc_measure_method = loc_measure_method.lower()
        logging.info("loc_measure_method: %s", loc_measure_method)
        if loc_measure_method == 'mean':
            exx_loc = portion_xx.mean()
            eyy_loc = portion_yy.mean()
            exy_loc = portion_xy.mean()
        elif loc_measure_method == 'median':
            exx_loc = np.median(portion_xx)
            eyy_loc = np.median(portion_yy)
            exy_loc = np.median(portion_xy)
        else:
            raise ValueError("loc_measure_method must be 'mean' or 'median'")
        adic = {"e_xx":exx_loc, "e_xx_std": portion_xx.std(),
                "e_yy":eyy_loc, "e_yy_std": portion_yy.std(),
                "e_xy":exy_loc, "e_xy_std": portion_xy.std()}
        #
        return adic     


    def process_grid_data(self, 
                reference_image:pathlib.Path|str, 
                image:pathlib.Path|str, 
                reference_points, 
                current_points, 
                interpolation_method, 
                strain_type, 
                remove_rigid_transform=False):
        """Process grid data by computing displacement, interpolating, and computing strain.

        Actions:
        - removes rigid body transform if specified
        - computes displacement and strain field
        - interpolates displacement field according to the specified method
        - computes strain field according to the specified strain type

        Args:
            reference_image (str): filename of the reference image
            image (str): filename of the current image
            reference_points (np.ndarray): reference coordinates for each marker
            current_points (np.ndarray): current coordinates for each marker 
                                    (reference_points + displacement)
            interpolation_method (str): method used for interpolating displacement
            strain_type (str): type of strain to compute ('green_lagrange', 'cauchy-eng', '2nd_order', or 'log')
            remove_rigid_transform (bool): whether to remove rigid body transform or not
        """
        logging.info(f"compute displacement and strain field of %s...", image )
        
        # Add raw data 
        self.reference_image = reference_image
        self.image:pathlib.Path = image # TODO sort out image type annotation. 
        self.reference_point = reference_points
        self.correlated_point = current_points

        # Compute displacement
        if remove_rigid_transform:
            logging.info("remove rigid body transform")
            self.disp = compute_disp_and_remove_rigid_transform(current_points, reference_points)
        else:
            logging.info("do not remove rigid body transform")
            self.disp = compute_displacement(current_points, reference_points)
        # interpolate displacement
        self.grid_interpolator = GridInterpolator(grid_x=self.grid_x, grid_y=self.grid_y)
        self.disp_x, self.disp_y = self.grid_interpolator.interpolate_displacement(
                    point=reference_points,
                    disp=self.disp,
                    method=interpolation_method)
        # Compute strain field
        sc = StrainCalculator(grid_x=self.grid_x, grid_y=self.grid_y)
        sc.compute_strain( disp_x=self.disp_x, disp_y=self.disp_y, method= strain_type)
        self.strain_xx = sc.strain_xx
        self.strain_yy = sc.strain_yy
        self.strain_xy = sc.strain_xy
        #
        return self.disp  # Optionally return disp if needed
    
    @classmethod
    def from_grid_size(cls, grid_size:GridSize):
        """Create a StrainCalculator object from a GridSize object"""

        return cls(grid_x=grid_size.grid_x, grid_y=grid_size.grid_y, size_x=grid_size.xnum, size_y=grid_size.ynum)
    
    @classmethod
    def from_gridsize(cls, grid_size_instance:GridSize):
        """This is a class method that creates a new instance of DIC_Grid from a GridSize instance.

        Args:
            grid_size_instance (GridSize): a GridSize 

        Returns:
            DIC_Grid: object
        """
        grid_size_instance.prepare_gridXY()
        new_grid = cls(
            grid_x=grid_size_instance.grid_x, grid_y=grid_size_instance.grid_y,
            size_x=int(grid_size_instance.xnum), size_y=int(grid_size_instance.ynum))
        # Is this (copy.deepcopy) really necessary
        return copy.deepcopy(new_grid)