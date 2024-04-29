FROM cgr.dev/chainguard/python:latest-dev as builder

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --user


FROM cgr.dev/chainguard/python:latest

# Set the working directory to /app
WORKDIR /app

COPY --from=builder /home/nonroot/.local/lib/python3.12/site-packages /home/nonroot/.local/lib/python3.12/site-packages

COPY ./model-training.py ./
CMD ["python", "model-training.py"]