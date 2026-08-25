# Correr el Gate en la Jetson — una sola ruta

Host: `tektron@192.168.100.84`  
Script: `/mnt/tektron/workspace/gate_capacidad_g1_g10.py`  
Salida: `/mnt/tektron/workspace/resultados_gate_v8.json`

Esto **no** cura corpus, **no** reconcilia FAISS, **no** calibra N0. Solo mide J.

Si en algún paso aparece el impulso de auditar “una fuente más” antes de terminar el Gate: no lo hagas. Seguí al paso siguiente.

---

## Paso 1 — En la iMac: bajar el medidor y copiarlo

```bash
curl -fsSL -o /tmp/gate_capacidad_g1_g10.py \
  https://raw.githubusercontent.com/FronterIA-Lab/romper-el-ciclo-tektron/cursor/estrategia-cierre-j-6496/gate_capacidad_g1_g10.py

curl -fsSL -o /tmp/emitir_acta_cierre_v8.py \
  https://raw.githubusercontent.com/FronterIA-Lab/romper-el-ciclo-tektron/cursor/estrategia-cierre-j-6496/emitir_acta_cierre_v8.py

scp /tmp/gate_capacidad_g1_g10.py /tmp/emitir_acta_cierre_v8.py \
  tektron@192.168.100.84:/mnt/tektron/workspace/
```

Comprobá que el scp terminó sin error. Si el `curl` a GitHub falla, usá el archivo local del clone:

```bash
scp gate_capacidad_g1_g10.py emitir_acta_cierre_v8.py \
  tektron@192.168.100.84:/mnt/tektron/workspace/
```

---

## Paso 2 — Entrar a la Jetson

```bash
ssh tektron@192.168.100.84
```

A partir de aquí, todos los comandos son **dentro** de la Jetson.

---

## Paso 3 — ¿Está vivo el sistema? (no es el Gate)

```bash
ss -ltnp | grep -E ':8000|:8001' || netstat -ltnp 2>/dev/null | grep -E ':8000|:8001'

curl -sS -m 10 http://127.0.0.1:8000/health ; echo
curl -sS -m 10 http://127.0.0.1:8001/health ; echo
```

- Si **ningún** puerto responde: levantá el bridge (`:8000`). No midas contra un proceso muerto.
- Si `:8000` está UP y `:8001` está caído: **seguí**. El L1 vivo es el bridge. `:8001` es el backend de análisis; no es prerrequisito para descubrir contrato. Un `/health` 404 no es fallo.
- `chosen=null` con `:8000` UP no significa “no hay API”. Suele ser 422 (payload) o timeout de 20 s al pegarle al LLM. Ver paso 4R.

---

## Paso 4 — Descubrir el contrato HTTP

```bash
cd /mnt/tektron/workspace

/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
  --timeout 120 \
  --dry-discover
```

Buscá `"chosen": { "url": ... }`.

- Si hay `url`: anotala y pasá al paso 5.
- Si `chosen` es `null` y `:8000` está UP: **no curar.** Paso 4R.

---

## Paso 4R — Si `chosen` salió `null` (caso real del 25 ago)

Hechos de esa corrida: bridge `:8000` OK (`chunks=13450`, `n_sit=8526`, `n_heg=4786`); `:8001` connection refused; `/analizar` 404; `/chat`+`mensaje` **422** (la ruta existe); `/chat`+`query` http 0 (el ping al LLM superó 20 s). **J no se midió.** El bottleneck `contrato_http` no se arregla con curación.

**4R.1** — Rutas reales del bridge:

```bash
curl -sS -m 10 http://127.0.0.1:8000/openapi.json \
  | /mnt/tektron/venv_tektron/bin/python3 -c "import json,sys; d=json.load(sys.stdin); print('\n'.join(sorted(d.get('paths',{}))))"
```

**4R.2** — Qué campo pide `/chat` (el 422 es el contrato):

```bash
curl -sS -m 15 -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"mensaje":"ping"}' ; echo
```

**4R.3** — Humo con el campo `query` y timeout largo (puede tardar 1–2 min; es el LLM):

```bash
curl -sS -m 120 -X POST http://127.0.0.1:8000/chat \
  -H 'Content-Type: application/json' \
  -d '{"query":"¿Qué es el MCC?"}' \
  | /mnt/tektron/venv_tektron/bin/python3 -c "import json,sys; d=json.load(sys.stdin); print(sorted(d.keys()) if isinstance(d,dict) else type(d)); print(str(d)[:800])"
```

**4R.4** — Dónde está `:8001` (solo lectura; no lo adivines):

```bash
ss -ltnp | grep -E ':8080|:8001|:8000'
ls -la /mnt/tektron/tektron_backend.py \
       /mnt/tektron/workspace/tektron_start_backend_y_probar.sh 2>&1
grep -n "8001\|analizar\|uvicorn\|FastAPI" /mnt/tektron/tektron_backend.py 2>/dev/null | head
```

No hace falta `:8001` para correr el Gate si `/chat` o `/retrieve` en `:8000` responden 2xx. Si 4R.3 devuelve JSON, recopy el script actualizado (descubre 422/timeout) y volvé al paso 4, después al 5.

Pegá la salida de 4R.1–4R.3 si el descubridor sigue en `chosen=null`.

---

## Paso 5 — Correr G1–G10 (puede tardar 10–25 min)

Diez consultas, timeout 120 s cada una. Dejala correr. No abras otra terminal para “un audit más”.

```bash
cd /mnt/tektron/workspace

/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
  --timeout 120 \
  --out /mnt/tektron/workspace/resultados_gate_v8.json
```

En pantalla vas a ver una línea por Gi (`OK` o `FAIL`). Al final:

```
J=... status=OK|FAIL bottleneck=[...]
siguiente: ...
escrito: /mnt/tektron/workspace/resultados_gate_v8.json
```

El código de salida `1` o `2` **no** es un crash: `1` = Gate no aprobó, `2` = no hubo contrato HTTP.

---

## Paso 6 — Leer J (una sola mirada)

```bash
/mnt/tektron/venv_tektron/bin/python3 - << 'PY'
import json
from pathlib import Path
p = Path("/mnt/tektron/workspace/resultados_gate_v8.json")
d = json.loads(p.read_text())
m = d.get("metricas") or d
print("status     :", d.get("status"))
print("J          :", d.get("J"))
print("Mirror     :", m.get("MirrorCoverage"))
print("DualPole   :", m.get("DualPoleDensity"))
print("Tension    :", m.get("TensionFaithfulness"))
print("Evidence   :", m.get("EvidenceIntegrity"))
print("Tree DUAL  :", m.get("TreeCoverage_DUAL"))
print("FalseN0    :", m.get("FalseN0"))
print("TrueN0Rate :", m.get("TrueN0Rate"))
print("Synthesis  :", m.get("SynthesisRate"))
print("PoloMislabel:", m.get("PoloMislabel"))
print("INDEX_GAP  :", m.get("INDEX_GAP"))
print("bottleneck :", d.get("bottleneck") or m.get("bottleneck"))
print("siguiente  :", d.get("siguiente"))
print("--- por query ---")
for r in d.get("por_query") or []:
    print(f"  {r['id']} ok={r['ok']} espera={r['espera']} modo={r['modo_detectado']} dual={r['DualPoleDensity']} tree={r['TreeCoverage']} FalseN0={r['FalseN0']}")
PY
```

Traé ese bloque al chat si querés que se decida el siguiente movimiento. **No interpretes en caliente.** El JSON ya nombra el cuello.

---

## Paso 7A — Solo si `status=OK` y `J>0`: acta C7

```bash
cd /mnt/tektron/workspace

/mnt/tektron/venv_tektron/bin/python3 emitir_acta_cierre_v8.py \
  --gate /mnt/tektron/workspace/resultados_gate_v8.json \
  --index /mnt/tektron/index_l1 \
  --out /mnt/tektron/workspace/ACTA_CIERRE_TEKTRON_v8.json
```

Si el Gate no aprobó, este script **se niega** a firmar. Eso es correcto.

Después:

```bash
cat /mnt/tektron/workspace/ACTA_CIERRE_TEKTRON_v8.json
```

Con `estado: CERRADO` y hashes de `chunks.jsonl` + `faiss.idx`, TEKTRON está cerrado. No abras ronda de curación “por si acaso”.

---

## Paso 7B — Si `status=FAIL`: una corrección, nada en paralelo

1. Leé `bottleneck` (paso 6).
2. Hacé **solo** lo que nombra `siguiente` (tabla en `ESTRATEGIA_CIERRE_J.md` §6).
3. Volvé al **paso 5**. No al paso 1 de un protocolo nuevo.

Prohibido en 7B: ronda 3 de 98 leyes, swap del unificado 60 652, mezclar ZIM en L1, otro `find` del disco, recalibrar N0 “para ser honestos”.

---

## Si el paso 5 se corta a mitad

El JSON puede no existir o estar incompleto. No uses un archivo a medias. Repetí el paso 5 entero. G1–G10 es la batería, no “las que alcanzaron a correr”.
