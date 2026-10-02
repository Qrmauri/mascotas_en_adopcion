from django.urls import path

from . import views

urlpatterns = [
    path("", views.MascotaList.as_view(), name="mascota-list"),
    path("nueva/", views.MascotaCreate.as_view(), name="mascota-create"),
    path("<int:pk>/", views.MascotaDetail.as_view(), name="mascota-detail"),
    path("<int:pk>/editar/", views.MascotaUpdate.as_view(), name="mascota-update"),
    path("<int:pk>/borrar/", views.MascotaDelete.as_view(), name="mascota-delete"),
    path("registro/", views.Registro.as_view(), name="registro"),
]
