#!/usr/bin/env python3
"""
Barrido COMPLETO, de una sola pasada, del patron "instrumento legal"
(Ley/Reglamento/Decreto/Convenio/CPEUM/Protocolo) -- el ULTIMO patron de
mislabel que queda sin cerrar. El patron "sentencia de tribunal" ya se
cerro hoy (482 chunks corregidos, 2 rondas, verificado en produccion).
Este es el que quedo de la sesion anterior como "~20 candidatos heuristicos
sin confirmar".

Mismo metodo que ya funciono hoy: para cada fuente que matchea el patron Y
tiene al menos un chunk SITUADO, imprime texto real (no el nombre) para que
la revision sea sobre evidencia, en un solo pase -- no una investigacion
por cada candidato.

Solo lectura. No relabelea nada.

Uso en Jetson:
  /mnt/tektron/venv_tektron/bin/python3 /mnt/tektron/workspace/tektron_auditar_instrumento_legal_v2.py
"""
from __future__ import annotations

import json
import re
from collections import Counter, defaultdict
from pathlib import Path

L1 = Path("/mnt/tektron/index_l1")

PATRON_LEGAL = re.compile(
    r"(^L[A-Z]{2,6}$|_Ley_|^Ley_|^LEY_|Reglamento|Convenio_\d|Decreto|CPEUM|Protocolo_)"
)


def polo_of(r):
    s = str(r.get("tipo_epistemico") or r.get("polo") or "").strip().upper()
    if s in ("SIT", "SITUADO", "SITUADA"):
        return "SITUADO"
    if s in ("HEG", "HEGEMONICO", "HEGEMÓNICO", "HEGEMONICA", "HEGEMÓNICA"):
        return "HEGEMONICO"
    if s in ("TEC", "TECNICO", "TÉCNICO", "TECH"):
        return "TECNICO"
    return s or "?"


def text_of(r):
    return r.get("text") or r.get("contenido") or r.get("chunk") or r.get("body") or ""


def main():
    por_fuente = defaultdict(list)
    with (L1 / "chunks.jsonl").open(encoding="utf-8", errors="ignore") as f:
        for line in f:
            line = line.strip()
            if not line:
                continue
            r = json.loads(line)
            fuente = str(r.get("fuente") or r.get("source") or "")
            if PATRON_LEGAL.search(fuente):
                por_fuente[fuente].append(r)

    print("fuentes que matchean patron instrumento legal:", len(por_fuente))
    print()

    total_sit_a_revisar = 0
    fuentes_con_sit = []
    for fuente, rows in sorted(por_fuente.items(), key=lambda kv: -len(kv[1])):
        polos = Counter(polo_of(r) for r in rows)
        sit = polos.get("SITUADO", 0)
        heg = polos.get("HEGEMONICO", 0)
        tec = polos.get("TECNICO", 0)
        print("===", fuente, "=== total=", len(rows), dict(polos))
        if sit == 0:
            print("  ya esta bien (heg=%d, sit=0) -- no requiere accion" % heg)
        else:
            total_sit_a_revisar += sit
            fuentes_con_sit.append((fuente, sit))
            print("  <-- tiene %d chunks SITUADO. Evidencia real:" % sit)
            muestras = [r for r in rows if polo_of(r) == "SITUADO"][:2]
            for m in muestras:
                print("    ---")
                print("   ", text_of(m)[:400].replace("\n", " "))
        print()

    print("=== resumen ===")
    print("fuentes con SITUADO a revisar:", len(fuentes_con_sit))
    for fuente, sit in fuentes_con_sit:
        print("  ", fuente, ":", sit, "chunks")
    print("total chunks SITUADO en patron instrumento legal:", total_sit_a_revisar)


if __name__ == "__main__":
    main()
