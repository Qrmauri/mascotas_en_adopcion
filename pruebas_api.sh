#!/usr/bin/env bash
# Uso: con el servidor corriendo (python manage.py runserver) y dos usuarios creados.
#   ./pruebas_api.sh ana CLAVE_ANA beto CLAVE_BETO
set -e
B=http://localhost:8000/api
J='Content-Type: application/json'
tok(){ curl -s -X POST $B/token/ -H "$J" -d "{\"username\":\"$1\",\"password\":\"$2\"}" | python3 -c "import sys,json;print(json.load(sys.stdin)['access'])"; }
TA=$(tok "$1" "$2"); TB=$(tok "$3" "$4")
D='{"nombre":"Luna","especie":"G","edad_meses":8,"descripcion":"Gatita cariñosa","estado":"D"}'
echo '1) 200 listar';         curl -s -i $B/mascotas/ | head -1
echo '2) 401 sin token';      curl -s -i -X POST $B/mascotas/ -H "$J" -d "$D" | head -1
echo '3) 201 con token';      curl -s -i -X POST $B/mascotas/ -H "$J" -H "Authorization: Bearer $TA" -d "$D" | head -1
ID=$(curl -s $B/mascotas/mios/ -H "Authorization: Bearer $TA" | python3 -c "import sys,json;print(json.load(sys.stdin)['results'][0]['id'])")
echo '4) 403 registro ajeno'; curl -s -i -X DELETE $B/mascotas/$ID/ -H "Authorization: Bearer $TB" | head -1
