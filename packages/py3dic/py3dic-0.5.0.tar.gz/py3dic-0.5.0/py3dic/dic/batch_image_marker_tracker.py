#%%[markdown]
# The `pydic_processor.py` module contains two classes, 
# - `SingleImageDisplacementProcessor` and 
# - `ImageDisplacementProcessorBatch`, 
# which are designed to perform digital image correlation (DIC) 
# on single and batch of images respectively. 
#
# 1. `SingleImageDisplacementProcessor`: 
#    This class processes a single image sequence to compute displacements. 
#    It's initialized with parameters including the reference image, 
#    window size, grid size, area of interest, and verbosity level. 
#    It supports both structured and unstructured grids for defining points of interest.
#    It also supports different optical flow calculation methods like 
#    Lucas-Kanade and deep flow.
#    The class includes methods for preprocessing the image,
#    initializing the correlation grid, displaying markers (points of interest),
#    processing the image to compute the displacement of points between different images, 
#    writing results to a file, and returning the configuration parameters.
#
# 2. `ImageDisplacementProcessorBatch`:
#    This class extends the functionality of the `SingleImageDisplacementProcessor` 
#    to a batch of images. It is capable of handling multiple image sequences and can
#    process each sequence individually to compute the displacements. It can also 
#    aggregate and organize the results from all sequences. The initialization 
#    parameters are similar to `SingleImageDisplacementProcessor` with additional 
#    parameters for handling multiple sequences. 
#    This class includes methods for setting up batch processing, processing each
#    image sequence, and managing results from all sequences.
#
# Both classes are central to the operation of digital image correlation (DIC) systems,
# where a grid of points on an image is tracked for movement between different images 
# in the sequence. 
# 
# The `SingleImageDisplacementProcessor` focuses on processing single image sequences,
# while `ImageDisplacementProcessorBatch` extends this functionality to process batches 
# of image sequences.
#%%
import logging
import glob
import pathlib
import cv2
import numpy as np

logging.getLogger(__name__)


from .gui_selectors.cv2_area_selector import AreaSelectorCV2
from .core.core_calcs import (compute_disp_and_remove_rigid_transform,
                             compute_displacement, remove_point_outside)
from ._obsolete.draw_opencv_v2 import draw_opencv_v2

from py3dic import __version__ as py3dic_version

#%%
class BatchImageMarkerTracker:
    """
    Class to process image sequences and compute displacements.
    Writes the displacement results to a file.

    Attributes:
        image_pattern (str): Path and pattern describing where the images are located.
        win_size_px (tuple): Size in pixels of the correlation windows as a (dx, dy) tuple.
        grid_size_px (tuple): Size of the correlation grid as a (dx, dy) tuple.
        result_file (str): Name of the result file.
        area_of_interest (list of two tuples, optional): Area of interest in [(top left x, top left y), (bottom right x, bottom right y)] format.
        img_list (list): List of image file paths.
        img_ref (array): First image in the image sequence.
        points (array): Points of interest in the image sequence.
    """
    def __init__(self, 
                 image_pattern, 
                 win_size_px, 
                 grid_size_px, 
                 result_file:pathlib.Path, 
                 area_of_interest=None, 
                 verbosity:int = 5, 
                 analysis_folder:str = 'pydic', #TODO replace this with a suitable 
                 *args, **kwargs):
        """
        Initialize the BatchImageMarkerTracker.

        Args:
            image_pattern (str): Path and pattern describing where the images are located.
            win_size_px (tuple): Size in pixels of the correlation windows as a (dx, dy) tuple.
            grid_size_px (tuple): Size of the correlation grid as a (dx, dy) tuple.
            result_file (str): Name of the result file.
            area_of_interest (list of two tuples, optional): Area of interest in [(top left x, top left y), (bottom right x, bottom right y)] format.
            verbosity (int) : verbosity level (0 is none e.g. unit testing, 5 is maximum DEBUG)
            analysis_foder (str | pathlib.Path) : Path to export the analysis results. 
        """
        self.image_pattern = image_pattern
        self.win_size_px = win_size_px
        self.grid_size_px = grid_size_px
        self.result_file_path = result_file
        self.result_file_path.parent.mkdir(parents=True, exist_ok=True)
        self.area_of_interest = area_of_interest
        self._verbosity_level = verbosity
        self.kwargs = kwargs
        self._analysis_folder = analysis_folder
    
        self.preprocess()

    def preprocess(self):
        self.img_list = sorted(glob.glob(self.image_pattern))
        self.img_ref = cv2.imread(self.img_list[0], 0)

        assert len(self.img_list) > 1, "there is not image in " + str(self.image_pattern)

        # TODO Change this with the new function developed that uses only matplotlib
        if self.area_of_interest is None:
            assert self._verbosity_level>0 , ""
            print("please pick your area of interest on the picture")
            print("Press 'c' to proceed")
            areaSelector = AreaSelectorCV2(self.img_ref)
            self.area_of_interest = areaSelector.pick_area_of_interest()

        self.points = self.init_correlation_grid()

        self.points_in = remove_point_outside(self.points, self.area_of_interest, shape='box')

        if self._verbosity_level >=3:
            self.display_markers(self.points_in)

    def init_correlation_grid(self):
        """
        Initialize the correlation grid with points of interest.

        Returns:
            points (array): Array of points of interest in the image sequence.

        # TODO simplify this three methods. 
        # create a grid_type option and use ('unstructured' or 'deepflow' or 'default')
        """
        area = self.area_of_interest
        points = []
        points_x = np.float64(np.arange(area[0][0], area[1][0], self.grid_size_px[0]))
        points_y = np.float64(np.arange(area[0][1], area[1][1], self.grid_size_px[1]))

        if 'unstructured_grid' in self.kwargs:
            block_size, min_dist = self.kwargs['unstructured_grid']
            feature_params = dict(maxCorners=50000,
                                  qualityLevel=0.01,
                                  minDistance=min_dist,
                                  blockSize=block_size)
            points = cv2.goodFeaturesToTrack(self.img_ref, mask=None, **feature_params)[:, 0]
        elif 'deep_flow' in self.kwargs:
            points_x = np.float64(np.arange(area[0][0], area[1][0], 1))
            points_y = np.float64(np.arange(area[0][1], area[1][1], 1))
            for x in points_x:
                for y in points_y:
                    points.append(np.array([np.float32(x), np.float32(y)]))
            points = np.array(points)
        else:
            for x in points_x:
                for y in points_y:
                    points.append(np.array([np.float32(x), np.float32(y)]))
            points = np.array(points)
        self.points_x = points_x
        self.points_y = points_y
        return points

    def display_markers(self, points_in):
        """
        Display the markers on the reference image.


        Args:
            points (array): Array of points of interest in the image sequence.
        """
        img_ref = cv2.imread(self.img_list[0], 0)
        img_ref = cv2.putText(img_ref, "Displaying markers... Press any buttons to continue", (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
        # TODO: remove dependence on draw_opencv (USe GridPlotter)
        draw_opencv_v2(img_ref, point=points_in)

    def compute_and_save_results(self):
        """
        Compute the grid and save it in the result file.
        """
        self.result_file = open(self.result_file_path, mode = 'w', encoding = 'utf-8')
        xmin = self.points_x[0]; xmax = self.points_x[-1]; xnum = len(self.points_x)
        ymin = self.points_y[0]; ymax = self.points_y[-1]; ynum = len(self.points_y)
        self.result_file.write(str(xmin) + '\t' + str(xmax) + '\t' + str(int(xnum)) + '\t' + str(int(self.win_size_px[0])) + '\n')
        self.result_file.write(str(ymin) + '\t' + str(ymax) + '\t' + str(int(ynum)) + '\t' + str(int(self.win_size_px[1])) + '\n')

        # param for correlation 
        lk_params = dict( winSize  = self.win_size_px, maxLevel = 10,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        # parse all files and write results file
        point_to_process = self.points_in
        self.write_result( self.img_list[0], point_to_process)
        logging.info('Starting to process images')
        for i in range(len(self.img_list)-1):
            if self._verbosity_level>=3 or (i%100==0):
                print('reading image {} / {} : "{}"'.format(i+1, len(self.img_list), self.img_list[i+1]))
            image_ref = cv2.imread(self.img_list[i], 0)
            image_new = cv2.imread(self.img_list[i+1], 0)

            if 'deep_flow' in self.kwargs:
                winsize_x = self.win_size_px[0]
                final_point = cv2.calcOpticalFlowFarneback(image_ref, image_new, None, 0.5, 3, winsize_x,
                                                           10, 5, 1.2, 0)
                index = 0
                ii_max = final_point.shape[0]
                jj_max = final_point.shape[1]

                for jj in range(jj_max):
                    for ii in range(ii_max):
                        if (jj >= self.area[0][0] and jj < self.area[1][0] and
                            ii >= self.area[0][1] and ii < self.area[1][1]):
                            point_to_process[index] += final_point[ii,jj]
                            index += 1

            else:
                final_point, st, err = cv2.calcOpticalFlowPyrLK(image_ref, image_new, point_to_process, None, **lk_params)
                point_to_process = final_point
            self.write_result( self.img_list[i+1], point_to_process)
        self.result_file.write('\n')
        self.result_file.close()
        logging.info('Results written to %s' % self.result_file_path)

    def write_result(self, image, points):
        """
        Used by the class to write the data for a file.

        Args:
            image (str): The name of the image file.
            points (list): List of point coordinates.
        """
        self.result_file.write(str(image) + '\t')
        for p in points:
            self.result_file.write(str(p[0]) + ',' + str(p[1]) + '\t')
        self.result_file.write('\n')

    @property
    def analysis_metadata(self):
        an_dic = {
            "py3dic_version" : py3dic_version,
            "result_file" :self.result_file_path,
            "area_of_interest" :self.area_of_interest,
            "corr_window_size_xy" :self.win_size_px,
            "grid_size_xy" :self.grid_size_px,
            "method_deep_flow" : True if 'deep_flow' in self.kwargs else False,
            "method_calcOpticalFlowPyrLK" : True if not 'deep_flow' in self.kwargs else False
        }
        return an_dic
# %%
