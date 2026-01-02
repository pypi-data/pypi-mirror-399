from __future__ import annotations

import logging
from dataclasses import dataclass, field
from typing import Dict, List, Optional

from py3dic.common.constants import STRAIN_COMPONENTS 

from py3dic.dic import DICAnalysisResultContainer

from py3dic.common.frame_range_parser import FrameRangeParser
from .core.strain_config import StrainComponentConfig
from .core.xlsx_zlim_loader import XlsxZLimitLoader


@dataclass
class StrainGeneratorModel:
    """
    Model for the Tk strain map generator.

    Holds configuration and wraps the underlying analysis container. It does
    not depend on any Tk types.
    """

    analysis_json_path: Optional[str] = None
    cpus: Optional[int] = None
    frame_pattern: str = "-1"
    global_alpha: float = 0.3

    # create a dictionary of strain component configurations strain_xx, strain_yy, strain_xy
    components: Dict[str, StrainComponentConfig] = field(
        default_factory=lambda: {
            name: StrainComponentConfig() for name in STRAIN_COMPONENTS
        }
    )

    _container: Optional[DICAnalysisResultContainer] = field(default=None, init=False, repr=False)
    _zlim_loader: Optional[XlsxZLimitLoader] = field(default=None, init=False, repr=False)

    def load_analysis(self, json_path: str) -> None:
        self.analysis_json_path = json_path
        self._container = DICAnalysisResultContainer(json_path, cpus=self.cpus)
        
        # Load xlsx file and populate zlims for components
        logging.debug("Starting to load xlsx z-limits during analysis load")
        try:
            logging.debug(f"Attempting to find and load xlsx file for JSON: {json_path}")
            self._zlim_loader = XlsxZLimitLoader.from_json_path(json_path)
            logging.debug("Xlsx file loaded successfully, computing z-limits for components")
            
            # Map component names to loader methods
            component_to_lims = {
                "strain_xx": self._zlim_loader.get_e_xx_lims,
                "strain_yy": self._zlim_loader.get_e_yy_lims,
                "strain_xy": self._zlim_loader.get_e_xy_lims,
            }
            
            # Populate zlims for all components (they will be used when use_auto_zlim is True)
            for comp_name, get_lims in component_to_lims.items():
                if comp_name in self.components:
                    zlims = get_lims()
                    self.components[comp_name].zlim = zlims
                    logging.debug(f"Initialized zlim for {comp_name}: zmin={zlims[0]:.6f}, zmax={zlims[1]:.6f}")
            
            logging.debug("Finished loading xlsx z-limits and initializing component zlims")
        except FileNotFoundError as e:
            logging.warning(f"Could not load xlsx z-limits: {e}")
            self._zlim_loader = None
        except Exception as e:
            logging.error(f"Error loading xlsx z-limits: {e}", exc_info=True)
            self._zlim_loader = None

    @property
    def container(self) -> DICAnalysisResultContainer:
        if self._container is None:
            raise RuntimeError("Analysis JSON not loaded")
        return self._container

    @property
    def num_frames(self) -> int:
        return len(self.container.image_flist)

    def resolve_frame_indices(self) -> List[int]:
        """returns a list of frame indices based on the user input and parsed by the FrameRangeParser 
        """
        parser = FrameRangeParser(self.frame_pattern)
        return parser.to_list(max_frames=self.num_frames)

    def compute_auto_zlims(self) -> Dict[str, tuple[float, float]]:
        """
        Compute z-limits for components that request it using the pre-loaded xlsx data.
        
        The z-limits are already computed and stored in the component configs during
        load_analysis. This method simply retrieves them for enabled components.
        """
        logging.debug("Starting compute_auto_zlims")
        
        if self.analysis_json_path is None:
            raise RuntimeError("Analysis JSON not loaded")

        if self._zlim_loader is None:
            logging.warning("No zlim loader available, returning empty dict")
            return {}

        auto_components = [
            name
            for name, cfg in self.components.items()
            if cfg.enabled and cfg.use_auto_zlim
        ]

        if not auto_components:
            logging.debug("No components with auto_zlim enabled, returning empty dict")
            return {}

        result: Dict[str, tuple[float, float]] = {}
        
        for comp_name in auto_components:
            cfg = self.components[comp_name]
            if cfg.zlim is not None:
                result[comp_name] = cfg.zlim
                logging.debug(f"Component '{comp_name}': zlim = {cfg.zlim}")
            else:
                logging.warning(f"No zlim available for component '{comp_name}'")
        
        logging.debug("Finished compute_auto_zlims")
        return result



