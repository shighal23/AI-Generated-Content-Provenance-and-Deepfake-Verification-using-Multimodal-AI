from pathlib import Path

from PIL import Image
import torch
from torchvision import models


class ImageDetector:

    def __init__(self):
        self.device = torch.device(
            "cuda" if torch.cuda.is_available() else "cpu"
        )

        weights = models.ResNet18_Weights.DEFAULT

        self.model = models.resnet18(
            weights=weights
        )

        self.model.to(self.device)
        self.model.eval()

        self.preprocess = weights.transforms()

    def analyze(self, image_path: str):

        image_path = Path(image_path)

        if not image_path.exists():
            raise FileNotFoundError(
                f"Image not found: {image_path}"
            )

        image = Image.open(image_path).convert("RGB")

        tensor = self.preprocess(image)

        tensor = tensor.unsqueeze(0).to(self.device)

        with torch.no_grad():
            output = self.model(tensor)

        probabilities = torch.softmax(output, dim=1)

        confidence, class_id = torch.max(
            probabilities,
            dim=1
        )

        return {
            "model": "ResNet18-baseline",
            "device": self.device.type,
            "class_id": int(class_id.item()),
            "confidence": round(
                float(confidence.item()),
                4
            )
        }