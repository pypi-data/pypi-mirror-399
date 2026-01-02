import cv2
import numpy as np
from .._obsolete.draw_opencv_v2 import draw_opencv_v2
from ..core.core_calcs import remove_point_outside
from ..core.dic_grid import GridSize
from ..gui_selectors.cv2_area_selector import AreaSelectorCV2


import logging
class RollingImageMarkerTracker:

    points_ref:np.ndarray = None   # array with initial X,Y position of markers
    img_ref:np.ndarray = None      # reference image

    def __init__(self,
            reference_image:np.ndarray,
            win_size_px:tuple,
            grid_size_px:tuple,
            area_of_interest:list[tuple]=None,
            verbosity:int = 1,
            *args, **kwargs):
        """
        Initialize the ImageDisplacementProcessor.

        Args:
            reference_image (numpy.ndarray): a reference image (the result of imread)
            win_size_px (tuple): Size in pixels of the correlation windows as a (dx, dy) tuple.
            grid_size_px (tuple): Size of the correlation grid as a (dx, dy) tuple.
            result_file (str): Name of the result file.
            area_of_interest (list of two tuples, optional): Area of interest in [(top left x, top left y), (bottom right x, bottom right y)] format.
            verbosity (int) : verbosity level (0 is none e.g. testing, 5 is maximum)
        """
        # self.img_ref = cv2.imread(self.img_list[0], 0)
        self.img_ref = reference_image.copy()
        self._last_img = reference_image.copy()
        self._curr_img = reference_image.copy()

        #
        self.win_size_px = win_size_px
        self.grid_size_px = grid_size_px
        self.area_of_interest = area_of_interest
        self._verbosity_level = verbosity

        self.kwargs = kwargs

        self.preprocess()

    def preprocess(self):

        # TODO replace AreaSelectorCV2 with matplatolib. 
        if self.area_of_interest is None:
            assert self._verbosity_level>0 , ""
            print("please pick your area of interest on the picture")
            print("Press 'c' to proceed")
            areaSelector = AreaSelectorCV2(self.img_ref)
            self.area_of_interest = areaSelector.pick_area_of_interest()

        self.init_correlation_grid()

        self.points_in = remove_point_outside(self.points_ref, self.area_of_interest, shape='box')

        if self._verbosity_level >=3:
            self.display_markers(self.points_in)

    def init_correlation_grid(self)-> np.ndarray:
        """
        Initialize the correlation grid with points of interest.

        Returns:
            points (array): Array of points of interest in the image sequence.
        """
        area = self.area_of_interest
        points = []

        if 'unstructured_grid' in self.kwargs:
            logging.info("Grid Type: unstructured grid")
            block_size, min_dist = self.kwargs['unstructured_grid']
            feature_params = dict(maxCorners=50000,
                                  qualityLevel=0.01,
                                  minDistance=min_dist,
                                  blockSize=block_size)
            points = cv2.goodFeaturesToTrack(self.img_ref, mask=None, **feature_params)[:, 0]
        else:
            # this is for deepflow and Lucas-Kanade method
            if 'deep_flow' in self.kwargs:
                logging.info("Grid Type: Structured grid - deepflow")
                points_x = np.float64(np.arange(area[0][0], area[1][0], 1))
                points_y = np.float64(np.arange(area[0][1], area[1][1], 1))
            else:
                logging.info("Grid Type: Structured grid - default")
                points_x = np.float64(np.arange(
                    start= area[0][0],
                    stop= area[1][0],
                    step = self.grid_size_px[0]))
                points_y = np.float64(np.arange(
                    start=area[0][1],
                    stop=area[1][1],
                    step=self.grid_size_px[1]))
            for x in points_x:
                for y in points_y:
                    points.append(np.array([np.float32(x), np.float32(y)]))
            points = np.array(points)
            self.points_x = points_x
            self.points_y = points_y
        self.points_ref = points.copy()

        return self.points_ref

    def display_markers(self, points_in):
        """
        Display the markers on the reference image.

        Args:
            points (array): Array of points of interest in the image sequence.
        """
        img_ref = self.img_ref.copy()
        img_ref = cv2.putText(img_ref, "Displaying markers... Press any buttons to continue",
                              (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)
        draw_opencv_v2(img_ref, point=points_in)

    def process_image(self, new_img:np.ndarray):
        """
        workhorse of the code

        Compute the grid and save it in the result file.
        """

        # replacing image with last image
        self._last_img = self._curr_img.copy()
        self._curr_img = new_img.copy()

        # param for correlation 
        lk_params = dict( winSize  = self.win_size_px, maxLevel = 10,
                          criteria = (cv2.TERM_CRITERIA_EPS | cv2.TERM_CRITERIA_COUNT, 10, 0.03))

        point_to_process = self.points_in

        # image_ref = cv2.imread(self.img_list[i], flag =cv2.IMREAD_GRAYSCALE)
        last_image = self._last_img.copy()
        # image_str = cv2.imread(self.img_list[i+1], flag = cv2.IMREAD_GRAYSCALE)
        curr_image = self._curr_img.copy()

        if 'deep_flow' in self.kwargs:
            winsize_x = self.win_size_px[0]
            final_point = cv2.calcOpticalFlowFarneback(last_image, curr_image,
                                                       None, 0.5, 3,
                                                       winsize_x,
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
            #  Lucas-Kanade method
            final_point, st, err = cv2.calcOpticalFlowPyrLK(last_image, curr_image, point_to_process, None, **lk_params)
            point_to_process = final_point
        # self.write_result( self.img_list[i+1], point_to_process)
        self.points_in = point_to_process.copy()
        # return
        return {"img":curr_image,"prev_img":last_image, "point_to_process":point_to_process.copy()}

    def dic_parameters(self):
        """returns the configuration parameters

        Returns:
            _type_: _description_
        """
        xmin = self.points_x[0]
        xmax = self.points_x[-1]
        xnum = len(self.points_x)
        ymin = self.points_y[0]
        ymax = self.points_y[-1]
        ynum = len(self.points_y)
        dic = {"xmin":xmin, "xmax":xmax,"xnum": int(xnum), "x_win_size_px":int(self.win_size_px[0]),
                "ymin":ymin, "ymax":ymax,"ynum": int(ynum), "y_win_size_px":int(self.win_size_px[1])}
        # self.result_file.write(str(xmin) + '\t' + str(xmax) + '\t' + str(int(xnum)) + '\t' + str(int(self.win_size_px[0])) + '\n')
        # self.result_file.write(str(ymin) + '\t' + str(ymax) + '\t' + str(int(ynum)) + '\t' + str(int(self.win_size_px[1])) + '\n')
        return dic

    def get_dic_gridsize(self)->GridSize:
        """returns the configuration parameters

        Returns:
            _type_: _description_
        """
        xmin = self.points_x[0]
        xmax = self.points_x[-1]
        xnum = len(self.points_x)
        ymin = self.points_y[0]
        ymax = self.points_y[-1]
        ynum = len(self.points_y)
        assert xmin < xmax, "xmin should be smaller than xmax"
        assert ymin < ymax, "ymin should be smaller than ymax"
        gridsize_obj = GridSize(
            xmin=xmin, xmax=xmax, xnum=int(xnum), win_size_x=int(self.win_size_px[0]),
            ymin=ymin, ymax=ymax, ynum=int(ynum), win_size_y=int(self.win_size_px[1]))
        return gridsize_obj

    def write_result(self, image, points):
        """
        Used by the class to write the data for a file.

        Args:
            image (str): The name of the image file.
            points (list of tuples()): List of point coordinates.
        """
        self.result_file.write(image + '\t')
        for p in points:
            self.result_file.write(str(p[0]) + ',' + str(p[1]) + '\t')
        self.result_file.write('\n')

    @property
    def last_image_array(self):
        return self._last_img

    @property
    def curr_image_array(self):
        return self._curr_img

    @property
    def ref_image_array(self):
        return self.img_ref

    @property
    def current_point_position(self):
        return self.points_in