from ...dic import DICAnalysisResultContainer

class DICViewerModel:
    selected_plots = {}
    plot_params = {}
    def __init__(self, json_file_path=None):
        self.dic_analysis = None
        if json_file_path:
            self.load_json(json_file_path)
        self.selected_plots = {
            "grid": False,
            "marker": False,
            "displacement": False,
            "displacement_hsv": False,
            "strainmap_xx": False,
            "strainmap_yy": False,
            "strainmap_xy": False
        }
        self.plot_params = {
            "grid": {},
            "marker": {},
            "displacement": {},
            "displacement_hsv": {},
            "strainmap_xx": {},
            "strainmap_yy": {},
            "strainmap_xy": {}
        }

    def load_json(self, file_path):
        self.dic_analysis = DICAnalysisResultContainer(file_path)

    def update_plot_params(self, plot_type, params):
        if plot_type in self.plot_params:
            self.plot_params[plot_type] = params
