import numpy as np
import pathlib
from .grid_size import GridSize

class DICResultFileContainer():
    """Class for storing and Grid data from DIC analysis results.

    """

    def __init__(self, xmin, xmax,xnum, x_window_size, 
                 ymin, ymax,ynum, y_window_size, 
                 imagelist, 
                 pointlist, 
                 data_source:str=None
                 ):
        """Initializes the AnalysisResults object.

        Requires:
            filename (str): The path to the result.dic file which contains the analysis
        """
        self.data_source = data_source
        self.xmin = xmin
        self.xmax = xmax
        self.xnum:int = xnum
        self.x_window_size = x_window_size
        self.ymin = ymin
        self.ymax = ymax
        self.ynum:int = ynum
        self.y_window_size = y_window_size
        self.data_source:str = None
    
        self.imagelist = imagelist
        self.pointlist = pointlist

        # TODO: replace attributs with properties that point ot GRIDSIZE
        self.gs:GridSize = GridSize(xmin=self.xmin, xmax=self.xmax,
                           xnum=self.xnum, win_size_x=self.x_window_size,
                           ymin=self.ymin, ymax=self.ymax,
                           ynum=self.ynum, win_size_y=self.y_window_size)       

    def get_winsize(self) ->tuple[int]:
        """Returns the size of the DIC window as a tuple (win_size_x, win_size_y).

        higher number means
         - wider area to check for tracking
         - greater confidence in the tracking
         - slower tracking (more computaional effort)
        """
        return (self.x_window_size, self.y_window_size)

    @property
    def grid_points_ref(self) -> np.ndarray:
        """Returns the reference grid points in the test imagelist.

        Returns:
            np.ndarray: The reference grid points (initial points).
        """
        return self.pointlist[0]

    def grid_point_xy_no(self, frame_id:int) -> np.ndarray:
        """Returns the position of the grid points in the test imagelist.

        args:
            frame_id (int): The frame id.
        Returns:
            np.ndarray: The [x,y] positions for grid with frameid .
        """
        return self.pointlist[frame_id]

    @property
    def no_frames(self) -> int:
        """Returns the number of frames in the test imagelist.

        this should be number of images 
        - the first frame is the reference frame

        Returns:
            int: The number of frames.
        """
        return len(self.imagelist)

    @classmethod
    def from_result_dic(cls, filename:str):
        """Initializes the AnalysisResults object.

        Requires:
            filename (str): The path to the result.dic file which contains the analysis
        """
        with open(filename, 'r', encoding='utf-8') as f:
            lines = f.readlines()

        # Parse grid dimensions and window sizes
        (xmin, xmax, xnum, x_window_size) = [int(float(x)) for x in lines[0].split()]
        (ymin, ymax, ynum, y_window_size) = [int(float(x)) for x in lines[1].split()]
        # self._gs:GridSize = GridSize(xmin=self.xmin, xmax=self.xmax, 
        #                     xnum = self.xnum, win_size_x=self.x_window_size,
        #                     ymin=self.ymin, ymax=self.ymax, 
        #                     ynum = self.ynum, win_size_y=self.y_window_size)    
        # grid_size = GridSize(xmin=xmin, xmax=xmax, 
        #                     xnum = xnum, win_size_x=x_window_size,
        #                     ymin=ymin, ymax=ymax, 
        #                     ynum = ynum, win_size_y=y_window_size)    
        # Parse image and point data
        imagelist, pointlist = cls._parse_displ_data(lines)
        return cls(xmin, xmax, xnum, x_window_size, ymin, ymax, ynum, y_window_size, imagelist, pointlist, filename)


    @classmethod
    def from_lines(cls, lines:str):
        """Initializes the AnalysisResults object.

        Requires:
            string (str): The string containing the analysis results
        """
        # lines = lines.split('\n')
        # Parse grid dimensions and window sizes
        (xmin, xmax, xnum, x_window_size) = [int(float(x)) for x in lines[0].split()]
        (ymin, ymax, ynum, y_window_size) = [int(float(x)) for x in lines[1].split()]
        # self._gs:GridSize = GridSize(xmin=self.xmin, xmax=self.xmax, 
        #                     xnum = self.xnum, win_size_x=self.x_window_size,
        #                     ymin=self.ymin, ymax=self.ymax, 
        #                     ynum = self.ynum, win_size_y=self.y_window_size)    
        # grid_size = GridSize(xmin=xmin, xmax=xmax, 
        #                     xnum = xnum, win_size_x=x_window_size,
        #                     ymin=ymin, ymax=ymax, 
        #                     ynum = ynum, win_size_y=y_window_size)    
        # Parse image and point data
        imagelist, pointlist = cls._parse_displ_data(lines)

        return cls(xmin, xmax, xnum, x_window_size, ymin, ymax, ynum, y_window_size, imagelist, pointlist, data_source="string lines")

    @classmethod
    def _parse_displ_data(cls, lines):
        imagelist = []
        pointlist = []
        for line in lines[2:-1]:
            val = line.split('\t')
            if len(val) > 2:
                imagelist.append(val[0])
                points = [np.array([float(x) for x in pair.split(',')], dtype=np.float32) for pair in val[1:-1]]
                pointlist.append(np.array(points))
        return imagelist,pointlist