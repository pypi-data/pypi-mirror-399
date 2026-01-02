#%%
import copy
import glob
import pathlib
import numpy as np

from ..core.dic_enums import EnumInterpolation, EnumStrainType, EnumTrackingMethodType
from ..core.core_calcs import (compute_disp_and_remove_rigid_transform,
                             compute_displacement)
from ..core.calc_strain_calculator import StrainCalculator
from ..core.calc_grid_interpolator import GridInterpolator
from ..core.dic_grid import DICGrid
from .rolling_image_marker_tracker import RollingImageMarkerTracker

import logging



#%% 
class RollingDICStrainProcessor:
    # grid_list:list[DIC_Grid] = [] # saving grid here
    # STRAINS_TIME_XLSX_FILE:str = "df_strain_wt.xlsx"
    _counter = 0   # number of images processed
    disp_list = [] # array with the calculated displacements
    sc: StrainCalculator = None

    def __init__(self,
            sidp:RollingImageMarkerTracker,
            interpolation:str=EnumInterpolation.RAW.value, 
            strain_type:str=EnumStrainType.GREEN_LAGRANGE.value, 
            scale_disp:float=1., scale_grid:float=1., 
            rm_rigid_body_transform:bool=True,
            save_image:bool=False
            ,*args, **kwargs
            ):
        """* required argument:
        - the first arg 'result_file' must be a result file given by the init() function
        * optional named arguments ;
        - 'interpolation' the allowed vals are 'raw', 'spline', 'linear', 'delaunnay', 'cubic', etc... 
        a good value is 'raw' (for no interpolation) or spline that smooth your data.
        - 'save_image ' is True or False. Here you can choose if you want to save the 'disp', 'grid' and 
        'marker' result images
        - 'scale_disp' is the scale (a float) that allows to amplify the displacement of the 'disp' images
        - 'scale_grid' is the scale (a float) that allows to amplify the 'grid' images
        - 'meta_info_file' is the path to a meta info file. A meta info file is a simple csv file 
        that contains some additional data for each pictures such as time or load values.
        - 'strain_type' should be 'green_lagrange' 'cauchy-eng' '2nd_order' or 'log'. Default value is green_lagrange (or engineering) strains. You 
        can switch to log or 2nd order strain if you expect high strains. 
        - 'rm_rigid_body_transform' for removing rigid body displacement (default is true)
        """
        self.sidp = sidp
        self._dic_grid_size = self.sidp.get_dic_gridsize()
        
        self.interpolation = interpolation
        self.strain_type = strain_type
        
        self.save_image = save_image
        self.scale_disp = scale_disp
        self.scale_grid = scale_grid
        self.rm_rigid_body_transform = rm_rigid_body_transform

        self._prepare_grid()

        self._gi = GridInterpolator(grid_x=self.__grid_x, grid_y=self.__grid_y)
        self.sc = StrainCalculator(grid_x=self.__grid_x, grid_y=self.__grid_y)
        self.meta_info = {}

    def _prepare_grid(self):
        xmin = self._dic_grid_size.xmin
        xmax = self._dic_grid_size.xmax
        xnum = self._dic_grid_size.xnum
        self.win_size = self._dic_grid_size.get_winsize()

        self.__grid_x, self.__grid_y = self._dic_grid_size.prepare_gridXY()
        # The new grid is used fo
        self.__newgrid = DICGrid(self.__grid_x, self.__grid_y, int(self._dic_grid_size.xnum), int(self._dic_grid_size.ynum))

    def create_new_grid(self):
        return copy.deepcopy(self.__newgrid)
    
    @property
    def ref_points(self):
        return self.sidp.points_ref

    def process_new_image(self, new_image:np.ndarray) -> DICGrid:
        """_summary_

        Args:
        """        
        mygrid:DICGrid = self.create_new_grid()
        
        res = self.sidp.process_image(new_img=new_image)
        self._counter +=1

        logging.info(f"compute displacement and strain field of img no: {self._counter} ...")
        disp = None
        self.point_list0 = self.sidp.points_ref
        self.point_listi = self.sidp.current_point_position
        # TODO chekc shape of points_ref and self.point_list[0]
        if self.rm_rigid_body_transform:
            logging.info("   - remove rigid body transform")
            disp = compute_disp_and_remove_rigid_transform(self.point_listi, self.point_list0)
        else:
            logging.info("   - rigid body transform is not removed")
            disp = compute_displacement(self.point_listi, self.point_list0)

        mygrid.reference_image = "ref image",
        mygrid.image = str("i") # TODO sort out image type annotation. 
        mygrid.reference_point = self.point_list0
        mygrid.correlated_point = self.point_listi
        mygrid.disp = disp
        
        self.disp_list.append(disp)
        mygrid.disp_x, mygrid.disp_y = self._gi.interpolate_displacement(
                    point=self.point_list0,
                    disp=mygrid.disp,
                    method=self.interpolation)
        

        # Compute strain field
        self.sc.compute_strain(disp_x=mygrid.disp_x, disp_y=mygrid.disp_y, method = self.strain_type)
        mygrid.strain_xx = self.sc.strain_xx.copy()
        mygrid.strain_yy = self.sc.strain_yy.copy()
        mygrid.strain_xy = self.sc.strain_xy.copy()

        # # write image files
        # TODO write to file, or delegate that to another class
        # if (self.save_image):
        #     self.write_image_files(mygrid)

        # # add meta info to grid if it exists
        # self.add_metadata_to_grid_object(mygrid)
        return mygrid


    def add_metadata_to_grid_object(self, mygrid):
        """Adds metadata to grid object.

        TODO I need to understand how this works in the original code
        or in DICProcessorBatch

        This could eventually add time and force info in the grid

        Args:
            mygrid (_type_): _description_
        """ 
        pass        
        # if (len(self.meta_info) > 0):
        #     img = os.path.basename(mygrid.image)
        #         #if not meta_info.has_key(img):
        #     if img not in self.meta_info.keys():
        #         print("warning, can't affect meta data for image", img)
        #     else:
        #         mygrid.add_meta_info(self.meta_info.get(img))
        #         print('add meta info', self.meta_info.get(img))


