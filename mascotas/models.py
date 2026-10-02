from django.conf import settings
from django.db import models


class Mascota(models.Model):
    ESPECIES = [("P", "Perro"), ("G", "Gato"), ("O", "Otro")]
    ESTADOS = [("D", "Disponible"), ("R", "Reservada"), ("A", "Adoptada")]

    nombre = models.CharField(max_length=80)
    especie = models.CharField(max_length=1, choices=ESPECIES)
    edad_meses = models.PositiveIntegerField(help_text="Edad aproximada en meses")
    descripcion = models.TextField()
    estado = models.CharField(max_length=1, choices=ESTADOS, default="D")
    autor = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="mascotas"
    )
    creado = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-creado"]

    def __str__(self):
        return f"{self.nombre} ({self.get_especie_display()})"
