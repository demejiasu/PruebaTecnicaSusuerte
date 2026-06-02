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

   pip install -r requirements.txt

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

## Decisiones tecnicas (Paso 2 - Modelos de datos)

### Diseno de las tablas

Se crearon dos modelos que reflejan exactamente el esquema base del enunciado:

**Usuario (tabla usuarios):**
- id: clave primaria autoincremental (la genera Django automaticamente).
- nombre: texto de hasta 255 caracteres.
- saldo: decimal de hasta 10 digitos con 2 decimales, valor por defecto 0.
- creado_en: fecha y hora de creacion, se asigna automaticamente al crear el registro.

**Tiquete (tabla tiquetes):**
- id: clave primaria autoincremental.
- usuario_id: clave foranea que referencia a usuarios.id. Se uso CASCADE para que al eliminar un usuario se eliminen sus tiquetes.
- monto: decimal de hasta 10 digitos con 2 decimales.
- estado: puede ser 'ganador', 'perdedor' o 'pendiente' (por defecto 'pendiente').
- creado_en: fecha y hora de creacion automatica.

Se agregaron los siguientes indices para optimizar las consultas:
- idx_usuario_nombre: sobre el campo nombre de usuarios, util para busquedas por nombre.
- idx_tiquete_usuario_estado: indice compuesto sobre usuario_id y estado en tiquetes, optimiza la consulta de tiquetes por usuario y estado.
- idx_tiquete_creado_en: sobre la fecha de creacion, util para ordenar o filtrar por fecha.

### Por que clave foranea con CASCADE

La relacion entre tiquete y usuario es de muchos a uno (un usuario puede tener muchos tiquetes). Se uso CASCADE en el on_delete para que si un usuario se elimina, todos sus tiquetes se eliminen en cascada. Esto evita registros huerfanos en la base de datos.

### Por que DecimalField para saldo y monto

Se eligio DecimalField en lugar de FloatField porque los valores monetarios requieren precision exacta. FloatField puede introducir errores de redondeo (por ejemplo, 0.1 + 0.2 = 0.30000000000000004). DecimalField almacena el valor exacto.

### Consultas SQL incluidas

En el archivo docs/sql/consultas.sql se incluyen:

1. Las sentencias CREATE TABLE con indices (equivalente a lo que genera Django).
2. La consulta para obtener los 3 usuarios con mayor monto total apostado en tiquetes ganadores. Usa INNER JOIN, GROUP BY, SUM, ORDER BY DESC y LIMIT.
3. La consulta para listar usuarios sin tiquetes registrados. Se usa LEFT JOIN con filtro WHERE t.id IS NULL, que es la forma mas eficiente en SQLite.

### Explicacion de transacciones (Parte 2.4)

Al registrar un tiquete que descuenta saldo del usuario, ocurren dos operaciones que deben ser atomicas:

1. Insertar el tiquete en la tabla tiquetes.
2. Actualizar (descontar) el saldo en la tabla usuarios.

Si no se usa una transaccion, una fallo entre el paso 1 y el paso 2 dejaria datos inconsistentes (tiquete registrado sin descuento). Con una transaccion, si algo falla se hace ROLLBACK y la base de datos vuelve al estado anterior. En Django esto se implementa con el decorador/context manager transaction.atomic().

## Avance hasta ahora

- Proyecto Django inicializado con Python 3.14 y Django 6.0.2.
- Django REST Framework 3.16.1 instalado y configurado.
- Aplicacion tickets creada.
- .gitignore configurado.
- SQLite como base de datos de desarrollo.
- Modelos Usuario y Tiquete creados con campos, claves foraneas e indices apropiados.
- Migraciones generadas y aplicadas a la base de datos.
- Archivo docs/sql/consultas.sql con las consultas de la Parte 2.
- Documentacion de decisiones tecnicas sobre el esquema de datos.

El siguiente paso sera crear los endpoints de la API (Parte 3) y exponerlos via Django REST Framework.
