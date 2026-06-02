from django.db import transaction
from django.shortcuts import get_object_or_404
from django.views.generic import TemplateView

from rest_framework import status
from rest_framework.decorators import api_view
from rest_framework.response import Response

from tickets.antifraud import (
    verificar_monto_sospechoso,
    verificar_rate_limit,
)
from tickets.models import Tiquete, Usuario
from tickets.serializers import TiqueteInputSerializer, TiqueteSerializer


class IndexView(TemplateView):
    template_name = "tickets/index.html"


@api_view(["POST"])
def crear_tiquete(request):
    """
    POST /api/tiquetes/
    Crea un tiquete y descuenta el monto del saldo del usuario en una transaccion.

    Incluye validacion antifraude:
    - Rate limiting: maximo 5 tiquetes por ventana de 60 segundos.
    - Monto sospechoso: si el monto supera el doble del promedio historico del usuario.
    """
    # Validar que el JSON sea valido y contenga los campos requeridos
    serializer = TiqueteInputSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(
            {"error": "JSON invalido o campos faltantes"},
            status=status.HTTP_400_BAD_REQUEST,
        )

    usuario_id = serializer.validated_data["usuario_id"]
    monto = serializer.validated_data["monto"]

    # Verificar que el usuario existe
    try:
        usuario = Usuario.objects.get(pk=usuario_id)
    except Usuario.DoesNotExist:
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    # Validacion antifraude 1: Rate limiting
    rate_check = verificar_rate_limit(usuario_id)
    if not rate_check["permitido"]:
        return Response(
            {"error": rate_check["mensaje"]},
            status=rate_check["codigo"],
        )

    # Validacion antifraude 2: Monto sospechoso
    monto_check = verificar_monto_sospechoso(usuario_id, monto)
    if not monto_check["permitido"]:
        return Response(
            {"error": monto_check["mensaje"]},
            status=monto_check["codigo"],
        )

    # Verificar que el saldo sea suficiente
    if usuario.saldo < monto:
        return Response(
            {"error": "Saldo insuficiente"},
            status=status.HTTP_422_UNPROCESSABLE_ENTITY,
        )

    try:
        with transaction.atomic():
            # Descontar el saldo del usuario
            Usuario.objects.filter(pk=usuario_id).update(
                saldo=usuario.saldo - monto
            )

            # Crear el tiquete
            tiquete = Tiquete.objects.create(
                usuario_id=usuario_id,
                monto=monto,
                estado=Tiquete.Estado.PENDIENTE,
            )
    except Exception:
        return Response(
            {"error": "Error inesperado del servidor"},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    # Serializar la respuesta con los datos completos del tiquete
    tiquete_serializer = TiqueteSerializer(tiquete)
    return Response(tiquete_serializer.data, status=status.HTTP_201_CREATED)


@api_view(["GET"])
def listar_tiquetes_usuario(request, usuario_id):
    """
    GET /api/usuarios/{id}/tiquetes/
    Devuelve la lista de tiquetes de un usuario.
    """
    # Verificar que el usuario existe
    if not Usuario.objects.filter(pk=usuario_id).exists():
        return Response(
            {"error": "Usuario no encontrado"},
            status=status.HTTP_404_NOT_FOUND,
        )

    tiquetes = Tiquete.objects.filter(usuario_id=usuario_id).order_by("-creado_en")
    serializer = TiqueteSerializer(tiquetes, many=True)
    return Response(serializer.data, status=status.HTTP_200_OK)