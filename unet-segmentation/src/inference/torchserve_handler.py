"""Custom TorchServe handler for U-Net segmentation model."""

from __future__ import annotations

import io
import json
import base64

import cv2
import numpy as np
import torch
from ts.torch_handler.base_handler import BaseHandler


class UNetHandler(BaseHandler):
    """TorchServe handler for U-Net C-scan defect segmentation."""

    def __init__(self) -> None:
        super().__init__()
        self.image_size = (384, 768)
        self.threshold = 0.5

    def preprocess(self, data: list) -> torch.Tensor:
        images = []
        for row in data:
            img_data = row.get("data") or row.get("body")
            if isinstance(img_data, (bytes, bytearray)):
                nparr = np.frombuffer(img_data, np.uint8)
                img = cv2.imdecode(nparr, cv2.IMREAD_COLOR)
            else:
                img = np.frombuffer(base64.b64decode(img_data), np.uint8)
                img = cv2.imdecode(img, cv2.IMREAD_COLOR)

            img = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
            img = cv2.resize(img, (self.image_size[1], self.image_size[0]))
            tensor = torch.from_numpy(img.transpose(2, 0, 1)).float() / 255.0
            images.append(tensor)

        return torch.stack(images).to(self.device)

    def inference(self, data: torch.Tensor, *args, **kwargs) -> torch.Tensor:
        self.model.eval()
        with torch.no_grad():
            return torch.sigmoid(self.model(data))

    def postprocess(self, inference_output: torch.Tensor) -> list:
        results = []
        for prob_map in inference_output:
            mask = (prob_map.squeeze().cpu().numpy() > self.threshold).astype(np.uint8)
            n_labels, labels, stats, centroids = cv2.connectedComponentsWithStats(mask, connectivity=8)

            defects = []
            for i in range(1, n_labels):
                area = int(stats[i, cv2.CC_STAT_AREA])
                if area < 50:
                    continue
                defects.append({
                    "area": area,
                    "centroid": [float(centroids[i][0]), float(centroids[i][1])],
                    "bbox": [int(stats[i, j]) for j in range(4)],
                })

            results.append(json.dumps({"defect_count": len(defects), "defects": defects}))

        return results
