FROM python:3.8

RUN apt-get update && apt-get upgrade -y

WORKDIR /app

RUN pip3 install --upgrade pip

RUN pip3 install twine setuptools
