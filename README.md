# romper-el-ciclo-tektron

Estrategia de cierre de TEKTRON bajo la función que el sistema debe maximizar:

```
J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity
```

N0 (abstención) es piso anti-confabulación, no meta. Un sistema que se calla siempre tiene error cero y valor cero.

## Empezá acá

1. **`ESTRATEGIA_CIERRE_J.md`** — qué está pasando (el ciclo de siete meses), las dos fórmulas de J, el estado real, la única acción siguiente y el árbol de decisión después de medir.
2. **`gate_capacidad_g1_g10.py`** — el medidor. Se copia a la Jetson y produce `resultados_gate_v8.json`. Sin ese JSON, J no tiene número y no hay cierre.
3. **`La Arquitectura Fija de TEKTRON`** — qué es TEKTRON. No se reabre.

Este git no hospeda el sistema vivo. El cierre se corre en `tektron@192.168.100.84:/mnt/tektron`.

## Única acción siguiente

```bash
/mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \
  --base-bridge http://127.0.0.1:8000 \
  --base-backend http://127.0.0.1:8001 \
  --out resultados_gate_v8.json
```

Si aprueba → acta C7. Si falla → el JSON nombra el factor o la constraint; una corrección puntual; re-medir. Nada de ronda 3 de curación, nada de protocolo v9, nada de esperar a `calibrar_n0.py` en el repo.

## Qué no leer como plan

| Archivo | Por qué |
|---------|---------|
| `PROTOCOLO DE CIERRE-MAL IMPLEMENTADO` | v7: Gate de silencio + reetiquetado por keyword |
| `SI VOLVÉS A ESTO…` | Pone auditoría de instrumento legal *antes* del Gate |
| `tektron_auditar_instrumento_legal_v2.py` | Traza de la ronda 3. No es paso de cierre |
| README anterior (error del asistente) | Se detuvo en un `.py` ausente del git; C4 ya estaba medido |

`TEKTRON_REPORTE_GAP_20260821.md` y `El error` siguen siendo diagnósticos válidos. La estrategia los sintetiza; no los sustituye como historia.
