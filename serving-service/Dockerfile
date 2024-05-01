FROM cgr.dev/chainguard/python:latest-dev

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --user

COPY __init__.py .
COPY ./main.py .

ENTRYPOINT ["python", "/app/main.py"]