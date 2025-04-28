# Use official Python base image
FROM python:3.13-slim

# Install git inside the container
RUN apt-get update && apt-get install -y git

# Set working directory
WORKDIR /app

# Clone the repository
RUN git clone https://github.com/SkeyRahaman/URL_Shortner.git .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Command to run the FastAPI app
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
