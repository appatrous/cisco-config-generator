# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy only the requirements file first to leverage Docker layer caching
COPY requirements.txt ./

# Install Python dependencies.  The `--no-cache-dir` option keeps the image smaller
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container
COPY . .

# Expose the port that the Flask app runs on
EXPOSE 5000

# Set environment variables for Flask (optional)
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0
ENV FLASK_RUN_PORT=5000

# Command to run the Flask application
CMD ["python", "app.py"]