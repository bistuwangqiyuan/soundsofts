"""Albumentations augmentation pipeline for C-scan images."""

from __future__ import annotations

import albumentations as A


def get_train_transforms(cfg: dict) -> A.Compose:
    return A.Compose([
        A.HorizontalFlip(p=cfg.get("horizontal_flip", 0.5)),
        A.VerticalFlip(p=cfg.get("vertical_flip", 0.5)),
        A.ShiftScaleRotate(
            shift_limit=0.05,
            scale_limit=cfg.get("scale_limit", 0.2),
            rotate_limit=cfg.get("rotate_limit", 15),
            p=0.5,
        ),
        A.RandomBrightnessContrast(
            brightness_limit=cfg.get("brightness_limit", 0.2),
            contrast_limit=cfg.get("contrast_limit", 0.2),
            p=0.5,
        ),
        A.GaussNoise(var_limit=tuple(cfg.get("gaussian_noise_var_limit", [10, 50])), p=0.3),
        A.ElasticTransform(alpha=cfg.get("elastic_transform_alpha", 120), sigma=120 * 0.05, p=0.3),
    ])


def get_val_transforms() -> A.Compose:
    return A.Compose([])
