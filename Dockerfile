# Use the official Python image from the Docker Hub
FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Install ffmpeg for video operations
RUN apt-get update && \
    apt-get install -y ffmpeg && \
    # apt-get install -y ffprobe && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy the requirements.txt for installing requried packages
COPY requirements.txt .

# Install the required pip packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code into the image
COPY videoSvc/ .
ENV PYTHONUNBUFFERED=1
# to start application
CMD ["python", "manage.py", "runserver", "0.0.0.0:5000"]
