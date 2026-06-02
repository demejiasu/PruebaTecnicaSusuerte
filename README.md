# Prueba Tecnica - Sistema de Tiquetes

## Instalacion y ejecucion

### Requisitos

- Python 3.14 o superior
- pip (gestor de paquetes de Python)

### Pasos para ejecutar el proyecto

1. Clonar el repositorio
2. Crear un entorno virtual (opcional pero recomendado):

   python -m venv venv
   source venv/bin/activate  # En Linux/Mac
   venv\Scripts\activate     # En Windows

3. Instalar las dependencias:

   pip install django djangorestframework

4. Ejecutar las migraciones:

   python manage.py migrate

5. Iniciar el servidor de desarrollo:

   python manage.py runserver

El servidor estara disponible en http://localhost:8000.

## Decisiones tecnicas (Paso 1 - Configuracion inicial)

### Framework elegido: Django + Django REST Framework

Se eligio Django porque el enunciado pide un endpoint REST en PHP, pero como se acordó hacerlo en Django, se optó por este framework por las siguientes razones:

- Django viene con ORM propio que permite modelar las tablas usuarios y tiquetes de forma natural.
- Django REST Framework (DRF) proporciona una capa adicional para construir APIs RESTful con manejo explicito de codigos HTTP (201, 400, 404, 422, 500), que es justamente lo que pide la Parte 3 de la prueba.
- La funcion transaction.atomic() de Django permite ejecutar operaciones en transacciones de base de datos, necesario para descontar saldo y crear tiquete de forma atomica.

### Base de datos

Se usa SQLite por defecto por su simplicidad para desarrollo. En produccion se migraria a PostgreSQL o MySQL sin cambiar el codigo de los modelos, solo la configuracion en settings.py.

### Estructura del proyecto

El proyecto se organiza en dos modulos principales:

- config/: Configuracion general del proyecto Django (settings, urls, wsgi).
- tickets/: Aplicacion Django que contendra los modelos Usuario y Tiquete, los endpoints de la API y la logica de negocio.

### .gitignore

Se incluye un .gitignore que excluye archivos comunes de Python (__pycache__, .pyc), entornos virtuales, configuraciones del IDE, variables de entorno y la base de datos SQLite (db.sqlite3). Esto evita subir al repositorio archivos que son especificos del entorno de desarrollo de cada persona.

## Avance hasta ahora

- Proyecto Django inicializado con Python 3.14 y Django 6.0.2.
- Django REST Framework 3.16.1 instalado y configurado.
- Aplicacion tickets creada.
- .gitignore configurado.
- SQLite como base de datos de desarrollo.

El siguiente paso sera crear los modelos Usuario y Tiquete que corresponden a la Parte 2 de la prueba (esquema de base de datos relacional).