# Use Ubuntu with FFmpeg support
FROM ubuntu:latest

# Install system packages
RUN apt-get update && \
    apt-get install -y ffmpeg python3-pip

# Set working directory
WORKDIR /app

# Copy local code to the container image
COPY requirements.txt .
COPY app/ ./app/
RUN mkdir -p uploads

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8000

# Start FastAPI server
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]