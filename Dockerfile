# Pull official base image
FROM python:3.9.5-slim-buster

# Set work directory
WORKDIR /usr/src/app

# Set env variables
ENV PYTHONWRITEBYTECODE 1
ENV PYTHONBUFFERED 1

# Install runtime packages
RUN apt-get -y update
RUN apt-get -y upgrade
RUN apt-get -y install libpq-dev
RUN apt-get -y install build-essential
# Install dependencies
RUN pip install --upgrade pip
COPY ./requirements.txt /usr/src/app/requirements.txt
RUN pip install -r requirements.txt

EXPOSE 5000

# Copy project
COPY . /usr/src/app