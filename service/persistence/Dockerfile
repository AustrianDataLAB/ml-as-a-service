# Use the official Python image
FROM python:3.10-slim

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt

# Copy the rest of your application
COPY main.py .

# Set the entry point for the container
ENTRYPOINT ["python", "/app/main.py"]
