import torch
import numpy as np
from typing import Union, List
from sentence_transformers import SentenceTransformer

from .base import BaseMLModel

class BERTEmbedding(BaseMLModel):
    def __init__(self, model_name='bert-base-nli-mean-tokens'):
        super(BERTEmbedding, self).__init__()
        self.model = SentenceTransformer(model_name)

    def predict(self, texts: Union[str, List[str]], verbose:bool=False):
        embeddings = np.array(self.model.encode(texts, show_progress_bar=verbose))
        return embeddings
    