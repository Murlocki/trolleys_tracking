import cv2
import numpy as np
import torch
from torch import nn
from torchvision.models import resnet18, ResNet18_Weights
from ultralytics import YOLO

from src.classification_service.classification_settings import classification_settings
from src.classification_service.models.BasicModel import BasicClassificator
from src.shared.logger_setup import setup_logger
from src.shared.schemas import BoundingBox

logger = setup_logger(__name__)

class DualResNet18(nn.Module):
    def __init__(self, num_classes):
        super().__init__()
        weights = ResNet18_Weights.IMAGENET1K_V1

        # RGB ветка
        self.rgb_branch = resnet18(weights=weights)
        self.rgb_branch.fc = nn.Identity()

        # HSV ветка
        self.hsv_branch = resnet18(weights=weights)
        self.hsv_branch.fc = nn.Identity()

        # Классификатор после объединения признаков
        self.classifier = nn.Sequential(
            nn.Linear(512 * 2, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, num_classes)
        )

    def forward(self, rgb, hsv):
        f_rgb = self.rgb_branch(rgb)  # (batch, 512)
        f_hsv = self.hsv_branch(hsv)  # (batch, 512)
        combined = torch.cat([f_rgb, f_hsv], dim=1)  # (batch, 1024)
        out = self.classifier(combined)
        return out


class DualResNet(BasicClassificator):
    def preprocess_image(self,img_bgr):
        # Чтение и авто-ориентация (если надо вручную — используйте PIL и EXIF)

        # Resize (растягивание)
        img_bgr = cv2.resize(img_bgr, (640, 640), interpolation=cv2.INTER_LINEAR)

        # Adaptive Equalization (CLAHE)
        img_lab = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2LAB)
        l, a, b = cv2.split(img_lab)
        clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
        cl = clahe.apply(l)
        img_lab = cv2.merge((cl, a, b))
        img_bgr = cv2.cvtColor(img_lab, cv2.COLOR_LAB2BGR)

        # Преобразование в RGB и HSV
        img_rgb = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2RGB).astype(np.float32) / 255.0
        img_hsv = cv2.cvtColor(img_bgr, cv2.COLOR_BGR2HSV).astype(np.float32) / 255.0

        img_rgb = torch.tensor(np.transpose(img_rgb, (2, 0, 1)), dtype=torch.float32).unsqueeze(0)
        img_hsv = torch.tensor(np.transpose(img_hsv, (2, 0, 1)), dtype=torch.float32).unsqueeze(0)

        return img_rgb, img_hsv

    def classify(self, image, bounding_boxes: list[BoundingBox]) -> list[BoundingBox]:
        try:
            results = []
            for box in bounding_boxes:
                x1, y1 = int(box.x), int(box.y)
                x2 = int(box.x + box.width)
                y2 = int(box.y + box.height)
                crop = image[y1:y2, x1:x2]
                if crop.size == 0:
                    continue
                rgb_tensor, hsv_tensor = self.preprocess_image(crop)
                rgb_tensor = rgb_tensor.to(self.device)
                hsv_tensor = hsv_tensor.to(self.device)
                with torch.no_grad():
                    logits = self.model_classify(rgb_tensor, hsv_tensor)
                    pred_class = torch.argmax(logits, dim=1).item()

                if pred_class in [0, 2]:
                    results.append(box)
            return results
        except Exception as e:
            logger.error(f"Error during classification: {str(e)}")
            return []

    def __init__(self, model_path:str, parameters:dict):
        self.model_classify = DualResNet18(num_classes=3)
        self.device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
        self.model_classify.load_state_dict(
            torch.load(model_path,
                       map_location=self.device))
        self.model_classify.to(self.device)
        self.model_classify.eval()
        self.parameters = parameters

dual_res_net = DualResNet(model_path=classification_settings.full_model_path,
                           parameters={
                               "num_classes":3
                           })

