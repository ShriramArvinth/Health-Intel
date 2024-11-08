FROM python:3.10

# Set the initial working directory to the root of the project
WORKDIR /

# Copy requirements.txt to the root directory in the container
COPY requirements.txt /requirements.txt

# Copy the entire 'app' directory to '/app' in the container
COPY ./app /app

# Install dependencies from requirements.txt located in the root
RUN pip install --no-cache-dir --upgrade -r /requirements.txt

# Set the working directory to /app/api for running the CMD command
WORKDIR /app/api

# Run the Uvicorn server from the /app/api directory
CMD ["uvicorn", "api:app", "--host", "0.0.0.0", "--port", "8090"]