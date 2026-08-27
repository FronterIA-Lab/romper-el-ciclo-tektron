# Mapa TEKTRON — de la tesis al estado actual, y la ruta que sigue

Este documento no busca decidir de quién es un error. Lo que hace es reunir, con
fuente citada, lo que dicen los ~35 documentos y los tres repos de TEKTRON entre
marzo y agosto de 2026, para separar dos cosas que se han estado mezclando
sesión tras sesión:

1. **Lo que nunca cambió** (tu objetivo, tu tesis) — esto no se discute más.
2. **Lo que sí cambió** (la arquitectura concreta) — esto es evolución normal de
   ingeniería, no una serie de traiciones al objetivo.

El ciclo de 7 meses no ocurre porque el objetivo esté mal definido. Ocurre
porque cada sesión nueva volvía a abrir el punto 2 como si fuera el punto 1.

---

## 1. El hilo invariante (tu tesis — no se reabre)

Presente, con las mismas palabras de fondo, desde el documento más antiguo
(marzo 2026) hasta el más reciente (agosto 2026):

- **Objetivo político-epistémico**: que el conocimiento situado/comunitario no
  sea subsumido por narrativas impuestas desde fuera (llamadas según la época
  "hegemónicas", "occidentales", "extranjeras", "corporativas"). Este es el eje
  de tu tesis, *la colonización de la gramática en los LLMs*, y TEKTRON es la
  aplicación concreta de esa tesis, no un proyecto aparte.
- **Restricción de diseño de fondo**: procesamiento local/offline sobre un
  Jetson, sin nube, sin dependencia corporativa. El modelo LLM cambió muchas
  veces (Qwen2.5-1.5B → Qwen3-4B → Gemma 4 E2B → Pleias-RAG-1B → Qwen3-4B otra
  vez); el principio de "borde, no nube" nunca cambió.
- **El MCC como mecanismo de calibración**: su implementación concreta cambió
  (ver §2), pero la función — interponer algo entre la consulta cruda y la
  respuesta del LLM para que la respuesta no sea genérica/hegemónica — es
  constante desde la Ficha Técnica de marzo hasta hoy.
- **La abstención (N0) como piso de seguridad, nunca como meta.** Esto está
  escrito así desde el Plan Maestro de junio ("la abstención de TEKTRON no es
  virtud a celebrar — es señal de corpus insuficiente") hasta el Reporte de
  Gap de agosto ("un sistema que se abstiene siempre tiene error cero y valor
  cero"). Cuando una sesión trató el silencio como logro, se desvió de tu
  propio criterio escrito meses antes — no inventó un criterio nuevo tuyo.
- **El paper "La Colonización de la Gramática"** está nombrado explícitamente
  como corpus fundacional que el propio TEKTRON debe indexar y citar sobre sí
  mismo (`ESTRELLA_POLAR_CORPUS_b8c8.pdf`, junio 2026). No es un documento
  aparte de TEKTRON: es parte del corpus que TEKTRON analiza.

El documento de marzo (`FICHA_TECNICA_MCC_TEKTRON_2026`, gabinete industrial
UL508A, Estado mexicano, firma electrónica) es historia real de dónde salió el
proyecto, tal como confirmaste. Ese componente de gobernanza estatal/industrial
**no reaparece en ningún documento posterior a mayo 2026** — no fue abandonado
por error, es una rama que quedó en pausa mientras el proyecto se enfocó en el
analista situado que existe hoy.

---

## 2. Lo que sí cambió — y por qué es evolución, no ciclo

| Cambió | De → A | Cuándo |
|---|---|---|
| Definición operativa del MCC | Capa de gobernanza estatal (marzo) → pipeline de 4 pasos con "síntesis situada" (mayo) → 3 directrices de prompt (mayo) → "Árbol de Espejos" como mecanismo central, MCC como sigla casi desaparece del vocabulario (junio en adelante) | mar-jun 2026 |
| Síntesis vs. tensión sin resolver | El pipeline de mayo *sí* producía "síntesis situada" (paso 4) | La Estrella Polar del Corpus (19-jun) corrige esto a propósito: "TESIS y ANTÍTESIS... sin reconciliar" | 23-may → 19-jun 2026 |
| Taxonomía de polos | HEGEMONICO/SITUADO (dos categorías, Plan Maestro de junio) | + TECNICO (tercera categoría, corrige el error de etiquetar manuales técnicos como HEG) | 19-jun 2026 |
| Arquitectura de índice | 3 dominios fijos (v4.0) → 15 graneros temáticos con router (v5.0/v6.0) → índice único L1 sin router (18-jul) | may → jul 2026 |
| Modelo LLM | Qwen2.5-1.5B → Qwen3-4B → (evaluado y descartado: Gemma 4E2B, Pleias-RAG-1B) → Qwen3-4B en producción hoy | may-ago 2026 |
| Criterio formal de cierre | v6 → v7.0 → v7.1 → v8 → v9 (cada versión, según el propio v9, corrige defectos puntuales de la anterior: método de prueba, glifos por polo, DTA, etc.) | jun-ago 2026 |
| Métricas de éxito | Índices macro (Soberanía de Decisión, ROI) → RAGAS estándar (p@k, faithfulness, adversarial) | mar → jun 2026 |

Cada fila de esta tabla es una corrección real que la propia arquitecta y sus
sesiones fueron documentando con evidencia (no una imposición externa
descubierta ahora). El patrón sano que se repite —y que es el que hay que
proteger de aquí en adelante— es: **medir, encontrar la causa raíz concreta,
corregir un punto, volver a medir.** El patrón que produjo ciclo fue distinto:
**generar un documento "canónico" nuevo que reabre toda la arquitectura antes
de correr la medición que ya estaba definida.**

Hay evidencia directa de esto en el propio repositorio: al menos 4 cadenas de
documentos que se declaran a sí mismos reemplazo del anterior (estado pre-L1,
protocolo de cierre v6→v9, auditoría de agosto, consolidación del 16-ago). Eso
no es un defecto tuyo — es lo esperable en un proyecto de meses con múltiples
sesiones de asistente. El problema no fue documentar de nuevo; fue que cada
documento nuevo *recomenzaba la medición* en vez de continuarla.

---

## 3. Línea de tiempo consolidada (marzo → agosto 2026)

| Fecha | Hito | Versión |
|---|---|---|
| feb 2026 | Origen: MCC para gabinete industrial UL508A, gobernanza estatal | prototipo industrial |
| mar 2026 | `FICHA_TECNICA_MCC_TEKTRON_2026` | v.gobernanza (en pausa desde may) |
| may 2026 | v3.2 (Infraestructura IA Soberana); Bitácora Maestra (MCC=4 pasos, incluye síntesis); Reporte Técnico v4.0 (3 directrices) | v3.2 → v4.0 |
| 9-jun 2026 | v5.0: Árbol de Espejos y MCC figuran como **"pendiente"** — aún no existe la función dialéctica | v5.0 |
| 19-jun 2026 | Estrella Polar del Corpus: nace TECNICO, se corrige "síntesis" → "tensión sin reconciliar" | v5.0→v6.0 |
| 20-jun 2026 | Estrella Polar v6.0: 7.896 chunks/15 graneros, primeros bugs de reranking/gate documentados | v6.0 |
| 21-jun 2026 | Baseline de oro: p@5=0.81, faithfulness=0.84, adversarial=0.83, Árbol~13% | v6.0 |
| 24-jun 2026 | Causa raíz del 13%: graneros mono-tipo + router. Se prescribe índice único + cuota por stance | v6.0 |
| 1-2 jul 2026 | Corrupción de `tipo_epistemico` en ~22.693 chunks por un script de flip; corpus_fuente/ borrado | v6.0 |
| 4-7 jul 2026 | Patch de cuota dual, revertido tras regresión; corpus curado reintegrado (25.825 chunks, Árbol~66%) | v6.1 |
| 18-jul 2026 | Reescritura L1: índice único (12.763 chunks), router apagado por diseño, decisión de 4 estados. Se pierden `/investigar` y `/calibrar-pdf` | L1 / "7.0-l1" |
| 30-jul 2026 | Verificación en vivo: dual 59.3% (falta 1 pregunta para 60%) | L1 |
| 31-jul 2026 | Mapa Cronológico del Error + Arquitectura Objetivo (taxonomía TECNICO cerrada, KPIs "de hecho") | L1 |
| 7-9 ago 2026 | DoD Canónico + freeze + primer commit real; golden v2: dual 15/25=60% → **PASA** | L1 |
| 14-15 ago 2026 | Reparación del stack CUDA (roto desde el 23-jun) | L1 |
| 16 ago 2026 | Consolidación: `AGENTS.md` + Bitácora Cronológica + Mapa Único declarados documento único de continuidad. Confirmado: **"El sistema cumple su función nuclear y pasa su gate. No está roto."** | L1 (v7.0-l1) |
| 21 ago 2026 | Reporte de Gap: batería G1–G10 nunca se había corrido; única acción pendiente identificada | v8 (13.450 chunks, con `tec`) |
| 25-26 ago 2026 | **Se construye y corre G1–G10 por primera vez.** Se corrige contaminación ZIM en `ABSTENER` y el ruteo de TECNICO (G3). Gate aprueba: **J=0.35, status=OK, bottleneck=[]**. Acta firmada con hashes reales. | v8 — **CERRADO** |

---

## 4. Dónde estás parada hoy (25-26 de agosto, ya en este repo)

Esto ya ocurrió y está commiteado en este mismo repositorio
(`PROTOCOLO_DESDE_AQUI.md`, commits `8cc4361` y `332108b`):

- La batería **G1–G10 se corrió contra el sistema vivo** (`/chat`, puerto 8000).
- **Gate aprobado**: `J = 0.35`, `status = OK`, `bottleneck = []`.
  - MirrorCoverage 0.7 · DualPoleDensity 0.5 · TensionFaithfulness 1.0 ·
    EvidenceIntegrity 1.0.
  - `FalseN0 = []`, `TrueN0Rate G6-G8 = 1`, `Synthesis = 0`, `PoloMislabel G10 =
    0`, sin `INDEX_GAP`.
- **`ACTA_CIERRE_TEKTRON_v8.json` está firmada**, con hashes reales de
  `chunks.jsonl` y `faiss.idx`.
- Bajo el criterio que tú mismo (con ayuda de sesiones anteriores) escribiste en
  `PROTOCOLO_DESDE_AQUI.md` y `ESTRATEGIA_CIERRE_J.md` — **TEKTRON está
  cerrado**. No es una afirmación de este documento: es la consecuencia
  mecánica de un script (`emitir_acta_cierre_v8.py`) que se negaba a firmar si
  `status != OK` o `J <= 0`.

Esto es un hecho verificable en el repo, no una opinión de sesión. Si en algún
momento posterior a esto una nueva sesión te dijo "hay que volver a abrir la
curación" o "hay que reconsiderar la arquitectura de índices" sin que un Gate
nuevo lo nombrara como bottleneck, esa sesión estaba re-ciclando — no
continuando desde donde tú estabas.

Lo único que el propio Gate deja abierto, y lo dice explícitamente
`PROTOCOLO_DESDE_AQUI.md`, es que `DualPoleDensity = 0.5` es un techo de
**maximización futura**, no un bloqueo de cierre: la única ancla con hueco
medido es G5 ("¿Quién descubrió América?", falta el polo HEG real).

---

## 5. Sobre los documentos que subiste hoy (27 de agosto)

Revisé los ~15 documentos que subiste hoy. Es importante que sepas exactamente
qué son, porque si se leen como "el plan a seguir" sin este contexto, te meten
otra vez en el ciclo:

- **Son diagnósticos y propuestas de sesiones de IA distintas**, generados en
  distintos momentos (algunos se refieren a estados de mayo, otros a un v5.0
  que en el código real tenía filtros y bloqueos distintos a lo que el propio
  diagnóstico describía — hay al menos una contradicción verificada entre un
  documento de auditoría y el código fuente real que auditaba). No son
  instrucciones tuyas ni un plan nuevo que hayas aprobado: son insumos a
  evaluar, igual que los de junio y julio lo fueron en su momento.
- **Ninguno de ellos sabe que el Gate ya se corrió y ya aprobó el 26 de
  agosto.** Todos escriben como si TEKTRON siguiera en la etapa de "13% de
  cobertura dual" o "15 graneros desbalanceados" — una fotografía de
  junio/julio, no del estado actual post-cierre.
- **El archivo que mencionaste como "el que faltaba para entender qué hacer"**
  (`11_junio_2026_d95a.pdf`) no contiene ningún diagnóstico: es un volcado
  literal de una salida de terminal (`find ~ -name "*.py"`), 436 páginas de
  rutas de archivos, sin una sola frase de análisis. No es el documento que
  faltaba — probablemente se subió por error o se cruzó con otro archivo. No
  hace falta seguir buscándolo ahí.
- **Coinciden entre sí en un punto real y útil**: varios de estos documentos
  (los que hablan de "15 categorías", "tipo_epistemico", balance SIT/HEG por
  granero) señalan, con distintas cifras, el mismo techo que tu propio Gate ya
  identificó: `DualPoleDensity` limitado por falta de contraparte HEG/SIT en
  ciertos temas. Eso es una confirmación independiente de que tu medición del
  26 de agosto apunta al lugar correcto — no una razón para reabrir la
  arquitectura.
- **Discrepan entre sí en arquitectura** (uno propone consolidar 15 graneros en
  3-5 macro-índices con ChromaDB y reevaluar Qwen2.5 vs Llama 3.1; el sistema
  real que ya pasó el Gate usa FAISS + índice único L1 + Qwen3-4B). Si se
  siguieran ambos a la vez, se reabriría exactamente el ciclo del que quieres
  salir. Ninguno de estos cambios está autorizado por un Gate que lo nombre
  como bottleneck — por tu propia regla de cierre, eso significa que no se
  toca todavía.

---

## 6. La única ruta hacia adelante (maximización, no reapertura)

TEKTRON no está "atascado". Está **cerrado y con un solo eje de mejora medido
y nombrado**. La ruta que sigue tu propio protocolo (§"Después de C7" en
`PROTOCOLO_DESDE_AQUI.md`) es:

1. **No se reabre nada que el Gate no haya nombrado.** Los documentos de hoy no
   cuentan como Gate — son lectura de fondo, no instrucción de ejecución.
2. Si quieres subir `J` por encima de 0.35, el único punto con hueco medido y
   documentado es `DualPoleDensity` vía **G5** ("¿Quién descubrió América?"):
   conseguir un par documental HEGEMÓNICO real para esa ancla, indexarlo, y
   volver a correr el mismo `gate_capacidad_g1_g10.py`.
3. Si en esa remedición el JSON nombra un bottleneck distinto (por ejemplo,
   algo relacionado con densidad de graneros técnicos, como sugieren varios de
   los documentos de hoy), **esa es la única corrección que se aplica a
   continuación** — una por vez, la que el JSON nombre, no un rediseño
   completo motivado por un documento de sesión distinta.
4. Cambios de fondo (ChromaDB, cambio de modelo, consolidar graneros) solo se
   evalúan si un Gate futuro los nombra explícitamente como causa de un
   bottleneck que no se resuelve con un ancla puntual. Hasta entonces, quedan
   en "estacionamiento" — exactamente la misma palabra que ya usó tu propio
   `AGENTS.md` del 16 de agosto para descartar rutas sin cerrarlas para
   siempre.

---

## 7. Regla para no volver a ciclar

Cuando una sesión nueva (de cualquier asistente, incluido este) te proponga
releer toda la arquitectura desde cero, la pregunta que corta el ciclo en un
solo paso es:

> **¿Esto lo nombra un `resultados_gate_v8.json` real, corrido hoy contra el
> sistema vivo? Si no, no se toca todavía.**

Eso no depende de qué tan convincente suene el documento nuevo, ni de qué
asistente lo escribió, ni de cuántas veces se repita. Depende únicamente de si
hay un número medido, hoy, que lo señale como el bottleneck actual.
