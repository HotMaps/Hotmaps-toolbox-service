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
RUN apt-get install -y \
	software-properties-common \
    wget

RUN add-apt-repository ppa:jonathonf/python-3.6

RUN apt-get update && apt-get install -y \
	python3.6 \
	python3.6-dev \
	python3.6-venv \
	libgeos-dev 

	
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python3

# Make Python3.6 default
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python

# Setup app server
RUN mkdir -p /data
COPY gunicorn-config.py /data/gunicorn-config.py
RUN pip3 install gunicorn

# Install required python modules
COPY requirements.txt /data/requirements.txt
RUN pip3 install -r /data/requirements.txt

# Copy app source code
COPY app /data

WORKDIR /data

EXPOSE 80

# Start server
CMD ["gunicorn", "--config", "/data/gunicorn-config.py", "--log-config", "/data/logging.conf", "wsgi:application"]
