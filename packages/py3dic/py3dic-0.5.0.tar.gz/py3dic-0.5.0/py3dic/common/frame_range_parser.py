from __future__ import annotations

from dataclasses import dataclass
from typing import Generator, Iterable, List, Optional, Set


@dataclass
class FrameRangeParser:
    """
    Utility to parse human-friendly frame selection strings into indices.

    Syntax (1-based indices):
        - Special: "-1"            -> all frames 1..N (requires max_frames)
        - Single index: "5"
        - Range: "10-20"        -> 10, 11, ..., 20
        - Range with step: "1-10:2" -> 1, 3, 5, 7, 9
        - Comma-separated list: "1,2,5,10-20,30-50:2"

    Duplicates are removed and indices are sorted in ascending order.

    The parser is completely independent of Tk and any DIC-specific types so
    that it can be reused by other front-ends (CLI, Qt, etc.).
    """

    pattern: str

    def _parse_item(self, item: str, max_frames: Optional[int]) -> Iterable[int]:
        item = item.strip()
        if not item:
            return []

        # Special case: "-1" means "all available frames"
        if item == "-1":
            if max_frames is None:
                raise ValueError(
                    "Pattern '-1' requires max_frames to be provided to "
                    "FrameRangeParser.iter_indices() / to_list()."
                )
            return list(range(1, max_frames + 1))

        # Single index
        if "-" not in item:
            try:
                idx = int(item)
            except ValueError as exc:
                raise ValueError(f"Invalid frame index '{item}'") from exc
            if idx < 1:
                raise ValueError(f"Frame indices must be >= 1 (got {idx})")
            if max_frames is not None and idx > max_frames:
                # Silently ignore indices beyond available frames
                return []
            return [idx]

        # Range (with optional step): A-B or A-B:S
        range_part, *step_parts = item.split(":")
        try:
            start_str, end_str = range_part.split("-")
            start = int(start_str)
            end = int(end_str)
        except ValueError as exc:
            raise ValueError(f"Invalid frame range '{item}'") from exc

        if start < 1 or end < 1:
            raise ValueError(f"Frame ranges must be >= 1 (got {start}-{end})")

        step = 1
        if step_parts:
            try:
                step = int(step_parts[0])
            except ValueError as exc:
                raise ValueError(f"Invalid step in range '{item}'") from exc
            if step <= 0:
                raise ValueError(f"Step must be > 0 in range '{item}'")

        if start > end:
            # Swap to keep behaviour intuitive
            start, end = end, start

        result: List[int] = []
        current = start
        while current <= end:
            if max_frames is None or current <= max_frames:
                result.append(current)
            current += step
        return result

    def iter_indices(self, max_frames: Optional[int] = None) -> Generator[int, None, None]:
        """
        Lazily yield frame indices according to the pattern.

        Args:
            max_frames: Optional maximum number of frames available.
                If provided, indices > max_frames are silently skipped.
        """
        seen: Set[int] = set()
        for raw_item in self.pattern.split(","):
            for idx in self._parse_item(raw_item, max_frames=max_frames):
                if idx not in seen:
                    seen.add(idx)
                    yield idx

    def to_list(self, max_frames: Optional[int] = None) -> List[int]:
        """Return all parsed indices as a sorted list."""
        return sorted(self.iter_indices(max_frames=max_frames))



