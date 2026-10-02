from django.contrib.auth.models import User
from django.test import TestCase
from django.urls import reverse
from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from .models import Mascota

DATOS = {
    "nombre": "Luna", "especie": "G", "edad_meses": 8,
    "descripcion": "Gatita cariñosa", "estado": "D",
}


class WebTests(TestCase):
    """Parte 1: app web."""

    def setUp(self):
        self.ana = User.objects.create_user("ana", password="clave-segura-123")
        self.beto = User.objects.create_user("beto", password="clave-segura-123")
        self.m = Mascota.objects.create(autor=self.ana, **DATOS)

    def test_lista_publica(self):
        self.assertEqual(self.client.get(reverse("mascota-list")).status_code, 200)

    def test_crear_requiere_login(self):
        r = self.client.get(reverse("mascota-create"))
        self.assertEqual(r.status_code, 302)
        self.assertIn("/cuentas/login/", r.url)

    def test_crear_asigna_autor(self):
        self.client.login(username="ana", password="clave-segura-123")
        r = self.client.post(reverse("mascota-create"), {**DATOS, "nombre": "Rocky"})
        self.assertEqual(r.status_code, 302)
        self.assertEqual(Mascota.objects.get(nombre="Rocky").autor, self.ana)

    def test_validacion_propia_edad(self):
        self.client.login(username="ana", password="clave-segura-123")
        r = self.client.post(reverse("mascota-create"), {**DATOS, "edad_meses": 999})
        self.assertEqual(r.status_code, 200)
        self.assertContains(r, "no puede superar 360 meses")

    def test_autor_edita(self):
        self.client.login(username="ana", password="clave-segura-123")
        r = self.client.post(reverse("mascota-update", args=[self.m.pk]), {**DATOS, "nombre": "Luna II"})
        self.assertEqual(r.status_code, 302)

    def test_otro_usuario_edita_403(self):
        self.client.login(username="beto", password="clave-segura-123")
        r = self.client.post(reverse("mascota-update", args=[self.m.pk]), DATOS)
        self.assertEqual(r.status_code, 403)

    def test_otro_usuario_borra_403(self):
        self.client.login(username="beto", password="clave-segura-123")
        r = self.client.post(reverse("mascota-delete", args=[self.m.pk]))
        self.assertEqual(r.status_code, 403)
        self.assertTrue(Mascota.objects.filter(pk=self.m.pk).exists())

    def test_registro_y_login(self):
        r = self.client.post(reverse("registro"), {
            "username": "nuevo", "password1": "Clave-Muy-Segura-9", "password2": "Clave-Muy-Segura-9",
        })
        self.assertEqual(r.status_code, 302)
        self.assertTrue(self.client.login(username="nuevo", password="Clave-Muy-Segura-9"))

    def test_logout(self):
        self.client.login(username="ana", password="clave-segura-123")
        self.client.post(reverse("logout"))
        self.assertEqual(self.client.get(reverse("mascota-create")).status_code, 302)


class APITests(APITestCase):
    """Parte 2: API REST (200 / 401 / 201 / 403)."""

    def setUp(self):
        self.ana = User.objects.create_user("ana", password="clave-segura-123")
        self.beto = User.objects.create_user("beto", password="clave-segura-123")

    def auth(self, user):
        token = RefreshToken.for_user(user).access_token
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {token}")

    def test_listar_200(self):
        self.assertEqual(self.client.get("/api/mascotas/").status_code, 200)

    def test_crear_sin_token_401(self):
        self.assertEqual(self.client.post("/api/mascotas/", DATOS).status_code, 401)

    def test_crear_con_token_201(self):
        self.auth(self.ana)
        r = self.client.post("/api/mascotas/", DATOS)
        self.assertEqual(r.status_code, 201)
        self.assertEqual(r.data["autor"], "ana")

    def test_autor_no_se_puede_falsear(self):
        self.auth(self.ana)
        r = self.client.post("/api/mascotas/", {**DATOS, "autor": "beto"})
        self.assertEqual(r.data["autor"], "ana")

    def test_editar_y_borrar_ajena_403(self):
        m = Mascota.objects.create(autor=self.ana, **DATOS)
        self.auth(self.beto)
        self.assertEqual(self.client.patch(f"/api/mascotas/{m.id}/", {"nombre": "X"}).status_code, 403)
        self.assertEqual(self.client.delete(f"/api/mascotas/{m.id}/").status_code, 403)

    def test_autor_edita_y_borra(self):
        m = Mascota.objects.create(autor=self.ana, **DATOS)
        self.auth(self.ana)
        self.assertEqual(self.client.patch(f"/api/mascotas/{m.id}/", {"nombre": "Nueva"}).status_code, 200)
        self.assertEqual(self.client.delete(f"/api/mascotas/{m.id}/").status_code, 204)

    def test_mios(self):
        Mascota.objects.create(autor=self.ana, **DATOS)
        Mascota.objects.create(autor=self.beto, **{**DATOS, "nombre": "Otro"})
        self.auth(self.ana)
        r = self.client.get("/api/mascotas/mios/")
        self.assertEqual(r.status_code, 200)
        self.assertEqual(r.data["count"], 1)

    def test_mios_sin_token_401(self):
        self.assertEqual(self.client.get("/api/mascotas/mios/").status_code, 401)

    def test_validacion_serializer(self):
        self.auth(self.ana)
        r = self.client.post("/api/mascotas/", {**DATOS, "edad_meses": 999})
        self.assertEqual(r.status_code, 400)

    def test_login_jwt(self):
        r = self.client.post("/api/token/", {"username": "ana", "password": "clave-segura-123"})
        self.assertEqual(r.status_code, 200)
        self.assertIn("access", r.data)
