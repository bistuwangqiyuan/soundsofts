"""Multi-level feature extraction: color histogram, LBP, Gabor."""

from __future__ import annotations

import cv2
import numpy as np


def color_histogram(image: np.ndarray, bins: int = 32) -> np.ndarray:
    """Compute normalized color histogram across all channels."""
    histograms = []
    for ch in range(image.shape[2] if len(image.shape) == 3 else 1):
        channel = image[:, :, ch] if len(image.shape) == 3 else image
        hist = cv2.calcHist([channel], [0], None, [bins], [0, 256])
        histograms.append(hist.flatten())
    combined = np.concatenate(histograms)
    total = combined.sum()
    return combined / total if total > 0 else combined


def lbp_features(image: np.ndarray) -> np.ndarray:
    """Simplified Local Binary Pattern histogram."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    h, w = gray.shape
    lbp = np.zeros_like(gray)

    for i in range(1, h - 1):
        for j in range(1, w - 1):
            center = gray[i, j]
            code = 0
            code |= (gray[i - 1, j - 1] >= center) << 7
            code |= (gray[i - 1, j] >= center) << 6
            code |= (gray[i - 1, j + 1] >= center) << 5
            code |= (gray[i, j + 1] >= center) << 4
            code |= (gray[i + 1, j + 1] >= center) << 3
            code |= (gray[i + 1, j] >= center) << 2
            code |= (gray[i + 1, j - 1] >= center) << 1
            code |= (gray[i, j - 1] >= center) << 0
            lbp[i, j] = code

    hist = cv2.calcHist([lbp], [0], None, [256], [0, 256]).flatten()
    total = hist.sum()
    return hist / total if total > 0 else hist


def gabor_features(image: np.ndarray, num_orientations: int = 4) -> np.ndarray:
    """Extract mean Gabor filter responses across orientations."""
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY) if len(image.shape) == 3 else image
    features = []
    for theta_idx in range(num_orientations):
        theta = theta_idx * np.pi / num_orientations
        kernel = cv2.getGaborKernel((21, 21), sigma=5, theta=theta, lambd=10, gamma=0.5)
        filtered = cv2.filter2D(gray, cv2.CV_64F, kernel)
        features.append(float(np.mean(np.abs(filtered))))
        features.append(float(np.std(filtered)))
    return np.array(features)
