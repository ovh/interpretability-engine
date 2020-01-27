ARG ENGINE_VERSION=1.0.2

FROM yjockshk.gra5.container-registry.ovh.net/infaas/serving-engine-base:${ENGINE_VERSION}

USER root

RUN yum update -y && yum upgrade -y

RUN yum install -y gcc gcc-c++ make

RUN yum install -y python3 python3-pip

RUN pip3 install --upgrade pip

COPY ./requirements.txt /app/requirements.txt

WORKDIR /app

RUN pip3 install -r requirements.txt

COPY ./requirements.dev.txt /app/requirements.dev.txt

RUN pip3 install -r requirements.dev.txt

RUN yum install -y psmisc
