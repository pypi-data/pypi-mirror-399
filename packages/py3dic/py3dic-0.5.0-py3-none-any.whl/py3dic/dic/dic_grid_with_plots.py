import pathlib
import cv2
import numpy as np
import pandas as pd 
from matplotlib import pyplot as plt

from .core.dic_grid import DICGrid
from ._obsolete.draw_opencv_v2 import draw_opencv_v2
from .plotting.dic2d_contour_plot import DIC2DContourInteractivePlot
from .plotting.dic_grid_plotter import DICGridPlotter

import logging

USE_GRID_PLOTTER = True
_dic_plotter = DICGridPlotter()

class DICGridWithPlots(DICGrid):
    #TODO refactor this to use DICGridPlotter class

    # def __init__(self, *args, **kwargs):
    #     """ init function that calls the parent class init function and initializes the plotter """
    #     super().__init__(*args, **kwargs)
    #     self.plotter = DICGridPlotter()
        


    def draw_marker_img(self, analysis_folder=None):
        if USE_GRID_PLOTTER:
            # example of how to use the plotter. 
            _dic_plotter.set_grid(self)
            name2 = self.prepare_saved_file(prefix='marker', extension='png', analysis_folder=analysis_folder)
            _dic_plotter.plot_markers(on_current_image=True, p_color=(1, 1, 0), text = None, t_color=(1, 1, 1), 
                                      filename=name2, save_memory=True)
        # else:
        else:
            # use cv2 (legacy code)
            name = self.prepare_saved_file(prefix='marker-cv', extension='png', analysis_folder=analysis_folder)
            draw_opencv_v2(self.image, point=self.correlated_point, l_color=(0, 0, 255), p_color=(255, 255, 0), filename=name, text=name)
        

    def draw_disp_img(self, scale, analysis_folder=None):
        # TODO: Refactor this to use the dic_grid_plotter
        name = self.prepare_saved_file('disp', 'png', analysis_folder=analysis_folder)
        draw_opencv_v2(self.reference_image, point=self.reference_point, pointf=self.correlated_point, l_color=(0, 0, 255), p_color=(255, 255, 0), scale=scale, filename=name, text=name)

    def draw_disp_hsv_img(self, analysis_folder=None, *args, **kwargs):
        name = self.prepare_saved_file('disp_hsv', 'png', analysis_folder=analysis_folder)
        img = self.reference_image
        if isinstance(img, str):
            img = cv2.imread(img, 0)

        disp = self.correlated_point - self.reference_point
        fx, fy = disp[:, 0], disp[:, 1]
        v_all = np.sqrt(fx * fx + fy * fy)
        v_max = np.mean(v_all) + 2. * np.std(v_all)

        rgb = cv2.cvtColor(img, cv2.COLOR_GRAY2BGR)
        hsv = cv2.cvtColor(rgb, cv2.COLOR_BGR2HSV)

        if v_max != 0.:
            for i, val in enumerate(self.reference_point):
                disp = self.correlated_point[i] - val
                ang = np.arctan2(disp[1], disp[0]) + np.pi
                v = np.sqrt(disp[0] ** 2 + disp[1] ** 2)
                pt_x = int(val[0])
                pt_y = int(val[1])

                hsv[pt_y, pt_x, 0] = int(ang * (180 / np.pi / 2))
                hsv[pt_y, pt_x, 1] = 255 if int((v / v_max) * 255.) > 255 else int((v / v_max) * 255.)
                hsv[pt_y, pt_x, 2] = 255 if int((v / v_max) * 255.) > 255 else int((v / v_max) * 255.)

        bgr = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)
        bgr = cv2.putText(bgr, name, (50, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 255), 4)

        if 'save_img' in kwargs:
            cv2.imwrite(name, bgr)
        if 'show_img' in kwargs:
            cv2.namedWindow('image', cv2.WINDOW_NORMAL)
            cv2.resizeWindow('image', bgr.shape[1], bgr.shape[0])
            cv2.imshow('image', bgr)
            cv2.waitKey(0)
            cv2.destroyAllWindows()

    def draw_grid_img(self, scale, analysis_folder=None):
        name = self.prepare_saved_file('grid', 'png', analysis_folder=analysis_folder)
        draw_opencv_v2(self.reference_image, grid=self, scale=scale, gr_color=(255, 255, 250), filename=name, text=name)

    def plot_field(self, field, title:str):
        image_ref = cv2.imread(self.image, 0)
        DIC2DContourInteractivePlot(image_ref, self, field, title)


    def create_strain_map(self,
            output_folder:pathlib.Path = None,
            strain_dir:str='strain_xx',
            zlim = (-0.1, 0.1),
            save_memory:bool=True,
            *args, **kwargs
            ):
        """
        Create and save a strain map from this grid.
         
        ORiginally this function was developed for the viewer, then moved to DICAnalysisResultContainer and finally moved here.
        

        Args:
            analysis_results (object): Object containing analysis results (like grid_points_ref and pointlist).
            image_list (list): List of image file paths.
            csv_files (list): List of CSV file paths containing strain data.
            output_folder (Path): output folder to save the strain map images.
            strain_dir (str):   strain direction/type. Default is 'strain_xx' (or strain_yy, strain_xy).
            zlim (tuple): Tuple containing the minimum and maximum values for the colorbar. Default is (-0.1, 0.1).
        """
        # gdc:GridDataContainer = data_analysis_res_container.grid_data_container
        # image_list:list = data_analysis_res_container.image_flist
        # csv_files:list = data_analysis_res_container.csv_flist
        assert strain_dir in ['strain_xx', 'strain_yy', 'strain_xy'], "Invalid strain direction. Choose from 'strain_xx', 'strain_yy', 'strain_xy'."
        assert output_folder is not None, "Output folder is not defined."
        
        _this_grid = self
        # Extract initial and final coordinates, and strain values
        # initial_coordinates = analysis_results.grid_points_ref
        final_coordinates = self._grid.correlated_point

        df_result_tmp = pd.DataFrame({
            "strain_xx": _this_grid.strain_xx.flatten(),
            "strain_yy": _this_grid.strain_yy.flatten(),
            "strain_xy": _this_grid.strain_xy.flatten()})
        strain_values = df_result_tmp[strain_dir].values

        # Create triangulation for plotting
        x_final, y_final = final_coordinates[:, 0], final_coordinates[:, 1]
        triangulation = tri.Triangulation(x_final, y_final)

        # Read the current frame image
        curr_frame = plt.imread(_this_grid.image)
        try:
            # get the shape of an RGB image
            (_Ypx, _Xpx, _COLS) = curr_frame.shape
        except ValueError:
            # get the shape of an Grayscale
            (_Ypx, _Xpx) = curr_frame.shape

        # Create the figure
        fig = plt.figure(figsize=(8, 2*(8*(_Ypx/_Xpx))))
        ax = fig.add_subplot(111)
        ax.imshow(curr_frame, cmap=plt.cm.binary, aspect='equal')

        # Option 2: Create the tripcolor plot
        tpc = ax.tripcolor(triangulation, strain_values, shading='flat',
                        alpha=kwargs.get('alpha',0.6),
                        vmin=zlim[0], vmax=zlim[1])
        ax.set_xlabel('')
        ax.set_ylabel('')

        # Add colorbar
        cbar = plt.colorbar(tpc, label='Strain', orientation='horizontal',
                shrink=0.8, aspect=40, pad=0.05)
        ax.set_xticks([])
        ax.set_yticks([])

        # Save the figure
        output_path = output_folder /f"{strain_dir}" /f"{_this_grid.image.stem}-{strain_dir}.png"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        logging.info("Saving strain map to %s",str(output_path))
        fig.savefig(output_path, dpi=300, bbox_inches='tight')
        if save_memory:
            plt.close(fig)  # Close the figure to free memory