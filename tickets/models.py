from django.db import models


class Usuario(models.Model):
    nombre = models.CharField(max_length=255)
    saldo = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "usuarios"
        verbose_name = "Usuario"
        verbose_name_plural = "Usuarios"
        indexes = [
            models.Index(fields=["nombre"], name="idx_usuario_nombre"),
        ]

    def __str__(self):
        return f"{self.nombre} (saldo: {self.saldo})"


class Tiquete(models.Model):
    class Estado(models.TextChoices):
        GANADOR = "ganador", "Ganador"
        PERDEDOR = "perdedor", "Perdedor"
        PENDIENTE = "pendiente", "Pendiente"

    usuario = models.ForeignKey(
        Usuario,
        on_delete=models.CASCADE,
        related_name="tiquetes",
        db_column="usuario_id",
    )
    monto = models.DecimalField(max_digits=10, decimal_places=2)
    estado = models.CharField(
        max_length=10,
        choices=Estado.choices,
        default=Estado.PENDIENTE,
    )
    creado_en = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = "tiquetes"
        verbose_name = "Tiquete"
        verbose_name_plural = "Tiquetes"
        indexes = [
            models.Index(fields=["usuario", "estado"], name="idx_tiquete_usuario_estado"),
            models.Index(fields=["creado_en"], name="idx_tiquete_creado_en"),
        ]

    def __str__(self):
        return f"Tiquete #{self.id} - Usuario {self.usuario_id} - {self.estado}"