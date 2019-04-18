# -*- coding: utf-8 -*-





#!/usr/bin/env python

import uuid
import time
import logging
import pika

from app.model import getCMList,delete_cm
from app import constants


LOG_FORMAT = ('%(levelname) -10s %(asctime)s %(name) -30s %(funcName) '
              '-35s %(lineno) -5d: %(message)s')
LOGGER = logging.getLogger(__name__)


class HeartBeatCalculationModuleProducer(object):
    def __init__(self):
        parameters = pika.URLParameters(constants.CELERY_BROKER_URL)
        self.connection = pika.BlockingConnection(parameters)

        self.channel = self.connection.channel()

        result = self.channel.queue_declare(exclusive=False)
        self.callback_queue = result.method.queue

        self.channel.basic_consume(self.on_response, no_ack=True,
                                   queue=self.callback_queue)

    def on_response(self, ch, method, props, body):
        if self.corr_id == props.correlation_id:
            self.response = body

    def call(self, queue_name):
        self.response = None
        self.corr_id = str(uuid.uuid4())
        self.channel.basic_publish(exchange='',
                                   routing_key=queue_name,
                                   properties=pika.BasicProperties(
                                       reply_to = self.callback_queue,
                                       correlation_id = self.corr_id,
                                   ),
                                   body=queue_name)
        timeout = time.time() + constants.TIMEOUT_DELETE_CM   # 5 minutes from now
        while self.response is None:
            self.connection.process_data_events()
            if time.time() > timeout:
                break
        return self.response






while True :
    listofCM = getCMList()
    start = time. time()
    if len(listofCM)>0:
        for value in enumerate(listofCM):
            time.sleep(constants.TIMEOUT_ALIVE_CM)
            end = time. time()
            print(end - start)


            heart_cm = HeartBeatCalculationModuleProducer()
            cm_id =  value[1]['cm_id']
            print(" [HTAPI] Requesting cm_id = ",cm_id)
            response = heart_cm.call(constants.RPC_CM_ALIVE + str(cm_id))
            if response is not None:
                print("[HTAPI]  is connected to the Calculation module with id: %s ", str(cm_id))
                LOGGER.info("[HTAPI]  is connected to the Calculation module with id: %s ", str(cm_id))
            else:
                LOGGER.info("[HTAPI]  is going to  delete: %s ",str(cm_id))
                delete_cm(str(cm_id))


