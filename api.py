from fastapi import FastAPI
import torch
from transformers import AutoTokenizer, AutoModelForSequenceClassification
import pandas as pd
import re

MAX_LENGTH = 512
access_token = "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"
checkpoint = "Nirij3m/roberta-finetuned-vishing"
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, token=access_token)
tokenizer = AutoTokenizer.from_pretrained(checkpoint, token=access_token)

def clean_special_char(text):
    if pd.isna(text):
        return text

    text = text.lower()

    try:
        text = text.encode('latin1').decode('utf-8', errors='ignore')
    except:
        pass

    text = text.replace('\\n', ' ').replace('\n', ' ').replace('\r', ' ')
    text = text.encode('ascii', errors='ignore').decode('ascii')
    text = re.sub(r'\s+', ' ', text).strip()
    return text


app = FastAPI()

@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/predict/")
async def predict_text(text: str):
    print(f"Received text: {text}")
    text = clean_special_char(text)
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    model.to(device)

    inputs = tokenizer(
        text,
        return_tensors="pt",
        truncation=True,
        max_length=MAX_LENGTH,
        padding=True
    )

    # Move inputs to the same device as the model
    inputs = {key: val.to(device) for key, val in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        predictions = torch.argmax(outputs.logits, dim=-1)

    predicted_id = predictions.item()
    predicted_label = model.config.id2label[predicted_id]
    return {"label": predicted_label, "id": predicted_id}


