"""
Modulo de validacion antifraude para el sistema de tiquetes.

Implementa dos mecanismos:
1. Rate limiting: controla la frecuencia con la que un usuario puede crear tiquetes.
2. Validacion de monto sospechoso: detecta montos que se desvian del comportamiento historico.
"""
from django.core.cache import cache
from django.db.models import Avg
from django.utils import timezone

from tickets.models import Tiquete


# Constantes de configuracion
MAX_TIQUETES_POR_VENTANA = 5
VENTANA_SEGUNDOS = 60
BLOQUEO_SEGUNDOS = 300  # 5 minutos
FACTOR_MONTO_SOSPECHOSO = 2.0


def verificar_rate_limit(usuario_id: int) -> dict:
    """
    Verifica si el usuario ha excedido el limite de tiquetes en la ventana de tiempo.

    Usa el cache de Django para llevar la cuenta de tiquetes creados por usuario
    en los ultimos VENTANA_SEGUNDOS segundos. Si supera MAX_TIQUETES_POR_VENTANA,
    se bloquea al usuario por BLOQUEO_SEGUNDOS segundos.

    Retorna un dict con:
      - permitido: bool indicando si puede continuar.
      - mensaje: str explicativo si fue bloqueado.
      - codigo: int con el codigo HTTP sugerido (429 si bloqueado).
    """
    # Verificar si el usuario esta bloqueado
    cache_key_bloqueo = f"bloqueo_usuario_{usuario_id}"
    if cache.get(cache_key_bloqueo):
        return {
            "permitido": False,
            "mensaje": (
                f"Has sido bloqueado temporalmente por exceder el limite de "
                f"{MAX_TIQUETES_POR_VENTANA} tiquetes en {VENTANA_SEGUNDOS} segundos. "
                f"Intenta de nuevo en unos minutos."
            ),
            "codigo": 429,
        }

    # Contar tiquetes del usuario en la ventana de tiempo actual
    cache_key_conteo = f"conteo_tiquetes_{usuario_id}"
    conteo = cache.get(cache_key_conteo, 0)

    if conteo >= MAX_TIQUETES_POR_VENTANA:
        # Bloquear al usuario
        cache.set(cache_key_bloqueo, True, BLOQUEO_SEGUNDOS)
        # Limpiar el contador
        cache.delete(cache_key_conteo)
        return {
            "permitido": False,
            "mensaje": (
                f"Has sido bloqueado temporalmente por exceder el limite de "
                f"{MAX_TIQUETES_POR_VENTANA} tiquetes en {VENTANA_SEGUNDOS} segundos. "
                f"Intenta de nuevo en unos minutos."
            ),
            "codigo": 429,
        }

    # Incrementar contador (expira despues de la ventana)
    cache.set(cache_key_conteo, conteo + 1, VENTANA_SEGUNDOS)
    return {"permitido": True}


def verificar_monto_sospechoso(usuario_id: int, monto: float) -> dict:
    """
    Verifica si el monto del tiquete es sospechoso comparado con el historial del usuario.

    Calcula el promedio de los ultimos 10 tiquetes del usuario. Si el monto actual
    supera el promedio por un factor de FACTOR_MONTO_SOSPECHOSO (2x), se considera
    sospechoso.

    Retorna un dict con:
      - permitido: bool indicando si puede continuar.
      - mensaje: str explicativo si fue rechazado.
      - codigo: int con el codigo HTTP sugerido (409 si sospechoso).
    """
    # Obtener el promedio de los ultimos 10 tiquetes
    ultimos_tiquetes = Tiquete.objects.filter(
        usuario_id=usuario_id
    ).order_by("-creado_en")[:10]

    if not ultimos_tiquetes:
        # Sin historial, no se puede comparar, se permite
        return {"permitido": True}

    # Calcular el monto promedio historico
    montos = [float(t.monto) for t in ultimos_tiquetes]
    promedio_historico = sum(montos) / len(montos)

    if promedio_historico > 0 and monto > promedio_historico * FACTOR_MONTO_SOSPECHOSO:
        return {
            "permitido": False,
            "mensaje": (
                f"El monto ${monto:.2f} supera mas del doble de tu promedio historico "
                f"(${promedio_historico:.2f}). La operacion ha sido rechazada por "
                f"posible fraude. Si crees que es un error, contacta al administrador."
            ),
            "codigo": 409,
        }

    return {"permitido": True}