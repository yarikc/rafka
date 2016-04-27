# -*- coding: utf-8 -*-

import argparse
import logging
import sys

import falcon
import pykafka
import six
from gevent.pywsgi import WSGIServer

log = logging.getLogger('rafka')

class KafkaResource(object):
    def __init__(self, **kwa):
        self.producers_by_topic = {}
        brokers = kwa.pop('brokers')
        self.client = pykafka.KafkaClient(hosts=brokers)

    def producer(self, topic):
        topic = six.b(topic)
        try:
            return self.producers_by_topic[topic]
        except KeyError:
            self.producers_by_topic[topic] = self.client.topics[topic].get_producer()
            return self.producers_by_topic[topic]

    def on_post(self, req, resp, topic):
        """Handles POST requests"""
        # message = req.get_param('message')
        # self.producer(topic).produce(message)
        msg = bytes()
        while True:
            chunk = req.stream.read(4096)
            #print ("->%s<-" % chunk)
            if not chunk:
                break
            msg += chunk
        self.producer(topic).produce(msg)
        resp.status = falcon.HTTP_201  # This is the default status
        resp.body = ('\nyou sent:.\n'
                     '\n'
                     '    ~ %s bytes\n\n' % len(msg))


    def on_get(self, req, resp, topic=None):
        resp.status = falcon.HTTP_200  # This is the default status
        resp.body = ('\nWelcome to the Kafka Proxy!\n\n')

def main(argv=sys.argv):
    parser = argparse.ArgumentParser(description='A rest proxy to kafka')
    parser.add_argument('--logging-level', choices=['DEBUG', 'INFO', 'WARN', 'ERROR', 'CRITICAL'], default='ERROR',
                        help='logging level, default: ERROR')
    parser.add_argument('--proxy-host',  default='', help='proxy host')
    parser.add_argument('--proxy-port', type=int, default=6666, help='proxy port')
    parser.add_argument('--proxy-read-buff', type=int, default=4096, help='read buffer')

    parser.add_argument('--kafka-brokers',  default='guedlpahdp002.devfg.rbc.com:9092,'+
                        'guedlpahdp003.devfg.rbc.com:9092,'+
                        'guedlpahdp004.devfg.rbc.com:9092',
                        help='host and ports of kafka brokers')
    parser.add_argument('--kafka-compression', type=int, default=0, help='he type of compression to use.')
    parser.add_argument('--kafka-max-retries',  type=int, default=3,
                        help=' How many times to attempt to produce a given batch of messages before raising an error.')
    parser.add_argument('--kafka-retry-backoff-ms',  type=int, default=100,
                        help='The amount of time (in milliseconds) to back off during produce request retries.')
    parser.add_argument('--kafka-required-acks',   type=int, default=1,
                        help=' The number of other brokers that must have committed the data to their log and'+
                             'acknowledged this to the leader before a request is considered complete')
    parser.add_argument('--kafka-ack-timeout-ms',  type=int, default=10000,
                        help=' The amount of time (in milliseconds) to wait for acknowledgment of a produce request.')
    parser.add_argument('--kafka-max-queued-messages',  type=int, default=100000,
                        help='The maximum number of messages the producer can have waiting to be sent to the broker.')
    parser.add_argument('--kafka-min-queued-messages',   type=int, default=70000,
                        help=' The minimum number of messages the producer can have waiting in a queue before it'+
                             ' flushes that queue to its broker (must be greater than 0).')
    parser.add_argument('--kafka-linger-ms',  type=int, default=5000,
                        help='This setting gives the upper bound on the delay for batching')
    parser.add_argument('--kafka-block-on-queue-full', action='store_true', default=True,
                        help='If True, this setting indicates we should block until space is available in the queue.'+
                             ' If False, we should throw an error immediately.')
    parser.add_argument('--kafka-max-request-size',   type=int, default=1000012,
                        help='The maximum size of a request in bytes. ')

    args = parser.parse_args(argv[1:])
    app = falcon.API()
    kafka = None
    try:
        kafka = KafkaResource(brokers = args.kafka_brokers)
        app.add_route('/{topic}', kafka)
        logging.basicConfig(format='%(asctime)s %(levelname)s:%(message)s', level=getattr(logging, args.logging_level) )
        WSGIServer((args.proxy_host, args.proxy_port), app).serve_forever()

    except KeyboardInterrupt:
        log.warn("ctrl-c out of rafka")
        raise
    except SystemExit:
        log.warn("exiting rafka")
        raise
    except:
        log.exception("crashing out of rafka")
        raise
    finally:
        if kafka:
            log.info("closing down producers")
            for topic in kafka.producers_by_topic:
                log.info("closing down producer[%s]", topic)
                kafka.producers_by_topic[topic].stop()

if __name__ == '__main__':
    main()
