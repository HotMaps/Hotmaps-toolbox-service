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
	#curl \
	#build-essential \
	#zlib1g-dev \
	#checkinstall \
	#libreadline-gplv2-dev \
	#libncursesw5-dev \
	#libssl-dev \
	#libsqlite3-dev \
	#tk-dev \
	#libgdbm-dev \
	#libc6-dev \
	#libbz2-dev \
	python3.6 \
	python3.6-dev \
	python3.6-venv \
	libgeos-dev 

	
RUN wget https://bootstrap.pypa.io/get-pip.py
RUN python3.6 get-pip.py
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python3
#RUN ln -s /usr/local/bin/pip /usr/local/bin/pip3


# Install Python 3.6 as python3
#WORKDIR /usr/src
#RUN wget https://www.python.org/ftp/python/3.6.0/Python-3.6.0.tgz
#RUN tar xzf Python-3.6.0.tgz
#WORKDIR /usr/src/Python-3.6.0
#RUN ./configure
#RUN make install
#WORKDIR /usr/src
#RUN rm -r Python-3.6.0.tgz



# Make Python3.6 default
RUN ln -s /usr/bin/python3.6 /usr/local/bin/python

# Install our settings
#ADD . /home/docker/settings/


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
