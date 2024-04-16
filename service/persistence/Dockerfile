# Use Alpine for the builder stage
FROM alpine:latest as builder

# Install Python and pip
RUN apk add --no-cache python3 py3-pip

# Set the working directory in the container
WORKDIR /app

# Copy the requirements file
COPY requirements.txt .

# Install Python dependencies
RUN pip install -r requirements.txt --user

# Start a new stage from scratch using Alpine
FROM alpine:latest

# Install Python
RUN apk add --no-cache python3

# Set the working directory in the container
WORKDIR /app

# Copy the installed Python packages from the builder stage
COPY --from=builder /root/.local/lib/python3.10/site-packages /usr/lib/python3.10/site-packages

# Copy the main application
COPY main.py .

# Set the entry point for the container
ENTRYPOINT [ "python3", "/app/main.py" ]
