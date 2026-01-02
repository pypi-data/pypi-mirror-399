"""
This module provides a class to handle batch Digital Image Correlation (DIC) processing.

Classes
-------
BatchDICStrainProcessor
    A class to process batch DIC data, save images, compute displacement and strain, add metadata, and more.
"""


#TODO add a parameter for selecting only some of the images (grid, marker, disp) to be saved.
#%%
import os
import copy
import pathlib
import sys

import pandas as pd
import numpy as np

import multiprocessing as mp
from multiprocessing import Pool
import copy

# from py3dic.dic.pydicGrid import DIC_Grid
from .core.core_calcs import (compute_disp_and_remove_rigid_transform,
                             compute_displacement)
from .core.dic_result_loader import DICResultFileContainer
from .dic_grid_with_plots import DICGridWithPlots as DIC_Grid
from ..misc.array_processing_plugins import ArrayProcessingPlugin, DefaultBorderRemovalPlugin

import logging
DRAW_ALL = False  
#%%

class BatchDICStrainProcessor:
    """
    A class to process batch DIC data, save images, compute displacement and strain, add metadata, and more.

    Attributes
    ----------
    grid_list : list of DIC_Grid
        List of DIC grids.
    STRAINS_TIME_XLSX_FILE : str
        Filename for saving strain time data. :noindex:

    Methods
    -------
    __init__(self, result_file, interpolation='raw', save_image=True, scale_disp=4., scale_grid=25., strain_type='green_lagrange', rm_rigid_body_transform=True, meta_info_file=None, unit_test_mode=False, analysis_folder=None)
        Initializes a DICProcessorBatch object.
    get_grid(self, id)
        Returns a specific grid by ID.
    process_data(self)
        Main function for processing files.
    add_metadata_to_grid_object(self, mygrid)
        Adds metadata to a grid object.
    write_image_files(self, mygrid)
        Writes image files (marked, displacement, grid).
    plot_strain_maps(self, id=100)
        Plots all three strain types.
    plot_strain_map_with_id(self, id, strain_type)
        Plots a strain map with a given ID and strain type.
    read_meta_info_file(self)
        Reads the meta info file.
    get_df_with_time(self, plugin, save_to_file=False, loc_measure_method="mean")
        Merges the results from the images with the meta_data file.
    """    
    grid_list:list[DIC_Grid] = [] # saving grid here
    STRAINS_TIME_XLSX_FILE:str = "df_strain_wt.xlsx"
    SAVE_EVERY_NTH_IMAGE:int = 10
    dic_result_file_container:DICResultFileContainer = None

    def __init__(self, result_file, 
            interpolation='raw', 
            save_image=True, 
            scale_disp=4., scale_grid=25., 
            strain_type='green_lagrange', 
            rm_rigid_body_transform=True, 
            meta_info_file=None,
            unit_test_mode:bool = False,
            analysis_folder:str= None):

        """
        Initializes a DICProcessorBatch object.

        Parameters
        ----------
        result_file : str
            Path to the result file.
        interpolation : str, optional
            Interpolation type for smoothing data (default is 'raw').
        save_image : bool, optional
            Whether to save result images (default is True).
        scale_disp : float, optional
            Scale to amplify the displacement of images (default is 4.).
        scale_grid : float, optional
            Scale to amplify the grid of images (default is 25.).
        strain_type : str, optional
            Strain type, can be 'green_lagrange', 'cauchy-eng', '2nd_order' or 'log' (default is 'green_lagrange').
        rm_rigid_body_transform : bool, optional
            Whether to remove rigid body displacement (default is True).
        meta_info_file : str, optional
            Path to a meta info file (default is None).
        unit_test_mode : bool, optional
            Whether to run in unit test mode (default is False).
        analysis_folder : str, optional
            Path to the analysis folder (default is None).
        """
        self.result_file = result_file
        self.interpolation = interpolation
        self.save_image = save_image
        self.scale_disp = scale_disp
        self.scale_grid = scale_grid
        self.strain_type = strain_type
        self.rm_rigid_body_transform = rm_rigid_body_transform
        self.meta_info_fname = meta_info_file
        self.__unit_test_mode = unit_test_mode
        self._analysis_folder = analysis_folder
        self.meta_info = {}

        if self.meta_info_fname:
            self.read_meta_info_file()

    def set_every_nth_image(self, n:int):
        """
        Sets the interval for saving images.

        Parameters
        ----------
        n : int
            The interval at which images will be saved.
        """
        self.SAVE_EVERY_NTH_IMAGE = n

    @property
    def grids(self)->list:
        """
        Returns the grid list.

        Returns
        -------
        list
            List of DIC_Grid objects.
        """      
        return self.grid_list
    
    def get_grid(self, id:int)->DIC_Grid:
        """
        Returns a specific grid by ID.

        Parameters
        ----------
        id : int
            The ID of the grid to return.

        Returns
        -------
        DIC_Grid
            The DIC_Grid object.
        """     
        return self.grid_list[id]


    def process_data(self):
        """
        Main function for processing files.
        
        - Reads the result.dic file with the displacements.
        - Processes each image.
        - Computes the displacement and strain field.
        - Writes image files.
        - Writes result files.
        - Adds metadata to grid if it exists.
        """       
        self.grid_list = [] # saving grid here
        self.disp_list = [] # This is not defined in here

        # read/parse dic result file
        self.dic_result_file_container = DICResultFileContainer.from_result_dic(self.result_file)
        self.point_list = self.dic_result_file_container.pointlist
        self.image_list = self.dic_result_file_container.imagelist
        self.win_size = self.dic_result_file_container.get_winsize()
        
        # prepare Gridlist
        for i in range(len(self.image_list)):
            dic_gr = DIC_Grid.from_gridsize(self.dic_result_file_container.gs)
            self.grid_list.append(dic_gr)

        # Create pool for image writing processes
        with Pool(processes=4) as pool:  # Adjust number of processes as needed
            image_write_futures = []
            
            # compute displacement and strain
            for i, mygrid in enumerate(self.grid_list):
                print("compute displacement and strain field of", self.image_list[i], "...")
                point_list = self.dic_result_file_container.pointlist
                disp = mygrid.process_grid_data(
                    reference_image=self.image_list[0], 
                    image=self.image_list[i], 
                    reference_points=point_list[0], 
                    current_points=point_list[i], 
                    interpolation_method=self.interpolation, 
                    strain_type=self.strain_type, 
                    remove_rigid_transform=self.rm_rigid_body_transform
                )
                self.disp_list.append(disp)

                # write image files using pool
                if (self.save_image and i % self.SAVE_EVERY_NTH_IMAGE == 0):
                    # Create a deep copy of the grid to avoid sharing mutable objects
                    grid_copy = copy.deepcopy(mygrid)
                    
                    # Submit image writing task to pool
                    future = pool.apply_async(self._write_image_files_worker, (grid_copy,))
                    image_write_futures.append(future)

                if not self.__unit_test_mode:
                    # in unit test mode, we don't want to write the result file
                    # write result file
                    mygrid.write_result(analysis_folder=self._analysis_folder)

                # add meta info to grid if it exists
                self.add_metadata_to_grid_object(mygrid)
            
            # Wait for all image writing tasks to complete
            for future in image_write_futures:
                try:
                    future.get()  # This will raise any exceptions that occurred
                except Exception as e:
                    print(f"Error writing image files: {e}")

    def _write_image_files_worker(self, grid):
        """
        Worker function to write image files in a separate process.
        This is a wrapper around the original write_image_files method.
        """
        try:
            self.write_image_files(grid)
        except Exception as e:
            print(f"Error writing image files: {e}")
            raise  # Re-raise so the main process knows about the error


    #region Metadata related ================================================================
    def read_meta_info_file(self):
        """ Read the meta info file and store the information in the meta_info dictionary.

        TODO: update the docstring to reflect the actual format of the meta info file.

        This function reads the meta info file specified by the `self.meta_info_file` attribute. 
        The file should be in CSV format, with the first row as the header containing field names. 
        The following  rows should contain values corresponding to the field names. 
        The function parses the file and stores the information in the `self.meta_info` dictionary, 
        with the first value in each row as the key and the rest of the values as a dictionary.

        Example of meta info file format:
            image , time, load
            img_001, 0.1, 500
            img_002, 0.2, 520
            img_003, 0.3, 550

        The resulting self.meta_info dictionary will look like:
            {
                "img_001": {"time": 0.1, "load": 500},
                "img_002": {"time": 0.2, "load": 520},
                "img_003": {"time": 0.3, "load": 550},
            }
        """
        print(f'read meta info file{self.meta_info_fname}...')
        with open(self.meta_info_fname, mode='r', encoding='utf-8') as f:
            lines = f.readlines()
            header = lines[0]
            field = header.split()
            for l in lines[1:-1]:
                val = l.split()
                if len(val) > 1:
                    dictionary = dict(zip(field, val))
                    self.meta_info[val[0]] = dictionary



    def add_metadata_to_grid_object(self, mygrid):
        """
        Adds metadata to a grid object.

        Parameters
        ----------
        mygrid : DIC_Grid
            The DIC_Grid object to add metadata to.
        """
        if len(self.meta_info) > 0:
            img = os.path.basename(mygrid.image)
                #if not meta_info.has_key(img):
            if img not in self.meta_info.keys():
                print("warning, can't affect meta deta for image", img)
            else:
                mygrid.add_meta_info(self.meta_info.get(img))
                print('add meta info', self.meta_info.get(img))
    #endregion

    #region Image files =====================================================================
    def write_image_files(self, mygrid:DIC_Grid):
        """
        Writes image files (marked, displacement, grid).

        Parameters
        ----------
        mygrid : DIC_Grid
            The DIC_Grid object to write image files for.
        """
        win_size_x, win_size_y = self.win_size[0], self.win_size[1]
        mygrid.draw_marker_img(analysis_folder=self._analysis_folder)

        # draw displacement and grid images
        if DRAW_ALL:
            mygrid.draw_disp_img(self.scale_disp, analysis_folder=self._analysis_folder)
            mygrid.draw_grid_img(self.scale_grid, analysis_folder=self._analysis_folder)
        if win_size_x == 1 and win_size_y == 1 : 
            #TODO: Demistify this condition
            mygrid.draw_disp_hsv_img()

    def plot_strain_maps(self, id:int=100):
        """
        Plots all three strain types.

        Parameters
        ----------
        id : int, optional
            The ID of the grid to plot (default is 100).
        """    
        self.plot_strain_map_with_id(id, strain_type='xx')
        self.plot_strain_map_with_id(id, strain_type='yy')
        self.plot_strain_map_with_id(id, strain_type='xy')


    def plot_strain_map_with_id(self, id, strain_type:str):
        """
        Plots a strain map with a given ID and strain type.

        Parameters
        ----------
        id : int
            The ID of the grid to plot.
        strain_type : str
            The type of strain to plot ('xx', 'yy', 'xy').
        """
        assert (id < len(self.grid_list) and id>0),  "id does not correspond to an image" 
        assert strain_type in ['xx', 'yy', 'xy'], "strain type should be one of ['xx', 'yy', 'xy']"
        # tmp_grid = self.grid_list[id]
        tmp_grid:DIC_Grid = self.get_grid(id)
        if strain_type == 'xx':
            tmp_grid.plot_field(tmp_grid.strain_xx, title='xx strain')
        elif strain_type == 'yy':
            tmp_grid.plot_field(tmp_grid.strain_yy, title='yy strain')
        elif strain_type == 'xy':
            tmp_grid.plot_field(tmp_grid.strain_xy, title='xy strain')

    #endregion    
    
    def get_df_with_time(self,  plugin: ArrayProcessingPlugin, 
                         save_to_file:bool=False, loc_measure_method:str="mean")->pd.DataFrame:
        """Merges the results from the images with the meta_data file

        Args:
            plugin (_type_, optional): Plugin for selecting a portion of the array. Defaults to None.
            save_to_file (bool, optional): whether to save to file. Defaults to False.
            loc_measure_method (str, optional): how the array data are processed (mean, or median). Defaults to "mean".

        Returns:
            pd.DataFrame: _description_
        """
        if plugin is None:
            plugin = DefaultBorderRemovalPlugin()
        assert isinstance(plugin, ArrayProcessingPlugin), "plugin must be an instance of ArrayProcessingPlugin"

        # collect data from grids
        grid_list = self.grid_list
        adic = []
        for j, gr in enumerate(grid_list):
            a_meta = {"id": j + 1, "file": pathlib.Path(gr.image).name}
            adic_gr = gr.obtain_strains(plugin=plugin,loc_measure_method=loc_measure_method)
            adic.append({**a_meta, **adic_gr})
        df_dic_notime = pd.DataFrame(adic)

        # Read the data from the *_meta-data.txt*
        if self.meta_info_fname is None:
            logging.info("No meta info file provided")
            lst_unit_test_mode = []
            for i in range(len(df_dic_notime)):
                lst_unit_test_mode.append(
                    {"file": self.grid_list[i].image.split("\\")[-1],
                     "time(s)": i*0.1,
                    "force(N)": i})
            df_img_meta = pd.DataFrame(lst_unit_test_mode)
        else:
            # FIXME : when a 4th column with the timestap is added int the meta-data.txt the 
            # import assums that the first column is the index.
            # assert df_img_meta.shape[1]>3, "The two dataframes must have the 3 columns"       
            # the current implementatin reads the first 3 columns only
            df_img_meta = pd.read_csv(self.meta_info_fname, sep="\t",usecols=[0,1,2])

        # assert df_img_meta.shape[1]>3, "The two dataframes must have the 3 columns"

        # merge the two files
        df_dic_tot = pd.merge(df_dic_notime, df_img_meta, how="inner", on="file")
        if save_to_file:
            pp_outputdir = pathlib.Path(self._analysis_folder)
            pp_outputdir.mkdir(parents=True, exist_ok=True)
            DIC_EXCEL_OUTPUT = pp_outputdir / self.STRAINS_TIME_XLSX_FILE
            df_dic_tot.to_excel(DIC_EXCEL_OUTPUT)
            df_dic_tot.to_csv(DIC_EXCEL_OUTPUT.with_suffix(".csv"))
            logging.info("Saved df with time to : %s", DIC_EXCEL_OUTPUT)
        return df_dic_tot
