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

## Decisiones tecnicas (Parte 1 - PHP y Recursividad)

### Funcion recursiva calcularPremioAcumulado

Se implemento la funcion en el archivo php/calcular_premio.php. La funcion recorre un arbol de premios anidados sin usar bucles, solo recursion.

**Estructura de cada nodo:**
- monto: valor numerico del premio en ese nivel.
- hijos: arreglo de nodos hijos (puede estar vacio).

**Algoritmo:**
1. Caso base: si el arreglo de niveles esta vacio, retorna 0. Esto detiene la recursion cuando se han procesado todos los nodos de un nivel.
2. Toma el primer elemento del arreglo con array_shift, que reduce el arreglo original.
3. Suma el monto del nodo actual mas el resultado de procesar recursivamente sus hijos.
4. Suma el resultado de procesar recursivamente los nodos restantes del mismo nivel.

**Por que array_shift en lugar de foreach:**
El enunciado pide explicitamente no usar bucles. array_shift extrae el primer elemento y acorta el arreglo, permitiendo que la recursion procese los elementos uno por uno sin iteracion.

**Resultado con el ejemplo del enunciado:**
- Nodo raiz: 1000
  - Hijo 1: 500
  - Hijo 2: 250
    - Hijo: 100
- Total: 1000 + 500 + 250 + 100 = 1850

**Explicacion del caso base:**
El caso base es cuando empty($niveles) retorna true, es decir, cuando el arreglo de niveles no tiene elementos. En ese punto se retorna 0 y se termina la recursion.

**Que ocurre con una estructura muy profunda (limite de stack):**
PHP tiene un limite de recursion configurable mediante xdebug.max_nesting_level o la directiva de XDebug. En entornos de produccion sin XDebug, el limite lo impone la memoria del stack de C. Si el arbol es demasiado profundo (tipicamente mas de 100-200 niveles en PHP estandar, o 256-512 con XDebug por defecto), se produce un error "Maximum function nesting level reached" o un segmentation fault. Para arboles muy profundos seria necesario convertir la funcion a una iterativa usando una pila explicita (array con array_push/array_pop), pero para la mayoria de los casos de uso reales la recursion es suficiente.

Para ejecutar la funcion:
    php php/calcular_premio.php

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

## Decisiones tecnicas (Paso 3 - API REST)

### Diseno de los endpoints

Se crearon dos endpoints REST que cumplen con los requisitos de la Parte 3:

**POST /api/tiquetes/**

Recibe un JSON con usuario_id y monto. La logica interna es:

1. Validar que el JSON tenga los campos requeridos (usuario_id y monto). Si falta alguno, responde 400.
2. Buscar al usuario por ID. Si no existe, responde 404.
3. Verificar que el saldo del usuario sea suficiente para cubrir el monto del tiquete. Si no, responde 422.
4. Dentro de una transaccion atomica, descontar el saldo del usuario y crear el tiquete con estado 'pendiente'.
5. Si todo sale bien, responde 201 con los datos del tiquete creado.
6. Si ocurre un error inesperado (excepcion en la transaccion), responde 500.

**GET /api/usuarios/{id}/tiquetes/**

1. Verificar que el usuario existe. Si no, responde 404.
2. Obtener todos los tiquetes del usuario ordenados por fecha de creacion descendente.
3. Responder 200 con la lista de tiquetes en formato JSON.

### Por que usar @api_view en lugar de ViewSets

Se eligio usar funciones decoradas con @api_view en lugar de las clases ViewSet o ModelViewSet de DRF por las siguientes razones:

- El enunciado pide codigos HTTP especificos y distintos para cada situacion. Con funciones es mas claro y explicito devolver cada Response con su status code.
- La logica de negocio (validar saldo, descontar dentro de una transaccion) es mas facil de leer y mantener en una funcion que en una vista generica.
- Para dos endpoints simples no se justifica la abstraccion de un ViewSet.

### Transaccion atomica con transaction.atomic()

Para el endpoint POST se uso el context manager transaction.atomic() de Django. Esto asegura que tanto el descuento de saldo como la creacion del tiquete se ejecuten como una sola operacion atomica. Si cualquiera de las dos falla, se hace rollback automaticamente y la base de datos queda como estaba antes.

Se uso Usuario.objects.filter(pk=...).update() en lugar de usuario.save() para evitar un race condition: filter+update se ejecuta en una sola consulta SQL, mientras que get+save requiere dos consultas (SELECT y UPDATE) y deja una ventana para que otro proceso modifique el saldo entre medio.

### Codigos HTTP implementados

| Situacion | Codigo HTTP | Mensaje |
|-----------|-------------|---------|
| Tiquete creado correctamente | 201 | Datos del tiquete en JSON |
| JSON invalido o campos faltantes | 400 | "JSON invalido o campos faltantes" |
| Usuario no existe | 404 | "Usuario no encontrado" |
| Saldo insuficiente | 422 | "Saldo insuficiente" |
| Error inesperado del servidor | 500 | "Error inesperado del servidor" |

### Datos de prueba

El archivo tickets/seed_data.py contiene un script para poblar la base de datos con datos de prueba. Se ejecuta con:

    python manage.py shell < tickets/seed_data.py

Los datos incluyen 5 usuarios (con saldos entre 150 y 3000) y varios tiquetes en estados ganador y perdedor. Un usuario (Pedro Ramirez) no tiene tiquetes, lo que permite probar la consulta de la Parte 2.3.

### Ejemplos de uso con curl

**Crear un tiquete (exitoso):**

    curl -X POST http://localhost:8000/api/tiquetes/ \
      -H "Content-Type: application/json" \
      -d '{"usuario_id": 1, "monto": 100}'

**Crear un tiquete (saldo insuficiente):**

    curl -X POST http://localhost:8000/api/tiquetes/ \
      -H "Content-Type: application/json" \
      -d '{"usuario_id": 4, "monto": 9999}'

**Listar tiquetes de un usuario:**

    curl http://localhost:8000/api/usuarios/1/tiquetes/

## Decisiones tecnicas (Paso 4 - Frontend)

### Diseno de la pagina web

Se creo una pagina web en tickets/templates/tickets/index.html que se sirve en la raiz del sitio (http://localhost:8000/). La pagina contiene:

**Formulario de envio:**
- Campo para el ID del usuario (numerico, obligatorio).
- Campo para el monto a apostar (numerico con decimales, obligatorio).
- Boton de envio que se deshabilita mientras se procesa la solicitud para evitar envios duplicados.

**Mensajes diferenciados segun codigo HTTP:**
- Exito (201): mensaje en verde con el numero de tiquete, monto y saldo restante del usuario.
- JSON invalido (400): mensaje en rojo.
- Usuario no encontrado (404): mensaje en amarillo indicando el ID del usuario.
- Saldo insuficiente (422): mensaje en amarillo.
- Error del servidor (500): mensaje en rojo.
- Error de conexion: mensaje en rojo si no se puede contactar al servidor.

**Lista de tiquetes en el DOM:**
- Los tiquetes creados exitosamente se agregan al inicio de la lista sin recargar la pagina.
- Cada tiquete muestra su ID, usuario, monto, fecha de creacion y estado (con codigo de colores: pendiente en amarillo, ganador en verde, perdedor en rojo).
- Si no hay tiquetes, se muestra un mensaje placeholder.

### Por que una sola pagina HTML con JavaScript vanilla

- El enunciado pide explicitamente una pagina index.html y no especifica un framework frontend.
- JavaScript vanilla con fetch es suficiente para hacer llamadas a la API y manipular el DOM sin necesidad de librerias externas.
- Mantiene el proyecto simple: no requiere Node.js, npm, webpack ni nada adicional para funcionar.
- El estilo CSS esta incluido en el mismo archivo para que sea autocontenido.

### Integracion con Django

La pagina se sirve a traves de una vista TemplateView de Django que renderiza el template. Esto permite que el frontend y el backend compartan el mismo servidor en desarrollo sin necesidad de configurar CORS ni servidores separados.

## Decisiones tecnicas (Parte 6 - Mejora Creativa: Validacion Antifraude)

### Que se implemento

Se agrego un modulo de validacion antifraude en tickets/antifraud.py que se ejecuta antes de procesar cualquier creacion de tiquete. Contiene dos mecanismos:

**1. Rate limiting (limite de frecuencia):**
- Un usuario no puede crear mas de 5 tiquetes en una ventana de 60 segundos.
- Si excede el limite, se bloquea automaticamente por 5 minutos.
- Se usa el cache de Django en memoria (locmem) para llevar el contador, que se reinicia solo despues de la ventana de tiempo.
- La respuesta HTTP es 429 (Too Many Requests) con un mensaje explicativo.
- Esto evita que un script automatizado pueda inundar el sistema de tiquetes en poco tiempo.

**2. Validacion de monto sospechoso:**
- Antes de crear un tiquete, se calcula el promedio de los ultimos 10 tiquetes del usuario.
- Si el monto actual supera el doble del promedio historico, se rechaza la operacion.
- La respuesta HTTP es 409 (Conflict) con un mensaje explicativo.
- Esto detecta comportamientos anormales, como un usuario que siempre apuesta montos pequenos y de repente intenta apostar una cantidad muy grande.

### Por que se eligio esta mejora

- Tiene valor directo para el negocio: protege tanto al sistema como a los usuarios de actividades fraudulentas.
- Es facil de justificar: cualquier sistema de apuestas o tiquetes necesita controles antifraude basicos para ser viable en produccion.
- Usa recursos minimos: el cache en memoria no requiere base de datos adicional.
- Se integra de forma no invasiva: las validaciones se ejecutan antes de la logica existente sin modificar el flujo de transacciones.

### Si tuviera mas tiempo (mejoras adicionales que dejaria pendientes)

- Almacenar los bloqueos en base de datos en lugar de cache en memoria, para que persistan incluso si el servidor se reinicia.
- Agregar un sistema de notificaciones al administrador cuando se detecte actividad sospechosa (por email o en un panel de administracion).
- Implementar un puntaje de riesgo por usuario que considere multiples factores (frecuencia, monto, hora del dia, ubicacion geografica) en lugar de solo dos reglas independientes.
- Crear una pagina de administracion para ver usuarios bloqueados y liberarlos manualmente.

## Si tuviera mas tiempo (reflexion general sobre todo el proyecto)

Ademas de la validacion antifraude, hay varias mejoras que implementaria si tuviera mas tiempo:

- Paginacion en el endpoint GET /api/usuarios/{id}/tiquetes/ para manejar grandes volumenes de datos.
- Autenticacion y autorizacion con JWT para que cada usuario solo pueda ver y crear sus propios tiquetes.
- Pruebas automatizadas (unitarias y de integracion) con pytest y el cliente de prueba de Django REST Framework.
- Contenedor Docker para facilitar la instalacion y ejecucion en cualquier entorno.
- Migrar de SQLite a PostgreSQL para mejor rendimiento y concurrencia en produccion.
- Un frontend mas completo con Vue.js o React para mejor experiencia de usuario.

## Avance hasta ahora

- Proyecto Django inicializado con Python 3.14 y Django 6.0.2.
- Django REST Framework 3.16.1 instalado y configurado.
- Aplicacion tickets creada.
- .gitignore configurado.
- SQLite como base de datos de desarrollo.
- Modelos Usuario y Tiquete creados con campos, claves foraneas e indices apropiados.
- Migraciones generadas y aplicadas a la base de datos.
- Archivo docs/sql/consultas.sql con las consultas de la Parte 2.
- Endpoint POST /api/tiquetes/ con manejo de codigos 201, 400, 404, 422, 500 y los nuevos 409, 429.
- Endpoint GET /api/usuarios/{id}/tiquetes/ con manejo de codigos 200 y 404.
- Transaccion atomica con transaction.atomic() para descontar saldo y crear tiquete.
- Datos de prueba en tickets/seed_data.py.
- Panel de administracion Django en /admin/ para gestionar usuarios y tiquetes.
- Pagina web frontend en http://localhost:8000/ con formulario, mensajes diferenciados y lista de tiquetes en el DOM sin recargar la pagina.
- Modulo de validacion antifraude con rate limiting (429) y deteccion de montos sospechosos (409).
