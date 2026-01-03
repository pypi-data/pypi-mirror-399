from typing import Any, Dict, List, Union, Optional
from ._http import HTTPClient
from .offline_normalizer import OfflineNormalizer

class TextNormalizer:
    """
    ProtonX TextNormalizer API wrapper
    Usage:
        client.text.correct(input = "Toi di hoc")
    """

    def __init__(self):

        self.normalizer = OfflineNormalizer()

    def correct(self, 
                input: Union[str, List[str]], 
                model: Optional[str] = None,
                top_k: int = 1,
                **kwargs: Any
        ) -> Dict[str, Any]:
        """
        Vietnamese correction
        """

        if model != None:
            return self.normalizer.correct(input, top_k, model)
        else:
            return self.normalizer.correct(input, top_k)

    def list_model(self) -> Dict[str, Any]:
        return self.normalizer.list_model()