from .table_detector import TableDetector

class ProtonX_OCR:
    """
    Main class for ProtonX OCR tool.
    """
    def __init__(self):
        self.table_detector = None
    def detect_table(self, image_path: str, model: str = "protonx-models/protonx-table-detector", device: str = 'cpu'):
        if self.table_detector is None:
            self.table_detector = TableDetector(model_name=model, device=device)
        return self.table_detector.predict(image_path)