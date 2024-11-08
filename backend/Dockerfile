# Use a Python base image
FROM python:3.9

# Set the working directory in the container
WORKDIR /app

# Copy the local files into the container
COPY . .

# Install dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Command to run your app (or define it in docker-compose.yml)
# CMD ["python", "app.py"]
