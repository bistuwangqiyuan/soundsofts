"""Visualization utilities: defect overlays, heatmaps, composite figures."""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import TYPE_CHECKING

import cv2
import numpy as np

if TYPE_CHECKING:
    from ..pipeline import DetectedDefect

_SEVERITY_COLORS = {
    "轻微": (0, 200, 0),
    "中等": (0, 180, 255),
    "严重": (0, 0, 255),
}

_TYPE_COLORS = {
    "气泡": (255, 200, 50),
    "弱粘": (50, 150, 255),
    "脱粘": (50, 50, 255),
    "正常粘接": (50, 220, 50),
    "未知": (180, 180, 180),
}


def draw_defect_overlay(
    image: np.ndarray,
    defects: list[DetectedDefect],
    mask: np.ndarray | None = None,
    alpha: float = 0.35,
) -> np.ndarray:
    """Draw colored contour overlays and labels on a BGR image."""
    overlay = image.copy()

    if mask is not None:
        color_mask = np.zeros_like(image)
        color_mask[mask > 0] = (0, 0, 255)
        overlay = cv2.addWeighted(overlay, 1.0, color_mask, alpha, 0)

    for d in defects:
        color = _SEVERITY_COLORS.get(d.severity.value, (200, 200, 200))
        x, y, w, h = d.bbox
        cv2.rectangle(overlay, (x, y), (x + w, y + h), color, 2)

        label = f"#{d.defect_id} {d.defect_type.value}"
        (tw, th), _ = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.45, 1)
        cv2.rectangle(overlay, (x, y - th - 6), (x + tw + 4, y), color, -1)
        cv2.putText(overlay, label, (x + 2, y - 4), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (255, 255, 255), 1)

    return overlay


def generate_heatmap(mask: np.ndarray) -> np.ndarray:
    """Apply JET colormap to a defect probability / binary mask."""
    if mask.dtype != np.uint8:
        norm = ((mask - mask.min()) / (mask.max() - mask.min() + 1e-8) * 255).astype(np.uint8)
    else:
        norm = mask
    return cv2.applyColorMap(norm, cv2.COLORMAP_JET)


def create_side_by_side(original: np.ndarray, overlay: np.ndarray, heatmap: np.ndarray | None = None) -> np.ndarray:
    """Horizontally concatenate images, resizing to same height."""
    panels = [original, overlay]
    if heatmap is not None:
        panels.append(heatmap)

    target_h = min(p.shape[0] for p in panels)
    resized = []
    for p in panels:
        if p.shape[0] != target_h:
            scale = target_h / p.shape[0]
            p = cv2.resize(p, (int(p.shape[1] * scale), target_h))
        resized.append(p)

    return np.hstack(resized)


def save_analysis_figure(
    original: np.ndarray,
    defects: list[DetectedDefect],
    mask: np.ndarray,
    output_dir: str | Path | None = None,
) -> tuple[str, str, str]:
    """Save overlay, heatmap, and composite to temp files. Returns (overlay_path, heatmap_path, composite_path)."""
    if output_dir is None:
        output_dir = Path(tempfile.mkdtemp(prefix="irs_"))
    else:
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

    overlay = draw_defect_overlay(original, defects, mask)
    heatmap = generate_heatmap(mask)
    composite = create_side_by_side(original, overlay, heatmap)

    overlay_path = str(output_dir / "defect_overlay.png")
    heatmap_path = str(output_dir / "defect_heatmap.png")
    composite_path = str(output_dir / "analysis_composite.png")

    cv2.imwrite(overlay_path, overlay)
    cv2.imwrite(heatmap_path, heatmap)
    cv2.imwrite(composite_path, composite)

    return overlay_path, heatmap_path, composite_path
