from rest_framework import serializers

from .models import Mascota


class MascotaSerializer(serializers.ModelSerializer):
    # AE 3.1.3: autor de solo lectura (se asigna desde el token, nunca desde el cliente)
    autor = serializers.ReadOnlyField(source="autor.username")

    class Meta:
        model = Mascota
        # AE 3.1.3: fields explícito (nunca "__all__")
        fields = [
            "id", "nombre", "especie", "edad_meses",
            "descripcion", "estado", "autor", "creado",
        ]
        read_only_fields = ["id", "autor", "creado"]

    # La API no pasa por el ModelForm, así que la validación se repite aquí
    def validate_nombre(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return value

    def validate_edad_meses(self, value):
        if value > 360:
            raise serializers.ValidationError("La edad no puede superar 360 meses (30 años).")
        return value
