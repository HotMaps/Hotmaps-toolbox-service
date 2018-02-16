#
# hotmaps/toolbox-backend image Dockerfile
#
#

FROM ubuntu:16.04

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
COPY gunicorn-config.py /data/gunicorn-config.py
RUN pip install gunicorn

# Install required python modules
COPY requirements.txt /data/requirements.txt
RUN pip install -r /data/requirements.txt

# Copy app source code
COPY app /data

WORKDIR /data

EXPOSE 80

# Start server
CMD ["gunicorn", "--config", "/data/gunicorn-config.py", "--log-config", "/data/logging.conf", "wsgi:application"]
