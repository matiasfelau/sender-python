#!/usr/bin/env python
import json
import threading

import pika
from Enumerations import Modules


def start_connection(host, port, username, password):
    """
    Inicia una conexión de RabbitMQ.
    :param host: Dirección IP del servidor Core.
    :param port: Puerto de la aplicación RabbitMQ.
    :param username: Nombre de usuario de las credenciales asignadas al módulo.
    :param password: Contraseña de las credenciales asignadas al módulo.
    :return: Conexión con RabbitMQ o None si ocurrió una excepción.
    """
    try:
        connection = pika.BlockingConnection(pika.ConnectionParameters(
            host=host,
            port=port,
            credentials=pika.PlainCredentials(
                username,
                password)))
        return connection
    except Exception as e:
        print(f'\nError in sender.start_rabbitmq_connection(): \n{str(e)}')
        return None


def check_valid_module(module):
    """
    Verifica que el módulo sea un publisher válido encontrándose en el enumeration PossiblePublishers.
    :param module: Requiere el nombre del módulo que se validará.
    :return: Devuelve un boolean indicando si es un módulo válido o no.
    """
    return module in Modules


def close_connection(connection):
    """
    Cierra una conexión de RabbitMQ.
    Una buena práctica sería iniciar una nueva conexión para usar publish() y cerrarla posteriormente.
    :param connection: Conexión de RabbitMQ dada por el método start_rabbitmq_connection().
    :return:
    """
    try:
        connection.close()
    except Exception as e:
        print(f'\nError in sender.close_rabbitmq_connection(): \n{str(e)}')


def publish(connection, message, origin, destination, use_case):
    """
    Envia un mensaje al módulo de destino.
    Convierte el mensaje automáticamente a un JSON.
    :param connection: Conexión de RabbitMQ dada por el método start_rabbitmq_connection().
    :param message: Diccionario que contenga la información que debe recibir el módulo de destino.
    :param origin: Módulo desde el que se está enviando el mensaje.
    :param destination: Módulo de destino del mensaje.
    :param use_case: Caso de uso que originó la información.
    :return:
    """
    try:
        if destination not in Modules:
            raise Exception
        body = {
            'origin': origin,
            'destination': destination,
            'case': use_case,
            'payload': message,
            'status': '0'
        }
        data = json.dumps(body).encode('utf-8')
        channel = connection.channel()
        channel.exchange_declare(exchange='core', exchange_type='direct')
        channel.basic_publish(exchange='core', routing_key='core', body=data)
    except Exception as e:
        print(f'\nError in sender.publish(): \n{str(e)}')


def start_consumer(connection, module):
    """
    Inicializa el consumo de los mensajes que llegan al módulo.
    Una vez iniciado no puede detenerse hasta cerrar la aplicación o ante una caída del servicio de RabbitMQ.
    :param connection: Conexión de RabbitMQ dada por el método start_rabbitmq_connection().
    :param module:
    :return:
    """
    try:
        if module not in Modules:
            raise Exception
        t1 = threading.Thread(
            target=_consume,
            args=(connection, module,),
            name='consumer'
        )
        t1.start()
    except Exception as e:
        print(f'\nError in sender.initialize_consumer_with_thread(): \n{str(e)}')


def callback(ch, method, properties, body):
    """
    Define el algoritmo que se ejecutará al recibir un nuevo mensaje.
    Es necesario implementar body.decode('utf-8') dentro del bloque de la función.
    :param ch:
    :param method:
    :param properties: Headers del mensaje.
    :param body: Mensaje. Es el único parámetro que se debería usar
    :return:
    """
    pass


def _consume(connection, module):
    """
    Método protegido que enlaza un hilo con su callback.
    :param connection: Conexión con RabbitMQ.
    :param module: Módulo desde el que se envian los mensajes.
    :return: Canal desde el que se está consumiendo o None si ocurre una excepción.
    """
    try:
        channel = connection.channel()
        channel.queue_declare(
            queue=module,
            exclusive=False,
            durable=True,
            arguments={
                'x-dead-letter-exchange': f'{module}.trapping',
                'x-dead-letter-routing-key': f'{module}.trapping'
            })
        channel.basic_consume(
            queue=module,
            on_message_callback=callback,
            auto_ack=True
        )
        channel.start_consuming()
        return channel
    except Exception as e:
        print(f'\nError in sender.initialize_consumer_with_thread(): \n{str(e)}')
        return None
