FROM cgr.dev/chainguard/python:latest-dev

ENV persistence_url /persistence

WORKDIR /app

COPY requirements.txt .

RUN pip install -r requirements.txt --user

# at the moment only single stage, because of problems concerning tensorflow and python-version
COPY ./src/* .

RUN mkdir -p /app/data

ENTRYPOINT ["python3", "/app/training-service.py"]