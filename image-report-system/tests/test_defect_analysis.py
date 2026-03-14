"""Tests for defect_analysis modules."""

import numpy as np
import pytest


def _make_mask_with_blob(h=100, w=100, cx=50, cy=50, r=10):
    """Create a binary mask with a circular blob."""
    mask = np.zeros((h, w), dtype=np.uint8)
    yy, xx = np.ogrid[:h, :w]
    mask[((yy - cy) ** 2 + (xx - cx) ** 2) <= r ** 2] = 255
    return mask


# --- segmenter ---

class TestSegmenter:
    def test_segment_uniform_image(self):
        from src.defect_analysis.segmenter import segment_defects
        img = np.full((100, 100, 3), 128, dtype=np.uint8)
        mask = segment_defects(img)
        assert mask.shape == (100, 100)

    def test_segment_with_defect(self):
        from src.defect_analysis.segmenter import segment_defects
        img = np.full((100, 100, 3), 200, dtype=np.uint8)
        img[30:50, 30:50] = 30  # dark region = defect
        mask = segment_defects(img, min_area=10)
        assert mask.dtype == np.uint8

    def test_segment_grayscale(self):
        from src.defect_analysis.segmenter import segment_defects
        img = np.full((100, 100), 128, dtype=np.uint8)
        mask = segment_defects(img)
        assert mask.shape == (100, 100)


# --- connected_component ---

class TestConnectedComponent:
    def test_no_components(self):
        from src.defect_analysis.connected_component import analyze_components
        mask = np.zeros((100, 100), dtype=np.uint8)
        components = analyze_components(mask)
        assert len(components) == 0

    def test_single_blob(self):
        from src.defect_analysis.connected_component import analyze_components
        mask = _make_mask_with_blob(100, 100, 50, 50, 15)
        components = analyze_components(mask, min_area=10)
        assert len(components) == 1
        assert components[0].area > 100

    def test_min_area_filter(self):
        from src.defect_analysis.connected_component import analyze_components
        mask = _make_mask_with_blob(100, 100, 50, 50, 3)  # tiny
        components = analyze_components(mask, min_area=100)
        assert len(components) == 0


# --- geometry ---

class TestGeometry:
    def test_compute_geometry_circle(self):
        import cv2
        from src.defect_analysis.geometry import compute_geometry
        mask = _make_mask_with_blob()
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        geo = compute_geometry(mask, contours[0])
        assert geo.area_px > 0
        assert geo.circularity > 0.5  # circle should be ~1.0
        assert geo.equivalent_diameter > 0

    def test_compute_geometry_rectangle(self):
        import cv2
        from src.defect_analysis.geometry import compute_geometry
        mask = np.zeros((100, 100), dtype=np.uint8)
        mask[20:30, 10:90] = 255  # wide thin rectangle
        contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
        geo = compute_geometry(mask, contours[0])
        assert geo.aspect_ratio > 2.0  # wide rectangle


# --- classifier ---

class TestClassifier:
    def test_classify_bubble(self):
        from src.defect_analysis.classifier import classify_defect, DefectType
        from src.defect_analysis.geometry import GeometricAttributes
        attrs = GeometricAttributes(
            area_px=200, perimeter_px=50, centroid=(50, 50), bbox=(40, 40, 20, 20),
            aspect_ratio=1.1, orientation_deg=0, circularity=0.85, equivalent_diameter=16,
        )
        cls = classify_defect(attrs, mean_intensity=128)
        assert cls.defect_type == DefectType.BUBBLE

    def test_classify_disbond(self):
        from src.defect_analysis.classifier import classify_defect, DefectType
        from src.defect_analysis.geometry import GeometricAttributes
        attrs = GeometricAttributes(
            area_px=1000, perimeter_px=200, centroid=(50, 50), bbox=(10, 40, 80, 20),
            aspect_ratio=4.0, orientation_deg=0, circularity=0.3, equivalent_diameter=36,
        )
        cls = classify_defect(attrs)
        assert cls.defect_type == DefectType.DISBOND

    def test_classify_weak_bond(self):
        from src.defect_analysis.classifier import classify_defect, DefectType
        from src.defect_analysis.geometry import GeometricAttributes
        attrs = GeometricAttributes(
            area_px=800, perimeter_px=120, centroid=(50, 50), bbox=(30, 30, 40, 40),
            aspect_ratio=1.5, orientation_deg=0, circularity=0.5, equivalent_diameter=32,
        )
        cls = classify_defect(attrs, mean_intensity=50)
        assert cls.defect_type == DefectType.WEAK_BOND

    def test_severity_severe(self):
        from src.defect_analysis.classifier import classify_defect, SeverityLevel
        from src.defect_analysis.geometry import GeometricAttributes
        attrs = GeometricAttributes(
            area_px=3000, perimeter_px=300, centroid=(50, 50), bbox=(10, 10, 80, 80),
            aspect_ratio=1.2, orientation_deg=0, circularity=0.5, equivalent_diameter=62,
        )
        cls = classify_defect(attrs)
        assert cls.severity == SeverityLevel.SEVERE


# --- confidence_filter ---

class TestConfidenceFilter:
    def test_filter_removes_low_confidence(self):
        from src.defect_analysis.confidence_filter import filter_by_confidence
        from src.defect_analysis.classifier import DefectClassification, DefectType, SeverityLevel
        defects = [
            (DefectClassification(DefectType.BUBBLE, SeverityLevel.MINOR, 0.3), 100, (50.0, 50.0)),
            (DefectClassification(DefectType.DISBOND, SeverityLevel.SEVERE, 0.8), 500, (60.0, 60.0)),
        ]
        filtered = filter_by_confidence(defects, min_confidence=0.5)
        assert len(filtered) == 1
        assert filtered[0].classification.defect_type == DefectType.DISBOND

    def test_merge_nearby(self):
        from src.defect_analysis.confidence_filter import FilteredDefect, merge_nearby_fragments
        from src.defect_analysis.classifier import DefectClassification, DefectType, SeverityLevel
        d1 = FilteredDefect(DefectClassification(DefectType.BUBBLE, SeverityLevel.MINOR, 0.7), 100, (50.0, 50.0))
        d2 = FilteredDefect(DefectClassification(DefectType.BUBBLE, SeverityLevel.MINOR, 0.7), 80, (55.0, 52.0))
        merged = merge_nearby_fragments([d1, d2], distance_threshold=20.0)
        assert len(merged) == 1
        assert merged[0].area > 100
