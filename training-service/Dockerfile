FROM python

# Set the working directory to /app
WORKDIR /training-service
COPY ./requirements.txt ./
RUN pip install -r ./requirements.txt

# RUN curl -X GET -H http://mlaas-service-persistence:1919
# RUN curl -X GET -H "Authorization: 001-token" -o file.tgz http://persistence-container:1919/data
COPY ./file.tgz ./
RUN mkdir ./data && tar -xf ./file.tgz -C ./data && rm file.tgz

COPY ./model-training.py ./
CMD ["python", "model-training.py"]