from enum import Enum

class ConnectionType(str, Enum):
    Amqp091 = "amqp-091",
    Amqp10 = "amqp-10",
    HttpPush = "http-push",
    Mqtt = "mqtt",
    Mqtt5 = "mqtt-5",
    Kafka = "kafka,",
    Hono = "hono",

