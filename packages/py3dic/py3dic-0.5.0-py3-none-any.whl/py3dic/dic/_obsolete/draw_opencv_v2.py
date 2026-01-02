import numpy as np
import cv2 

__ADD_IMAGE_NAME__ = False


def draw_opencv_v2(
    image, 
    text: str = None,
    point=None, # used in marker plotting
    pointf=None,
    grid: 'DIC_Grid' = None,
    scale: float = 1,
    p_color: tuple = (0, 255, 255),
    l_color: tuple = (255, 120, 255),
    gr_color: tuple = (255, 255, 255),
    filename=None,
    *args, **kwargs):
    """A generic function used to draw opencv image. Depending on the arguments it plots 
    
    - markers
    - grid
    - lines
    - displacement

    Args:
        image (str|np.ndarray): _description_
        text (str, optional): _description_. Defaults to None.
        point (_type_, optional): arg must be an array of (x,y) point. Defaults to None.
        pointf (_type_, optional): to draw lines between point and pointf, pointf  (must be an array of same lenght than the point array). Defaults to None.
        scale (int, optional): scaling parameter. Defaults to 1.
        p_color (tuple, optional): arg to choose the color of point in (r,g,b) format. Defaults to (0, 255, 255).
        l_color (tuple, optional): color of lines in (RGB). Defaults to (255, 120, 255).
        gr_color (tuple, optional): color of grid in (RGB). Defaults to (255, 255, 255).
        filename (_type_, optional): _description_. Defaults to None.
    """
    if isinstance(image, str):
        image = cv2.imread(image, 0)

    if text is not None and __ADD_IMAGE_NAME__:
        # text = pathlib.Path(text).name # consider this alternatively needs testing.
        image = cv2.putText(image, text, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)

    frame = cv2.cvtColor(image, cv2.COLOR_GRAY2BGR)

    if point is not None:
        for pt in point:
            if not np.isnan(pt[0]) and not np.isnan(pt[1]):
                x, y = int(pt[0]), int(pt[1])
                frame = cv2.circle(frame, (x, y), 4, p_color, -1)

    if pointf is not None and point is not None:
        assert len(point) == len(pointf), 'size between initial  point and final point does not match.'
        for pt0, pt1 in zip(point, pointf):
            if not np.isnan(pt0[0]) and not np.isnan(pt0[1]) and not np.isnan(pt1[0]) and not np.isnan(pt1[1]):
                disp_x, disp_y = (pt1[0] - pt0[0]) * scale, (pt1[1] - pt0[1]) * scale
                frame = cv2.line(frame, (int(pt0[0]), int(pt0[1])), (int(pt0[0] + disp_x), int(pt0[1] + disp_y)), l_color, 2)

    if grid is not None:
        # this requires a grid object. 
        dic_grid = grid
        # HACK: Deferred import to avoid circular import (replace this function)
        from ..core.dic_grid import DICGrid
        from .._obsolete._old_dic_grid import OLD_grid
        
        assert isinstance(dic_grid, DICGrid) or isinstance(dic_grid, OLD_grid), "grid should be DIC_Grid"
        for i in range(dic_grid.size_x):
            for j in range(dic_grid.size_y):
                if dic_grid.is_valid_number(i, j):
                    x = int(dic_grid.grid_x[i, j]) - int(dic_grid.disp_x[i, j] * scale)
                    y = int(dic_grid.grid_y[i, j]) - int(dic_grid.disp_y[i, j] * scale)

                    if i < (dic_grid.size_x - 1) and dic_grid.is_valid_number(i + 1, j):
                        x1 = int(dic_grid.grid_x[i + 1, j]) - int(dic_grid.disp_x[i + 1, j] * scale)
                        y1 = int(dic_grid.grid_y[i + 1, j]) - int(dic_grid.disp_y[i + 1, j] * scale)
                        frame = cv2.line(frame, (x, y), (x1, y1), gr_color, 2)

                    if j < (dic_grid.size_y - 1) and dic_grid.is_valid_number(i, j + 1):
                        x1 = int(dic_grid.grid_x[i, j + 1]) - int(dic_grid.disp_x[i, j + 1] * scale)
                        y1 = int(dic_grid.grid_y[i, j + 1]) - int(dic_grid.disp_y[i, j + 1] * scale)
                        frame = cv2.line(frame, (x, y), (x1, y1), gr_color, 4)

    if filename is not None:
        cv2.imwrite(filename, frame)
        return

    cv2.namedWindow('image', cv2.WINDOW_NORMAL)
    cv2.resizeWindow('image', frame.shape[1], frame.shape[0])
    cv2.imshow('image', frame)
    cv2.waitKey(0)
    cv2.destroyAllWindows()