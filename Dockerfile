# Use an official Python runtime as a parent image
FROM python:3.9

# Set environment variables
ENV PIP_DISABLE_PIP_VERSION_CHECK 1
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# Set the working directory in the container
WORKDIR /code

# Copy the current directory contents into the container at /usr/src/app
COPY . /code

# Install any needed packages specified in requirements.txt
COPY ./requirements.txt .
RUN pip install -r requirements.txt
