from .dic_viewer_model import DICViewerModel
from .support.options_window import OptionsWindow
import logging

logger = logging.getLogger(__name__)

class DICViewerController:
    def __init__(self, view, starting_dir=None):
        self.view = view
        self.model = DICViewerModel()
        self.starting_dir = starting_dir  # Store the starting directory


    def load_json(self, file_path):
        try:
            self.model.load_json(file_path)
            print(f"Loaded JSON: {file_path}")
            self.view.enable_controls()  # Enable controls after successful load
        except Exception as e:
            print(f"Failed to load JSON: {e}")

    def display_json_data(self):
        if self.model.dic_analysis:
            self.model.dic_analysis.print_analysis_data()

    def open_options(self):
        if self.model.dic_analysis:
            self.view.options_frame.deiconify()

    def dry_run(self):
        print("Dry run - Plotting parameters for enabled plots")
        for plot_type,is_enabled in self.model.selected_plots.items():
            if is_enabled:
                print(f"{plot_type:15s}: {self.model.plot_params.get(plot_type)}")

    def generate_images(self):
        print("Controller: Generating images")
        # this does not work because the names of the methods od not correspond to the keys in the selected_plots dictionary
        # if self.model.dic_analysis:
        #     for key, selected in self.model.selected_plots.items():
        #         if selected:
        #             plot_method = getattr(self.model.dic_analysis, f"plot_all_{key}", None) 
        #             if plot_method:
        #                 plot_method(**self.model.plot_params[key])
        
        if self.model.selected_plots.get('grid'):
            logging.debug("Controller: Plotting grids")
            self.model.dic_analysis.plot_all_grids(**self.model.plot_params["grid"])
        if self.model.selected_plots.get('marker'):
            logging.debug("Controller: Plotting markers")
            marker_dict = self.model.plot_params["marker"].copy()
            marker_dict.pop("scale")
            self.model.dic_analysis.plot_all_markers(**marker_dict)
        if self.model.selected_plots.get('displacement'):
            logging.debug("Controller: Plotting displacement")
            self.model.dic_analysis.plot_all_displ(**self.model.plot_params["displacement"])
        if self.model.selected_plots.get('displacement_hsv'):
            logging.debug("Controller: Plotting displacement hsv")
            hack_dict = self.model.plot_params["displacement_hsv"].copy()
            hack_dict.pop("scale")
            hack_dict.pop("p_color")
            self.model.dic_analysis.plot_all_displ_hsv(**hack_dict)
        if self.model.selected_plots.get('strainmap_xx'):
            logging.debug("Controller: Plotting strainmap_xx")
            self.model.dic_analysis.plot_all_strain_maps(strain_dir="strain_xx", **self.model.plot_params["strainmap_xx"])
        if self.model.selected_plots.get('strainmap_yy'):
            logging.debug("Controller: Plotting strainmap_yy")
            self.model.dic_analysis.plot_all_strain_maps(strain_dir="strain_yy", **self.model.plot_params["strainmap_yy"])
        if self.model.selected_plots.get('strainmap_xy'):
            logging.debug("Controller: Plotting strainmap_xy")
            self.model.dic_analysis.plot_all_strain_maps(strain_dir="strain_xy", **self.model.plot_params["strainmap_xy"])