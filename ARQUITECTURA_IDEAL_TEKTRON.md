# Arquitectura ideal de TEKTRON — de "cerrado por Gate" a "empaquetado"

Este documento corrige un error de encuadre del `MAPA_TEKTRON.md`: tratar el
acta firmada (`J=0.35`) como si fuera la meta. No lo es. `J=0.35` confirma un
**piso mecánico** (no confabula, no sintetiza donde no debe, no mislabelea los
traps). No confirma que TEKTRON sea una herramienta valiosa, ni que esté
empaquetada. Ese es el objetivo real que nunca cambió — lo que cambiaba, sesión
tras sesión, era la ruta técnica para llegar ahí, y varias veces esa ruta se
perdió por bugs de bajo nivel (indexado, memoria, CUDA), no por falta de
claridad sobre el objetivo.

Este documento responde tres preguntas concretas que quedaron abiertas:

1. ¿Qué dice la literatura académica de RAG (tus 14-15 papers) sobre cómo subir
   `DualPoleDensity` y resistir la sicofancia de recuperación, sin inflar el
   corpus?
2. ¿Qué pasó con el cosechador?
3. ¿Qué falta para que esto esté empaquetado — no solo el backend, hasta el
   HTML?

---

## 1. Qué significa "empaquetado" (nadie lo había definido)

Revisé los ~35 documentos y ninguno define "empaquetado" o "producto
terminado". Lo más cercano es la definición de **CERRADO** en `La Arquitectura
Fija de TEKTRON` (6 fases, termina en el Gate + acta), y el propio
`PROTOCOLO_CIERRE_TEKTRON_v9` dice explícitamente que el frontend **no bloquea
el acta** — queda en "Bloque F, post-cierre".

Eso es correcto como definición de *cierre técnico mínimo*, pero no es lo que
tú buscas. Propongo esta definición operativa de **empaquetado**, para que
dejemos de discutir sobre un término sin criterio:

> **TEKTRON está empaquetado cuando una persona sin acceso a ti, con el
> hardware documentado (Jetson Orin Nano 8GB) y el HTML servido por el bridge,
> puede: (a) hacer una pregunta de conflicto epistémico y recibir un Árbol de
> Espejos correcto o una abstención honesta; (b) hacer una pregunta fáctica
> simple ("¿quién descubrió América?") y recibir una respuesta directa y útil,
> no un abstenerse ni un árbol forzado; (c) subir un documento propio desde la
> interfaz y que el sistema lo use en esa sesión; y (d) instalar el sistema
> desde cero siguiendo un solo documento, sin tu intervención.**

Bajo esta definición, TEKTRON **no está empaquetado hoy**, aunque el Gate haya
aprobado. Las secciones 2-4 explican exactamente qué falta y en qué orden.

---

## 2. El caso G5 ("¿quién descubrió América?") — por qué es el síntoma correcto

Tienes razón en usar esta pregunta como ejemplo. En el Gate v8, G5 es una
pregunta *dialéctica* (la narrativa colonial del "descubrimiento" vs. la
perspectiva de los pueblos que ya habitaban el territorio) — y salió
`MONO_SIT` porque el corpus no tiene el polo HEGEMONICO real para esa ancla.

Pero tu punto es más amplio: **TEKTRON también necesita poder responder
preguntas simples, directas, sin forzar dialéctica donde no hay conflicto
real** ("¿qué hora es?", "¿cómo configuro un bloque de datos en un S7?" — esto
último ya está resuelto, es el caso TECNICO). El riesgo, si no se distingue
bien, es un sistema que o siempre abstiene, o siempre arma un árbol aunque sea
forzado. Las recomendaciones P4-P6 de la sección 3 atacan exactamente esto: una
decisión explícita, por polo, de si hay evidencia suficiente — no una
heurística de "si hay 2 chunks, hay árbol".

---

## 3. Qué dice la literatura (síntesis de 15 papers, priorizada por impacto/esfuerzo)

Se leyeron completos los 15 papers en `/tmp/papers/` (abstención honesta,
retrieval con metadatos estructurales, evaluación de RAG, SLMs fieles). Ninguna
recomendación implica agregar contenido genérico "para balancear" — todas
actúan sobre cómo se recupera, se pondera o se decide con lo que **ya existe**
en el corpus (13.450 chunks: 8.526 SIT, 4.786 HEG, 138 TEC).

### Fase 1 — bajo esfuerzo, se implementan sobre el bridge actual (no tocan modelo ni corpus)

| # | Qué hacer | Por qué (paper) | Efecto esperado |
|---|---|---|---|
| P1 | **Query Twin Expansion**: antes de embeber la pregunta, generar con el propio Qwen3-4B dos reescrituras (framing hegemónico / framing situado) y recuperar con ambas. Hoy la query "neutra" hereda el vocabulario de quien pregunta y sesga el retrieval hacia el polo léxicamente más cercano — esa es una causa concreta de sicofancia de recuperación. | *Agent-Based RAG* (query structuring), *IslamicLegalBench* (el framing induce sicofancia) | Sube `DualPoleDensity` sin tocar el corpus |
| P2 | **Recuperación por cuotas**: tratar SIT y HEG como dos índices/expertos independientes, recuperar top-N de cada uno por separado, en vez de un pool único donde el polo con más masa (8.526 vs 4.786) domina por defecto | *SOPRAG* (multi-expert routing) | Evita que HEG quede sistemáticamente sub-representado en el pool final |
| P3 | **Boost de escasez de polo en el reranker**: `score_final = CrossEncoder(q,d) + w · escasez(polo(d), pool_actual)` — fórmula determinística, sin fine-tuning | *technologies-14-00129* (boosting curricular por metadatos, mismo tipo de CrossEncoder que ya usa TEKTRON) | Re-prioriza sin inflar corpus |
| P4 | **Chequeo de suficiencia por polo** (no solo relevancia): antes de generar, verificar si el conjunto HEG y el conjunto SIT, cada uno por separado, alcanzan un umbral real de "hay respuesta construible con esto" — con el propio CrossEncoder, sin modelo nuevo | *Sufficient Context* (más contexto reduce la abstención incluso sin ayudar — riesgo real de "falso MirrorCoverage") | Evita árboles forzados con un polo débil |
| P6 | **Salida estructurada con status explícito por polo** en el prompt: `STATUS_THESIS: ANSWERABLE/UNANSWERABLE` + cita literal, `STATUS_ANTITHESIS: ídem`, antes de construir el árbol. Solo cambio de prompt, sin entrenamiento | *OCC-RAG* | Mejora `EvidenceIntegrity`; además da al frontend un dato limpio para mostrar (ver §4) |
| P8 | **No usar ejemplos few-shot de contenido** en el prompt de generación (solo few-shot de formato/estructura de abstención si hace falta) | *IslamicLegalBench* (few-shot de contenido sube la sicofancia +3.49pp de forma consistente) | Reduce sicofancia sin costo |

### Fase 2 — esfuerzo medio, formalizan y auditan lo de la fase 1

- **P5**: decisión de 4 celdas en el router (solo THESIS soportada / solo ANTITHESIS / ambas → árbol / ninguna → "no sé"), usando como señal el score del reranker + el chequeo P4, sin necesitar acceso a hidden states del modelo (que no son triviales de extraer vía `llama.cpp`/GGUF).
- **P7**: taxonomía de abstención — distinguir "tema mono-epistémico real" de "query ambigua" o "contradicción interna del polo", en vez de un "No sé" único. Esto es lo que permite decidir, con criterio y no a ciegas, cuándo sí vale la pena cosechar más corpus para un tema puntual (ver §5).
- **P9**: evaluación generativa/dinámica de anti-sicofancia (perturbar las queries existentes con premisas falsas/contradicciones, no depender solo de las 10 fijas del Gate) + separar el modelo que evalúa faithfulness del modelo que genera (hoy ambos son Qwen3-4B — riesgo de sesgo de auto-preferencia).
- **P10**: clustering temático offline de los chunks existentes (sin agregar contenido) para medir `DualPoleDensity` por clúster y distinguir "tema sin ambos polos en el corpus" de "polo presente pero el retriever no lo trae".

### Fase 3 — alto esfuerzo, opcional, solo si 1-2 no alcanzan

- **P11**: fine-tuning estilo GRACE de Qwen3-4B (mismo modelo que ya usás) para que la decisión de suficiencia por polo sea aprendida, no heurística. Requiere GPU externa al Jetson; el resultado final es un `.gguf` que cae en el pipeline actual sin cambiar la arquitectura de inferencia.
- **P12**: arquitectura evidencial completa (cabezas Dirichlet + Dempster-Shafer) o probes de hidden-state — la solución más elegante conceptualmente, pero cara de integrar con un modelo cuantizado GGUF. Diferir hasta confirmar que P4/P5 no bastan.

**Ninguna fase requiere cambiar FAISS por ChromaDB, ni Qwen3 por Qwen2.5, ni
consolidar los graneros.** Esas propuestas venían de documentos de sesiones que
no conocían el estado real del sistema (ver `MAPA_TEKTRON.md` §5) y no están
respaldadas por brecha medida alguna — se archivan como "estacionamiento",
igual que ya hizo `AGENTS.md` el 16 de agosto con otras rutas.

---

## 4. El frontend (lo que falta hasta el HTML)

Estado verificado (16-ago-2026, `TEKTRON_BITACORA_CRONOLOGICA_2026-08-16` y
`AGENTS.md`): `tektron.html` existe y corre, pero de 5 funciones que la
interfaz promete, solo 2.5 están vivas.

| Función de la interfaz | Endpoint | Estado |
|---|---|---|
| Consultar en modo soberano | `POST /chat` | Viva |
| Ver estado del sistema | `GET /health` | Viva |
| Modo asistido con web | `POST /chat` (`use_web=true`) | Muerta por diseño (offline-first) |
| **Agregar documento propio (subir PDF)** | `POST /calibrar-pdf` | Muerta desde la reescritura L1 (18-jul) |
| **Investigación profunda** | `POST /investigar` | Muerta desde la reescritura L1 (18-jul) |

Esto es exactamente tu punto (c) de la definición de empaquetado: "subir un
documento propio desde la interfaz". Hoy el botón existe en el HTML pero no
hace nada — es lo que `AGENTS.md` ya señaló como inaceptable ("una pantalla que
promete lo que el sistema no hace") sin que se haya tomado la decisión.

**La decisión pendiente, con las dos opciones reales:**

1. **Restaurar `/calibrar-pdf` en L1** con el mismo contrato de "memoria de
   usuario" que ya define `La Arquitectura Fija de TEKTRON` (punto 3.2): el PDF
   subido vive en `memoria_usuario.json`/sesión, nunca se integra al corpus
   base ni afecta `index_l1`. Esto es coherente con la arquitectura fija — no
   es una función nueva, es restaurar algo que la reescritura de julio dejó
   afuera sin querer.
2. Si no se restaura ahora, **ocultar el botón muerto en el HTML** para no
   prometer algo que el sistema no hace. Esto es aceptable como estado
   temporal, nunca como estado final, porque tu propia definición de
   empaquetado (punto c) lo requiere.

Recomendación: opción 1. Es la pieza que más directamente conecta con "para
que esté empaquetado debe estar resuelto hasta el HTML" — sin esto, el HTML
miente sobre lo que el sistema hace, y eso no es un detalle cosmético.

`/investigar` (investigación web profunda) es distinto: choca con el principio
"offline-first, sin DDGS" que la propia arquitectura decidió a propósito para
L1. Ahí la recomendación es ocultarlo del HTML de forma permanente, no
restaurarlo — no es una función perdida por accidente, es una función
descartada por diseño que el HTML todavía anuncia por error.

---

## 5. El cosechador — no se rompió, se pausó, y es la pieza correcta para crecer el corpus

Verificado con los documentos del 16-ago: el cosechador **no causó** el bug del
1-2 de julio. Al contrario — es citado textualmente como *"la única pieza que
ya hacía lo correcto"*: `tektron_harvester_inmune.py` asignaba el polo
HEG/SIT **a mano, por la arquitecta, en el momento de la cosecha**, exactamente
el principio que `AGENTS.md` después escribió como regla no negociable ("el
polo lo decide la arquitecta, en ingesta, por archivo — nunca script, nunca
frontmatter"). El bug vino de un script de remediación *distinto*, que sí
intentó asignar/corregir el polo de forma algorítmica.

Estado real: el cosechador es un subsistema de 6 piezas que corría **solo en el
iMac**, nunca en la Jetson, respaldado por hash en `~/Vault/`. No está roto; no
está activo en el pipeline de producción L1 (que hoy no ingesta nada nuevo).

Esto importa para el punto P7/P10 de arriba: cuando la taxonomía de abstención
o el clustering por tema identifiquen *qué* ancla específica necesita el otro
polo (como ya pasó con G5, "quién descubrió América"), **el cosechador con
asignación manual de polo es la herramienta correcta para llenar ese hueco
puntual** — no un script automático, y no una purga masiva. Es la misma lógica
que ya usaste para cerrar G3 (Siemens S7): una corrección dirigida, no una
ronda general.

---

## 6. Ruta completa hacia el empaquetado (orden de ejecución)

Esto no reabre el Gate ya aprobado; lo continúa hacia el objetivo real.

1. **Fase 1 de la sección 3** (P1, P2, P3, P4, P6, P8) sobre el bridge L1
   actual. Bajo esfuerzo, no toca corpus ni modelo. Re-medir con
   `gate_capacidad_g1_g10.py` después de cada cambio — igual que ya hiciste con
   ZIM/G3.
2. **Decisión de frontend** (sección 4): restaurar `/calibrar-pdf` con
   contrato de memoria de usuario, ocultar `/investigar` permanentemente.
3. **Fase 2 de la sección 3** (P5, P7, P9, P10) para formalizar y auditar, y
   para decidir con datos —no a ojo— si algún ancla puntual (como G5) necesita
   una cosecha manual dirigida vía el cosechador.
4. **Empaquetado real**: un solo documento de instalación que cubra
   `tektron-llm.service`, `tektron-bridge.service`, `tektron-clocks.service`,
   el `.gguf`, `index_l1/`, y el HTML — de forma que alguien sin tu
   intervención pueda levantar una instancia nueva. Este paso no existe hoy en
   ningún documento como tal (lo más cercano es la "Fase 5 — Despliegue
   soberano" de la Bitácora Maestra de mayo, nunca ejecutada).
5. Solo si después de 1-3 sigue habiendo techo estructural: evaluar P11
   (fine-tuning GRACE-style de Qwen3-4B). P12 se difiere indefinidamente salvo
   que 1-3 demuestren ser insuficientes con evidencia medida.

Cada paso se mide con el mismo Gate que ya existe, más las extensiones de la
fase 2 (P9: evaluación generativa de sicofancia). Ningún paso está autorizado a
saltarse la medición ni a "adelantarse" al anterior — esa es la regla que ya
protegió el cierre del 26 de agosto y es la misma que protege esto.
