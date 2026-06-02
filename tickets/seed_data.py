"""
Script para poblar la base de datos con datos de prueba.
Ejecutar con: python manage.py shell < tickets/seed_data.py
"""
import django
import os

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from tickets.models import Usuario, Tiquete

# Crear usuarios de prueba
usuario1, _ = Usuario.objects.get_or_create(
    id=1, defaults={"nombre": "Carlos Lopez", "saldo": 1000}
)
usuario2, _ = Usuario.objects.get_or_create(
    id=2, defaults={"nombre": "Maria Garcia", "saldo": 500}
)
usuario3, _ = Usuario.objects.get_or_create(
    id=3, defaults={"nombre": "Juan Perez", "saldo": 2000}
)
usuario4, _ = Usuario.objects.get_or_create(
    id=4, defaults={"nombre": "Ana Martinez", "saldo": 150}
)
usuario5, _ = Usuario.objects.get_or_create(
    id=5, defaults={"nombre": "Pedro Ramirez", "saldo": 3000}
)

print("Usuarios creados:")
for u in Usuario.objects.all():
    print(f"  {u.id}: {u.nombre} - Saldo: {u.saldo}")

# Crear tiquetes de prueba
Tiquete.objects.all().delete()

tiquetes_data = [
    {"usuario_id": 1, "monto": 100, "estado": "ganador"},
    {"usuario_id": 1, "monto": 50, "estado": "perdedor"},
    {"usuario_id": 1, "monto": 200, "estado": "ganador"},
    {"usuario_id": 2, "monto": 300, "estado": "ganador"},
    {"usuario_id": 2, "monto": 75, "estado": "perdedor"},
    {"usuario_id": 3, "monto": 150, "estado": "ganador"},
    {"usuario_id": 3, "monto": 250, "estado": "ganador"},
    {"usuario_id": 3, "monto": 100, "estado": "perdedor"},
    {"usuario_id": 4, "monto": 50, "estado": "ganador"},
]

for t_data in tiquetes_data:
    Tiquete.objects.create(**t_data)

print(f"\nTiquetes creados: {Tiquete.objects.count()}")
print("Usuarios sin tiquetes: 5 (Pedro Ramirez)")