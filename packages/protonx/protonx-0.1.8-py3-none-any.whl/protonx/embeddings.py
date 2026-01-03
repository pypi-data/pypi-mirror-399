from typing import Any, Dict, List, Union
from ._http import HTTPClient
import warnings


import json
from pathlib import Path

# Find project root and look for model_list.json there
project_root = Path(__file__).parent  # Adjust based on your structure
CONFIG_PATH = project_root / 'model_list.json'

with open(CONFIG_PATH, 'r') as f:
    model_config = json.load(f)


class Embeddings:
    """
    ProtonX Embeddings API wrapper
    Usage:
        client.embeddings.create(input="Hello world")
    """

    def __init__(self, http: HTTPClient, mode: str = "online"):
        self._http = http
        self.mode = mode

        embeddings_models = model_config['embeddings'][mode]

        if len(embeddings_models) == 0:
            warnings.warn(f"Embeddings do not yet support {mode} mode. Defaulting to online mode", UserWarning)


    def create(self, input: Union[str, List[str]], model: str = None, **kwargs: Any) -> Dict[str, Any]:
        if isinstance(input, str):
            texts = [input]
        else:
            texts = input

        payload = {"input": texts}
        if model is not None:
            payload["model"] = model  # optional, if your API supports it
        payload.update(kwargs)

        return self._http.post("/embeddings/", payload)

    def list_model(self) -> Dict[str, Any]:
        embeddings_models = model_config['embeddings']

        return {"embeddings_models": embeddings_models}