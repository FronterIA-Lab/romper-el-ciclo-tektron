#!/usr/bin/env python3
"""Gate de capacidad TEKTRON (v8 §4.3–4.4).

Mide la función estratégica:

    J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity

N0 es piso (G6–G8), no premio. INDEX_GAP en G4 es fallo, no honestidad.
No reetiqueta corpus. No reconcilia FAISS. No calibra N0.

Uso en Jetson:
  /mnt/tektron/venv_tektron/bin/python3 gate_capacidad_g1_g10.py \\
      --base-bridge http://127.0.0.1:8000 \\
      --base-backend http://127.0.0.1:8001 \\
      --out resultados_gate_v8.json
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import time
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

# ---------------------------------------------------------------------------
# Batería verbatim v8 §4.3
# ---------------------------------------------------------------------------

GATES: list[dict[str, Any]] = [
    {
        "id": "G1",
        "query": "¿Qué establece la Ley Minera sobre consulta previa?",
        "espera": "DUAL",
        "cuenta_j": True,
        "false_n0_si_calla": True,
    },
    {
        "id": "G2",
        "query": "¿Qué dice Quijano sobre la colonialidad del poder?",
        "espera": "MONO_SIT_O_DUAL",
        "cuenta_j": True,
        "false_n0_si_calla": True,
        "trap_quijano": True,
    },
    {
        "id": "G3",
        "query": "¿Cómo configurar un bloque de datos en Siemens S7?",
        "espera": "TECNICO",
        "cuenta_j": False,
        "false_n0_si_calla": True,
    },
    {
        "id": "G4",
        "query": "¿Qué es el MCC?",
        "espera": "GROUNDED",
        "cuenta_j": True,
        "false_n0_si_calla": True,
        "index_gap_es_fallo": True,
    },
    {
        "id": "G5",
        "query": "¿Quién descubrió América?",
        "espera": "DUAL_O_MONO_HONESTO",
        "cuenta_j": True,
        "false_n0_si_calla": True,
    },
    {
        "id": "G6",
        "query": "¿Cuál es la receta del pozole rojo?",
        "espera": "N0",
        "cuenta_j": False,
        "false_n0_si_calla": False,
        "true_n0": True,
    },
    {
        "id": "G7",
        "query": "¿Cómo se juega al ajedrez?",
        "espera": "N0",
        "cuenta_j": False,
        "false_n0_si_calla": False,
        "true_n0": True,
    },
    {
        "id": "G8",
        "query": "cuál es el clima en Oslo mañana",
        "espera": "N0",
        "cuenta_j": False,
        "false_n0_si_calla": False,
        "true_n0": True,
    },
    {
        "id": "G9",
        "query": "grieta generativa",
        "espera": "GROUNDED",
        "cuenta_j": True,
        "false_n0_si_calla": True,
    },
    {
        "id": "G10",
        "query": "Quijano colonialidad del poder polo hegemónico",
        "espera": "TRAP_POLO",
        "cuenta_j": False,
        "false_n0_si_calla": True,
        "trap_quijano": True,
    },
]

SYNTHESIS_PATTERNS = re.compile(
    r"(se complementan|en resumen ambos|punto medio|sintetiz|promedi|"
    r"las dos visiones coinciden|ambos tienen raz[oó]n|"
    r"integrar las dos narrativas|equilibrio entre ambas)",
    re.I,
)
SHA_RE = re.compile(r"\b[a-fA-F0-9]{64}\b")
QUIJANO_RE = re.compile(r"quijano", re.I)

HEG_LABELS = {"HEG", "HEGEMONICO", "HEGEMÓNICO", "HEGEMONICA", "HEGEMÓNICA"}
SIT_LABELS = {"SIT", "SITUADO", "SITUADA"}
TEC_LABELS = {"TEC", "TECNICO", "TÉCNICO", "TECH", "TECNICA", "TÉCNICA"}
N0_KINDS = {
    "N0",
    "ABSTENER",
    "ABSTENCION",
    "ABSTENCIÓN",
    "ABSTENIDO",
    "NO_SE",
    "NO SÉ",
    "INDEX_EMPTY",
}


def polo_norm(raw: Any) -> str:
    s = str(raw or "").strip().upper()
    if s in SIT_LABELS:
        return "SITUADO"
    if s in HEG_LABELS:
        return "HEGEMONICO"
    if s in TEC_LABELS:
        return "TECNICO"
    return s or "?"


QUERY_FIELD_KEYS = (
    "query",
    "pregunta",
    "mensaje",
    "text",
    "message",
    "prompt",
    "q",
    "consulta",
    "input",
)


def fields_from_422(body: Any) -> list[str]:
    """FastAPI 422: loc=['body', '<campo>'] — el contrato está en el error."""
    fields: list[str] = []
    if not isinstance(body, dict):
        return fields
    detail = body.get("detail")
    if isinstance(detail, list):
        for item in detail:
            if not isinstance(item, dict):
                continue
            loc = item.get("loc") or []
            if isinstance(loc, list) and len(loc) >= 2 and str(loc[0]) == "body":
                fields.append(str(loc[-1]))
    return fields


def ping_payloads(query: str) -> list[dict[str, Any]]:
    return [
        {"query": query},
        {"query": query, "modo": "soberano"},
        {"pregunta": query},
        {"mensaje": query},
        {"text": query},
        {"message": query},
        {"prompt": query},
        {"consulta": query},
        {"q": query},
        {"input": query},
    ]


def rank_endpoint(url: str) -> int:
    u = url.lower()
    if "/analizar" in u:
        return 0
    if "/chat" in u:
        return 1
    if "/retrieve" in u:
        return 2
    return 3


def paths_from_openapi(spec: dict[str, Any], base: str) -> list[str]:
    urls: list[str] = []
    for path, ops in (spec.get("paths") or {}).items():
        if not isinstance(ops, dict):
            continue
        if "post" not in {k.lower() for k in ops}:
            continue
        urls.append(base.rstrip("/") + (path if path.startswith("/") else "/" + path))
    urls.sort(key=rank_endpoint)
    return urls


def http_json(url: str, payload: dict[str, Any] | None, timeout: int) -> tuple[int, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    req = Request(url, data=data, method="GET" if payload is None else "POST")
    req.add_header("Accept", "application/json")
    if payload is not None:
        req.add_header("Content-Type", "application/json")
    try:
        with urlopen(req, timeout=timeout) as resp:
            body = resp.read().decode("utf-8", errors="replace")
            try:
                return resp.status, json.loads(body)
            except json.JSONDecodeError:
                return resp.status, {"_raw_text": body[:4000]}
    except HTTPError as e:
        raw = e.read().decode("utf-8", errors="replace") if e.fp else ""
        try:
            parsed = json.loads(raw) if raw else {"error": str(e)}
        except json.JSONDecodeError:
            parsed = {"error": str(e), "_raw_text": raw[:2000]}
        return e.code, parsed
    except (URLError, TimeoutError, OSError) as e:
        return 0, {"error": str(e)}


def first(*vals: Any) -> Any:
    for v in vals:
        if v is None or v == "" or v == [] or v == {}:
            continue
        return v
    return None


def as_list(v: Any) -> list[Any]:
    if v is None:
        return []
    if isinstance(v, list):
        return v
    return [v]


def nonempty_text(v: Any) -> bool:
    if v is None:
        return False
    if isinstance(v, list):
        return any(nonempty_text(x) for x in v)
    return str(v).strip() not in ("", "null", "None", "N/A", "n/a")


def extract(data: Any) -> dict[str, Any]:
    """Campo-defensivo: el contrato de /analizar no está versionado en git."""
    if not isinstance(data, dict):
        return {
            "modo": "?",
            "tesis": "",
            "antitesis": "",
            "tension": "",
            "preguntas": [],
            "hashes": [],
            "fuentes": [],
            "polos": [],
            "abstenido": False,
            "index_gap": False,
            "ausencia_polo": None,
            "texto": str(data)[:4000],
        }

    fuentes = as_list(
        first(
            data.get("fuentes"),
            data.get("sources"),
            data.get("chunks"),
            data.get("evidencias"),
            (data.get("evidencia_trazable") if isinstance(data.get("evidencia_trazable"), list) else None),
        )
    )
    polos = []
    for f in fuentes:
        if isinstance(f, dict):
            polos.append(
                polo_norm(
                    first(
                        f.get("tipo_epistemico"),
                        f.get("polo"),
                        f.get("pole"),
                        f.get("label"),
                    )
                )
            )

    hashes: list[str] = []
    evid = data.get("evidencia_trazable")
    if isinstance(evid, str):
        hashes.extend(SHA_RE.findall(evid))
    elif isinstance(evid, list):
        for item in evid:
            hashes.extend(SHA_RE.findall(str(item)))
    for key in ("hashes", "sha256", "hash"):
        hashes.extend(SHA_RE.findall(str(data.get(key) or "")))
    for f in fuentes:
        if isinstance(f, dict):
            hashes.extend(
                SHA_RE.findall(
                    str(first(f.get("sha256"), f.get("hash"), f.get("id"), ""))
                )
            )

    modo = str(
        first(
            data.get("modo"),
            data.get("decision"),
            data.get("kind"),
            data.get("status"),
            "",
        )
        or ""
    ).upper()
    if isinstance(data.get("decision"), dict):
        modo = str(data["decision"].get("kind") or modo).upper()

    preguntas = as_list(
        first(
            data.get("preguntas_criticas"),
            data.get("preguntas"),
            data.get("mcc"),
            data.get("critical_questions"),
        )
    )
    texto = json.dumps(data, ensure_ascii=False)[:8000]
    index_gap = bool(
        data.get("index_gap")
        or modo in {"INDEX_GAP", "INDEXGAP"}
        or (modo in N0_KINDS and "mcc" in str(data.get("query", "")).lower())
    )
    abstenido = bool(
        data.get("abstenido")
        or modo in N0_KINDS
        or str(data.get("respuesta") or "").strip().lower() in {"no sé", "no se", "n0"}
    )

    return {
        "modo": modo,
        "tesis": str(first(data.get("tesis"), data.get("heg"), data.get("thesis"), "") or ""),
        "antitesis": str(
            first(data.get("antitesis"), data.get("sit"), data.get("antithesis"), "") or ""
        ),
        "tension": str(first(data.get("tension"), data.get("tensión"), "") or ""),
        "preguntas": preguntas,
        "hashes": sorted(set(h.lower() for h in hashes)),
        "fuentes": fuentes,
        "polos": polos,
        "abstenido": abstenido,
        "index_gap": index_gap,
        "ausencia_polo": first(data.get("ausencia_polo"), data.get("polo_ausente")),
        "texto": texto,
        "n_fuentes": len(fuentes),
    }


def discover_contract(bridge: str, backend: str, timeout: int) -> dict[str, Any]:
    """Descubre el contrato real. 422 y timeout no significan 'no existe'."""
    ping = "ping tektron gate"
    bases: list[str] = []
    for b in (backend, bridge):
        if b and b not in bases:
            bases.append(b.rstrip("/"))

    health: dict[str, Any] = {}
    reachable: list[str] = []
    openapi_by_base: dict[str, Any] = {}
    for base in bases:
        code, body = http_json(f"{base}/health", None, timeout=min(timeout, 10))
        health[base] = {"http": code, "body": body}
        refused = isinstance(body, dict) and "Connection refused" in str(body.get("error") or "")
        if refused:
            continue
        reachable.append(base)
        oc, ob = http_json(f"{base}/openapi.json", None, timeout=min(timeout, 10))
        if oc == 200 and isinstance(ob, dict) and ob.get("paths"):
            openapi_by_base[base] = {
                "http": oc,
                "paths": sorted(ob["paths"].keys()),
                "post": paths_from_openapi(ob, base),
            }

    urls: list[str] = []
    for base in reachable:
        posted = (openapi_by_base.get(base) or {}).get("post") or []
        fallback = [
            f"{base}/analizar",
            f"{base}/chat",
            f"{base}/retrieve",
        ]
        for u in list(posted) + fallback:
            if u not in urls:
                urls.append(u)
    urls.sort(key=rank_endpoint)

    probed: list[dict[str, Any]] = []
    chosen = None
    post_timeout = max(timeout, 90)

    def try_one(url: str, payload: dict[str, Any], to: int) -> dict[str, Any]:
        code, body = http_json(url, payload, timeout=to)
        entry = {
            "url": url,
            "payload_keys": sorted(payload.keys()),
            "http": code,
            "ok": 200 <= int(code) < 300 and isinstance(body, dict),
            "required_from_422": fields_from_422(body) if int(code) == 422 else [],
            "timeout": False,
        }
        err = str((body or {}).get("error") if isinstance(body, dict) else body).lower()
        entry["timeout"] = int(code) == 0 and "refused" not in err and (
            "timed out" in err or "timeout" in err or "time out" in err
        )
        if isinstance(body, dict) and entry["ok"]:
            entry["sample_keys"] = sorted(body.keys())
        elif int(code) == 422 and isinstance(body, dict):
            entry["detail_head"] = str(body.get("detail"))[:400]
        probed.append(entry)
        return {"code": code, "body": body, "entry": entry}

    for url in urls:
        if chosen:
            break
        timeout_candidate = None
        for payload in ping_payloads(ping):
            result = try_one(url, payload, post_timeout)
            if result["code"] == 404:
                break
            if result["entry"]["ok"]:
                chosen = {
                    "url": url,
                    "payload_template": payload,
                    "sample_keys": result["entry"].get("sample_keys") or [],
                    "via": "2xx",
                }
                break
            if result["entry"].get("timeout") and any(k in payload for k in QUERY_FIELD_KEYS):
                timeout_candidate = payload
                break
            needed = result["entry"].get("required_from_422") or []
            if result["code"] == 422 and needed:
                retry_payload = {}
                for f in needed:
                    retry_payload[f] = "soberano" if f == "modo" else ping
                if not any(k in retry_payload for k in QUERY_FIELD_KEYS):
                    retry_payload["query"] = ping
                retry = try_one(url, retry_payload, post_timeout)
                if retry["entry"]["ok"]:
                    chosen = {
                        "url": url,
                        "payload_template": retry_payload,
                        "sample_keys": retry["entry"].get("sample_keys") or [],
                        "via": "422-retry",
                    }
                    break
                if retry["entry"].get("timeout"):
                    timeout_candidate = retry_payload
        if chosen:
            break
        if timeout_candidate:
            chosen = {
                "url": url,
                "payload_template": timeout_candidate,
                "sample_keys": [],
                "via": "timeout-after-live-endpoint",
                "nota": "El POST existe pero el ping al LLM superó el timeout de descubrimiento. El Gate usará --timeout completo.",
            }
            break

    nota = []
    if backend.rstrip("/") not in reachable:
        nota.append("backend :8001 no está escuchando (connection refused). No es fallo de J ni de corpus.")
    if any(p.get("http") == 422 for p in probed):
        nota.append("Hay POST vivo que respondió 422: el endpoint existe; el payload era el incorrecto.")
    if any(p.get("timeout") for p in probed):
        nota.append("Hubo timeout: /chat o /retrieve probablemente pegó al LLM. No significa que la ruta no exista.")
    if chosen is None:
        nota.append("chosen=null: inspeccionar openapi.json del bridge y el 422. No curar.")

    return {
        "health": health,
        "reachable": reachable,
        "openapi": {k: {"paths": v.get("paths")} for k, v in openapi_by_base.items()},
        "probes": probed,
        "chosen": chosen,
        "nota": nota,
    }


def call_query(contract: dict[str, Any], query: str, timeout: int) -> tuple[dict[str, Any], dict[str, Any]]:
    chosen = contract.get("chosen")
    if not chosen:
        return {"error": "sin contrato HTTP", "http": 0}, extract({})
    payload = dict(chosen["payload_template"])
    for k in list(payload.keys()):
        if k in QUERY_FIELD_KEYS:
            payload[k] = query
    if not any(k in payload for k in QUERY_FIELD_KEYS):
        payload["query"] = query
    code, body = http_json(chosen["url"], payload, timeout=timeout)
    meta = {"http": code, "url": chosen["url"], "payload": payload}
    if not isinstance(body, dict):
        body = {"_non_dict": body, "error": "respuesta no JSON"}
    return meta, extract(body)


def slots_mirror(ex: dict[str, Any], espera: str) -> dict[str, int]:
    polos = set(ex["polos"])
    has_heg = int(bool(ex["tesis"].strip()) or "HEGEMONICO" in polos)
    has_sit = int(bool(ex["antitesis"].strip()) or "SITUADO" in polos)
    has_tension = int(bool(ex["tension"].strip()))
    has_mcc = int(nonempty_text(ex["preguntas"]))
    has_sha = int(bool(ex["hashes"]))
    if espera == "TECNICO":
        has_tec = int("TECNICO" in polos or bool(ex["tesis"].strip()))
        return {
            "HEG": 0,
            "SIT": 0,
            "TEC": has_tec,
            "TENSION": 0,
            "MCC": has_mcc,
            "SHA": has_sha,
        }
    if espera in {"MONO_SIT_O_DUAL", "GROUNDED", "DUAL_O_MONO_HONESTO", "TRAP_POLO"}:
        ausencia = int(nonempty_text(ex["ausencia_polo"]) or (has_heg + has_sit == 1))
        return {
            "HEG": has_heg,
            "SIT": has_sit,
            "TENSION": has_tension if (has_heg and has_sit) else ausencia,
            "MCC": has_mcc,
            "SHA": has_sha,
        }
    return {
        "HEG": has_heg,
        "SIT": has_sit,
        "TENSION": has_tension,
        "MCC": has_mcc,
        "SHA": has_sha,
    }


def dual_density_query(ex: dict[str, Any]) -> float:
    polos = set(ex["polos"])
    if "HEGEMONICO" in polos and "SITUADO" in polos:
        return 1.0
    if ex["tesis"].strip() and ex["antitesis"].strip():
        return 1.0
    return 0.0


def tension_faithfulness(ex: dict[str, Any], espera: str) -> float:
    blob = " ".join(
        [
            ex["tesis"],
            ex["antitesis"],
            ex["tension"],
            " ".join(str(p) for p in ex["preguntas"]),
            ex["texto"],
        ]
    )
    if SYNTHESIS_PATTERNS.search(blob):
        return 0.0
    if espera == "N0":
        return 1.0 if ex["abstenido"] else 0.0
    if espera == "TECNICO":
        # Relativizar TEC (inventar dualidad) es infidelidad.
        if dual_density_query(ex) and ex["tension"].strip():
            return 0.0
        return 1.0 if not ex["abstenido"] else 0.0
    if espera == "DUAL":
        if not ex["tension"].strip():
            return 0.0
        if dual_density_query(ex) < 1.0:
            return 0.5
        return 1.0
    # MONO honesto: tensión cosmética no exigida; síntesis sigue siendo 0.
    if espera in {"MONO_SIT_O_DUAL", "DUAL_O_MONO_HONESTO", "GROUNDED", "TRAP_POLO"}:
        if dual_density_query(ex) >= 1.0:
            return 1.0 if ex["tension"].strip() else 0.5
        return 1.0 if (nonempty_text(ex["ausencia_polo"]) or ex["tesis"] or ex["antitesis"]) else 0.0
    return 0.0


def evidence_integrity(ex: dict[str, Any], espera: str) -> float:
    if espera == "N0":
        return 1.0 if (ex["abstenido"] and not ex["hashes"]) else 0.0
    if ex["abstenido"] or ex["index_gap"]:
        return 0.0
    return 1.0 if ex["hashes"] else 0.0


def polo_mislabel(ex: dict[str, Any]) -> int:
    """1 si alguna fuente Quijano viene como HEGEMONICO."""
    hits = 0
    for f in ex["fuentes"]:
        if not isinstance(f, dict):
            continue
        blob = " ".join(
            str(f.get(k) or "")
            for k in ("fuente", "source", "title", "text", "contenido", "autor")
        )
        if QUIJANO_RE.search(blob) and polo_norm(
            first(f.get("tipo_epistemico"), f.get("polo"))
        ) == "HEGEMONICO":
            hits += 1
    if hits == 0 and QUIJANO_RE.search(ex["tesis"]) and "HEGEMONICO" in set(ex["polos"]):
        # Heurística débil: tesis HEG citando Quijano como si fuera el polo hegemónico.
        if QUIJANO_RE.search(ex["texto"]) and dual_density_query(ex) < 1.0:
            hits += 1
    return hits


def is_n0(ex: dict[str, Any]) -> bool:
    if ex["abstenido"] or ex["modo"] in N0_KINDS:
        return True
    if ex["n_fuentes"] == 0 and not ex["tesis"] and not ex["antitesis"]:
        return True
    return False


def score_query(spec: dict[str, Any], ex: dict[str, Any]) -> dict[str, Any]:
    espera = spec["espera"]
    sl = slots_mirror(ex, espera)
    if espera == "DUAL":
        keys = ["HEG", "SIT", "TENSION", "MCC", "SHA"]
    elif espera == "TECNICO":
        keys = ["TEC", "MCC", "SHA"]
    else:
        keys = ["HEG", "SIT", "TENSION", "MCC", "SHA"]
    tree = sum(sl[k] for k in keys) / max(len(keys), 1)

    dual = dual_density_query(ex)
    tens = tension_faithfulness(ex, espera)
    evid = evidence_integrity(ex, espera)
    n0 = is_n0(ex)
    false_n0 = int(bool(spec.get("false_n0_si_calla") and n0))
    true_n0 = int(bool(spec.get("true_n0") and n0))
    true_n0_fail = int(bool(spec.get("true_n0") and not n0))
    index_gap = int(bool(ex["index_gap"] or (spec.get("index_gap_es_fallo") and ex["n_fuentes"] == 0)))
    if spec.get("index_gap_es_fallo") and n0:
        index_gap = 1
        false_n0 = 1
    synth = int(bool(SYNTHESIS_PATTERNS.search(ex["texto"])))
    mislabel = polo_mislabel(ex) if spec.get("trap_quijano") else 0
    honest_mono = 0.0
    if espera in {"MONO_SIT_O_DUAL", "DUAL_O_MONO_HONESTO", "GROUNDED"} and not n0:
        honest_mono = 1.0 if (dual >= 1.0 or nonempty_text(ex["ausencia_polo"]) or sl.get("SIT") or sl.get("HEG")) else 0.0

    j_op = (
        0.2 * tree
        + 0.2 * dual
        + 0.2 * tens
        + 0.2 * honest_mono
        + 0.2 * evid
        - 1.0 * false_n0
        - 1.0 * synth
        - 1.0 * int(mislabel > 0)
    )

    ok = None
    if espera == "DUAL":
        ok = dual >= 1.0 and tree >= 0.8 and not n0 and not synth and evid > 0
    elif espera == "MONO_SIT_O_DUAL":
        ok = (not n0) and mislabel == 0 and evid > 0 and ("SITUADO" in set(ex["polos"]) or ex["antitesis"].strip())
    elif espera == "TECNICO":
        ok = (not n0) and dual == 0.0 and ("TECNICO" in set(ex["polos"]) or bool(ex["tesis"].strip()))
    elif espera == "GROUNDED":
        ok = (not n0) and not index_gap and (ex["n_fuentes"] > 0 or nonempty_text(ex["tesis"]))
    elif espera == "DUAL_O_MONO_HONESTO":
        ok = (not n0) and not synth and evid > 0 and (dual >= 1.0 or honest_mono >= 1.0)
    elif espera == "N0":
        ok = bool(n0) and evid > 0
    elif espera == "TRAP_POLO":
        ok = mislabel == 0 and not n0
    else:
        ok = False

    return {
        "id": spec["id"],
        "query": spec["query"],
        "espera": espera,
        "modo_detectado": ex["modo"],
        "n_fuentes": ex["n_fuentes"],
        "polos": sorted(set(ex["polos"])),
        "slots": sl,
        "TreeCoverage": round(tree, 4),
        "DualPoleDensity": round(dual, 4),
        "TensionFaithfulness": round(tens, 4),
        "EvidenceIntegrity": round(evid, 4),
        "HonestMono": round(honest_mono, 4),
        "FalseN0": false_n0,
        "TrueN0": true_n0,
        "TrueN0Fail": true_n0_fail,
        "INDEX_GAP": index_gap,
        "Synthesis": synth,
        "PoloMislabel": mislabel,
        "J_op": round(j_op, 4),
        "ok": bool(ok),
        "cuenta_j": bool(spec.get("cuenta_j")),
        "hashes_n": len(ex["hashes"]),
        "tesis_len": len(ex["tesis"]),
        "antitesis_len": len(ex["antitesis"]),
        "tension_len": len(ex["tension"]),
    }


def mean(xs: list[float]) -> float:
    return sum(xs) / len(xs) if xs else 0.0


def aggregate(rows: list[dict[str, Any]]) -> dict[str, Any]:
    j_rows = [r for r in rows if r["cuenta_j"]]
    dual_expected = [r for r in rows if r["espera"] in {"DUAL", "DUAL_O_MONO_HONESTO"}]
    mirror = mean([r["TreeCoverage"] for r in dual_expected] or [r["TreeCoverage"] for r in j_rows])
    dual = mean([r["DualPoleDensity"] for r in dual_expected] or [r["DualPoleDensity"] for r in j_rows])
    tens = mean([r["TensionFaithfulness"] for r in j_rows])
    evid = mean([r["EvidenceIntegrity"] for r in j_rows])
    j = mirror * dual * tens * evid

    false_n0 = [r for r in rows if r["FalseN0"]]
    true_n0_ok = [r for r in rows if r["espera"] == "N0" and r["TrueN0"]]
    true_n0_all = [r for r in rows if r["espera"] == "N0"]
    synth = [r for r in rows if r["Synthesis"]]
    mislabel = [r for r in rows if r["PoloMislabel"]]
    gaps = [r for r in rows if r["INDEX_GAP"]]

    tree_dual = mean([r["TreeCoverage"] for r in rows if r["espera"] == "DUAL"])
    status_ok = (
        j > 0
        and tree_dual >= 0.8
        and len(false_n0) == 0
        and (len(true_n0_ok) == len(true_n0_all) if true_n0_all else False)
        and len(mislabel) == 0
        and len(synth) == 0
        and len(gaps) == 0
        and all(r["ok"] for r in rows)
    )
    bottleneck = []
    if mirror == 0:
        bottleneck.append("MirrorCoverage")
    if dual == 0:
        bottleneck.append("DualPoleDensity")
    if tens == 0:
        bottleneck.append("TensionFaithfulness")
    if evid == 0:
        bottleneck.append("EvidenceIntegrity")
    if false_n0:
        bottleneck.append("FalseN0")
    if true_n0_all and len(true_n0_ok) < len(true_n0_all):
        bottleneck.append("TrueN0")
    if synth:
        bottleneck.append("Synthesis")
    if mislabel:
        bottleneck.append("PoloMislabel")
    if gaps:
        bottleneck.append("INDEX_GAP")

    return {
        "MirrorCoverage": round(mirror, 4),
        "DualPoleDensity": round(dual, 4),
        "TensionFaithfulness": round(tens, 4),
        "EvidenceIntegrity": round(evid, 4),
        "J": round(j, 6),
        "TreeCoverage_DUAL": round(tree_dual, 4),
        "FalseN0Rate": round(len(false_n0) / max(len([r for r in rows if r["espera"] != "N0"]), 1), 4),
        "TrueN0Rate": round(len(true_n0_ok) / max(len(true_n0_all), 1), 4),
        "SynthesisRate": round(len(synth) / max(len(rows), 1), 4),
        "PoloMislabel": int(sum(r["PoloMislabel"] for r in rows)),
        "INDEX_GAP": [r["id"] for r in gaps],
        "FalseN0": [r["id"] for r in false_n0],
        "status": "OK" if status_ok else "FAIL",
        "bottleneck": bottleneck,
        "criterio": {
            "J_producto_gt_0": j > 0,
            "TreeCoverage_DUAL_ge_0.8": tree_dual >= 0.8,
            "FalseN0Rate_eq_0": len(false_n0) == 0,
            "TrueN0Rate_eq_1": len(true_n0_ok) == len(true_n0_all) and bool(true_n0_all),
            "PoloMislabel_eq_0": len(mislabel) == 0,
            "SynthesisRate_eq_0": len(synth) == 0,
            "sin_INDEX_GAP": len(gaps) == 0,
            "todas_ok": all(r["ok"] for r in rows),
        },
    }


def next_action(agg: dict[str, Any]) -> str:
    if agg["status"] == "OK":
        return (
            "Gate aprobado. Emitir ACTA_CIERRE_TEKTRON_v8.json con hashes reales "
            "de chunks.jsonl y faiss.idx. No abrir ronda de curación."
        )
    b = agg.get("bottleneck") or []
    if "INDEX_GAP" in b:
        return "G4/G9 INDEX_GAP: verificar retrieve del andamiaje MCC (zenodo 17728016/21500800). Un ingest atómico si falta. No celebrar N0."
    if "PoloMislabel" in b:
        return "G10: reetiquetar la fuente Quijano que salió HEG. No auditar el corpus entero."
    if "TensionFaithfulness" in b or "Synthesis" in b:
        return "Fase 5: tensión cosmética o síntesis. Corregir mcc_layer/prompt. Prohibir árbol vacío = árbol completo."
    if "MirrorCoverage" in b:
        return "Backend no llena slots {HEG,SIT,TENSION,MCC,SHA}. Fase 5 /analizar, no curación."
    if "DualPoleDensity" in b:
        return "Falta un polo en G1/G5. Poblar ESA ancla (par HEG/SIT). No ronda 3 de 98 leyes. No swap del unificado 60652."
    if "EvidenceIntegrity" in b:
        return "SHA ausente o no vacío en N0. Arreglar evidencia_trazable."
    if "FalseN0" in b:
        return "Calló en positiva. N0 es piso: bajar umbral o arreglar suficiencia. No subir abstención."
    if "TrueN0" in b:
        return "Confabuló OOD (G6–G8). Selectividad solo en negativas."
    return "Releer por-query en el JSON. Una sola corrección. Re-medir."


def main() -> int:
    ap = argparse.ArgumentParser(description="Gate de capacidad TEKTRON G1–G10")
    ap.add_argument("--base-bridge", default="http://127.0.0.1:8000")
    ap.add_argument("--base-backend", default="http://127.0.0.1:8001")
    ap.add_argument("--out", default="resultados_gate_v8.json")
    ap.add_argument("--timeout", type=int, default=120)
    ap.add_argument("--dry-discover", action="store_true", help="Solo descubrir contrato HTTP")
    args = ap.parse_args()

    contract = discover_contract(args.base_bridge.rstrip("/"), args.base_backend.rstrip("/"), args.timeout)
    if args.dry_discover:
        json.dump(contract, sys.stdout, ensure_ascii=False, indent=2)
        print()
        return 0 if contract.get("chosen") else 2

    if not contract.get("chosen"):
        report = {
            "proyecto": "TEKTRON v8.0",
            "fecha": datetime.now(timezone.utc).isoformat(),
            "status": "FAIL",
            "error": "No se fijó un contrato HTTP usable (chosen=null).",
            "contrato_detectado": contract,
            "J": 0,
            "bottleneck": ["contrato_http"],
            "nota": contract.get("nota"),
            "siguiente": (
                "Esto no es J ni curación. :8001 caído no bloquea si :8000/chat o /retrieve viven. "
                "Inspeccionar openapi.json y el 422; recopy del script si el descubridor viejo cortó a 20s. No curar."
            ),
        }
        with open(args.out, "w", encoding="utf-8") as f:
            json.dump(report, f, ensure_ascii=False, indent=2)
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 2

    rows = []
    raws = []
    for spec in GATES:
        t0 = time.time()
        meta, ex = call_query(contract, spec["query"], args.timeout)
        scored = score_query(spec, ex)
        scored["latencia_s"] = round(time.time() - t0, 3)
        scored["http"] = meta.get("http")
        rows.append(scored)
        raws.append(
            {
                "id": spec["id"],
                "http": meta,
                "extract": {
                    k: ex[k]
                    for k in (
                        "modo",
                        "n_fuentes",
                        "polos",
                        "hashes",
                        "abstenido",
                        "index_gap",
                        "ausencia_polo",
                    )
                },
                "tesis_head": ex["tesis"][:400],
                "antitesis_head": ex["antitesis"][:400],
                "tension_head": ex["tension"][:400],
            }
        )
        mark = "OK" if scored["ok"] else "FAIL"
        print(
            f"{spec['id']} {mark} J_op={scored['J_op']} "
            f"dual={scored['DualPoleDensity']} tree={scored['TreeCoverage']} "
            f"modo={scored['modo_detectado']} polos={scored['polos']} "
            f"FalseN0={scored['FalseN0']} SHA={scored['hashes_n']}",
            flush=True,
        )

    agg = aggregate(rows)
    report = {
        "proyecto": "TEKTRON v8.0",
        "fecha": datetime.now(timezone.utc).isoformat(),
        "funcion_objetivo": "J = MirrorCoverage × DualPoleDensity × TensionFaithfulness × EvidenceIntegrity",
        "n0": "piso, no meta",
        "contrato_detectado": contract.get("chosen"),
        "health": contract.get("health"),
        "metricas": agg,
        "J": agg["J"],
        "status": agg["status"],
        "bottleneck": agg["bottleneck"],
        "siguiente": next_action(agg),
        "por_query": rows,
        "muestras": raws,
        "prohibido_como_exito": [
            "abstencion_alta",
            "solo_NO_ENTRA",
            "dos_sondas_manuales",
            "calibrar_n0_ausente_del_git",
            "60k_sin_traza",
        ],
    }
    blob = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=False)
    report["hash_reporte"] = hashlib.sha256(blob.encode("utf-8")).hexdigest()
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(report, f, ensure_ascii=False, indent=2)
    print()
    print(f"J={agg['J']} status={agg['status']} bottleneck={agg['bottleneck']}")
    print(f"siguiente: {report['siguiente']}")
    print(f"escrito: {args.out}")
    return 0 if agg["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
