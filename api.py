from fastapi import FastAPI, UploadFile, File, HTTPException
import vosk, json, wave, torch, re, ffmpeg, io
from transformers import AutoTokenizer, AutoModelForSequenceClassification
from dotenv import load_dotenv
import pandas as pd
import os
import warnings




load_dotenv()
HF_TOKEN = os.getenv("HF_TOKEN")
if HF_TOKEN is None:
    HF_TOKEN = ""
    warnings.warn("HF_TOKEN not found in environment variables")


MAX_LENGTH = 512
access_token = HF_TOKEN
checkpoint = "Nirij3m/roberta-finetuned-vishing"
model = AutoModelForSequenceClassification.from_pretrained(checkpoint, token=access_token)
vosk_model = vosk.Model("vosk-model-en-us-0.22")
tokenizer = AutoTokenizer.from_pretrained(checkpoint, token=access_token)


def convert_audio(file_bytes: bytes) -> bytes:
    out, _ = (
        ffmpeg
        .input("pipe:0")
        .output("pipe:1",
            ar=16000,
            ac=1,
            acodec="pcm_s16le",
            format="wav"
        )
        .run(input=file_bytes, capture_stdout=True, capture_stderr=True)
    )
    return out

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


def predict_text(text: str):
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

    inputs = {key: val.to(device) for key, val in inputs.items()}

    with torch.no_grad():
        outputs = model(**inputs)
        probabilities = torch.nn.functional.softmax(outputs.logits, dim=-1)
        confidence, predictions = torch.max(probabilities, dim=-1)

    score = confidence.item()
    predicted_id = predictions.item()
    predicted_label = model.config.id2label[predicted_id]
    print("Received text:", text)
    print("Predicted label:", predicted_label, "with confidence:", score)
    return {"label": predicted_label, "id": predicted_id, "confidence": score}


app = FastAPI()


@app.get("/")
async def root():
    return {"message": "Hello World"}


'''
@app.post("/number/{number}")
async def number_suspicious(number: int):
    return {"isSuspicious": False}
'''

@app.post("/send_audio/")
async def send_audio(file: UploadFile):
    recognizer = vosk.KaldiRecognizer(vosk_model, 16000)

    content = await file.read()
    print(f"Content-Type: {file.content_type}, Filename: {file.filename}, Size: {len(content)} bytes")

    '''
    # Sauvegarde du fichier AVANT conversion
    original_ext = os.path.splitext(file.filename or "audio")[1] or ".bin"
    original_path = f"debug_before{original_ext}"
    with open(original_path, "wb") as f:
        f.write(content)
    print(f"Fichier original sauvegardé : {original_path}")
    '''
    converted = convert_audio(content)

    '''
    # Sauvegarde du fichier APRÈS conversion (toujours un WAV PCM 16-bit 16kHz mono)
    converted_path = "debug_after.wav"
    with open(converted_path, "wb") as f:
        f.write(converted)
    print(f"Fichier converti sauvegardé : {converted_path}")
    '''

    with wave.open(io.BytesIO(converted)) as wf:
        while True:
            data = wf.readframes(4000)
            if len(data) == 0:
                break
            recognizer.AcceptWaveform(data)

    result = json.loads(recognizer.FinalResult())
    return predict_text(result.get("text", ""))
@app.get("/get_health/")
async def get_health():
    print("Health check received")
    return {"status": "ok", "server_name":"UQAC Server", "model_name": "RoBERTa (Fine-tuned)", "stt_model": "Vosk (en)"}