#%% 
# Analysis viewer
# this is a viewer for the DIC analysis results
#
# it aims to create a class that acts as a container for the DIC analysis results
# and provides methods to visualize the results

#%%
import logging
import pathlib
# from datetime import datetime
import json

# import tkinter as tk
# from tkinter import filedialog

# import pandas as pd
# from matplotlib import pyplot as plt
# import matplotlib.tri as tri
import multiprocessing
from tqdm import tqdm # Import the tqdm library


from py3dic.dic.core.dic_result_loader import DICResultFileContainer
from py3dic.dic.core.core_calcs import compute_disp_and_remove_rigid_transform, compute_displacement
from py3dic.dic import DICGrid
from py3dic.dic.io_utils import get_file_list 
from py3dic.dic.plotting.dic_grid_plotter import DICGridPlotter



logger = logging.getLogger(__name__)
#%%

class PlotCommand:
    """The PlotCommand class is a simple command pattern implementation. 
    It's used to encapsulate a method name and a filename suffix for a 
    DICGridPlotter object. The   init   method initializes the object with these parameters. 
    
    The  execute  method takes 
    - a DICGridPlotter object, 
    - a DICGrid object, a filename, 
    - and keyword arguments (from a parameter window), 
     and calls the method stored in self.method_name on the DICGridPlotter
    object with the given filename and keyword arguments.
    """
    def __init__(self, method_name, filename_suffix):
        """
        Initializes the PlotCommand object.

        Args:
            method_name (str): The name of the method to call on the DICGridPlotter object.
            filename_suffix (str): The suffix to append to the filename when saving the plot.
        """
        self.method_name = method_name
        self.filename_suffix = filename_suffix

    def execute(self, dgp, grid, filename, **kwargs):
        dgp.set_grid(grid)
        method = getattr(dgp, self.method_name)
        method(filename=filename, **kwargs)


class DICAnalysisResultContainer:
    COMPUTATION_CPUS = None

    def __init__(self, analysis_json_fname:str, img_extension:str = 'png',
                 cpus:int =None) -> None:
        """Initializes the DICAnalysisResultContainer object.

        Args:
            analysis_json (str): The path to the analysis json file.
            img_extension (str, optional): The image file extension. Defaults to 'png'. 
        """
        # load the analysis json file	
        self.analysis_json = analysis_json_fname
        self._load_analysis_json()
        self.COMPUTATION_CPUS = cpus if cpus is not None else max(1, multiprocessing.cpu_count() -1)

        # initialise the grid data container
        self.grid_data_container = DICResultFileContainer.from_result_dic(str(self.pp_DISPL_ANALYSIS_OUTPUT))
        self.dgp = DICGridPlotter()

        # load image file list:
        
        # or 'png', 'bmp', etc.
        # TODO this is also available from DICResultFileContainer, 
        # however we should use a list RELATIVE to the json file. 
        self.image_flist = get_file_list(self.pp_IMG_DIR.absolute(), img_extension)

        # load all the csv files from the result folder
        self.csv_flist = get_file_list(str(self.pp_ANALYSIS_RES_FOLDER/"result"),
                             file_extension='csv')
        # self._load_analysis_results()

    def _load_analysis_json(self):
        """Loads and parses the analysis json file 
        and stores the data in the object's attributes.
        """
        # Read the contents of the JSON file
        with open(self.analysis_json, 'r', encoding='utf-8') as file:
            self.analysis_data = json.load(file)

        # Store the path of the JSON file
        self.pp_json = pathlib.Path(self.analysis_json)
        self.pp_ANALYSIS_RES_FOLDER = self.pp_json.parent

        # Extract relevant paths from the JSON data
        self.pp_IMG_DIR = pathlib.Path(self.analysis_data.get('Image Folder', None))

        # Calculate the Experiment Root folder
        self.pp_EXPERIMENT_DIR = self.pp_ANALYSIS_RES_FOLDER.parents[1]

        # Modify the pp_IMG_DIR to use the stem of the original path
        self.pp_IMG_DIR = self.pp_EXPERIMENT_DIR / self.pp_IMG_DIR.stem

        # Assertions to ensure the paths exist
        assert self.pp_IMG_DIR.exists(), f"The directory {self.pp_IMG_DIR} does not exist."
        assert (self.pp_EXPERIMENT_DIR / "data_tensile").exists(), f"The directory {self.pp_EXPERIMENT_DIR / 'data_tensile'} does not exist."

        self.pp_DISPL_ANALYSIS_OUTPUT = self.pp_ANALYSIS_RES_FOLDER / 'result.dic'

        # Add analysis configuration parameters
        self.roi_window = self.analysis_data.get('ROI Selection', None)
        self.window_size = self.analysis_data.get('correl_window_size', None)
        self.grid_size = self.analysis_data.get('correl_grid_size', None)
        self.interpolation = self.analysis_data.get('interpolation', None)
        self.strain_type = self.analysis_data.get('strain type', None)
        self.remove_rigid_translation = self.analysis_data.get('remove translation', True)


    def print_analysis_data(self):
        """Prints the analysis data.

        """	
        for k,v in self.analysis_data.items():
            print(f"{k:25s} : {v:}")
        print(f"================ Config Parameters ================")
        print(f"image dir    : {self.pp_IMG_DIR}")
        print(f"analysis dir : {self.pp_ANALYSIS_RES_FOLDER}")
        print(f"analysis file: {self.pp_json}")
        print(f"ROI          : {self.roi_window}")
        print(f"window size  : {self.window_size}")
        print(f"grid size    : {self.grid_size}")
        print(f"remove rigid : {self.remove_rigid_translation}")
        print(f"interpolation: {self.interpolation}")
        print(f"strain type  : {self.strain_type}")

    @property
    def point_list(self)   -> list:
        """Returns the list for all frames with for the XY coordinate for all grid points.

        e.g. point_list[0] returns the XY coordinates for the first frame
        """ 
        return self.grid_data_container.pointlist

    def get_grid(self, frame_id:int) -> DICGrid:
        """Returns the grid points in the test imagelist.

        Args:
            frame_id (int): The frame id (keep in mind that it starts with 1).
        Returns:
            np.ndarray: The grid points.
        """
        assert frame_id >=1 and isinstance(frame_id, int), "frame_id must be an integer >=1"
        mygrid = DICGrid.from_gridsize(self.grid_data_container.gs)

        zb_fr_id = frame_id - 1

        logging.info("compute displacement and strain field of %s ...", self.image_flist[zb_fr_id])
        mygrid.process_grid_data(reference_image=self.image_flist[0],
                                 image=self.image_flist[zb_fr_id],
                                 reference_points=self.point_list[0],
                                 current_points=self.point_list[zb_fr_id],
                                 interpolation_method=self.interpolation,
                                 strain_type=self.strain_type,
                                 remove_rigid_transform= self.remove_rigid_translation)
        
        return mygrid
    
    def _plot_all_grids_generic_single_thread(self, plot_command:PlotCommand, **kwargs):
        """"
        this is the single-threaded version of the plot_all_grids method.

        Args:
            plot_command (PlotCommand): The command to execute for plotting.
            **kwargs: Additional keyword arguments to pass to the plot command.

        NOTE: This method is not used in the current implementation, because it introduces a memory leak in the Tkinter app.
        It is kept here for reference and can be used in a non-Tkinter environment.
        """
        OUT_IMG_FOLDER = self.pp_ANALYSIS_RES_FOLDER /"proc_img" / f"{plot_command.filename_suffix}s"
        OUT_IMG_FOLDER.mkdir(exist_ok=True, parents=True)

        for frame_id, img_fname in enumerate(self.image_flist):
            print(f"Processing frame {frame_id:d} : {plot_command.filename_suffix} - {img_fname.name}")
            frame_no = frame_id + 1
            grid = self.get_grid(frame_no)
            filename = OUT_IMG_FOLDER / f"{img_fname.stem}_{plot_command.filename_suffix}.png"
            plot_command.execute(self.dgp, grid, filename, **kwargs)



    def _plot_all_grids_generic(self, plot_command: PlotCommand, **kwargs):
        """
        Manages a pool of worker processes and tracks progress.
        """
        tasks = []
        for frame_id, img_fname in enumerate(self.image_flist):
            task_args = (
                self.analysis_json,
                frame_id,
                img_fname.stem,
                plot_command.method_name,
                plot_command.filename_suffix,
                kwargs
            )
            tasks.append(task_args)


        if self.COMPUTATION_CPUS <= 0:
            self.COMPUTATION_CPUS = multiprocessing.cpu_count()

        logging.warning("Using %d available processes.", self.COMPUTATION_CPUS)

        # Keep track of successful jobs
        successful_jobs = 0
        total_jobs = len(tasks)

        try:
            with multiprocessing.Pool(processes=self.COMPUTATION_CPUS) as pool:
                # ✅ Use imap_unordered to get results as they complete
                results_iterator = pool.imap_unordered(analysis_worker, tasks)
                
                # ✅ Wrap the iterator with tqdm for a nice progress bar
                print("Processing frames...")
                for result in tqdm(results_iterator, total=total_jobs, desc="Generating Images"):
                    # 'result' is the value returned by the worker (1 or 0)
                    successful_jobs += result
                
            print(f"\nProcessing complete. {successful_jobs}/{total_jobs} tasks succeeded.")

        except Exception as e:
            print(f"An error occurred during multiprocessing: {e}")


    def plot_all_grids(self, **kwargs):
        """plots all the grids

        Args:
            **kwargs: keyword arguments to pass to the plot (See DICGridPlotter.plot_grid)
        """
        plot_command = PlotCommand(method_name='plot_grid', filename_suffix='grid')
        self._plot_all_grids_generic(plot_command, **kwargs)

    def plot_all_markers(self, **kwargs):
        """plots all the markers	

        Args:
            **kwargs: keyword arguments to pass to the plot (See DICGridPlotter.plot_markers)
        """
        plot_command = PlotCommand('plot_markers', filename_suffix='marker')
        self._plot_all_grids_generic(plot_command, **kwargs)

    def plot_all_displ(self, **kwargs):
        """plots all displacement fields	

        Args:
            **kwargs: keyword arguments to pass to the plot (See DICGridPlotter.plot_displacement)
        """
        plot_command = PlotCommand('plot_displacement', filename_suffix='disp')
        self._plot_all_grids_generic(plot_command, **kwargs)

    def plot_all_displ_hsv(self, **kwargs):
        """plots all displacement fields as HSV intensity

        Args:
            **kwargs: keyword arguments to pass to the plot (see DICGridPlotter.plot_displacement_hsv)
        """
        plot_command = PlotCommand(method_name='plot_displacement_as_hsv', filename_suffix='disp_hsv')
        self._plot_all_grids_generic(plot_command, **kwargs)


    def plot_all_strain_maps(self, **kwargs):
        """plots all strain maps

        Args:
            **kwargs: keyword arguments to pass to the plot (see DICGridPlotter.plot_strain_map)
        """
        fname_suffix = kwargs.get("strain_dir", None)
        assert fname_suffix in ['strain_xx', 'strain_yy', 'strain_xy', 'all'], "Invalid strain_dir"

        if fname_suffix == 'all':
            strain_dirs = ['strain_xx', 'strain_yy', 'strain_xy']
        else:
            strain_dirs = [fname_suffix]

        for suffix in strain_dirs:
            print (f"Strain dirs: {suffix}")
            # I want to create a copy of kwargs and update the strain_dir
            # so that the original kwargs is not modified
            kwargs_copy = kwargs.copy()
            kwargs_copy['strain_dir'] = suffix
            plot_command = PlotCommand('plot_strain_map', filename_suffix=suffix)
            self._plot_all_grids_generic(plot_command, **kwargs_copy)
        
# %%



def analysis_worker(task_args):
    """
    Worker function to process and plot a single frame in an isolated process.

    This is necessary when working with tk app. Otherwise there was a persstent memory leak bug (relevant only to Tk). 
    """
    # Unpack the arguments
    analysis_json_fname, frame_id, img_fname_stem, plot_method_name, plot_filename_suffix, kwargs = task_args
    
    # Import necessary libraries INSIDE the worker
    import pathlib
    
    # print(f"Worker processing > '{plot_method_name}': # {frame_id:>8d}... ")
    
    try:
        # Each worker has its own, temporary container and plotter
        container = DICAnalysisResultContainer(analysis_json_fname)
        plotter = DICGridPlotter()
        plot_command = PlotCommand(method_name=plot_method_name, filename_suffix=plot_filename_suffix)

        # Get the specific grid for this frame
        grid = container.get_grid(frame_id + 1)
        
        # Define the output path
        out_folder = container.pp_ANALYSIS_RES_FOLDER / "proc_img" / f"{plot_command.filename_suffix}s"
        out_folder.mkdir(exist_ok=True, parents=True)
        filename = out_folder / f"{img_fname_stem}_{plot_command.filename_suffix}.png"
        
        # Execute the plot command
        plot_command.execute(plotter, grid, filename, **kwargs)

        return 1

    except Exception as e:
        print(f"Error in worker for frame {frame_id}: {e}")
        return 0 # Return 0 or None for f
    finally:
        # The process will exit, so cleanup is handled by the OS, 
        # but this is still good practice.
        # del container, plotter, plot_command, grid
        # gc.collect()
        pass
