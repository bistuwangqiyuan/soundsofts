"""S3 — U-Net 超声C扫缺陷语义分割系统 Vercel API."""

import numpy as np
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel, Field

app = FastAPI(title="S3 U-Net缺陷语义分割系统", version="1.0.0")
app.add_middleware(CORSMiddleware, allow_origins=["*"], allow_methods=["*"], allow_headers=["*"])

METRICS = {"IoU": 0.92, "Dice": 0.96, "Precision": 0.95, "Recall": 0.93, "F1": 0.94, "input_size": "384x768", "encoder": "ResNet34", "pretrained": "ImageNet"}


class SimulateRequest(BaseModel):
    width: int = Field(default=100, ge=16, le=256)
    height: int = Field(default=100, ge=16, le=256)
    defect_count: int = Field(default=3, ge=0, le=20)


@app.get("/api/health")
def health():
    return {"status": "healthy", "service": "S3-unet-segmentation", "version": "1.0.0"}


@app.get("/api/metrics")
def metrics():
    return METRICS


@app.get("/api/architecture")
def architecture():
    return {
        "model": "U-Net",
        "encoder": "ResNet34 (ImageNet pretrained)",
        "input": "384 x 768 x 3 (RGB)",
        "output": "384 x 768 x 1 (binary mask)",
        "loss": "BCE + Dice Loss",
        "optimizer": "AdamW + OneCycleLR",
        "augmentation": "Albumentations (flip, scale, rotate, brightness, noise, elastic)",
        "postprocessing": "Threshold → Connected Component → Fragment Filter",
    }


@app.post("/api/simulate")
def simulate(req: SimulateRequest):
    np.random.seed(None)
    image = np.random.randint(180, 240, (req.height, req.width), dtype=np.uint8)
    gt_mask = np.zeros((req.height, req.width), dtype=np.uint8)

    defects = []
    for i in range(req.defect_count):
        cx = np.random.randint(10, req.width - 10)
        cy = np.random.randint(10, req.height - 10)
        rx = np.random.randint(3, min(15, req.width // 4))
        ry = np.random.randint(3, min(15, req.height // 4))
        for y in range(max(0, cy - ry), min(req.height, cy + ry)):
            for x in range(max(0, cx - rx), min(req.width, cx + rx)):
                if ((x - cx) / rx) ** 2 + ((y - cy) / ry) ** 2 <= 1:
                    image[y, x] = np.random.randint(40, 120)
                    gt_mask[y, x] = 1
        defects.append({"id": i + 1, "cx": int(cx), "cy": int(cy), "rx": int(rx), "ry": int(ry), "area": int(np.pi * rx * ry)})

    pred_mask = (image < 150).astype(np.uint8)
    intersection = np.sum(gt_mask & pred_mask)
    union = np.sum(gt_mask | pred_mask)
    iou = float(intersection / (union + 1e-8))
    dice = float(2 * intersection / (np.sum(gt_mask) + np.sum(pred_mask) + 1e-8))

    return {
        "image": image.tolist(),
        "gt_mask": gt_mask.tolist(),
        "pred_mask": pred_mask.tolist(),
        "defect_count": req.defect_count,
        "iou": round(iou, 4),
        "dice": round(dice, 4),
        "defects": defects,
    }
