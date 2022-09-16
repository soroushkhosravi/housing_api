# Pull official base image
FROM python:3.9.5-slim-buster

# Set work directory
WORKDIR /usr/src/app

# Set env variables
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

# Copy project
COPY . /usr/src/app