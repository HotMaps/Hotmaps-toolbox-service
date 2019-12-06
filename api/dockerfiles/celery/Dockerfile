#
# hotmaps/toolbox-backend image Dockerfile
#
#


#
# hotmaps/cm image Dockerfile
#
#


FROM geographica/gdal2:latest

ENV CELERY_BROKER_URL amqp://admin:mypass@rabbit:5672/
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

MAINTAINER lesly Houndole <lesly.houndole@crem.ch>


# setup volume
RUN mkdir -p /data
VOLUME /data

RUN mkdir -p /var/hotmaps/users


# Build commands
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y

# Install required software

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    software-properties-common \
    wget \
    gdal-bin \
    ca-certificates \
    curl \
    gcc \
    git \
    libpq-dev \
    libgeos-dev \
    libgdal-dev \
    python-gdal \
    make \
    python-pip \
    ssh \
    && apt-get autoremove \
    && apt-get clean






# Setup app server
RUN mkdir -p /data
COPY .. /api
WORKDIR /api

RUN ls

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    software-properties-common \
    wget

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py

RUN pip3 install -r requirements/celery/requirements.txt
RUN pip3 install gunicorn







# Install required python modules


# Copy app source code





COPY . /api
WORKDIR /api

RUN pip3 install -r requirements/requirements_celery_queue.txt

ENTRYPOINT celery -A celery_worker.celery worker --loglevel=info
