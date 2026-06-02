from django.urls import path

from tickets import views

urlpatterns = [
    path("", views.IndexView.as_view(), name="index"),
    path("api/tiquetes/", views.crear_tiquete, name="crear-tiquete"),
    path(
        "api/usuarios/<int:usuario_id>/tiquetes/",
        views.listar_tiquetes_usuario,
        name="listar-tiquetes-usuario",
    ),
]
