# Use slim Python image to reduce size
FROM python:3.11-slim

# Install dependencies and Tesseract OCR
RUN apt-get update && apt-get install -y \
    tesseract-ocr \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy dependencies first
COPY requirements.txt .

# Install Python packages
RUN pip install --no-cache-dir -r requirements.txt

# Copy app source code
COPY . .

# Expose port
EXPOSE 5000

# Start the app using gunicorn
CMD ["gunicorn", "--workers=1", "--timeout=120", "--bind=0.0.0.0:5000", "app:app"]
