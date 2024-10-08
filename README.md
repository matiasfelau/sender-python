# sender-python

## Descripción
Este es un proyecto académico para la UADE, un paquete que permite la comunicación entre los distintos módulos a través del Core.

## Tabla de Contenidos
- [Instalación](#instalación)
- [Uso](#uso)
- [Ejemplo](#ejemplo)

## Instalación
Para instalar el paquete abrí una terminal en el directorio del proyecto y escribí:
```bash
pip install Squad1CoreSender
```

## Uso
Usá el proyecto de la siguiente manera:
1. Iniciá dos conexiones con el servidor, una será para enviar mensajes y la otra para recibirlos. 
La conexión te va a pedir especificar un host, un puerto, un usuario y una contraseña. Todos los datos te van a ser dados por el Squad del Core.
2. Definí una función de callback, o sea lo que va a hacer tu aplicación cada vez que reciba un mensaje. Esto te va a permitir procesarlo.
Es importante aclarar que los mensajes viajan en formato de bytes[] así que será necesario usar decode.
3. Iniciá el servicio consumidor dándole una conexión e indicándole cuál es tu módulo, el cual estará restringido por el enum Modules.
Es importante aclarar que invocar a esta función bloqueará un hilo de procesamiento para estar permanentemente a la escucha.
4. Por último, podés usar el método publish para enviar mensajes a cualquier módulo válido. También se encuentra restringido por el enum Modules.
Necesitarás ingresar por parámetro una conexión (distinta a la del servicio consumidor), el mensaje en formato String, el nombre del módulo de origen, el de destino y el caso de uso que genera al mensaje.
Recomendamos cerrar la conexión usada después de enviar un mensaje, o un lote de ellos, y abrir una nueva cuando vuelva a ser necesaria.

## ACLARACIÓN

Tené en cuenta que la conexión es un objeto del tipo AutoCloseable, por lo que deberías manejar las excepciones e implementar una lógica de reconexión.

## Ejemplo
```Python
import os

import sender
from sender import *

pool_connections = []

#Abro tantas conexiones como quiera.
for i in range(2):
    pool_connections.append(
        start_connection(
            os.getenv('HOST'),
            os.getenv('PORT'),
            os.getenv('USER'),
            os.getenv('PASSWORD')
        )
    )

def new_callback(ch, method, properties, body):
    #Este sería el JSON que encapsula a los datos enviados desde el módulo de origen.
    #   .loads() convertirá el byte[] en un objeto manejable de Python
    #   .dumps() convertirá el byte[] de vuelta en un JSON (formatted String)
    message = json.loads(body.decode('utf-8'))

    #Estos serían los datos enviados desde el módulo de origen.
    payload = message.get('payload')

#Esta línea es esencial para el funcionamiento del servicio consumidor.
sender.callback = new_callback

start_consumer(pool_connections[0], Modules.USUARIO.value)

publish(pool_connections[1], '¡Hola, mundo!', Modules.USUARIO.value, Modules.USUARIO.value, 'Prueba')

close_connection(pool_connections[1])
```
