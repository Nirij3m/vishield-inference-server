from transformers import AutoTokenizer, AutoModelForSequenceClassification
from peft import PeftModel
from dotenv import load_dotenv
import pandas as pd
import os
import warnings
import spacy
import joblib
from preprocessing import pipeline_clean_transformer


load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    HF_TOKEN = None
    warnings.warn("HF_TOKEN not found in environment variables")

MAX_LENGTH = 512
access_token = HF_TOKEN
base_checkpoint = "roberta-base"
checkpoint = "Nirij3m/roberta-synth-vishing"
base_model = AutoModelForSequenceClassification.from_pretrained(base_checkpoint, num_labels=2, token=access_token)
model = PeftModel.from_pretrained(base_model, checkpoint, token=access_token)
tokenizer = AutoTokenizer.from_pretrained(checkpoint, token=access_token)

preprocessor = joblib.load("text_preprocessing.joblib")
text = "Hello this is John from Netflix"
preprocessed_text = preprocessor.transform([text])
print(preprocessed_text)
text = "Hello this is John from Netflix"


print(model)
print(model.config)
model.print_trainable_parameters()
