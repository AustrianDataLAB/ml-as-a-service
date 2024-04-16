# Use Alpine latest version as the base image
FROM alpine:latest

# Install Python, pip, and necessary build tools
RUN apk add --no-cache python3 py3-pip python3-dev gcc musl-dev

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip3 install -r requirements.txt

# Copy the rest of your application
COPY main.py .

# Set the entry point for the container
ENTRYPOINT ["python3", "/app/main.py"]
