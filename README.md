# 🐾 Mascotas en adopción — Django + DRF + JWT

Ejercicio *de la web a la API REST* (Unidad 3). Tema: **mascotas en adopción**.
Primero una app web con Django (vistas genéricas) y luego la misma app expuesta como API REST con Django REST Framework y SimpleJWT.

## Modelo `Mascota`

| Campo | Tipo | Nota |
|---|---|---|
| `nombre` | CharField(80) | validación propia: mínimo 2 caracteres |
| `especie` | CharField (P/G/O) | perro, gato, otro |
| `edad_meses` | PositiveIntegerField | validación propia: máximo 360 |
| `descripcion` | TextField | |
| `estado` | CharField (D/R/A) | disponible, reservada, adoptada |
| `autor` | ForeignKey(User) | asignado automáticamente al crear |
| `creado` | DateTimeField | `auto_now_add` |

## Cómo correrlo

```bash
git clone <URL_DEL_REPO> && cd mascotas_adopcion
python -m venv venv && source venv/bin/activate      # Windows: venv\Scripts\activate
pip install -r requirements.txt
cp .env.example .env                                  # y cambia SECRET_KEY
python manage.py migrate
python manage.py createsuperuser                      # opcional (panel /admin/)
python manage.py runserver
```

Generar una `SECRET_KEY` nueva:

```bash
python -c "from django.core.management.utils import get_random_secret_key as g; print(g())"
```

- Web: <http://localhost:8000/>
- API: <http://localhost:8000/api/>
- Tests: `python manage.py test` (19 tests)

> El archivo `.env` **no se sube** al repositorio (está en `.gitignore`); se incluye `.env.example` como plantilla.

## Parte 1 · App web

| Ruta | Descripción | Acceso |
|---|---|---|
| `/` | Lista paginada | público |
| `/<id>/` | Detalle | público |
| `/nueva/` | Crear | logueado |
| `/<id>/editar/` | Editar | **solo el autor** (otro usuario → 403) |
| `/<id>/borrar/` | Borrar | **solo el autor** (otro usuario → 403) |
| `/registro/` | Registro | público |
| `/cuentas/login/` · `/cuentas/logout/` | Login / logout | — |

- CRUD con vistas genéricas (`ListView`, `DetailView`, `CreateView`, `UpdateView`, `DeleteView`).
- Validaciones propias en el servidor: `clean_nombre` y `clean_edad_meses` en `mascotas/forms.py`.
- Permiso de autor con `UserPassesTestMixin` (`SoloAutorMixin`).

## Parte 2 · API REST

### Endpoints

| Método | Ruta | Auth | Descripción |
|---|---|---|---|
| POST | `/api/token/` | No | Obtener `access` y `refresh` JWT |
| POST | `/api/token/refresh/` | No | Renovar el `access` |
| GET | `/api/mascotas/` | No | Listar (paginado) |
| POST | `/api/mascotas/` | Sí | Crear (el autor sale del token) |
| GET | `/api/mascotas/{id}/` | No | Detalle |
| PUT / PATCH | `/api/mascotas/{id}/` | Solo autor | Editar |
| DELETE | `/api/mascotas/{id}/` | Solo autor | Borrar |
| GET | `/api/mascotas/mios/` | Sí | Mascotas del usuario del token |

### Qué se hizo en cada actividad

- **AE 3.1.1** — DRF y SimpleJWT instalados y configurados en `config/settings.py` (autenticación JWT, permisos, throttling, paginación).
- **AE 3.1.3** — `MascotaSerializer` con `fields` explícito y `autor` de solo lectura (`mascotas/serializers.py`).
- **AE 3.1.4** — `MascotaViewSet` (CRUD completo) + `DefaultRouter` + acción `mios` (`mascotas/api.py`, `mascotas/api_urls.py`).
- **AE 3.1.2** — login con JWT y permiso por autor `EsAutorOSoloLectura` (`mascotas/permissions.py`), más la auditoría con IA de abajo.

### Pruebas (salida real del servidor)

Script reproducible: `./pruebas_api.sh ana CLAVE_ANA beto CLAVE_BETO`

```text
### 1) 200 - Listar (sin token)
HTTP/1.1 200 OK
{"count":0,"next":null,"previous":null,"results":[]}

### 2) 401 - Crear sin token
HTTP/1.1 401 Unauthorized
{"detail":"Las credenciales de autenticación no se proveyeron."}

### 3) 201 - Crear con token de ana
HTTP/1.1 201 Created
{"id":1,"nombre":"Luna","especie":"G","edad_meses":8,"descripcion":"Gatita cariñosa","estado":"D","autor":"ana","creado":"2026-10-02T18:11:18.766081-03:00"}

### 4) 403 - beto intenta borrar la mascota de ana
HTTP/1.1 403 Forbidden
{"detail":"Usted no tiene permiso para realizar esta acción."}

### 5) 200 - /mios/ de ana
HTTP/1.1 200 OK
{"count":1,"next":null,"previous":null,"results":[{"id":1,"nombre":"Luna", ... ,"autor":"ana", ...}]}
```

Además hay 19 tests automatizados (`mascotas/tests.py`) que cubren los mismos casos (200, 401, 201, 403), la validación, `/mios/` y la parte web.

## Auditoría con IA (OWASP API Security Top 10)

Se revisó el código (`settings.py`, `api.py`, `serializers.py`, `permissions.py`, `urls.py`) con una IA usando el OWASP API Security Top 10 (2023).

| # | Recomendación de la IA | OWASP | Decisión | Por qué |
|---|---|---|---|---|
| 1 | Aplicar throttling a anónimos y autenticados | API4 Consumo irrestricto de recursos | ✅ Aplicada | Mitiga abuso y fuerza bruta contra `/api/token/`. Ver `DEFAULT_THROTTLE_*`. |
| 2 | Sacar `SECRET_KEY`, `DEBUG` y `ALLOWED_HOSTS` a `.env` | API8 Mala configuración de seguridad | ✅ Aplicada | Evita filtrar secretos en GitHub. `.env` ignorado y `.env.example` incluido. |
| 3 | Acortar la vida del token de acceso (30 min) y del refresh (1 día) | API2 Autenticación rota | ✅ Aplicada | Reduce el daño si un token se filtra. Ver `SIMPLE_JWT`. |
| 4 | Paginar los listados | API4 Consumo irrestricto de recursos | ✅ Aplicada | Evita respuestas enormes. `PAGE_SIZE = 10`. |
| 5 | Autorización a nivel de objeto en cada recurso | API1 BOLA | ✅ Aplicada | `EsAutorOSoloLectura` + `IsAuthenticatedOrReadOnly`; probado con el 403. |
| 6 | Que `autor` nunca venga del cliente | API3 Autorización a nivel de propiedad | ✅ Aplicada | `autor` es `ReadOnlyField` y se asigna en `perform_create` (hay un test). |
| 7 | Usar UUID en lugar de IDs secuenciales | API1 BOLA | ❌ Rechazada | El permiso por objeto ya impide modificar datos ajenos y la información es pública por diseño. |
| 8 | Rate limit distinto por endpoint | API4 | ❌ Rechazada | El throttling global alcanza para el tamaño de este ejercicio. |
| 9 | Forzar HTTPS, HSTS y cookies seguras | API8 | ❌ Rechazada | Se usa `runserver` local; es un cambio de despliegue, no de código. |
| 10 | Lista negra de refresh tokens al hacer logout | API2 | ❌ Rechazada | Requiere `token_blacklist` y migraciones extra; con refresh de 1 día el riesgo es bajo para este alcance. |

## Estructura

```text
config/            settings (lee .env), urls
mascotas/          models, forms, views (web) · serializers, permissions, api, api_urls (API) · tests
templates/         base, mascotas/*, registration/*
pruebas_api.sh     pruebas 200/401/201/403 con curl
.env.example       plantilla de variables (el .env real no se sube)
```
