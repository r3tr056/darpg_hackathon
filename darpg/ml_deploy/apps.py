from django.apps import AppConfig
import os
import pathlib

from transformers import BertTokenizer, BertModel
from sentence_transformers import SentenceTransformer

# encoding_model = SentenceTransformer('bert-base-nli-max-tokens')

class MlDeployConfig(AppConfig):
    default_auto_field = "django.db.models.BigAutoField"
    name = "ml_deploy"

    MODEL_PATH = pathlib.Path("model")
    BERT_PRETRAINED_PATH = pathlib.Path("label/")

