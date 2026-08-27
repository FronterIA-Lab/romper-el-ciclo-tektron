# romper-el-ciclo-tektron

Estrategia de cierre de TEKTRON bajo la función que el sistema debe maximizar:

```
J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity
```

N0 (abstención) es piso anti-confabulación, no meta. Un sistema que se calla siempre tiene error cero y valor cero.

## Empezá acá

0. **`MAPA_TEKTRON.md`** — el mapa completo: tesis invariante, evolución real
   mar-ago 2026, estado actual (Gate aprobado desde el 26-ago), y qué hacer con
   los diagnósticos nuevos que aparezcan sin volver a ciclar.
0.1. **`ARQUITECTURA_IDEAL_TEKTRON.md`** — el Gate aprobado (`J=0.35`) es un piso
   mecánico, no el objetivo. Acá está la ruta real hacia una herramienta
   valiosa y empaquetada (backend con literatura RAG aplicada + frontend/HTML
   completo + instalación reproducible), sin reabrir arquitectura sin que un
   Gate lo nombre.
1. **`PROTOCOLO_DESDE_AQUI.md`** — dónde estamos tras el Gate: aprobado, acta firmada.
2. **`ESTRATEGIA_CIERRE_J.md`** — por qué J es un producto y por qué N0 no es la meta.
3. **`gate_capacidad_g1_g10.py`** — el medidor. Se copia a la Jetson y produce `resultados_gate_v8.json`.
4. **`La Arquitectura Fija de TEKTRON`** — qué es TEKTRON. No se reabre.

Este git no hospeda el sistema vivo. El cierre se corre en `tektron@192.168.100.84:/mnt/tektron`.

## Estado: Gate aprobado (26-ago-2026), empaquetado NO terminado

El Gate ya se corrió y aprobó: `J=0.35`, `status=OK`, `bottleneck=[]`.
`ACTA_CIERRE_TEKTRON_v8.json` está firmada con hashes reales. Ver
`PROTOCOLO_DESDE_AQUI.md` §"Cierre del Gate" y `MAPA_TEKTRON.md` §4.

Eso es un piso mecánico (no confabula), no la meta. La meta —una herramienta
realmente valiosa y empaquetada hasta el HTML— sigue abierta: ver
`ARQUITECTURA_IDEAL_TEKTRON.md` para la ruta priorizada (retrieval/reranking
con literatura RAG aplicada, decisión del frontend, instalación reproducible).

El trabajo de aquí en adelante sube `J` y cierra el empaquetado corrigiendo
únicamente lo que un `resultados_gate_v8.json` nuevo, corrido contra el sistema
vivo, nombre como bottleneck — más las fases de `ARQUITECTURA_IDEAL_TEKTRON.md`.
Mismos comandos de siempre (**`CORRER_EN_JETSON.md`**):

```bash
/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
  --out resultados_gate_v8.json
```

Si el JSON nombra un factor o constraint → una corrección puntual → re-medir.
Ningún documento de diagnóstico nuevo (de esta sesión o de otra) autoriza tocar
algo que el Gate no haya nombrado.

## Qué no leer como plan

| Archivo | Por qué |
|---------|---------|
| `PROTOCOLO DE CIERRE-MAL IMPLEMENTADO` | v7: Gate de silencio + reetiquetado por keyword |
| `SI VOLVÉS A ESTO…` | Pone auditoría de instrumento legal *antes* del Gate |
| `tektron_auditar_instrumento_legal_v2.py` | Traza de la ronda 3. No es paso de cierre |
| README anterior (error del asistente) | Se detuvo en un `.py` ausente del git; C4 ya estaba medido |

`TEKTRON_REPORTE_GAP_20260821.md` y `El error` siguen siendo diagnósticos válidos. La estrategia los sintetiza; no los sustituye como historia.
