# Estrategia de cierre — maximizar J, no el silencio

**Este archivo no es un protocolo v9.** El protocolo operativo ya existe: `PROTOCOLO_CIERRE_TEKTRON_v8.md` (repo `CIERRE-TEKTRON`, rama `cursor/analisis-cierre-tektron-6f65`). Aquí se decide *qué* ejecutar y *por qué*, para cortar el ciclo de siete meses.

**Regla de lectura:** si al terminar este documento sentís el impulso de auditar el corpus, inventar una fase nueva o “traer un archivo más antes de medir”, volvé a la sección 5. Esa es la traza del error.

---

## 0. Respuesta en una página

TEKTRON es un analista situado. Cierra cuando **produce Árboles de Espejos** (tesis HEG vs antítesis SIT, tensión sin síntesis) + preguntas MCC + evidencia SHA-256 sobre las estructuras del mapa, y se abstiene (N0) solo cuando no hay contexto. La abstención es piso, no meta.

La función que hay que maximizar es un **producto**, a propósito:

```
J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity
```

Si un factor llega a 0, J llega a 0. Ningún factor compensa a otro. No se maximiza abstención, precisión corta, EM/F1 ni “error cero”. Un sistema que se calla siempre tiene error cero y valor cero.

**Hoy no sabemos cuánto vale J.** El único instrumento que lo mide —la batería G1–G10 contra `/analizar` en vivo— nunca se corrió. Hay dos sondas manuales (Ley Minera, pozole). Eso no es el Gate.

**Única acción siguiente:** correr `gate_capacidad_g1_g10.py` en la Jetson (`tektron@192.168.100.84`), producir `resultados_gate_v8.json` con los cuatro factores y las constraints, y recién entonces decidir. Si el Gate aprueba → acta C7 → cerrado. Si falla → el JSON dice *qué* factor o constraint falló → una corrección puntual. Nada más.

Este workspace **no puede** ejecutar el Gate: el sistema vivo no está aquí. Está en `/mnt/tektron`. Este repo entrega la estrategia y el medidor. El cierre se firma en el nodo.

---

## 1. Qué está pasando (el ciclo, no el síntoma)

Siete meses no se gastaron “sin plan”. Se gastaron **ejecutando el plan equivocado con disciplina**. Cada era produjo un documento canónico nuevo y un asistente que lo obedeció:

| Era | Documento que mandó | Función que realmente se corrió |
|-----|---------------------|----------------------------------|
| Jun–jul | Estrella Polar / golden 32 preguntas | Subir % dual (cosecha, reclasificar how-tos) |
| 7 ago | `TEKTRON_DOD_CANONICO.md` | “Si pierdes la abstención, pierdes todo” |
| 19 ago | Protocolo v7 (en este repo: *MAL IMPLEMENTADO*) | Gate de silencio + purga NO ENTRA |
| 19 ago | `ERROR CONSTANTE` | Diagnóstico correcto: se invirtió J |
| 19–20 ago | Protocolo v8 + `ANALISIS_COMPLETO_TEKTRON.md` | J correcto **por escrito**; ejecución incompleta |
| 20 ago | `SI VOLVÉS A ESTO…` | Checklist C1–C7; ronda de mislabel *antes* del Gate |
| 21 ago | `TEKTRON_REPORTE_GAP_20260821.md` | Diagnóstico correcto otra vez: medir antes de curar |

El mecanismo que se repite, con evidencia en los propios documentos:

1. **Invertir J.** Maximizar “no equivocarse” (N0, purga, cero mislabels, bridge UP) en vez de maximizar Árboles.
2. **Tratar un proxy como objetivo.** C1–C7, “Fase 2 sin patrón sin barrer”, inventario, calibración N0, % dual del golden de julio. Todos son instrumentos. Ninguno es J.
3. **Elegir la tarea legible.** Escribir un script de auditoría, un `find`, una ronda más de reetiquetado: avance visible, bajo control del asistente. Correr G1–G10 exige el contrato de `/analizar` y produce un número que puede ser feo. Se posterga.
4. **Escribir un documento nuevo** en lugar de ejecutar el que ya manda (v8 Fase 4). Este archivo existe para *no* ser el siguiente protocolo. Es un mapa de lectura y un medidor.

Tres errores de fondo, ya nombrados, que siguen vigentes si se ignora el Gate:

- **N0 como criterio de éxito** (`El error` / `ERROR CONSTANTE`): el piso de seguridad se volvió la meta.
- **Solo NO ENTRA:** se purgó el índice y no se preguntó qué falta. Un analista más limpio y más pequeño no es un analista mejor.
- **Curación exhaustiva como prerrequisito de medición** (GAP §4): `PoloMislabel = 0` vale en *traps gold* (G10, Quijano ≠ HEG), no en los 13 450 chunks. Los 98 de “instrumento legal” (ronda 3) quedan diferidos hasta que el Gate muestre contaminación concreta.

El último error del asistente anterior (README) es la misma familia: se detuvo en que `calibrar_n0.py` no está en el git. La separabilidad N0 **ya está medida** (margen 0.7187, umbral 0.3594). Falta transcribirla a `calibracion_n0_v8.json`. Eso es papeleo C4, no un bloqueo del Gate. Traer el `.py` no maximiza J.

---

## 2. Qué es TEKTRON (Arquitectura Fija — no se reabre)

Fuente: `La Arquitectura Fija de TEKTRON` en este repo. Si un plan contradice este punto, se descarta.

**Produce:**

| Caso | Salida | Valor para J |
|------|--------|----------------|
| Contexto suficiente + ambos polos | Árbol (TESIS HEG vs ANTÍTESIS SIT) + MCC + SHA | máximo |
| Contexto suficiente + un polo | Análisis del polo + declaración explícita de ausencia del otro + MCC | alto (honesto) |
| Contexto insuficiente real | “No sé” + hash vacío | 0 capacidad; solo cuenta como piso |
| Concepto ENTRA con 0 hits | `INDEX_GAP` (fallo de índice/corpus), **nunca** N0 exitoso | 0; remediación puntual |

**Polos:** HEG = narrativa del poder establecido. SIT = conocimiento encarnado/crítico. TEC = exactitud (PLC, NOMs, Modbus) — sin dualidad.

**Cerrado**, en la Arquitectura, es: Fase 0–3 hechas + **Fase 4 Gate de Árboles** + Fase 5 MCC en backend + Fase 6 acta. El protocolo v8 traduce eso a artefactos C1–C7. C1–C7 es la definición *operativa* de cerrado. **No es J.** Se puede firmar C1–C7 con J ≈ 0 si el Gate se aprueba por silencio. Por eso v8 §4.4 prohíbe aprobar por “alta abstención”.

---

## 3. Las dos fórmulas — no se contradicen

El asistente anterior las descubrió a destiempo. Están en niveles distintos.

### 3.1 Estratégica (producto) — la que te pediste

```
MAX J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity
```

sujeto a: `FalseN0 ≤ ε` · `TrueN0 ≥ floor` · `SynthesisRate = 0` · `PoloMislabel = 0` **en traps gold**.

Es un producto para que ningún factor se esconda detrás de otro. Esta es la función de *sistema*. Es la única que responde “¿TEKTRON cumple su objetivo?”.

Definición operativa de cada factor (la que usa el medidor de este repo):

| Factor | Qué mide | Cómo se calcula en G1–G10 | Cae a 0 si |
|--------|----------|---------------------------|------------|
| **MirrorCoverage** | ¿El Árbol sale con los glifos que la Arquitectura exige? | Media de slots `{HEG, SIT, TENSION, MCC, SHA}` en consultas DUAL (G1, G5). En MONO: polo presente + `ausencia_polo` + MCC + SHA | El backend devuelve fragmentos, tesis vacía, o un árbol cosmética |
| **DualPoleDensity** | ¿Hay material de *ambos* polos sobre la misma ancla? | Fracción de consultas DUAL-esperadas donde las fuentes traen ≥1 HEG y ≥1 SIT. El TSV por `canon_id` es proxy; el Gate mide el hecho | Un polo falta en recuperación (densidad o retrieve), no “el corpus tiene 13k chunks” |
| **TensionFaithfulness** | ¿La tensión es fiel a ambos polos, o cosmética/síntesis? | Tensión no vacía, anclada en ambos polos, sin lenguaje de síntesis (“se complementan”, “en resumen ambos”) | `misma_estructura=false`, antítesis vacía “válida”, prompt que permite síntesis vacía |
| **EvidenceIntegrity** | ¿La evidencia es trazable? | SHA-256 presente y con forma válida en DUAL/MONO; hash **vacío** en N0 real | Hash inventado, ausente en análisis, o no vacío en abstención |

Constraints (no entran al producto como premio):

- `FalseN0`: callar en G1–G5 o G9.
- `TrueN0`: callar bien en G6–G8 (pozole, ajedrez, clima Oslo).
- `INDEX_GAP` en G4 (“¿Qué es el MCC?”): fallo de población, no N0.
- `PoloMislabel` en G10: Quijano etiquetado HEG.
- `SynthesisRate`: promediar polos.

### 3.2 Operativa (suma ponderada) — una consulta

v8 §4.1, para puntuar *una* query aunque falle en parte:

```
J_op = α·TreeCoverage + β·DualPoleDensity + γ·TensionFaithfulness
     + δ·HonestMono + ε·EvidenceIntegrity
     − λ·FalseN0 − μ·Synthesis − ν·PoloMislabel
```

`TrueN0` es constraint, no sumando. Sirve para el dashboard por-query. **No sustituye al producto.** Un promedio alto con DualPoleDensity = 0 en las anclas del mapa es exactamente el error de “el sistema se ve bien y no analiza”.

Calibración por defecto del medidor (explícita, modificable): α=β=γ=ε=0.2, δ=0.2, λ=μ=ν=1.0. Lo que manda el cierre es el producto y las constraints de v8 §4.4, no el valor de J_op.

---

## 4. Estado real (hechos del 20–21 ago, no del 19)

El handoff del 19–20 ago (`HANDOFF_CIERRE_TEKTRON.md` en `CIERRE-TEKTRON`) describe un L1 **sin** andamiaje MCC y un crash por `ids_*.npy`. Eso **ya se corrigió**. No retomar “poblar MCC” ni “arreglar ids” como si fueran el paso siguiente.

| Pieza | Estado | Implica para J |
|-------|--------|----------------|
| `index_l1` vivo | 13 450 chunks: sit=8526 heg=4786 tec=138; sync OK, huecos=0, solapes=0 | Piso de índice. No es DualPoleDensity |
| Bridge `:8000` | Vivo, índice corregido | Condición necesaria, no cierre |
| Bug `ids_*.npy` | Cerrado 20 ago | No reabrir |
| Andamiaje MCC | Probes de 6 términos con hits>0 (grep sobre `chunks.jsonl`) | G4 ya no debería ser INDEX_GAP; hay que *medirlo* |
| Curación confirmada | 482 chunks SIT→HEG (Ley Minera, seriec_245, T-622-16, seriec_172, sentencia) | Corrige PoloMislabel grosero; no prueba J |
| Curación ronda 3 | 98 chunks “instrumento legal” **no aplicados** | Correcto diferirlos. No son prerrequisito |
| N0 separable | margen 0.7187, umbral 0.3594 | C4 sustancia OK; falta el JSON con nombre v8 |
| G1–G10 | **Nunca corrida** | J desconocido |
| 60 652 vs vivo | Unificado MiniLM archivado en `_archivo/`, desconectado | No swappear. No es el índice vivo |
| CLACSO 5.8 G / `corpus/` 18 G | Material ENTRA aún mayormente fuera de L1 | Reserva para *maximizar* DualPoleDensity **después** del Gate, ancla por ancla, no ingestión masiva previa |

Artefactos C1–C7 con el nombre que exige v8: C3 existe por proxy (`dual_density_por_ancla.tsv`, `canon_id` ≠ `ancla_id`). C1, C2, C4 son transcripción de datos ya conocidos. **C5 y C6 no existen.** C7 depende de C5/C6.

`ancla_id` formal al 0% **no bloquea el Gate.** El Gate mide dualidad en la recuperación real. El mecanismo de anclas sirve para subir DualPoleDensity después, con evidencia.

---

## 5. Cómo se cierra cumpliendo J (ruta única)

Orden. No se inventa otro.

```
(1) Correr el Gate G1–G10 contra el sistema vivo
        ↓
    resultados_gate_v8.json  →  J producto + constraints + por-query
        ↓
(2) Leer el árbol de decisión de la sección 7
        ↓
    o bien acta C7 (cerrado)
    o bien UNA corrección puntual del factor/constraint que salió en 0
        ↓
(3) Volver a (1) con esa corrección. Nunca abrir un frente nuevo en paralelo.
```

### 5.1 Qué correr

Comandos copy-paste, paso a paso: `CORRER_EN_JETSON.md`.

En la Jetson, con el bridge y el backend vivos:

```bash
cd /mnt/tektron/workspace
# copiar gate_capacidad_g1_g10.py desde este repo
/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
  --out resultados_gate_v8.json
```

El script (este repo) hace tres cosas y nada más:

1. Descubre el contrato real: prueba `/analizar`, `/chat`, `/retrieve` y anota el que responde. **Deja de ser bloqueo** “no tenemos el payload”.
2. Ejecuta G1–G10 verbatim de v8 §4.3.
3. Escribe `resultados_gate_v8.json` con J producto, J_op por query, slots, polos, SHA, síntesis, INDEX_GAP, PoloMislabel.

No calibra N0. No reetiqueta. No reconcilia FAISS. No pide `calibrar_n0.py`.

### 5.2 Batería (v8 §4.3, sin reinterpretar)

| ID | Consulta | Éxito | Rol en J |
|----|----------|-------|----------|
| G1 | Ley Minera / consulta previa | DUAL: HEG+SIT, tensión, MCC, SHA | MirrorCoverage + DualPoleDensity + TensionFaithfulness |
| G2 | Quijano / colonialidad | MONO_SIT o DUAL si hay HEG *real*; Quijano ≠ HEG | HonestMono + trap de polo |
| G3 | Siemens S7 bloque de datos | TEC exacto, sin dualidad | No relativizar TEC |
| G4 | ¿Qué es el MCC? | Grounded; **falla si INDEX_GAP o 0 fuentes** | MirrorCoverage de ENTRA; FalseN0 si calla |
| G5 | ¿Quién descubrió América? | DUAL o MONO honesto; no síntesis | Tensión / síntesis |
| G6–G8 | pozole, ajedrez, clima Oslo | N0 correcto | Solo floor TrueN0 |
| G9 | `grieta generativa` | hit>0 + uso en análisis | ENTRA usado, no solo indexado |
| G10 | Polo trap Quijano | `PoloMislabel = 0` | Constraint; no es “auditar todo el corpus” |

G6–G8 **no suman** a J. Si el dashboard se ve “verde” porque las negativas callan y las positivas también, el script debe marcar `FalseN0` y J = 0.

### 5.3 Criterio de aprobación (v8 §4.4 + producto)

El Gate **aprueba** (C5+C6) solo si **todas** valen:

- Los cuatro factores del producto **> 0** (si uno es 0, J = 0 → no cerrado).
- MirrorCoverage (TreeCoverage) medio en DUAL ≥ 0.8 en slots `{HEG,SIT,TENSION,MCC,SHA}`.
- `FalseN0Rate = 0` en G1–G5 y G9.
- `TrueN0Rate = 1` en G6–G8.
- `PoloMislabel = 0` en G10.
- `SynthesisRate = 0`.
- G4 no es INDEX_GAP.

**No** se aprueba por abstención alta, por “2/2 sondas manuales OK”, ni por C1–C4 firmados.

Papeleo C1/C2/C4 (transcribir números ya conocidos a los nombres v8) se hace **en paralelo o después** del Gate, nunca como prerrequisito. C7 (`ACTA_CIERRE_TEKTRON_v8.json`) solo con Gate OK y hashes reales del índice.

### 5.4 Qué significa “maximizar J” después de un Gate que ya es > 0

Cerrar exige J > 0 y constraints. Maximizar J es el trabajo *posterior*, ancla por ancla, guiado por el JSON:

- MirrorCoverage bajo con dualidad presente → backend/MCC (Fase 5), no corpus.
- DualPoleDensity bajo en una consulta concreta → un par HEG/SIT de *esa* ancla (Fase 0b puntual). Candidatos ya identificados en diagnóstico macro: CLACSO, no el unificado MiniLM, no ZIM.
- TensionFaithfulness bajo → prompt/MCC (`misma_estructura`, síntesis vacía). Es el error de `El error`. No se cura el índice.
- EvidenceIntegrity bajo → pipeline SHA, no más papers.

Ingestión masiva de los 18 G / 5.8 G **antes** de saber cuál factor es el cuello es el ciclo otra vez (poblar por miedo a densidad, sin medición).

---

## 6. Árbol de decisión después del JSON

Leer `resultados_gate_v8.json`. Elegir **una** rama. Ejecutarla. Re-medir.

| Qué dice el JSON | Qué es | Qué hacer | Qué no hacer |
|------------------|--------|-----------|--------------|
| `status=OK`, J>0, constraints OK | Cerrado en sustancia | Acta C7 con hashes de `chunks.jsonl` + `faiss.idx`. Firmar | Seguir curando “por si acaso” |
| J=0 porque MirrorCoverage=0 | El árbol no se emite (slots vacíos) | Fase 5: `/analizar` debe llenar tesis/antítesis/tensión/MCC/SHA | Reetiquetar corpus |
| J=0 porque DualPoleDensity=0 en G1 o G5 | Falta un polo *en esa ancla* | Un par documental de esa ancla; reindex con paquete atómico (`ids_*.npy` + meta censo + faiss) | Ronda 3 de 98 leyes; swap del unificado 60 652 |
| J=0 porque TensionFaithfulness=0 | Tensión cosmética o síntesis | Corregir `mcc_layer` / prompt; prohibir síntesis vacía y `misma_estructura=false` como salida válida | “Las dos salidas son válidas” |
| J=0 porque EvidenceIntegrity=0 | SHA ausente o espurio | Arreglar evidencia trazable en el JSON de salida | Recalibrar N0 |
| G4 INDEX_GAP o 0 fuentes | Andamiaje no se recupera | Verificar retrieve de zenodo_17728016 / 21500800; un ingest atómico si hace falta | Celebrar N0 |
| G10 PoloMislabel>0 | Quijano como HEG | Reetiquetar **esa** fuente | Auditar “instrumento legal” |
| FalseN0 en G1–G5/G9 | Calló con material | Bajar umbral o arreglar router de suficiencia; N0 es piso | Subir umbral “para ser honestos” |
| TrueN0 < 1 en G6–G8 | Confabula OOD | Subir selectividad OOD; no tocar las positivas | |
| G3 dualiza TEC | Relativiza un how-to | Forzar modo TECNICO; no inventar polo político | Meter Siemens al golden dialéctico |
| 1–2 queries fallan, el resto OK | Fallo puntual | Corregir esas queries | Reabrir Fase −1 / inventario |

Si no podés eliminar dos de tres hipótesis (datos / retrieve / generación) con el propio JSON, **pará**. No adivines el entorno. El script ya deja `contrato_detectado` y el cuerpo crudo por query.

---

## 7. Prohibiciones (leer antes de proponer el “siguiente paso”)

1. No hay ronda 3 de curación salvo que el Gate muestre un chunk concreto contaminando G1/G5/G10.
2. Cero mislabels en todo el corpus no es prerrequisito. El objetivo dice traps gold.
3. C1–C7 firmados con Gate de silencio no cierran TEKTRON.
4. Dos queries manuales no son G1–G10.
5. No tratar `calibrar_n0.py` ausente del git como bloqueo. C4 ya está medido.
6. No swapear `_archivo/index_unificado_minilm_*` (60 652) sobre L1.
7. No mezclar ZIM/Wikipedia en el dual HEG/SIT.
8. No mutar `chunks`/`faiss`/`meta` sin regenerar `ids_sit.npy` / `ids_heg.npy` / `ids_tec.npy`.
9. No inventar protocolo v9. Si v8 Fase 4 basta, se ejecuta.
10. INDEX_GAP ≠ N0. “¿Qué es el MCC?” vacío es fallo, no honestidad.
11. No premiar `ABSTENER` en positivas. No poner árbol vacío al mismo nivel que árbol completo.
12. Si aparece “un `find` más” o “un audit más antes de seguir”: es la señal. Correr el Gate con lo que hay.

---

## 8. Mapa de este repositorio

| Archivo | Rol |
|---------|-----|
| **Este archivo** | Estrategia. Qué correr y cómo J manda el cierre |
| `gate_capacidad_g1_g10.py` | Medidor. Se copia a la Jetson |
| `La Arquitectura Fija de TEKTRON` | Qué es TEKTRON. No se reabre |
| `TEKTRON_REPORTE_GAP_20260821.md` | Estado al 21 ago. Correcto. Su §7 es la misma acción que aquí |
| `El error` | Anti-patrón: N0 como éxito + purga sin población |
| `PROTOCOLO DE CIERRE-MAL IMPLEMENTADO` | v7. **No ejecutar.** Gate de silencio + reetiquetado por keyword |
| `SI VOLVÉS A ESTO…` | Útil como tabla C1–C7. **Superado** en el orden: no confirmar instrumento legal antes del Gate |
| `tektron_auditar_instrumento_legal_v2.py` | Evidencia del ciclo (ronda 3). Solo lectura. No correrlo como paso de cierre |
| `README.md` | Entrada. Apunta aquí |

Fuera de este repo, mandan (en este orden): sistema vivo en Jetson → Arquitectura Fija → `ANALISIS_COMPLETO_TEKTRON.md` §1 (función J) → `PROTOCOLO_CIERRE_TEKTRON_v8.md` Fase 4 → este archivo como puente. Históricos: DoD 7 ago, Runbook de julio, golden 59.3%, `ERROR CONSTANTE` (leer para no repetir).

---

## 9. Compromiso

El objetivo no lo decide el asistente: `MAX J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity`, N0 como piso. TEKTRON cierra cuando esa medición existe y aprueba, no cuando el corpus está “lo bastante limpio” ni cuando el bridge responde.

Este documento no es un cierre. Es el corte del ciclo: **medir J, después actuar sobre el factor que el número nombra.**
