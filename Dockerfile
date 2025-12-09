FROM python:3.12-slim

WORKDIR /app

COPY . /app

# Install dependencies (optional)
# RUN pip install -r requirements.txt

# Default command
CMD ["python", "main.py"]
