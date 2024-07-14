# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Install dependencies
COPY requirements.txt /code/
RUN pip install --upgrade pip && pip install -r requirements.txt

# Copy the current directory contents into the container at /code/
COPY . /code/

# Expose the port that Django runs on
EXPOSE 8000

# Collect static files
RUN python manage.py collectstatic --noinput

# Run Django application
ENTRYPOINT ["sh","/code/entrypoint.sh"]
