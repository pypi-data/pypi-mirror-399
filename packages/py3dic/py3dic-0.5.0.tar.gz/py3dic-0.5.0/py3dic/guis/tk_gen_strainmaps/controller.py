from __future__ import annotations

from typing import Dict

from py3dic.common.constants import STRAIN_COMPONENTS
from .model import StrainGeneratorModel


class StrainGeneratorController:
    """
    Controller for the Tk strain map generator.

    Glues the Tk view to the model and the existing analysis / plotting
    utilities. The controller itself is intentionally lightweight.
    """

    def __init__(self, model: StrainGeneratorModel, view) -> None:
        self.model = model
        self.view = view

    # ----- Model lifecycle -------------------------------------------------
    def load_json(self, path: str) -> None:
        self.model.load_analysis(path)
        self.view.on_analysis_loaded()

    # ----- Configuration updates from view --------------------------------
    def set_cpus(self, cpus: int | None) -> None:
        self.model.cpus = cpus
        if self.model.analysis_json_path is not None:
            # Recreate the container with updated CPU setting
            self.model.load_analysis(self.model.analysis_json_path)

    def set_frame_pattern(self, pattern: str) -> None:
        self.model.frame_pattern = pattern

    def set_global_alpha(self, alpha: float) -> None:
        self.model.global_alpha = alpha

    def update_component_config(
        self,
        name: str,
        *,
        enabled: bool | None = None,
        use_ref_background: bool | None = None,
        use_cur_background: bool | None = None,
        use_auto_zlim: bool | None = None,
        lower_percentile: float | None = None,
        upper_percentile: float | None = None,
        manual_zlim: tuple[float, float] | None = None,
    ) -> None:
        if name not in self.model.components:
            raise KeyError(f"Unknown component '{name}'")
        cfg = self.model.components[name]

        if enabled is not None:
            cfg.enabled = enabled
        if use_ref_background is not None:
            cfg.use_ref_background = use_ref_background
        if use_cur_background is not None:
            cfg.use_cur_background = use_cur_background
        if use_auto_zlim is not None:
            cfg.use_auto_zlim = use_auto_zlim
        if lower_percentile is not None:
            cfg.lower_percentile = lower_percentile
        if upper_percentile is not None:
            cfg.upper_percentile = upper_percentile
        if manual_zlim is not None:
            cfg.zlim = manual_zlim

    # ----- Actions ---------------------------------------------------------
    def dry_run(self) -> Dict[str, dict]:
        """
        Return a summary of the configuration that would be used.
        Useful for debugging / logging.
        """
        frame_indices = []
        try:
            frame_indices = self.model.resolve_frame_indices()
        except Exception:
            # Let the caller decide how to surface the error
            pass

        return {
            "json": self.model.analysis_json_path,
            "cpus": self.model.cpus,
            "global_alpha": self.model.global_alpha,
            "frame_indices": frame_indices,
            "components": {
                name: vars(cfg) for name, cfg in self.model.components.items()
            },
        }

    def generate_images(self) -> None:
        """
        Generate strain map images using the existing multiprocessing worker.

        This method does not block the UI from updating per se (Tk side should
        call it from a button, potentially in a separate thread if needed).
        """
        container = self.model.container
        frame_indices = self.model.resolve_frame_indices()

        if not frame_indices:
            self.view.report_status("No frames selected for processing.")
            return

        # TODO: This is not correct. It scans all data indepenent of the frame subset. 
        auto_zlims = self.model.compute_auto_zlims()

        # Map component names to suffixes expected by the existing API
        component_suffix_map = {
            "strain_xx": "strain_xx",
            "strain_yy": "strain_yy",
            "strain_xy": "strain_xy",
        }
        for name in STRAIN_COMPONENTS:
            cfg = self.model.components[name]
            if not cfg.enabled:
                continue

            # Skip components that have no background selected
            if not (cfg.use_ref_background or cfg.use_cur_background):
                continue

            # Decide base z-limits: from auto computation (if enabled) or a
            # small default window, which will then be overridden by manual
            # values if provided.
            if cfg.use_auto_zlim:
                if name not in auto_zlims:
                    # Nothing to do for this component
                    continue
                base_zlim = auto_zlims[name]
            else:
                base_zlim = (-0.1, 0.1)

            zlim = cfg.resolved_zlim(base_zlim)

            # We do not change the internal implementation of
            # DICAnalysisResultContainer; instead we use its worker at a more
            # primitive level so that we can control the frame subset and,
            # additionally, the output naming/background variants.
            from py3dic.dic.viewer.analysis_viewer import analysis_worker  # type: ignore
            import multiprocessing
            from tqdm import tqdm

            # Process each background selection in its own pass so that, e.g.,
            # Ref images are fully generated before Deformed images.
            bg_configs = [
                ("Ref", cfg.use_ref_background, False, "ref"),
                ("Deformed", cfg.use_cur_background, True, "def"),
            ]

            for bg_label, use_bg, on_current_image, bg_suffix in bg_configs:
                if not use_bg:
                    continue

                tasks = []
                for zero_based_id in range(len(container.image_flist)):
                    frame_id = zero_based_id + 1
                    if frame_id not in frame_indices:
                        continue

                    # Use a simple numeric stem so the final filename is:
                    #   00005_strain_xx_ref.png
                    # or
                    #   00005_strain_xx_def.png
                    frame_tag = f"{frame_id:05d}"
                    img_fname_stem = frame_tag

                    # Filename suffix controls both directory name and final suffix:
                    #   proc_img/strain_xx_refs/00005_strain_xx_ref.png
                    #   proc_img/strain_xx_defs/00005_strain_xx_def.png
                    filename_suffix = f"{component_suffix_map[name]}_{bg_suffix}"

                    task_args = (
                        container.analysis_json,
                        zero_based_id,
                        img_fname_stem,
                        "plot_strain_map",
                        filename_suffix,
                        {
                            "strain_dir": name,
                            "zlim": zlim,
                            "on_current_image": on_current_image,
                            "alpha": self.model.global_alpha,
                        },
                    )
                    tasks.append(task_args)

                if not tasks:
                    continue

                cpus = container.COMPUTATION_CPUS
                if cpus is None or cpus <= 0:
                    cpus = multiprocessing.cpu_count()

                successful_jobs = 0
                total_jobs = len(tasks)

                self.view.report_status(
                    f"Processing {total_jobs} frames for {name} ({bg_label}) using {cpus} processes..."
                )

                try:
                    with multiprocessing.Pool(processes=cpus) as pool:
                        results_iterator = pool.imap_unordered(analysis_worker, tasks)
                        for result in tqdm(results_iterator, total=total_jobs):
                            successful_jobs += result
                    self.view.report_status(
                        f"{name} ({bg_label}): {successful_jobs}/{total_jobs} tasks succeeded."
                    )
                except Exception as exc:  # pragma: no cover - defensive
                    self.view.report_status(
                        f"Error while processing {name} ({bg_label}): {exc}"
                    )



