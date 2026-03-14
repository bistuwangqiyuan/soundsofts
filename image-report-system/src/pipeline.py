"""Full analysis pipeline orchestrator."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path

import cv2
import numpy as np

from .image_processing.preprocessor import preprocess_cscan
from .roi_detection.roi_generator import ROI, detect_rois
from .roi_detection.weld_filter import detect_weld_region
from .defect_analysis.segmenter import segment_defects
from .defect_analysis.connected_component import ComponentInfo, analyze_components
from .defect_analysis.geometry import GeometricAttributes, compute_geometry
from .defect_analysis.classifier import (
    DefectClassification, DefectType, SeverityLevel, classify_defect,
)
from .defect_analysis.confidence_filter import (
    FilteredDefect, filter_by_confidence, merge_nearby_fragments,
)
from .defect_analysis.feature_extractor import color_histogram, gabor_features
from .multimodal_fusion.fusion import FusionResult, fuse_results
from .multimodal_fusion.rule_engine import RuleEngine


@dataclass
class DetectedDefect:
    """Rich per-defect record used throughout the system."""
    defect_id: int
    defect_type: DefectType
    severity: SeverityLevel
    confidence: float
    area_px: int
    centroid: tuple[float, float]
    bbox: tuple[int, int, int, int]
    aspect_ratio: float
    circularity: float
    mean_intensity: float = 0.0


@dataclass
class PipelineConfig:
    """Tunable parameters exposed to the GUI."""
    target_size: tuple[int, int] = (384, 768)
    seg_block_size: int = 51
    seg_c_offset: int = 15
    seg_morph_kernel: int = 5
    min_defect_area: int = 30
    confidence_threshold: float = 0.5
    merge_distance: float = 20.0
    fusion_visual_weight: float = 0.4
    fusion_acoustic_weight: float = 0.3
    fusion_rule_weight: float = 0.3


@dataclass
class AnalysisResult:
    """Complete output of the analysis pipeline."""
    original_image: np.ndarray
    preprocessed_image: np.ndarray
    defect_mask: np.ndarray
    rois: list[ROI]
    weld_region: tuple[int, int] | None
    defects: list[DetectedDefect]
    defect_count: int
    defect_area_ratio: float
    total_area: int
    fusion_result: FusionResult
    feature_summary: dict = field(default_factory=dict)


class AnalysisPipeline:
    """Orchestrate the full C-scan analysis flow."""

    def __init__(self, config: PipelineConfig | None = None) -> None:
        self.config = config or PipelineConfig()
        self.rule_engine = RuleEngine()
        self._step_callback: callable | None = None

    def set_step_callback(self, fn: callable) -> None:
        """Register a function called with (step_name, progress_pct) during run."""
        self._step_callback = fn

    def _notify(self, step: str, pct: int) -> None:
        if self._step_callback:
            self._step_callback(step, pct)

    def run(self, image_path: str | Path) -> AnalysisResult:
        image_path = Path(image_path)
        if not image_path.exists():
            raise FileNotFoundError(f"Image not found: {image_path}")

        cfg = self.config

        # Step 1: preprocess
        self._notify("图像预处理", 10)
        original = cv2.imread(str(image_path))
        if original is None:
            raise FileNotFoundError(f"Cannot read image: {image_path}")
        preprocessed = preprocess_cscan(image_path, target_size=cfg.target_size)
        # Convert back to BGR for cv2 operations
        preprocessed_bgr = cv2.cvtColor(preprocessed, cv2.COLOR_RGB2BGR)

        # Step 2: ROI detection
        self._notify("ROI 检测", 20)
        rois = detect_rois(preprocessed_bgr)
        weld_region = detect_weld_region(preprocessed_bgr)

        # Step 3: segmentation
        self._notify("缺陷分割", 35)
        mask = segment_defects(
            preprocessed_bgr,
            block_size=cfg.seg_block_size,
            c_offset=cfg.seg_c_offset,
            morph_kernel=cfg.seg_morph_kernel,
            min_area=cfg.min_defect_area,
        )

        # Step 4: connected components
        self._notify("连通域分析", 50)
        components = analyze_components(mask, min_area=cfg.min_defect_area)

        # Step 5: geometry + classification for each component
        self._notify("缺陷分类", 60)
        gray = cv2.cvtColor(preprocessed_bgr, cv2.COLOR_BGR2GRAY)
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)

        raw_defects: list[tuple[DefectClassification, int, tuple[float, float]]] = []
        defect_records: list[DetectedDefect] = []

        for idx, contour in enumerate(contours):
            area = int(cv2.contourArea(contour))
            if area < cfg.min_defect_area:
                continue

            geo = compute_geometry(mask, contour)

            # Mean intensity inside the contour
            cnt_mask = np.zeros(gray.shape, dtype=np.uint8)
            cv2.drawContours(cnt_mask, [contour], -1, 255, -1)
            mean_val = float(cv2.mean(gray, mask=cnt_mask)[0])

            cls = classify_defect(geo, mean_intensity=mean_val)
            raw_defects.append((cls, geo.area_px, geo.centroid))

            defect_records.append(DetectedDefect(
                defect_id=idx + 1,
                defect_type=cls.defect_type,
                severity=cls.severity,
                confidence=cls.confidence,
                area_px=geo.area_px,
                centroid=geo.centroid,
                bbox=geo.bbox,
                aspect_ratio=geo.aspect_ratio,
                circularity=geo.circularity,
                mean_intensity=mean_val,
            ))

        # Step 6: confidence filtering + merge
        self._notify("置信度过滤", 75)
        filtered = filter_by_confidence(raw_defects, min_confidence=cfg.confidence_threshold)
        merged = merge_nearby_fragments(filtered, distance_threshold=cfg.merge_distance)

        # Keep only defect_records that passed filtering
        kept_centroids = {(round(m.centroid[0], 1), round(m.centroid[1], 1)) for m in merged}
        final_defects: list[DetectedDefect] = []
        for d in defect_records:
            c_key = (round(d.centroid[0], 1), round(d.centroid[1], 1))
            if c_key in kept_centroids or d.confidence >= cfg.confidence_threshold:
                final_defects.append(d)

        if not final_defects:
            final_defects = defect_records  # keep all if nothing passed

        # Re-number defect IDs
        for i, d in enumerate(final_defects):
            d.defect_id = i + 1

        # Step 7: compute metrics
        self._notify("融合决策", 85)
        h, w = preprocessed_bgr.shape[:2]
        total_area = h * w
        defect_pixels = int(np.sum(mask > 0))
        defect_area_ratio = defect_pixels / (total_area + 1e-8)

        # Feature summary
        feat_hist = color_histogram(preprocessed_bgr)
        feat_gabor = gabor_features(preprocessed_bgr)

        # Predicted force heuristic (when no RF model available)
        predicted_force = max(0.0, 100.0 - defect_area_ratio * 800.0)

        # Rule checks
        checks = self.rule_engine.run_all_checks(
            force=predicted_force,
            defect_area=defect_pixels,
            total_area=total_area,
            defects=final_defects,
        )

        # Visual confidence from segmentation
        visual_conf = 0.85 if len(contours) > 0 else 0.5

        # Fusion
        mask_float = (mask > 0).astype(np.float32)
        fusion = fuse_results(mask_float, visual_conf, predicted_force, checks)

        self._notify("分析完成", 100)

        return AnalysisResult(
            original_image=original,
            preprocessed_image=preprocessed,
            defect_mask=mask,
            rois=rois,
            weld_region=weld_region,
            defects=final_defects,
            defect_count=len(final_defects),
            defect_area_ratio=defect_area_ratio,
            total_area=total_area,
            fusion_result=fusion,
            feature_summary={
                "color_hist_dim": len(feat_hist),
                "gabor_dim": len(feat_gabor),
                "gabor_mean": float(np.mean(feat_gabor)),
            },
        )
