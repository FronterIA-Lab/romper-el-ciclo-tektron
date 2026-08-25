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

- Si **ningún** puerto responde: levantá bridge/backend como ya lo hacés (`tektron_start_backend_y_probar.sh` o el systemd que esté activo). No midas contra un proceso muerto.
- Si solo uno responde: seguí igual. El script prueba `:8001` y `:8000` y usa el que tenga `/analizar`, `/chat` o `/retrieve`.
- Un `/health` 404 no es fallo: algunos servicios no exponen esa ruta. El paso 4 lo confirma.

---

## Paso 4 — Descubrir el contrato HTTP (30–60 s)

```bash
cd /mnt/tektron/workspace

/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
  --dry-discover
```

Buscá en la salida `"chosen": { "url": ... }`.

- Si `chosen` es `null` o falta: no hay `/analizar`, `/chat` ni `/retrieve` vivos. **Pará.** No curar. Levantá el backend y repetí este paso.
- Si hay `url`: anotala (ej. `http://127.0.0.1:8001/analizar`) y pasá al paso 5.

---

## Paso 5 — Correr G1–G10 (puede tardar 10–25 min)

Diez consultas, timeout 120 s cada una. Dejala correr. No abras otra terminal para “un audit más”.

```bash
cd /mnt/tektron/workspace

/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
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
