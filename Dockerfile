# should be 1.0.2
ARG ENGINE_VERSION=latest

FROM docker.pkg.github.com/ovh/serving-runtime/api-full:${ENGINE_VERSION}

USER root

RUN yum update -y && yum upgrade -y

RUN yum install -y gcc gcc-c++ make psmisc

RUN yum install -y python3 python3-pip python3-wheel

RUN pip3 install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./requirements.dev.txt /app/requirements.dev.txt

RUN pip3 install -r requirements.dev.txt

COPY ./interpretability_engine /app/interpretability_engine/

COPY ./tests /app/tests/

COPY ./misc /app/misc/

COPY ./bin /app/bin/

COPY ./setup.py /app/
