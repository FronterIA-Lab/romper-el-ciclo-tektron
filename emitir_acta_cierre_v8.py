#!/usr/bin/env python3
"""Emite ACTA_CIERRE_TEKTRON_v8.json solo si el Gate aprobó.

No firma silencio. No firma J=0. No sustituye resultados_gate_v8.json.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for chunk in iter(lambda: f.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--gate", default="/mnt/tektron/workspace/resultados_gate_v8.json")
    ap.add_argument("--index", default="/mnt/tektron/index_l1")
    ap.add_argument("--out", default="/mnt/tektron/workspace/ACTA_CIERRE_TEKTRON_v8.json")
    args = ap.parse_args()

    gate_path = Path(args.gate)
    if not gate_path.is_file():
        print("FAIL: no existe", gate_path, file=sys.stderr)
        print("Corré primero gate_capacidad_g1_g10.py. No hay acta sin medición.", file=sys.stderr)
        return 2

    gate = json.loads(gate_path.read_text(encoding="utf-8"))
    metricas = gate.get("metricas") or {}
    status = gate.get("status")
    j = gate.get("J")
    if j is None:
        j = metricas.get("J")

    if status != "OK" or not (isinstance(j, (int, float)) and j > 0):
        print("FAIL: el Gate no aprobó. No se firma el acta.", file=sys.stderr)
        print("status:", status, "J:", j, file=sys.stderr)
        print("bottleneck:", gate.get("bottleneck") or metricas.get("bottleneck"), file=sys.stderr)
        print("siguiente:", gate.get("siguiente"), file=sys.stderr)
        return 1

    index = Path(args.index)
    chunks = index / "chunks.jsonl"
    faiss = index / "faiss.idx"
    missing = [str(p) for p in (chunks, faiss) if not p.is_file()]
    if missing:
        print("FAIL: faltan artefactos del índice:", missing, file=sys.stderr)
        return 2

    acta = {
        "proyecto": "TEKTRON v8.0",
        "fecha": datetime.now(timezone.utc).isoformat(),
        "arquitecta": "Dolores Méndez Valdez",
        "funcion_objetivo": "J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity",
        "n0": "piso, no meta",
        "fase_4_gate": {
            "status": status,
            "J": j,
            "MirrorCoverage": metricas.get("MirrorCoverage"),
            "DualPoleDensity": metricas.get("DualPoleDensity"),
            "TensionFaithfulness": metricas.get("TensionFaithfulness"),
            "EvidenceIntegrity": metricas.get("EvidenceIntegrity"),
            "TreeCoverage_DUAL": metricas.get("TreeCoverage_DUAL"),
            "FalseN0": metricas.get("FalseN0"),
            "TrueN0Rate": metricas.get("TrueN0Rate"),
            "SynthesisRate": metricas.get("SynthesisRate"),
            "PoloMislabel": metricas.get("PoloMislabel"),
            "INDEX_GAP": metricas.get("INDEX_GAP"),
            "archivo_gate": str(gate_path),
            "hash_reporte": gate.get("hash_reporte"),
        },
        "fase_3_indice": {
            "path": str(index),
            "hash_chunks_jsonl": sha256_file(chunks),
            "hash_faiss_idx": sha256_file(faiss),
        },
        "estado": "CERRADO",
        "prohibido_como_exito": [
            "abstencion_alta",
            "solo_NO_ENTRA",
            "dos_sondas_manuales",
            "calibrar_n0_ausente_del_git",
            "60k_sin_traza",
        ],
    }
    out = Path(args.out)
    out.write_text(json.dumps(acta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print("OK acta:", out)
    print("estado:", acta["estado"], "J:", j)
    print("hash_chunks:", acta["fase_3_indice"]["hash_chunks_jsonl"])
    print("hash_faiss :", acta["fase_3_indice"]["hash_faiss_idx"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
