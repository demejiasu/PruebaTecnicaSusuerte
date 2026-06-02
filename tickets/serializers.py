from rest_framework import serializers

from tickets.models import Tiquete, Usuario


class TiqueteInputSerializer(serializers.Serializer):
    """Serializer para validar la entrada del endpoint POST /api/tiquetes/."""
    usuario_id = serializers.IntegerField()
    monto = serializers.DecimalField(max_digits=10, decimal_places=2)


class UsuarioSerializer(serializers.ModelSerializer):
    class Meta:
        model = Usuario
        fields = ["id", "nombre", "saldo", "creado_en"]


class TiqueteSerializer(serializers.ModelSerializer):
    usuario = UsuarioSerializer(read_only=True)
    usuario_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = Tiquete
        fields = ["id", "usuario", "usuario_id", "monto", "estado", "creado_en"]