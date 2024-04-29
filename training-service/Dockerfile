FROM python:3.9-slim as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --user

COPY /data/ ./data/
COPY ./model-training.py ./

CMD ["python", "model-training.py"]