"""PyTorch Dataset for C-scan images and segmentation masks."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import torch
from torch.utils.data import Dataset


class CScanDataset(Dataset):
    """Load C-scan images and binary masks for defect segmentation.

    Args:
        image_dir: Directory containing C-scan images.
        mask_dir: Directory containing binary mask images.
        image_size: (H, W) to resize all images.
        transform: Optional albumentations transform pipeline.
    """

    def __init__(
        self,
        image_dir: str | Path,
        mask_dir: str | Path,
        image_size: tuple[int, int] = (384, 768),
        transform: object | None = None,
    ) -> None:
        self.image_dir = Path(image_dir)
        self.mask_dir = Path(mask_dir)
        self.image_size = image_size
        self.transform = transform

        self.image_files = sorted(
            [f for f in self.image_dir.iterdir() if f.suffix.lower() in (".png", ".jpg", ".bmp", ".tiff")]
        )

    def __len__(self) -> int:
        return len(self.image_files)

    def __getitem__(self, idx: int) -> dict[str, torch.Tensor]:
        img_path = self.image_files[idx]
        mask_path = self.mask_dir / img_path.name

        image = cv2.imread(str(img_path))
        image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        image = cv2.resize(image, (self.image_size[1], self.image_size[0]))

        if mask_path.exists():
            mask = cv2.imread(str(mask_path), cv2.IMREAD_GRAYSCALE)
            mask = cv2.resize(mask, (self.image_size[1], self.image_size[0]))
            mask = (mask > 127).astype(np.float32)
        else:
            mask = np.zeros((self.image_size[0], self.image_size[1]), dtype=np.float32)

        if self.transform is not None:
            augmented = self.transform(image=image, mask=mask)
            image = augmented["image"]
            mask = augmented["mask"]

        image_tensor = torch.from_numpy(image.transpose(2, 0, 1)).float() / 255.0
        mask_tensor = torch.from_numpy(mask).float().unsqueeze(0)

        return {"image": image_tensor, "mask": mask_tensor, "filename": img_path.name}
