# Protocolo de cierre — desde el Gate del 26 ago (no es v9)

Este archivo **instancia** la ruta que ya estaba en `ESTRATEGIA_CIERRE_J.md` §5. No la sustituye. Si aparece un menú (G3 vs G5 vs parar) o un inventario nuevo, se descarta.

## La ruta (invariante)

```
medir G1–G10 contra /chat vivo
  → resultados_gate_v8.json (J producto + constraints)
  → si aprueba → acta C7 → CERRADO
  → si falla → UNA corrección de lo que el JSON nombra → re-medir
Nada en paralelo. No hay v9.
```

Aprobación (la misma de siempre):

- J > 0
- TreeCoverage DUAL ≥ 0.8
- FalseN0 = 0
- TrueN0 = 1 en G6–G8
- Synthesis = 0
- PoloMislabel = 0 en G10
- G4 no INDEX_GAP

J es el producto. Las constraints no son J. N0 es piso, no meta.

## Dónde estamos (26 ago, segunda corrida)

| Criterio | Valor | ¿Cierra? |
|---|---|---|
| J | 0.35 | sí (> 0). Factores: Mirror 0.7 · Dual 0.5 · Tension 1.0 · Evidence 1.0 |
| TreeCoverage DUAL | 0.8 (G1) | sí |
| FalseN0 | **G3** | **no** |
| TrueN0 G6–G8 | 1 | sí (tras cortar ZIM en ABSTENER) |
| Synthesis | 0 | sí |
| PoloMislabel G10 | 0 | sí |
| G4 INDEX_GAP | no | sí |

Primera corrección (ya hecha, no reabrir): ZIM no rellena `ABSTENER`. G6–G8 OK. G1 sigue `ARBOL`.

El JSON nombra **`FalseN0`**, query **G3**. Eso es la única corrección permitida ahora.

DualPoleDensity 0.5 (G5 MONO_SIT) **no** está en `bottleneck` y **no** bloquea el acta bajo la regla de aprobación. No se toca en paralelo. Si tras G3 el Gate aprueba, se firma. Si el próximo JSON nombra DualPoleDensity, recién ahí.

## Única corrección ahora

**G3 / Siemens S7:** `/chat` devolvió `ABSTENER` con 0 fuentes. En `index_l1` ya hay chunks `TECNICO` (manuales S7-1500, Modbus, etc.). No es densidad. No es bajar umbral N0.

Cambio permitido: retrieve/router del bridge para que una query TEC recupere polo `TECNICO` y **responda** (sin dualidad, sin ZIM).

Prohibido en este paso: curar corpus, ronda 3, `calibrar_n0`, bajar umbral, indexar PDFs, inventariar, tocar G5, `tektron_restart_bridge.sh` (usar `systemctl restart tektron-bridge.service`).

## Después de esa corrección

1. `sudo systemctl restart tektron-bridge.service` (un solo python en `:8000`).
2. Un humo G3. Si habla TEC, correr G1–G10 otra vez.
3. Si `status=OK` → `emitir_acta_cierre_v8.py` → CERRADO.
4. Si `status=FAIL` → leer `bottleneck` del JSON nuevo. Una corrección. Stop.

El `siguiente` del medidor que decía “bajar umbral” era un error del script (familia ERROR CONSTANTE). Quedó corregido: FalseN0/G3 = modo TEC, no umbral.

## Cierre del Gate (26 ago, tercera corrida)

Corrección G3 completa: `retrieve_l1.py::decidir()` responde TEC cuando solo hay `sel_tec` (antes caía a `ABSTENER`); `tektron_bridge_l1.py::llamar_llm` recibe `ctx_tec` y usa una rama de prompt "TEC exacto, sin dualidad" (antes el contexto técnico se perdía y salía el mensaje genérico de ausencia dialéctica).

Gate re-corrido tras el parche:

```
G1  OK  ARBOL   HEG+SIT
G2  OK  ARBOL   HEG+SIT
G3  OK  MONO    TECNICO   (antes: ABSTENER, FalseN0)
G4  OK  UN_SOLO_LADO  SITUADO (MCC grounded)
G5  OK  UN_SOLO_LADO  SITUADO
G6  OK  ABSTENER  (N0 limpio, sin ZIM)
G7  OK  ABSTENER
G8  OK  ABSTENER
G9  OK  UN_SOLO_LADO  SITUADO (grieta generativa, grounded)
G10 OK  ARBOL   HEG+SIT (trap Quijano, PoloMislabel=0)

J=0.35  status=OK  bottleneck=[]
```

**Gate aprobado.** Siguiente y único paso: `emitir_acta_cierre_v8.py` con hashes reales de `chunks.jsonl` + `faiss.idx`. No reabrir curación, no tocar G5/DualPoleDensity — quedan documentados como frente de *maximización* posterior a C7, no como bloqueo del cierre.

## Sub-paso 2 (histórico, ya resuelto): router corregido, generación de texto no

Parche 1 en `retrieve_l1.py::decidir()`: dialéctica sin HEG/SIT pero con TEC → `_pack("MONO", "TECNICO", ...)` en vez de `ABSTENER`. Confirmado con restart + humo:

- `decision=MONO`, `n_fuentes=1`, `polos=['TECNICO']` — el router ya no aborta.
- `respuesta="No tengo material situado/hegemónico suficiente sobre esto."` — **texto equivocado**, no responde con el chunk TEC recuperado.

Causa probable: `_pack` no seteó `lado_unico` para la rama TEC nueva; el bridge decide el mensaje/prompt según `lado_unico` y cae al genérico de ausencia dialéctica en vez de usar `llamar_llm` con el contexto técnico.

Sigue siendo la corrección G3, no un frente nuevo. Próximo: leer en `tektron_bridge_l1.py` cómo se arma la respuesta para `decision.kind == "MONO"` con `clase == "TECNICO"`, y ajustar ese único tramo para que use el chunk TEC recuperado.
