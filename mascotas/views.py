from django.contrib import messages
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.urls import reverse_lazy
from django.views.generic import (
    CreateView,
    DeleteView,
    DetailView,
    ListView,
    UpdateView,
)

from .forms import MascotaForm
from .models import Mascota


class SoloAutorMixin(UserPassesTestMixin):
    """Solo el autor puede editar/borrar. Otro usuario autenticado recibe 403."""

    def test_func(self):
        return self.get_object().autor == self.request.user


class MascotaList(ListView):
    model = Mascota
    paginate_by = 9

    def get_queryset(self):
        return Mascota.objects.select_related("autor")


class MascotaDetail(DetailView):
    model = Mascota


class MascotaCreate(LoginRequiredMixin, CreateView):
    model = Mascota
    form_class = MascotaForm
    success_url = reverse_lazy("mascota-list")

    def form_valid(self, form):
        form.instance.autor = self.request.user
        messages.success(self.request, "Mascota publicada.")
        return super().form_valid(form)


class MascotaUpdate(LoginRequiredMixin, SoloAutorMixin, UpdateView):
    model = Mascota
    form_class = MascotaForm
    success_url = reverse_lazy("mascota-list")

    def form_valid(self, form):
        messages.success(self.request, "Mascota actualizada.")
        return super().form_valid(form)


class MascotaDelete(LoginRequiredMixin, SoloAutorMixin, DeleteView):
    model = Mascota
    success_url = reverse_lazy("mascota-list")

    def form_valid(self, form):
        messages.success(self.request, "Mascota eliminada.")
        return super().form_valid(form)


class Registro(CreateView):
    form_class = UserCreationForm
    template_name = "registration/registro.html"
    success_url = reverse_lazy("login")

    def form_valid(self, form):
        messages.success(self.request, "Cuenta creada. Ya puedes iniciar sesión.")
        return super().form_valid(form)
