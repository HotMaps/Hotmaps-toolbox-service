# hotmaps/toolbox-backend image Dockerfile

FROM geographica/gdal2:latest

ENV CELERY_BROKER_URL amqp://admin:mypass@rabbit:5672/
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true
ARG DEBIAN_FRONTEND=noninteractive

LABEL maintainers="lesly Houndole <lesly.houndole@crem.ch>, Daniel Hunacek <daniel.hunacek@hevs.ch>"


# setup volume
RUN mkdir -p /data
VOLUME /data

RUN mkdir -p /var/hotmaps/users

# Install required software
RUN apt-get update && apt-get autoremove -y
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
    make \
    ssh \
    && apt-get autoremove \
    && apt-get clean

# Setup app server
RUN mkdir -p /data

# Install required python modules
COPY api/requirements/api/requirements.txt /api/api/requirements/api/requirements.txt
WORKDIR /api

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get install -y \
    build-essential \
    software-properties-common \
    wget

RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3 get-pip.py


RUN pip3 install -r requirements/api/requirements.txt
RUN pip3 install gunicorn

# Copy app source code
COPY . /api

EXPOSE 80

# Start server
RUN apt-get update && apt-get install -y supervisor
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# CMD ["gunicorn", "--config", "gunicorn-config.py", "--log-config", "app/logging.conf", "run:application"]

# Start processes
CMD ["/usr/bin/supervisord"]


