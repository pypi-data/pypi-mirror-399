from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, Iterable, List, Tuple

import numpy as np

from py3dic.dic import DICAnalysisResultContainer


@dataclass
class StrainComponentConfig:
    """Configuration for a single strain component (e.g. strain_xx)."""

    enabled: bool = True

    # Background selection
    # When only use_ref_background is True  -> reference image only
    # When only use_cur_background is True  -> current/deformed image only
    # When both are True                    -> generate both variants
    use_ref_background: bool = False
    use_cur_background: bool = True

    # Auto z-limit configuration (percentile-based)
    use_auto_zlim: bool = True
    lower_percentile: float = 2.0
    upper_percentile: float = 98.0

    # Manual override; used when use_auto_zlim is False
    zlim: Tuple[float, float] | None = None

    def resolved_zlim(self, auto_zlim: Tuple[float, float]) -> Tuple[float, float]:
        """
        Return the z-limits to use, combining auto/manual settings.
        
        If use_auto_zlim is True and zlim is set (from xlsx loading), use zlim.
        Otherwise, use the provided auto_zlim parameter or manual zlim if set.
        """
        if self.use_auto_zlim:
            # If zlim was pre-populated (e.g., from xlsx), use it
            if self.zlim is not None:
                return self.zlim
            # Otherwise fall back to the provided auto_zlim
            return auto_zlim
        # Manual mode: use manual zlim if set, otherwise use auto_zlim as fallback
        if self.zlim is not None:
            return self.zlim
        return auto_zlim


class StrainZLimitCalculator:
    """
    Utility to compute percentile-based z-limits for strain components.

    This class is deliberately independent of any GUI concerns. It relies on
    the public interface of DICAnalysisResultContainer only.
    """

    def __init__(self, analysis_json_fname: str) -> None:
        self.analysis_json_fname = analysis_json_fname

    def _collect_strain_values(
        self,
        component: str,
        frame_indices: Iterable[int],
    ) -> np.ndarray:
        """
        Collect strain values for a given component over selected frames.

        Args:
            component: One of 'strain_xx', 'strain_yy', 'strain_xy'.
            frame_indices: Iterable of 1-based frame indices.
        """
        if component not in {"strain_xx", "strain_yy", "strain_xy"}:
            raise ValueError(f"Invalid strain component '{component}'")

        values: List[float] = []

        for frame_id in frame_indices:
            container = DICAnalysisResultContainer(self.analysis_json_fname)
            grid = container.get_grid(frame_id)

            if component == "strain_xx":
                arr = grid.strain_xx
            elif component == "strain_yy":
                arr = grid.strain_yy
            else:
                arr = grid.strain_xy

            flat = np.asarray(arr).ravel()
            # Filter out NaNs if any
            flat = flat[~np.isnan(flat)]
            if flat.size:
                values.append(flat)

        if not values:
            return np.array([], dtype=float)

        return np.concatenate(values)

    def compute_percentile_limits(
        self,
        components: Iterable[str],
        frame_indices: Iterable[int],
        lower_percentile: float,
        upper_percentile: float,
    ) -> Dict[str, Tuple[float, float]]:
        """
        Compute percentile-based z-limits for each requested component.

        Args:
            components: Iterable of component names.
            frame_indices: 1-based frame indices to use.
            lower_percentile: Lower percentile (e.g. 2.0).
            upper_percentile: Upper percentile (e.g. 98.0).
        """
        result: Dict[str, Tuple[float, float]] = {}
        components = list(components)

        for comp in components:
            vals = self._collect_strain_values(comp, frame_indices)
            if vals.size == 0:
                # Fallback to symmetrical small range if no data
                result[comp] = (-0.1, 0.1)
                continue

            lo = float(np.percentile(vals, lower_percentile))
            hi = float(np.percentile(vals, upper_percentile))

            # Guard against degenerate ranges
            if lo == hi:
                eps = max(1e-6, abs(lo) * 0.05)
                lo -= eps
                hi += eps

            result[comp] = (lo, hi)

        return result



