from __future__ import annotations

import logging
import math
import pathlib
import re
from dataclasses import dataclass
from typing import Optional, Tuple

import pandas as pd


def _pretty_round(value: float) -> float:
    """
    Round a value to a "nice" number similar to MATLAB's pretty function.
    
    This rounds to nice increments based on the magnitude of the value.
    For example: 0.123 -> 0.12, 1.234 -> 1.2, 12.34 -> 12
    
    Args:
        value: The value to round
    
    Returns:
        Rounded value
    """
    if value == 0:
        return 0.0
    
    magnitude = abs(value)
    
    # Determine nice step size based on magnitude
    if magnitude >= 1:
        # For values >= 1, find order of magnitude
        order = 10 ** int(math.log10(magnitude))
        # Use steps like 1, 2, 5, 10, 20, 50, 100, etc.
        if magnitude >= 10 * order:
            step = 10 * order / 2
        elif magnitude >= 5 * order:
            step = 5 * order / 2
        else:
            step = order / 2
    else:
        # For values < 1, use steps like 0.1, 0.2, 0.5, 0.01, 0.02, 0.05, etc.
        if magnitude >= 0.1:
            step = 0.05
        elif magnitude >= 0.01:
            step = 0.005
        elif magnitude >= 0.001:
            step = 0.0005
        else:
            step = 0.00005
    
    # Round to nearest step
    rounded = round(value / step) * step
    
    return float(rounded)


@dataclass
class XlsxZLimitLoader:
    """
    Loads z-limits from xlsx file and provides methods to retrieve padded limits.
    
    The xlsx file is expected to be in the same folder as the analysis JSON file
    and follow the pattern "dic_vs_img<float number>.xlsx". It contains columns
    e_xx, e_yy, e_xy with strain values.
    """
    
    xlsx_path: pathlib.Path
    df: pd.DataFrame
    _e_xx_lims: Optional[Tuple[float, float]] = None
    _e_yy_lims: Optional[Tuple[float, float]] = None
    _e_xy_lims: Optional[Tuple[float, float]] = None
    
    @classmethod
    def from_json_path(cls, json_path: str | pathlib.Path) -> XlsxZLimitLoader:
        """
        Create a loader by finding the xlsx file associated with the given JSON path.
        
        Args:
            json_path: Path to the analysis JSON file
            
        Returns:
            XlsxZLimitLoader instance
            
        Raises:
            FileNotFoundError: If no matching xlsx file is found
        """
        json_path = pathlib.Path(json_path)
        json_folder = json_path.parent
        
        # Pattern: dic_vs_img<any value>.xlsx (accepts negative numbers, strings, etc.)
        # Examples: dic_vs_img4.0.xlsx, dic_vs_img-4.0s.xlsx, dic_vs_img123.xlsx
        pattern = re.compile(r"dic_vs_img_.*\.xlsx$", re.IGNORECASE)
        xlsx_files = [f for f in json_folder.glob("dic_vs_img_*.xlsx") if pattern.match(f.name)]
        
        if not xlsx_files:
            raise FileNotFoundError(
                f"No xlsx file matching pattern 'dic_vs_img*.xlsx' found in {json_folder}"
            )
        
        if len(xlsx_files) > 1:
            logging.warning(
                f"Multiple xlsx files found matching pattern, using first: {xlsx_files[0]}"
            )
        
        xlsx_path = xlsx_files[0]
        logging.info(f"Loading xlsx file: {xlsx_path}")
        
        # Load the xlsx file
        # The first column (unnamed) is elapsed time, columns e_xx, e_yy, e_xy contain strain values
        df = pd.read_excel(xlsx_path)
        logging.info(f"Loaded xlsx file successfully: {xlsx_path}")
        logging.debug(f"Xlsx file shape: {df.shape}, columns: {list(df.columns)}")
        
        return cls(xlsx_path=xlsx_path, df=df)
    
    def _compute_lims(self, column_name: str) -> Tuple[float, float]:
        """
        Compute padded limits for a given column.
        
        Args:
            column_name: Name of the column (e.g., 'e_xx', 'e_yy', 'e_xy')
            
        Returns:
            Tuple of (zmin, zmax) with 10% padding and pretty rounding
        """
        if column_name not in self.df.columns:
            logging.warning(f"Column '{column_name}' not found in xlsx file, using default range")
            return (-0.1, 0.1)
        
        # Extract values and remove NaN
        values = self.df[column_name].dropna()
        
        if len(values) == 0:
            logging.warning(f"No valid values found for '{column_name}', using default range")
            return (-0.1, 0.1)
        
        # Get min and max
        min_val = float(values.min())
        max_val = float(values.max())
        
        # Pad by 10% on each side
        range_val = max_val - min_val
        padding = range_val * 0.1
        
        # Handle case where min == max
        if range_val == 0:
            padding = max(abs(min_val) * 0.1, 0.01) if min_val != 0 else 0.01
        
        zmin = min_val - padding
        zmax = max_val + padding
        
        # Apply pretty rounding
        zmin = _pretty_round(zmin)
        zmax = _pretty_round(zmax)
        
        return (zmin, zmax)
    
    def get_e_xx_lims(self) -> Tuple[float, float]:
        """Get padded z-limits for e_xx component."""
        if self._e_xx_lims is None:
            self._e_xx_lims = self._compute_lims("e_xx")
        return self._e_xx_lims
    
    def get_e_yy_lims(self) -> Tuple[float, float]:
        """Get padded z-limits for e_yy component."""
        if self._e_yy_lims is None:
            self._e_yy_lims = self._compute_lims("e_yy")
        return self._e_yy_lims
    
    def get_e_xy_lims(self) -> Tuple[float, float]:
        """Get padded z-limits for e_xy component."""
        if self._e_xy_lims is None:
            self._e_xy_lims = self._compute_lims("e_xy")
        return self._e_xy_lims
    
    def get_lims_for_component(self, component_name: str) -> Tuple[float, float]:
        """
        Get padded z-limits for a component by name.
        
        Args:
            component_name: One of 'strain_xx', 'strain_yy', 'strain_xy'
            
        Returns:
            Tuple of (zmin, zmax)
        """
        component_to_method = {
            "strain_xx": self.get_e_xx_lims,
            "strain_yy": self.get_e_yy_lims,
            "strain_xy": self.get_e_xy_lims,
        }
        
        method = component_to_method.get(component_name)
        if method is None:
            raise ValueError(f"Unknown component '{component_name}'")
        
        return method()

