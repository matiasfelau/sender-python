from setuptools import setup, find_packages

setup(
    name="Squad1CoreSender",  # Nombre del paquete
    version="1.0.2",  # Versión del paquete
    description="paquete utilizado para enviar mensajes entre los módulos y el core en un proyecto académico",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",  # Formato del README
    author="matiasfelau",
    author_email="matiasfelau@gmail.com",
    url="https://github.com/matiasfelau/sender-python",  # URL del proyecto
    packages=find_packages(),  # Encuentra todos los módulos automáticamente
    install_requires=[
        'pika',
    ],
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",  # Tipo de licencia
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.6',  # Versión mínima de Python requerida
)
