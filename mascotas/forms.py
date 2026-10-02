from django import forms

from .models import Mascota


class MascotaForm(forms.ModelForm):
    class Meta:
        model = Mascota
        fields = ["nombre", "especie", "edad_meses", "descripcion", "estado"]
        widgets = {"descripcion": forms.Textarea(attrs={"rows": 4})}

    # Validaciones propias en el servidor (Parte 1)
    def clean_nombre(self):
        nombre = self.cleaned_data["nombre"].strip()
        if len(nombre) < 2:
            raise forms.ValidationError("El nombre debe tener al menos 2 caracteres.")
        return nombre

    def clean_edad_meses(self):
        edad = self.cleaned_data["edad_meses"]
        if edad > 360:
            raise forms.ValidationError("La edad no puede superar 360 meses (30 años).")
        return edad
