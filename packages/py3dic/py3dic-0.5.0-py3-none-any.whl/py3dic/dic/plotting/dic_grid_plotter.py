import pathlib
import numpy as np
import logging
import cv2
import matplotlib.pyplot as plt
import pandas as pd
from matplotlib import pyplot as plt
import matplotlib.tri as tri

from ..core.dic_grid import DICGrid


class DICGridPlotter:
    """This class is an attempt to replace the draw_opencv_v2 function in pydicGrid.
    
    The class should only be used to plot a single grid at the time. 

    TODO: It could additionally be provided with the initial image. 

    #TODO It is not yet complete  
    
    Each grid needs to plot:
    - grid (to current image)
    - markers (to current image)
    - displacement (to ref image)
    - strain map (to ref / current image)

    The idea for this class is to have a factory of plots and the following steps are performed:
    - create a plotter object
    - once the plotter object is created
        - set the grid
        - set the image (ref or current)
        - plot the desired plot
    - rinse and repeat
    """

    
    DPI_DEFAULT:int = 100
    figsize:tuple=None

    def __init__(self):
        self._grid = None
        

        self.gr_color:tuple=(1.,1.,1.) # grid color
        self.t_color=(1.,1.,1.) # Text color
        self.p_color=(1.,1.,0.) # marker color
        self.l_color=(255, 120, 255)


    def set_grid(self, grid: DICGrid):
        """Set the DIC grid for the DIC_GridPlots object.

        Args:
            grid (DIC_Grid): The DIC grid to be set.

        Raises:
            ValueError: If the provided grid is not an instance of DIC_Grid.
        """
        assert isinstance(grid, DICGrid), ValueError('grid is not DIC_Grid')
        self._grid = grid
        #% TODO in create maps I am using a plt.imread. See if I can get rid of the cv2 library altogether from this class
        #e.g.:
        #  self._ref_image_array = plt.imread(_this_grid.reference_image)
        # as a reminder the default color code for cv2 is BGR, while for mpl is RGB
        self._ref_image_gray_array = cv2.imread(str(grid.reference_image), cv2.IMREAD_GRAYSCALE)
        self._current_image_gray_array = cv2.imread(str(grid.image), cv2.IMREAD_GRAYSCALE)
        
        # set the image shape (height, width)
        self._img_shape= self._ref_image_gray_array.shape
        self.figsize = (self._img_shape[1] / self.DPI_DEFAULT, self._img_shape[0] / self.DPI_DEFAULT)




    def _get_image_data(self, on_current_image:bool) -> np.ndarray:
        """returns the image data based on the plot_on_image argument.

        Args:
            plot_on_image (int): 0 for reference image, 1 for current image.

        Raises:
            ValueError: _description_

        Returns:
            np.ndarray: grayscale image data
        """
        if on_current_image not in [0,1]:
            raise ValueError('plot_on_image must be 0 (reference) or 1 (current)')
        if on_current_image == 0:
            image_data_gray = self._ref_image_gray_array
        elif on_current_image == 1:
            image_data_gray = self._current_image_gray_array
        return image_data_gray

    def plot_markers(self,
                    on_current_image: bool = True,
                    p_color: tuple[float] = (1, 1, 0),
                    text: str = None, 
                    t_color: tuple[float] = (1, 1, 1),
                    filename: str = None,
                    save_memory: bool = True):
        """Plots markers on the image
        
        Args:
            on_current_image (bool): Option for plotting on the reference (False) or the current image (True)
            p_color (tuple[float], optional): Marker color. Defaults to (1, 1, 0).
            text (str, optional): Annotation text.
            t_color (tuple[float], optional): Text color. Defaults to (1, 1, 1).
            filename (str, optional): Filename to save the plot.
            save_memory (bool, optional): Whether to close the figure to save memory. Defaults to True.
        """  
        image_data = self._get_image_data(on_current_image)
        frame_rgb = cv2.cvtColor(image_data, cv2.COLOR_GRAY2RGB)
        height, width, _ = frame_rgb.shape

        # Create a figure that matches the dimensions of the image exactly
        fig = plt.figure(figsize=(width / self.DPI_DEFAULT, height / self.DPI_DEFAULT), dpi=self.DPI_DEFAULT)
        ax = fig.add_axes([0, 0, 1, 1])  # Add axes that take up the whole figure
        ax.imshow(frame_rgb, aspect='auto')
        ax.axis('off')  # Hide the axes

        points_xy = self._grid.correlated_point

        if points_xy is not None:
            for pt_xy in points_xy:
                if not np.isnan(pt_xy[0]) and not np.isnan(pt_xy[1]):
                    x, y = int(pt_xy[0]), int(pt_xy[1])
                    circ = plt.Circle((x, y), 4, color=p_color)
                    ax.add_patch(circ)

        if text is not None:
            ax.text(50, 50, text, fontsize=12, color=t_color)

        if filename is not None:
            plt.savefig(filename, dpi=self.DPI_DEFAULT, bbox_inches='tight', pad_inches=0, transparent=True)
            if save_memory:
                plt.close(fig)
        else:
            plt.show()

    def plot_grid(self,
                  on_current_image:bool=False , 
                  text: str = None,
                  scale: float = 1,
                  gr_color: tuple = (1, 1, 1),
                  filename: str = None,
                  save_memory:bool=True,
                  *args, **kwargs):
        """Plot the original grid on top of the input image.

        Args:
            image (np.ndarray): The input image, normally an array (if not then if 0 then reference image, if 1 a current image). Defaults to None.
            text (str, optional): Additional annotation text to be displayed on the plot. Defaults to None.
            scale (float, optional): Scaling factor for the grid. Defaults to 1.
            gr_color (tuple, optional): Color of the grid lines. Defaults to (1, 1, 1).
            filename (str, optional): File path to save the plot. Defaults to None.
            *args, **kwargs: Additional arguments to be passed to the plot function.

        Returns:
            None
        """
        
        # image_data = self._validate_image(plot_on_image)
        image_data_gray = self._get_image_data(on_current_image)
        assert self._grid is not None, "Grid is not set. Please set the grid first."
        dic_grid = self._grid

        from ..core.grid_size import GridSize  
        if on_current_image:
            gr_x, gr_y = GridSize.flat_array_to_grid(
                    dic_grid.correlated_point, 
                    grid_shape=dic_grid.grid_size.shape, 
                    reverse_flag=True
                )
            dsp_x = dic_grid.disp_x
            dsp_y = dic_grid.disp_y
        else:
            gr_x = dic_grid.grid_x
            gr_y = dic_grid.grid_y
            dsp_x = dic_grid.disp_x
            dsp_y = dic_grid.disp_y
            
        fig, ax = plt.subplots(nrows=1, ncols=1, figsize=self.figsize, dpi=self.DPI_DEFAULT)
        
        ax.imshow(image_data_gray, cmap='gray', aspect='equal')
        ax.axis('off')
        for i in range(dic_grid.size_x):
            for j in range(dic_grid.size_y):
                if dic_grid.is_valid_number(i, j):
                    # dx_scaled = position - displacement * scale
                    x = int(gr_x[i, j]) - int(dsp_x[i, j] * scale)
                    y = int(gr_y[i, j]) - int(dsp_y[i, j] * scale)

                    if i < (dic_grid.size_x - 1) and dic_grid.is_valid_number(i + 1, j):
                        x1 = int(gr_x[i + 1, j]) - int(dsp_x[i + 1, j] * scale)
                        y1 = int(gr_y[i + 1, j]) - int(dsp_y[i + 1, j] * scale)
                        ax.plot([x, x1], [y, y1], color=gr_color, linewidth=2)

                    if j < (dic_grid.size_y - 1) and dic_grid.is_valid_number(i, j + 1):
                        x1 = int(gr_x[i, j + 1]) - int(dsp_x[i, j + 1] * scale)
                        y1 = int(gr_y[i, j + 1]) - int(dsp_y[i, j + 1] * scale)
                        ax.plot([x, x1], [y, y1], color=gr_color, linewidth=2)

        if text is not None:
            ax.text(50, 50, text, fontsize=12, color=(1, 1, 1))

        if filename is not None:
            plt.savefig(filename, dpi=self.DPI_DEFAULT, bbox_inches='tight', pad_inches=0)
            if save_memory:
                plt.close(fig)
        else:
            pass
            # plt.show()

    def quiver_plot(self, 
            on_current_image:bool=False, 
            scale:float=1, 
            color:tuple=(0,0,1), 
            text:str=None,
            filename:str=None, 
            save_memory:bool=True): 
        """Plot the displacement vectors on the image. (EXPERIMENTAL)

        """
        grid = self._grid
        image_gray = self._get_image_data(on_current_image)
        
        coordinates  = grid.reference_point 
        new_coordinates = grid.correlated_point 
        # new_coordinates[1][1]=2
        fig, axs = plt.subplots(2,1, figsize=(10,10))
        axs[0].imshow(image_gray, cmap='gray')
        axs[0].quiver(grid.grid_size.grid_x, grid.grid_size.grid_y, grid.disp_x, grid.disp_y)
        # axs[0].invert_yaxis() # reverse the y-axis only if imshow is not used.
        axs[1].imshow(image_gray, cmap='gray')
        axs[1].plot(coordinates[:,0], coordinates[:,1], 'o')
        axs[1].plot(new_coordinates[:,0], new_coordinates[:,1], 'o') 
        axs[1].set_aspect('equal')
        # axs[1].invert_yaxis()

        if text is not None:
            fig.suptitle(text)

        if filename is not None:
            plt.savefig(filename)
            if save_memory:
                plt.close(fig)
        else:
            pass
            # plt.show()

    def plot_displacement(self, 
                        on_current_image:bool=False,
                        scale:float=1,
                        p_color: tuple = (0, 1, 1), 
                        l_color: tuple = (1, 120/255,1 ), 
                        text: str = None,
                        filename: str = None,
                        figsize:tuple[int]=(10, 10),
                        save_memory:bool=True
                        ):
        """
        Plots the given image with markers at reference points and arrows indicating displacements.

        Parameters:
        

        Returns:
        None
        """
        image_data = self._get_image_data(False)
        reference_points = self._grid.reference_point
        correlated_points = self._grid.correlated_point


        fig, axs = plt.subplots(1,1,figsize=self.figsize, dpi=self.DPI_DEFAULT)
        axs.imshow(image_data,cmap='gray', aspect='equal')

        for ref, cor in zip(reference_points, correlated_points):
            # Plot the reference point
            axs.plot(ref[0], ref[1], 'o', color=p_color)  # 'ro' means red color, circle marker
            
            # Plot a line from the reference point to the correlated point
            axs.arrow(ref[0], ref[1], (cor[0]-ref[0])*scale, (cor[1]-ref[1])*scale, 
                      head_width=2, head_length=2, 
                      fc=l_color, ec=l_color
                    #   fc='blue', ec='blue'
                      )

        plt.axis('off')  # Hide axes
        # plt.show()

        if text is not None:
            axs.text(50, 50, text, fontsize=12, color=(1, 1, 1))

        if filename is not None:
            plt.savefig(filename, bbox_inches='tight', pad_inches=0)
            if save_memory:
                plt.close(fig)
        else:
            pass
            # plt.show()



    def plot_displacement_as_hsv(self, 
                on_current_image: bool = False, 
                text: str = None,
                filename: str = None,
                figsize:tuple[int]=(10, 10),
                save_memory:bool=True
                ):
        """
        Plots the given image using hsv color space and overlays markers using the same transformation.

        Parameters:
        on_current (bool): Flag to indicate whether to plot on the current image.
        scale (float): Scale factor for the arrows.
        p_color (tuple): Color for the markers.
        l_color (tuple): Color for the lines.
        figsize (tuple): Size of the figure.

        Returns:
        None
        """
        NO_STDS = 3
        image_data = self._get_image_data(on_current_image)
        
        reference_points = self._grid.reference_point
        correlated_points = self._grid.correlated_point
        if on_current_image:
            marker_points = correlated_points
        else:
            marker_points = reference_points

        # calculate displacement statistics (to determine color)
        disp = correlated_points - reference_points
        fx, fy = disp[:, 0], disp[:, 1]
        v_all = np.sqrt(fx * fx + fy * fy)
        v_mean = np.mean(v_all)
        v_std = np.std(v_all)
        v_max = np.mean(v_all) + NO_STDS  * np.std(v_all)
        no_points = len(v_all)
        
        fig, axs = plt.subplots(1, 1,figsize=self.figsize, dpi=self.DPI_DEFAULT)
        # Convert the grayscale image to RGB for plotting 
        rgb = cv2.cvtColor(image_data, cv2.COLOR_GRAY2BGR)
        axs.imshow(rgb, aspect='equal')
        plt.axis('off')  # Hide axes

        # Overlay markers using the same HSV transformation
        hsv_colors =[]
        marker_colors = []
        for i, val in enumerate(reference_points):
            disp = correlated_points[i] - val
            ang = np.arctan2(disp[1], disp[0]) + np.pi
            v = np.sqrt(disp[0] ** 2 + disp[1] ** 2)
            z_v = (v-v_mean)/v_std
            if z_v > NO_STDS :
                z_v = NO_STDS 
            if z_v <-NO_STDS :
                z_v = -NO_STDS 
            z_rng = z_v*127/NO_STDS +127
            # marker_color = (int(ang * (180 / np.pi / 2)), 
            #             255 if int((v / v_max) * 255.) > 255 else int((v / v_max) * 255.), 
            #                 255 if int((v / v_max) * 255.) > 255 else int((v / v_max) * 255.))
            marker_colors.append((int(ang * (180 / np.pi / 2)), 
                            z_rng, 
                            z_rng))

        # Convert HSV markers to RGB for plotting
        marker_colors = np.array(marker_colors)
        for k in range(no_points):
            # TODO When I have more time I should try to understand this 
            # hsv_c = np.array([[marker_colors[k,:].astype(np.uint8).tolist()]], dtype=np.uint8)
            hsv_c = np.array([[marker_colors[k,:]]], dtype=np.uint8)
            m_col = cv2.cvtColor(hsv_c , cv2.COLOR_HSV2RGB) / 255.0
            hsv_colors.append(m_col.flatten())
        
        axs.scatter(marker_points[:,0], marker_points[:,1], c=np.array(hsv_colors))
        
        fig.tight_layout()

        if text is not None:
            axs.text(50, 50, text, fontsize=12, color=(1, 1, 1))

        if filename is not None:
            plt.savefig(filename, bbox_inches='tight', pad_inches=0)
            if save_memory:
                plt.close(fig)
        else:
            pass
            # plt.show()

    def plot_strain_map(self,
            strain_dir:str='strain_xx',
            zlim = (-0.1, 0.1),
            on_current_image:bool = False,
            filename:pathlib.Path = None,            
            text:str = None,
            figsize:tuple[int]=(10, 10),
            save_memory:bool=True,
            *args, **kwargs
            ):
        """
        Create and save a strain map from this grid.
         
        """
        # gdc:GridDataContainer = data_analysis_res_container.grid_data_container
        # image_list:list = data_analysis_res_container.image_flist
        # csv_files:list = data_analysis_res_container.csv_flist
        assert strain_dir in ['strain_xx', 'strain_yy', 'strain_xy'], "Invalid strain direction. Choose from 'strain_xx', 'strain_yy', 'strain_xy'."
        
        
        _this_grid:DICGrid = self._grid
        # Extract initial and final coordinates, and strain values
        # initial_coordinates = analysis_results.grid_points_ref
        if on_current_image:
            vortices_xy = _this_grid.correlated_point
            curr_frame = cv2.cvtColor(self._current_image_gray_array, cv2.COLOR_BGR2RGB)
            # plt.imread(_this_grid.image)
        else:
            vortices_xy = _this_grid.reference_point
            # curr_frame = plt.imread(_this_grid.reference_image)
            curr_frame = cv2.cvtColor(self._ref_image_gray_array, cv2.COLOR_BGR2RGB)
        df_result_tmp = pd.DataFrame({
            "strain_xx": _this_grid.strain_xx.flatten(),
            "strain_yy": _this_grid.strain_yy.flatten(),
            "strain_xy": _this_grid.strain_xy.flatten()})
        strain_values = df_result_tmp[strain_dir].values

        # Create triangulation for plotting
        x_final, y_final = vortices_xy[:, 0], vortices_xy[:, 1]
        triangulation = tri.Triangulation(x_final, y_final)

        # TODO This could serves as the backbone of a fucntion that will return the proper aspect ratio based on the image size
        (_Ypx, _Xpx) = curr_frame.shape[:2]
        figsize=(8, 1.3*(8*(_Ypx/_Xpx)))
        # Create the figure =============================================
        fig, ax = plt.subplots(1,1,figsize =figsize)
        # ax = fig.add_subplot(111)
        ax.imshow(curr_frame, cmap=plt.cm.binary, aspect='equal')

        # Option 2: Create the tripcolor plot
        tpc = ax.tripcolor(triangulation, strain_values, shading='flat',
                        alpha=kwargs.get('alpha',0.6),
                        vmin=zlim[0], vmax=zlim[1])
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Add colorbar
        cbar = plt.colorbar(tpc, label=strain_dir, orientation='horizontal',
                shrink=0.8, aspect=40, pad=0.05)
        ax.set_xticks([])
        ax.set_yticks([])

        fig.tight_layout()

        if text is not None:
            ax.text(50, 50, text, fontsize=12, color=(1, 1, 1))

        if filename is not None:
            plt.savefig(filename)
            if save_memory:
                plt.close(fig)
        else:
            pass
            # plt.show()




