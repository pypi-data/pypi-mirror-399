# ============================= IMPORTANT =============================
# this file is frozen because the old_pydic verison depends on it. 
# Eventully this will be removed. 
# 
# The reason this is here is to keep the old_pydic working, and provide the same results. 
#=========================================================
import math
import pathlib
import copy

import cv2
import numpy as np
import pandas as pd

import scipy.interpolate
import logging

from matplotlib import pyplot as plt
import matplotlib.tri as tri
from scipy.interpolate import Rbf, griddata
from ..core.core_calcs import compute_disp_and_remove_rigid_transform, compute_displacement

from ..plotting.dic2d_contour_plot import DIC2DContourInteractivePlot
from ..core.grid_size import GridSize
# the  import `draw_opencv_v2` should be removed
from .draw_opencv_v2 import draw_opencv_v2
from ...misc.array_processing_plugins import ArrayProcessingPlugin, DefaultBorderRemovalPlugin

class OLD_grid:
    """The DIC_Grid class is the main class of pydic. This class embed a lot of usefull
    method to treat and post-treat results
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
        self._grid_x = grid_x
        self._grid_y = grid_y
        self._size_x = size_x
        self._size_y = size_y
        self.disp_x =  self.grid_x.copy().fill(0.)
        self.disp_y =  self.grid_y.copy().fill(0.)
        self.strain_xx = None
        self.strain_yy = None
        self.strain_xy = None

    # >>>>>>>>>>>>> Properties
    # the following properties are to ease the introductino of GridSize
    @property
    def grid_x(self):
        return self._grid_x
    
    @property
    def grid_y(self):
        return self._grid_y
    
    @property
    def size_x(self):
        return self._size_x
    
    @property
    def size_y(self):
        return self._size_y
    #>>>>>>>>>>>>> End Properties

    def add_raw_data(self,
            winsize:tuple,
            reference_image:str,
            image:str,
            reference_point:np.ndarray,
            correlated_point:np.ndarray,
            disp:list[tuple]):
        """Save raw data to the current object. 
        
        These raw data are used as initial data 
        for digital image correlation

        Args:
            winsize (tuple): the size in pixel of the correlation windows
            reference_image (str): filename of the reference image
            image (str): filename of the current image
            reference_point (np.ndarray[(size_x*size_y),2]): Reference coordinates for each marker 
            correlated_point (np.ndarray[(size_x*size_y),2]): Current coordinate for each marker
            disp (list of tuples): List of tuples with dispacement for each marker (first column, then second column ....)
        """
        self.winsize = winsize
        self.reference_image = reference_image
        self.image:pathlib.Path = image 
        self.reference_point = reference_point
        self.correlated_point = correlated_point
        self.disp = disp

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
        return  (not math.isnan(self.grid_x[i,j]) and
            not math.isnan(self.grid_y[i,j]) and
            not math.isnan(self.disp_x[i,j]) and
            not math.isnan(self.disp_y[i,j]))

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
            # if analyis folder is None create the a pydic folder in the image folder
            folder = pathlib.Path(self.image).parent / 'pydic' / prefix

        folder.mkdir(parents=True, exist_ok=True)
        base = pathlib.Path(self.image).stem
        name = folder / f"{base}_{prefix}.{extension}"
        print("saving", name, "file...")
        return str(name)

    def draw_marker_img(self,analysis_folder=None):
        """Draw marker image"""
        name = self.prepare_saved_file(prefix ='marker',
            extension='png', analysis_folder=analysis_folder)
        draw_opencv_v2(self.image, point=self.correlated_point,
                l_color=(0,0,255), p_color=(255,255,0),
                filename=name, text=name)

    def draw_disp_img(self, scale,analysis_folder=None):
        """Draw displacement image. 
        A scale value can be passed to amplify the displacement field
        """
        name = self.prepare_saved_file('disp', 'png',analysis_folder=analysis_folder)
        draw_opencv_v2(self.reference_image,
                    point=self.reference_point,
                    pointf=self.correlated_point,
                    l_color=(0,0,255), p_color=(255,255,0),
                    scale=scale,
                    filename=name, text=name)

    def draw_disp_hsv_img(self,analysis_folder=None, *args, **kwargs):
        """Draw displacement image in a hsv view."""
        name = self.prepare_saved_file('disp_hsv', 'png',analysis_folder=analysis_folder)
        img = self.reference_image
        if isinstance(img, str):
            img = cv2.imread(img, 0)

        disp = self.correlated_point - self.reference_point
        fx, fy = disp[:,0], disp[:,1]
        v_all = np.sqrt(fx*fx + fy*fy)
        v_max = np.mean(v_all) + 2.*np.std(v_all)

        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

        if v_max != 0.:
            for i, val in enumerate(self.reference_point):
                disp = self.correlated_point[i] - val
                ang = np.arctan2(disp[1], disp[0]) + np.pi
                v = np.sqrt(disp[0]**2 + disp[1]**2)
                pt_x = int(val[0])
                pt_y = int(val[1])

                hsv[pt_y,pt_x, 0] = int(ang*(180/np.pi/2))
                hsv[pt_y,pt_x, 1] = 255 if int((v/v_max)*255.) > 255 else int((v/v_max)*255.)
                hsv[pt_y,pt_x, 2] = 255 if int((v/v_max)*255.) > 255 else int((v/v_max)*255.)

        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        bgr = cv2.putText(bgr, name, (50,50), cv2.FONT_HERSHEY_SIMPLEX, 1,(255,255,255),4)

        if 'save_img' in kwargs:
            cv2.imwrite(name, bgr)
        if 'show_img' in kwargs:
            cv2.namedWindow('image', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('image', bgr.shape[1], bgr.shape[0])
            cv2.imshow('image', bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()


    def draw_grid_img(self, scale, analysis_folder=None):
        """Draw grid image. 
        
        A scale value can be passed to amplify the displacement field
        """
        name = self.prepare_saved_file('grid', 'png', analysis_folder=analysis_folder)
        draw_opencv_v2(self.reference_image,
                    grid = self,
                    scale=scale, gr_color=(255,255,250),
                    filename=name, text=name)

    def plot_field(self, field, title):
        """Plot the chosen field such as strain_xx, disp_xx, etc. 
        in a matplotlib interactive map
        """
        image_ref = cv2.imread(self.image, 0)
        DIC2DContourInteractivePlot(image_ref, self, field, title)

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

    def interpolate_displacement(self, point:np.ndarray, disp:np.ndarray,
        # *args,
        **kwargs):
        """Interpolate the displacement field.
        
        It allows to:
        (i) construct the displacement grid and to 
        (ii) smooth the displacement field thanks to the chosen method (raw, linear, spline,etc.)

        Args:
            point (np.ndarray): Original position (rows x 2 columns)
            disp (np.ndarray): New position (rows x 2 columns)
            method(str): Interpolation method
        """
        x = np.array([p[0] for p in point])
        y = np.array([p[1] for p in point])
        dx = np.array([d[0] for d in disp])
        dy = np.array([d[1] for d in disp])
        method = kwargs.get('method','linear')

        logging.info('interpolate displacement with %s method.', method )
        
        if method=='delaunay':
            inter_x = scipy.interpolate.LinearNDInterpolator(point, dx)
            inter_y = scipy.interpolate.LinearNDInterpolator(point, dy)
            self.disp_x = inter_x(self.grid_x, self.grid_y)
            self.disp_y = inter_y(self.grid_x, self.grid_y)

        elif method=='raw':
            # need debugging
            self.disp_x = self.grid_x.copy()
            self.disp_y = self.grid_y.copy()

            assert self.disp_x.shape[0] == self.disp_y.shape[0], "bad shape"
            assert self.disp_x.shape[1] == self.disp_y.shape[1], "bad shape"
            assert len(dx) == len(dy), "bad shape"
            assert self.disp_x.shape[1]*self.disp_x.shape[0] == len(dx), "bad shape"
            count = 0
            for i in range(self.disp_x.shape[0]):
                for j in range(self.disp_x.shape[1]):
                    self.disp_x[i,j] = dx[count]
                    self.disp_y[i,j] = dy[count]
                    count = count + 1

        elif method=='spline':
            # x displacement
            tck_x = scipy.interpolate.bisplrep(self.grid_x, self.grid_y, dx, kx=5, ky=5)
            self.disp_x = scipy.interpolate.bisplev(self.grid_x[:,0], self.grid_y[0,:],tck_x)
    	    # y displacement
            tck_y = scipy.interpolate.bisplrep(self.grid_x, self.grid_y, dy, kx=5, ky=5)
            self.disp_y = scipy.interpolate.bisplev(self.grid_x[:,0], self.grid_y[0,:],tck_y)
        else:
            # probably linear
            self.disp_x = griddata((x, y), dx, (self.grid_x, self.grid_y), method=method)
            self.disp_y = griddata((x, y), dy, (self.grid_x, self.grid_y), method=method)

    def compute_strain_field(self):
        """Compute strain field from displacement using numpy
        """
        #get strain fields
        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]

        
        strain_xx, strain_xy = np.gradient(self.disp_x, dx, dy, edge_order=2)
        strain_yx, strain_yy = np.gradient(self.disp_y, dx, dy, edge_order=2)

        # Check that strain_yx and  strain_xy were not mixed up
        self.strain_xx = strain_xx + .5*(np.power(strain_xx,2) + np.power(strain_yx,2))
        self.strain_yy = strain_yy + .5*(np.power(strain_xy,2) + np.power(strain_yy,2))
        # this is the shear strain e_xy (not the engineering shear strain $\gamma_{xy}$
        self.strain_xy = .5*(strain_xy + strain_yx + strain_xx*strain_xy + strain_yx*strain_yy)

    def compute_strain_field_DA(self):
        """Compute strain field from displacement field using a  large strain method 

        
        """
        smap_shape = self.disp_x.shape
        self.strain_xx = np.full(smap_shape, np.NaN)
        self.strain_xy = np.full(smap_shape, np.NaN)
        self.strain_yy = np.full(smap_shape, np.NaN)
        self.strain_yx = np.full(smap_shape, np.NaN)

        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]

        for i in range(self.size_x):
            for j in range(self.size_y):
                du_dx = 0.
                dv_dy = 0. 
                du_dy = 0.
                dv_dx = 0.

                if i-1 >=0 and i+1< self.size_x:
                    du1 = (self.disp_x[i+1,j] - self.disp_x[i-1,j])/2.
                    du_dx = du1/dx
                    dv2 = (self.disp_y[i+1,j] - self.disp_y[i-1,j])/2.
                    dv_dx = dv2/dx

                if j-1>=0 and j+1 < self.size_y:
                    dv1 = (self.disp_y[i,j+1] - self.disp_y[i,j-1])/2.
                    dv_dy = dv1/dx
                    du2 = (self.disp_x[i,j+1] - self.disp_x[i,j-1])/2.
                    du_dy = du2/dy

                self.strain_xx[i,j] = du_dx + .5*(du_dx**2 + dv_dx**2)
                self.strain_yy[i,j] = dv_dy + .5*(du_dy**2 + dv_dy**2)
                self.strain_xy[i,j] = .5*(du_dy + dv_dx + du_dx*du_dy + dv_dx*dv_dy)

    def compute_strain_field_log(self):
        """Compute strain field from displacement field for large strain (logarithmic strain)
        """
        smap_shape = self.disp_x.shape
        self.strain_xx = np.full(smap_shape, np.NaN)
        self.strain_xy = np.full(smap_shape, np.NaN)
        self.strain_yy = np.full(smap_shape, np.NaN)
        self.strain_yx = np.full(smap_shape, np.NaN)

        dx = self.grid_x[1][0] - self.grid_x[0][0]
        dy = self.grid_y[0][1] - self.grid_y[0][0]
        for i in range(self.size_x):
            for j in range(self.size_y):
                du_dx = 0.
                dv_dy = 0. 
                du_dy = 0.
                dv_dx = 0.


                if i-1 >= 0 and i+1 < self.size_x:
                    du1 = (self.disp_x[i+1,j] - self.disp_x[i-1,j])/2.
                    du_dx = du1/dx
                    dv2 = (self.disp_y[i+1,j] - self.disp_y[i-1,j])/2.
                    dv_dx = dv2/dx
                      
                if j-1 >= 0 and j+1 < self.size_y:
                    dv1 = (self.disp_y[i,j+1] - self.disp_y[i,j-1])/2.
                    dv_dy = dv1/dx
                    du2 = (self.disp_x[i,j+1] - self.disp_x[i,j-1])/2.
                    du_dy = du2/dy
                t11=1+2.*du_dx+du_dx**2+dv_dx**2
                t22=1+2.*dv_dy+dv_dy**2+du_dy**2
                t12=du_dy+dv_dx+du_dx*du_dy+dv_dx*dv_dy
                deflog=np.log([[t11,t12],[t12,t22]])

                self.strain_xx[i,j] = .5*deflog[0,0]
                self.strain_yy[i,j] = .5*deflog[1,1]
                self.strain_xy[i,j] = .5*deflog[0,1]
    
    def obtain_strains(self, plugin: ArrayProcessingPlugin=None, loc_measure_method:str='mean')->dict:
        """this is a function that calculates the strains xx, yy, xy  on this grid. 
        
        OBSOLETE AND REDUNDANT - TO BE REMOVED

        Returns:
            dict: dataframe that contains (e_xx, e_xx_std, e_yy, e_yy_std, e_xy, e_xy_std) for this grid
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
        
        return adic     

    @classmethod
    def from_gridsize(cls, grid_size_instance:GridSize):
        """This is a class method that creates a new instance of DIC_Grid from a GridSize instance.

        Args:
            grid_size_instance (GridSize): a GridSize 

        Returns:
            DIC_Grid: object
        """
        grid_size_instance.win_size = grid_size_instance.get_winsize()
        grid_size_instance.prepare_gridXY()
        new_grid = cls(
            grid_x=grid_size_instance.grid_x, grid_y=grid_size_instance.grid_y,
            size_x=int(grid_size_instance.xnum), size_y=int(grid_size_instance.ynum))
        return copy.deepcopy(new_grid)

    def process_grid_data(self, win_size, reference_image, image, reference_points, current_points, interpolation_method, strain_type, remove_rigid_transform=False):
        """Process grid data by computing displacement, interpolating, and computing strain.

        Actions:
        - removes rigid body transform if specified
        - computes displacement and strain field
        - interpolates displacement field according to the specified method
        - computes strain field according to the specified strain type

        Args:
            win_size (tuple): size of the correlation window
            reference_image (str): filename of the reference image
            image (str): filename of the current image
            reference_points (np.ndarray): reference coordinates for each marker
            current_points (np.ndarray): current coordinates for each marker
            interpolation_method (str): method used for interpolating displacement
            strain_type (str): type of strain to compute ('green_lagrange', 'cauchy-eng', '2nd_order', or 'log')
            remove_rigid_transform (bool): whether to remove rigid body transform or not
        """
        print(f"compute displacement and strain field of {image}...")
        
        # Compute displacement
        if remove_rigid_transform:
            print("remove rigid body transform")
            disp = compute_disp_and_remove_rigid_transform(current_points, reference_points)
        else:
            print("do not remove rigid body transform")
            disp = compute_displacement(current_points, reference_points)
        
        # Add raw data and interpolate displacement
        self.add_raw_data(winsize=win_size, 
                          reference_image=reference_image, 
                          image=image, 
                          reference_point=reference_points, 
                          correlated_point=current_points, 
                          disp=disp)
        self.interpolate_displacement(reference_points, disp, method=interpolation_method)

        # Compute strain field
        if strain_type == 'green_lagrange':
            self.compute_strain_field()
        elif strain_type == '2nd_order':
            self.compute_strain_field_DA()
        elif strain_type == 'log':
            self.compute_strain_field_log()
        else:
            raise ValueError("please specify a correct strain_type: 'green_lagrange', 'cauchy-eng', '2nd_order' or 'log'")
    
        
        return disp  # Optionally return disp if needed