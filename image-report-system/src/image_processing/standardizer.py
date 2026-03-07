"""Resolution unification and color space conversion."""

from __future__ import annotations

import cv2
import numpy as np


def standardize(
    image: np.ndarray,
    target_size: tuple[int, int] = (384, 768),
    color_space: str = "RGB",
) -> np.ndarray:
    """Resize and convert color space."""
    resized = cv2.resize(image, (target_size[1], target_size[0]))
    if color_space == "RGB":
        return cv2.cvtColor(resized, cv2.COLOR_BGR2RGB)
    elif color_space == "HSV":
        return cv2.cvtColor(resized, cv2.COLOR_BGR2HSV)
    return resized
