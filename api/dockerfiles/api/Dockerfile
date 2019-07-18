FROM hotmaps/base_cm:latest

ENV CELERY_BROKER_URL amqp://admin:mypass@rabbit:5672/
ENV CELERY_RESULT_BACKEND redis://redis:6379/0
ENV C_FORCE_ROOT true

LABEL maintainers="lesly Houndole <lesly.houndole@crem.ch>, Daniel Hunacek <daniel.hunacek@hevs.ch>"


# setup volume
RUN mkdir -p /data
VOLUME /data

RUN mkdir -p /var/hotmaps/users

# Setup app server
RUN mkdir -p /api/requirements/api
WORKDIR /api

RUN pip3 install gunicorn

COPY requirements/api/requirements.txt requirements/api

RUN pip3 install -r requirements/api/requirements.txt

# Copy app source code
COPY . /api

EXPOSE 80

# Start server
RUN mkdir -p /var/log/supervisor
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Start processes
CMD ["/usr/bin/supervisord"]