# import torch
# import torch.nn as nn
# import torchvision
# from torchvision import transforms
# from torchvision import models as pretrained_models
from PIL import Image
from huggingface_hub import hf_hub_download
import warnings

from protonx.utils.import_utils import (
    is_torch_available,
    is_torchvision_available,
    require_version,
)

warnings.filterwarnings("ignore")

class TableDetector:
    def __init__(self, model_name: str, device: str = 'cpu'):
        # --- Dependency checks ---
        if not is_torch_available():
            raise ImportError(
                "PyTorch is required to use TableDetector. "
                "Install it with: pip install torch>=1.12.0"
            )

        if not is_torchvision_available():
            raise ImportError(
                "torchvision is required to use TableDetector. "
                "Install it with: pip install torchvision>=0.13.0"
            )

        require_version("torch>=1.12.0")
        require_version("torchvision>=0.13.0")

        # --- Safe imports (AFTER checks) ---
        import torch

        self.torch = torch
        self.device = torch.device(device)
        self.model_name = model_name
        self.model = None

    def load_model(self, model_path: str):
        torch = self.torch
        import torch.nn as nn
        from torchvision import models as pretrained_models

        model = pretrained_models.mobilenet_v2(
            weights=None, 
            progress=False
        )
        model.classifier[1]  = nn.Linear(
            in_features=model.classifier[1].in_features, 
            out_features=2
        )
        model.load_state_dict(torch.load(model_path, map_location=self.device))
        return model

    def preprocess_image(self, image_path: str):
        torch = self.torch
        from torchvision import transforms

        transform = transforms.Compose([
            transforms.Resize((224, 224)),
            transforms.ToTensor(),
        ])

        image = Image.open(image_path).convert('RGB')
        image = transform(image).unsqueeze(0)  # Add batch dimension
        return image.to(self.device)

    def predict(self, image_path: str):
        torch = self.torch

        if self.model is None:
            self.model_path = hf_hub_download(
                repo_id=self.model_name, 
                filename="model/table_detector.pth"
            )
            self.model = self.load_model(self.model_path)
            self.model.to(self.device)
            self.model.eval()

        image = self.preprocess_image(image_path)

        with torch.no_grad():
            outputs = self.model(image)
            _, preds = torch.max(outputs, 1)

        return 'table' if preds.item() == 1 else 'no_table'