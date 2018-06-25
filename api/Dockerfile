#
# hotmaps/toolbox-backend image Dockerfile
#
#

FROM ubuntu:16.04

ENV CELERY_BROKER_URL amqp://admin:mypass@rabbit:5672/
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

MAINTAINER Daniel Hunacek <daniel.hunacek@hevs.ch>

# setup volume
RUN mkdir -p /data
VOLUME /data


# Build commands
RUN apt-get update && apt-get dist-upgrade -y && apt-get autoremove -y

# Install required software
RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    software-properties-common \
    wget \
    ca-certificates \
    gcc \
    git \
    libpq-dev \
    libgeos-dev \
    make \
    python-pip \
    python2.7 \
    python2.7-dev \
    ssh \
    && apt-get autoremove \
    && apt-get clean

RUN pip install -U "setuptools==38.5.1"
RUN pip install -U "pip==9.0.1"




# Setup app server
RUN mkdir -p /data
COPY . /api
WORKDIR /api

RUN ls
RUN pip install gunicorn
# Install required python modules

RUN pip install -r requirements.txt

# Copy app source code



EXPOSE 80

# Start server
CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-config", "app/logging.conf", "run_wsgi:application"]



