from typing import Any, Dict, List, Union
from transformers import AutoTokenizer, AutoModelForSeq2SeqLM
import json
import warnings
from pathlib import Path
import math

# Find project root and look for model_list.json there
project_root = Path(__file__).parent
CONFIG_PATH = project_root / 'model_list.json'

with open(CONFIG_PATH, 'r') as f:
    model_config = json.load(f)

class OfflineNormalizer:
    """
    ProtonX TextNormalizer API wrapper
    Usage:
        client.text.correct(input = "Toi di hoc")
    """

    def __init__(self):
        normalizer_models = model_config['text_correction']['offline']
        if len(normalizer_models) == 0:
            warnings.warn("Text correction do not yet support offline mode.", UserWarning)

    def correct(self, 
            input: Union[str, List[str]], 
            top_k: int = 1,
            model: str = "protonx-models/protonx-legal-tc",
            **kwargs: Any
    ) -> Dict[str, Any]:
        """
        Vietnamese text correction using local HuggingFace model inference.
        """
        # Validate input
        if input is None:
            raise ValueError("Input cannot be None")
        
        if isinstance(input, str):
            texts = [input]
        elif isinstance(input, list):
            texts = input
        else:
            raise TypeError(f"Input must be str or list, got {type(input).__name__}")
        
        if len(texts) == 0:
            raise ValueError("Input list cannot be empty")
        
        if any(not text or not text.strip() for text in texts):
            raise ValueError("Input cannot contain empty or whitespace-only strings")
        
        # Load model and tokenizer (device handling is automatic)
        tokenizer = AutoTokenizer.from_pretrained(model)
        model_obj = AutoModelForSeq2SeqLM.from_pretrained(model).eval()
        
        results = []
        
        for text in texts:
            # Encode input
            inputs = tokenizer(text, return_tensors="pt", max_length=128, truncation=True)
            
            # Generate corrections
            outputs = model_obj.generate(
                **inputs,
                max_length=kwargs.get("max_length", 128),
                num_beams=top_k + 1,
                num_return_sequences=top_k,
                output_scores=True,
                return_dict_in_generate=True,
            )
            
            # Decode and score candidates
            candidates = []
            for i, seq in enumerate(outputs.sequences):
                decoded = tokenizer.decode(seq, skip_special_tokens=True)
                # Get raw score (log-probability)
                raw_score = outputs.sequences_scores[i].item() if hasattr(outputs, 'sequences_scores') else 1.0 / (i + 1)
                
                # Convert log-probability to probability (0-1)
                score = 1 / (1 + math.exp(-raw_score))  # Sigmoid normalization
                candidates.append({
                    "output": decoded,
                    "score": round(score, 4)
                })
            
            results.append({
                "input": text,
                "candidates": candidates
            })
        
        return {
            "model": model,
            "data": results
        }
        
    def list_model(self) -> Dict[str, Any]:
        normalizer_models = model_config['text_correction']
        return {"models": normalizer_models}