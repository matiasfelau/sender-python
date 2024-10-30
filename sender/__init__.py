#!/usr/bin/env python
import json
import threading
from enum import Enum

import pika


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
    if module in Modules:
        return True
    else:
        raise Exception


def check_valid_type(type):
    """
    Verifica que el tipo de dato sea válido encontrándose en el enumeration PossibleDataTypes.
    :param type: Requiere el nombre del tipo de dato que se validará.
    :return: Devuelve un boolean indicando si es un tipo de dato válido o no.
    """
    if type in Types:
        return True
    else:
        raise Exception


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


def publish(connection, message, origin, destination, use_case, token, type, target):
    """
    Envia un mensaje al módulo de destino.
    Convierte el mensaje automáticamente a un JSON.
    :param target:
    :param token:
    :param type:
    :param connection: Conexión de RabbitMQ dada por el método start_rabbitmq_connection().
    :param message: Diccionario que contenga la información que debe recibir el módulo de destino.
    :param origin: Módulo desde el que se está enviando el mensaje.
    :param destination: Módulo de destino del mensaje.
    :param use_case: Caso de uso que originó la información.
    :return:
    """
    try:
        check_valid_module(destination)
        check_valid_type(type)
        body = {
            'origin': origin,
            'destination': destination,
            'case': use_case,
            'payload': message,
            'status': '0',
            'token': token,
            'type': type,
            'target': target
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


def convert_body(body):
    """
    Convierte el body de un mensaje a un objeto JSON manejable por Python.
    :param body:
    :return:
    """
    try:
        return json.loads(body.decode('utf-8'))
    except Exception as e:
        print(f'\nError in sender.convert_body(): \n{str(e)}')
        return None


def convert_payload(payload):
    """
    Convierte el payload de un body a un JSON manejable por Python
    :param payload:
    :return:
    """
    try:
        return json.loads(payload)
    except Exception as e:
        print(f'\nError in sender.convert_payload(): \n{str(e)}')
        return None


def convert_class(clase):
    """
    Convierte un objeto en un JSON String para ser enviado a otro módulo.
    :param clase:
    :return:
    """
    try:
        return json.dumps(clase.to_dict())
    except Exception as e:
        print(f'\nError in sender.convert_class(): \n{str(e)}')
        return None


def convert_array(array):
    """
    Convierte un Array de Strings y/o JSON String a un único String que enviar a otro módulo.
    :param array:
    :return:
    """
    try:
        return '--!--##-->>DELIMITER<<--##--!--'.join(array)
    except Exception as e:
        print(f'\nError in sender.convert_array(): \n{str(e)}')
        return None


def convert_string(string):
    """
    Convierte un String con formato de Array a un Array real.
    :param string:
    :return:
    """
    try:
        if string.find("--!--##-->>DELIMITER<<--##--!--") == -1:
            raise Exception
        return string.split("--!--##-->>DELIMITER<<--##--!--")
    except Exception as e:
        print(f'\nError in sender.convert_string(): \n{str(e)}')
        return None


class Modules(Enum):
    E_COMMERCE = 'e_commerce'
    GESTION_FINANCIERA = 'gestion_financiera'
    GESTION_INTERNA = 'gestion_interna'
    USUARIO = 'usuario'


class Types(Enum):
    STRING = 'string'
    JSON = 'json'
    ARRAY = 'array'
