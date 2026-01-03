import os
from ._http import HTTPClient
from .embeddings import Embeddings
from .evaluator import Evaluator
from .normalizer import TextNormalizer
from .ocr import ProtonX_OCR

class ProtonX:
    """
    ProtonX SDK entrypoint (similar to openai.OpenAI)
    """

    def __init__(self, base_url: str = None, api_key: str = None, mode: str = "online"):
        embeddings_url = base_url or os.getenv("PROTONX_EMBEDDINGS_URL", "https://embeddings.protonx.io")

        api_key = api_key or os.getenv("PROTONX_API_KEY")

        self.embeddings_http = HTTPClient(base_url=embeddings_url, api_key=api_key, mode = mode)
        self.embeddings = Embeddings(self.embeddings_http, mode = mode)
        self.text = TextNormalizer()

        self.ocr = ProtonX_OCR()
        
    def evals(self):
        """Return an Evaluator instance for LLM response evaluation"""
        return Evaluator(self.embeddings_http)
    
    
    
