# Use the official TensorFlow Serving Docker image
FROM tensorflow/serving

# Set the environment variable for model name
ENV MODEL_NAME=half_plus_two

# Copy the demo models to the appropriate directory
COPY saved_model_half_plus_two_cpu /models/half_plus_two

# Expose the REST API port
EXPOSE 8501

# Start TensorFlow Serving when the container starts
ENTRYPOINT ["tensorflow_model_server", "--port=8500", "--rest_api_port=8501", "--model_name=half-plus-two", "--model_base_path=/models/half_plus_two"]
