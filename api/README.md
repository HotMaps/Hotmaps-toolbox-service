# HotMaps-toolbox Docker image

This Docker image offers a GIS Flask + uWSGI + Nginx setup to run a webservice in Python 3.6.
It is based on Ubuntu 16.04.

### Software installed:
#### Basic software
* GRASS GIS 7.2
* Python 3.6
* Python 2.7 (to be compatible with GRASS GIS that currently only supports Python 2.7)
* Flask 0.12
* Flask-RESTful 0.3.5
* Flask-Login 0.4.0
* Flask-Bcrypt 0.5
* Geoalchemy2
#### Services
* nginx
* uWSGI
* supervisor

### Build and run:
#### Build
To build this image from Dockerfile run this command in your Docker or Docker Toolbox shell:

`docker build -t hotmaps/toolbox .`

### Setup celery

start celery:
`celery -A celery_worker.celery worker --loglevel=info`



### Setup flower
celery -A celery_worker.celery flower --port=5555
### Setup rabbitMq
by default rabbitmq server will run on the port 5672
#### Setup rabbitMq server on the OS

start a rabbitmq server installed in the system :
`sudo service rabbitmq-server start`

check the status of the server :
`sudo rabbitmqctl status`

#### Install redis on the OS
Add the repository, update your APT cache and install redis

` wget -q -O - http://www.dotdeb.org/dotdeb.gpg | sudo apt-key add - `

`sudo apt-get update`

`sudo apt-get install redis-server`

#### Setup redis
by default redis server will run on the port 6379
#### Setup redis server on the OS

start a redis server installed in the system :
`sudo service redis-server start`

check the status of the server :
`sudo service redis-server status`

#### Run

**Important:** Before running make sure you have a directory containing some code. This directory will be linked to the volume of the container. Here is the most basic file that needs to be in that directory*:

**wsgi.py**

    # -*- coding: utf-8 -*-
    
    from flask import Flask
    
    
    application = Flask(__name__)
    
    @application.route('/', methods=['GET'])
    def index():
    return 'Hello World!'
    
    def test():
    application.run(debug=True)
    
    if __name__ == '__main__':
    test()
    

You can edit this file afterward and replace it with your own code.

To create a container use this command*:

`docker run -d -v "`*absolute/path/to/your/code*`:/data" -p 8181:80 -it hotmaps/res-potential`

On Windows the absolute path to your code directory should be in the format */c/My-first-dir/my-second-dir/my-code-dir*

**Note that you can pull the image directly from the repository with this same command but make sure you have a "data" directory (linked to the volume -v) containing some working code (see example above).*

After successfuly running this command, open your web browser and go to `{ip-of-your-docker-host}:8181`

If you don't know the IP address of your docker machine type `docker-machine ip` in your terminal.

### How to add your own application

To place your own code, go to the directory linked with your volume that your previously created (cf. Build) and replace the *wsgi.py* content with your own code. Note that this file is your entry point to the site.

Note that if you build this image from scratch, uWSGI chdirs to root path of the shared volume "data" so in uwsgi.ini you will need to make sure the python path to the *wsgi.py* file is relative to that if you want to do any changes.

### Credits

**Special thanks** to the work done on the repository [https://github.com/atupal/dockerfile.flask-uwsgi-nginx](https://github.com/atupal/dockerfile.flask-uwsgi-nginx) that helped me build a basic and working setup of Flask, uWSGI and Nginx.

