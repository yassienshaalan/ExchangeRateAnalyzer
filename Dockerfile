# An official Python runtime as a parent image
FROM python:3.8-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Run the tests to ensure the application is working as expected
RUN python -m unittest test_exchange_rate_analyzer.py

# Define environment variable, the value below needs to be updated with the valid subscription
ENV EXCHANGE_RATE_API_KEY s3dd36566e522e1e55eee51e1e4 

# Run app.py when the container launches
CMD ["python", "exchange_rate_analyzer.py"]
