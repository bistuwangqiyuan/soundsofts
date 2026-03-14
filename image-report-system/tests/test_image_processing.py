"""Tests for image_processing modules."""

import numpy as np
import pytest
from PIL import Image


def _make_bgr_image(h=200, w=300, val=128):
    return np.full((h, w, 3), val, dtype=np.uint8)


def _save_image(tmp_path, name="test.png", h=200, w=300, val=128):
    img = Image.fromarray(np.full((h, w, 3), val, dtype=np.uint8), mode="RGB")
    path = tmp_path / name
    img.save(path)
    return path


# --- reader ---

class TestReader:
    def test_read_supported_format(self, tmp_path):
        from src.image_processing.reader import read_cscan
        path = _save_image(tmp_path, "test.png")
        img = read_cscan(path)
        assert img is not None
        assert img.shape[0] > 0

    def test_read_unsupported_format(self, tmp_path):
        from src.image_processing.reader import read_cscan
        path = tmp_path / "test.xyz"
        path.write_text("not an image")
        with pytest.raises(ValueError, match="Unsupported"):
            read_cscan(path)

    def test_read_missing_file(self, tmp_path):
        from src.image_processing.reader import read_cscan
        with pytest.raises(FileNotFoundError):
            read_cscan(tmp_path / "nonexistent.png")


# --- cropper ---

class TestCropper:
    def test_auto_crop_uniform(self):
        from src.image_processing.cropper import auto_crop
        img = _make_bgr_image(100, 100, 128)
        cropped = auto_crop(img)
        assert cropped.shape[0] > 0 and cropped.shape[1] > 0

    def test_auto_crop_preserves_content(self):
        from src.image_processing.cropper import auto_crop
        img = _make_bgr_image(200, 300, 128)
        img[50:150, 50:250] = 200  # bright region
        cropped = auto_crop(img)
        assert cropped.shape[0] <= 200
        assert cropped.shape[1] <= 300


# --- standardizer ---

class TestStandardizer:
    def test_resize_rgb(self):
        from src.image_processing.standardizer import standardize
        img = _make_bgr_image(100, 200)
        result = standardize(img, target_size=(50, 100), color_space="RGB")
        assert result.shape == (50, 100, 3)

    def test_resize_hsv(self):
        from src.image_processing.standardizer import standardize
        img = _make_bgr_image(100, 200)
        result = standardize(img, target_size=(50, 100), color_space="HSV")
        assert result.shape == (50, 100, 3)

    def test_resize_raw(self):
        from src.image_processing.standardizer import standardize
        img = _make_bgr_image(100, 200)
        result = standardize(img, target_size=(50, 100), color_space="BGR")
        assert result.shape == (50, 100, 3)


# --- preprocessor ---

class TestPreprocessor:
    def test_preprocess_full(self, tmp_path):
        from src.image_processing.preprocessor import preprocess_cscan
        path = _save_image(tmp_path)
        result = preprocess_cscan(path, target_size=(64, 128))
        assert result.shape == (64, 128, 3)

    def test_clahe(self):
        from src.image_processing.preprocessor import apply_clahe
        img = _make_bgr_image()
        result = apply_clahe(img)
        assert result.shape == img.shape

    def test_denoise_bilateral(self):
        from src.image_processing.preprocessor import denoise
        img = _make_bgr_image()
        result = denoise(img, method="bilateral")
        assert result.shape == img.shape

    def test_denoise_gaussian(self):
        from src.image_processing.preprocessor import denoise
        img = _make_bgr_image()
        result = denoise(img, method="gaussian")
        assert result.shape == img.shape
