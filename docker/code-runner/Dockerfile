FROM python:3.11-slim

# Set working directory
WORKDIR /code

# Install common packages users might need
RUN pip install numpy pandas requests

# Copy execution script
COPY execute.py /execute.py

# Create a non-root user for security
RUN useradd -m -u 1000 coderunner && \
    chown -R coderunner:coderunner /code

USER coderunner

# Set resource limits
ENV PYTHONUNBUFFERED=1

CMD ["python", "/execute.py"]