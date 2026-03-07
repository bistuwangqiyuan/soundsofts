"""U-Net defect segmentation wrapper for the standalone analyzer."""

from __future__ import annotations

from pathlib import Path

import cv2
import numpy as np
import onnxruntime as ort


class DefectSegmentor:
    """Run U-Net segmentation on C-scan images via ONNX Runtime."""

    def __init__(
        self,
        model_path: str | Path,
        image_size: tuple[int, int] = (384, 768),
        threshold: float = 0.5,
    ) -> None:
        self.image_size = image_size
        self.threshold = threshold
        self.session = ort.InferenceSession(
            str(model_path), providers=["CPUExecutionProvider"]
        )
        self.input_name = self.session.get_inputs()[0].name

    def segment(self, image: np.ndarray) -> np.ndarray:
        """Return binary defect mask for a C-scan image (BGR input)."""
        rgb = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
        resized = cv2.resize(rgb, (self.image_size[1], self.image_size[0]))
        tensor = resized.transpose(2, 0, 1).astype(np.float32) / 255.0
        tensor = np.expand_dims(tensor, axis=0)

        logits = self.session.run(None, {self.input_name: tensor})[0]
        prob = 1.0 / (1.0 + np.exp(-logits))  # sigmoid
        return (prob.squeeze() > self.threshold).astype(np.uint8)
