FROM python:3

WORKDIR /usr/src/app

RUN apt update && apt install -y wget unzip

COPY api.py requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

RUN <<EOF
wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
unzip vosk-model-en-us-0.22.zip
EOF

EXPOSE 8000
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8000"]