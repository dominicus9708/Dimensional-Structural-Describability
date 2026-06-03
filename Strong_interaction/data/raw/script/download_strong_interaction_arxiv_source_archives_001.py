#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
download_strong_interaction_arxiv_source_archives_001.py

ArXiv source-archive acquisition and candidate extraction pipeline for the
Strong_interaction benchmark workflow in the Dimensional-Structural Describability
project.

Author: Kwon Dominicus

Purpose
-------
Direct HEPData CSV/YAML/YODA URLs were not reliably discoverable by automated web
search.  This script therefore uses verified arXiv source/e-print links as a
fallback raw acquisition route.  It downloads the source archives for the OPAL,
JADE, L3, and DELPHI candidate papers, preserves them under raw/source_tables/01,
and extracts candidate text/table/data files for later numerical cleaning.

This is not the same as confirmed numerical benchmark CSV.  It is an audited raw
fallback route.  Any extracted candidate must still be reviewed and cleaned before
promotion into numerical cleaned_tables and derived/input.

Inputs
------
Built-in verified arXiv e-print URLs.

Outputs
-------
Archives:
    Strong_interaction/data/raw/source_tables/01/source_archives/

Extracted candidates:
    Strong_interaction/data/raw/source_tables/01/extracted_candidates/

References/manifests:
    Strong_interaction/data/raw/references/01/
"""

from __future__ import annotations

import argparse
import csv
import datetime as _dt
import gzip
import hashlib
import io
import pathlib
import re
import shutil
import sys
import tarfile
import time
import urllib.error
import urllib.request
import zipfile
from dataclasses import dataclass, asdict
from typing import Any, Iterable, Optional


SCRIPT_VERSION = "001"
RAW_BATCH = "01"
USER_AGENT = (
    "Dimensional-Structural-Describability/Strong_interaction arXiv source acquisition "
    "(Kwon Dominicus; fallback raw source route)"
)
TIMEOUT_SECONDS = 120
SLEEP_SECONDS = 1.0
MAX_SIZE_MB_DEFAULT = 200


@dataclass(frozen=True)
class ArxivSourceTarget:
    target_id: str
    source_id: str
    arxiv_id: str
    source_url: str
    output_filename: str
    expected_role: str
    priority: int
    notes: str


TARGETS: list[ArxivSourceTarget] = [
    ArxivSourceTarget(
        target_id="OPAL_2005_ARXIV_SOURCE_ARCHIVE_001",
        source_id="OPAL_EVENT_SHAPES_91_209GEV_2005",
        arxiv_id="hep-ex/0503051",
        source_url="https://arxiv.org/e-print/hep-ex/0503051",
        output_filename="opal_2005_event_shapes_arxiv_source_raw_001.bin",
        expected_role="fallback_source_archive_for_standard_event_shape_tables",
        priority=1,
        notes="OPAL 91-209 GeV event-shape source archive. Extract text/table candidates; not final numerical input.",
    ),
    ArxivSourceTarget(
        target_id="JADE_1997_ARXIV_SOURCE_ARCHIVE_001",
        source_id="JADE_EVENT_SHAPES_22_44GEV",
        arxiv_id="hep-ex/9708034",
        source_url="https://arxiv.org/e-print/hep-ex/9708034",
        output_filename="jade_1997_event_shapes_arxiv_source_raw_001.bin",
        expected_role="fallback_source_archive_for_lower_energy_event_shape_tables",
        priority=2,
        notes="JADE 22-44 GeV event-shape source archive. Extract text/table candidates; not final numerical input.",
    ),
    ArxivSourceTarget(
        target_id="L3_2009_ARXIV_SOURCE_ARCHIVE_001",
        source_id="L3_FLAVOUR_TAGGED_EVENT_SHAPE_197GEV",
        arxiv_id="0907.2658",
        source_url="https://arxiv.org/e-print/0907.2658",
        output_filename="l3_2009_flavour_event_shapes_arxiv_source_raw_001.bin",
        expected_role="fallback_source_archive_for_flavour_tagged_event_shape_tables",
        priority=3,
        notes="L3 flavour-tagged event-shape source archive. Extract table candidates; not final numerical input.",
    ),
    ArxivSourceTarget(
        target_id="DELPHI_2025_ARXIV_SOURCE_ARCHIVE_001",
        source_id="DELPHI_OPEN_DATA_THRUST_EEC_NOTE_2025",
        arxiv_id="2510.18762",
        source_url="https://arxiv.org/e-print/2510.18762",
        output_filename="delphi_2025_open_data_thrust_eec_arxiv_source_raw_001.bin",
        expected_role="fallback_source_archive_for_data_availability_and_event_sample_route",
        priority=4,
        notes="DELPHI 2025 source archive. Used to inspect data availability/code links, not as event-level data itself.",
    ),
]


TEXTLIKE_SUFFIXES = {
    ".tex", ".txt", ".dat", ".csv", ".tsv", ".yaml", ".yml", ".json", ".bib", ".bbl", ".sty", ".cls", ".md", ".log"
}

DATA_CANDIDATE_SUFFIXES = {
    ".csv", ".tsv", ".dat", ".txt", ".yaml", ".yml", ".json"
}

KEYWORD_PATTERN = re.compile(
    r"(table|tabular|thrust|broadening|heavy\s+jet|durham|y23|c-parameter|alpha|eec|energy[- ]energy|data\s+availability|github|hepdata|rivet|yoda|root|cern\s+open\s+data)",
    re.IGNORECASE,
)

NUMBER_PATTERN = re.compile(r"[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?")


def utc_now() -> str:
    return _dt.datetime.now(_dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "references_01": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "source_tables_01": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH,
        "archives_dir": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "source_archives",
        "extracted_dir": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "extracted_candidates",
    }


def write_csv(path: pathlib.Path, rows: Iterable[dict[str, Any]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def sha256_bytes(data: bytes) -> str:
    h = hashlib.sha256()
    h.update(data)
    return h.hexdigest()


def sanitize_path_component(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9_.-]+", "_", value).strip("._")
    return value[:160] or "unnamed"


def safe_request(url: str, max_size_mb: int) -> tuple[bool, bytes | None, str, int | str]:
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT, "Accept": "application/octet-stream, */*"})
    try:
        with urllib.request.urlopen(request, timeout=TIMEOUT_SECONDS) as response:
            status = getattr(response, "status", "")
            content_length = response.headers.get("Content-Length")
            if content_length and int(content_length) > max_size_mb * 1024 * 1024:
                return False, None, f"blocked_by_size_limit:{int(content_length)}>{max_size_mb}MB", status
            data = response.read(max_size_mb * 1024 * 1024 + 1)
            if len(data) > max_size_mb * 1024 * 1024:
                return False, None, f"blocked_by_size_limit_after_read:>{max_size_mb}MB", status
            return True, data, "", status
    except urllib.error.HTTPError as exc:
        return False, None, f"HTTPError {exc.code}: {exc.reason}", exc.code
    except urllib.error.URLError as exc:
        return False, None, f"URLError: {exc.reason}", ""
    except Exception as exc:
        return False, None, f"{type(exc).__name__}: {exc}", ""


def decode_text(data: bytes) -> str:
    for enc in ("utf-8", "latin-1", "cp1252"):
        try:
            return data.decode(enc)
        except UnicodeDecodeError:
            continue
    return data.decode("utf-8", errors="replace")


def classify_archive(data: bytes) -> str:
    bio = io.BytesIO(data)
    try:
        if tarfile.is_tarfile(bio):
            return "tar"
    except Exception:
        pass
    bio.seek(0)
    if zipfile.is_zipfile(bio):
        return "zip"
    if data[:2] == b"\x1f\x8b":
        return "gzip_single_or_tar_gz"
    if b"\\documentclass" in data[:5000] or b"\\begin{document}" in data[:5000]:
        return "plain_tex"
    return "unknown_binary_or_plain"


def safe_extract_name(name: str) -> str:
    # Prevent path traversal while preserving a traceable flattened name.
    parts = [p for p in pathlib.PurePosixPath(name.replace("\\", "/")).parts if p not in ("..", "/", "")]
    return sanitize_path_component("__".join(parts))


def should_extract_member(name: str, data: bytes) -> tuple[bool, str, int, bool]:
    suffix = pathlib.PurePosixPath(name).suffix.lower()
    textlike = suffix in TEXTLIKE_SUFFIXES
    if not textlike and len(data) > 2_000_000:
        return False, "non_text_or_too_large", 0, False
    text = decode_text(data[:2_000_000])
    numeric_count = len(NUMBER_PATTERN.findall(text))
    has_keyword = bool(KEYWORD_PATTERN.search(text))
    data_suffix = suffix in DATA_CANDIDATE_SUFFIXES
    if data_suffix or has_keyword or numeric_count >= 50:
        return True, "data_suffix_or_keyword_or_numeric_dense", numeric_count, has_keyword
    return False, "no_relevant_keyword_or_numeric_density", numeric_count, has_keyword


def extract_from_tar(data: bytes, target: ArxivSourceTarget, outdir: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as tf:
        for member in tf.getmembers():
            if not member.isfile():
                continue
            try:
                f = tf.extractfile(member)
                if f is None:
                    continue
                content = f.read()
            except Exception as exc:
                rows.append({"target_id": target.target_id, "member_name": member.name, "extracted": False, "reason": f"read_error:{exc}"})
                continue
            ok, reason, numeric_count, has_keyword = should_extract_member(member.name, content)
            if not ok:
                rows.append({
                    "target_id": target.target_id,
                    "source_id": target.source_id,
                    "member_name": member.name,
                    "output_file": "",
                    "extracted": False,
                    "reason": reason,
                    "numeric_count_preview": numeric_count,
                    "has_keyword": has_keyword,
                    "size_bytes": len(content),
                    "sha256": sha256_bytes(content),
                    "created_utc": utc_now(),
                })
                continue
            target_dir = outdir / sanitize_path_component(target.target_id)
            target_dir.mkdir(parents=True, exist_ok=True)
            out = target_dir / safe_extract_name(member.name)
            out.write_bytes(content)
            rows.append({
                "target_id": target.target_id,
                "source_id": target.source_id,
                "member_name": member.name,
                "output_file": str(out),
                "extracted": True,
                "reason": reason,
                "numeric_count_preview": numeric_count,
                "has_keyword": has_keyword,
                "size_bytes": len(content),
                "sha256": sha256_bytes(content),
                "created_utc": utc_now(),
            })
    return rows


def extract_from_zip(data: bytes, target: ArxivSourceTarget, outdir: pathlib.Path) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    with zipfile.ZipFile(io.BytesIO(data)) as zf:
        for info in zf.infolist():
            if info.is_dir():
                continue
            try:
                content = zf.read(info)
            except Exception as exc:
                rows.append({"target_id": target.target_id, "member_name": info.filename, "extracted": False, "reason": f"read_error:{exc}"})
                continue
            ok, reason, numeric_count, has_keyword = should_extract_member(info.filename, content)
            if ok:
                target_dir = outdir / sanitize_path_component(target.target_id)
                target_dir.mkdir(parents=True, exist_ok=True)
                out = target_dir / safe_extract_name(info.filename)
                out.write_bytes(content)
                output_file = str(out)
            else:
                output_file = ""
            rows.append({
                "target_id": target.target_id,
                "source_id": target.source_id,
                "member_name": info.filename,
                "output_file": output_file,
                "extracted": ok,
                "reason": reason,
                "numeric_count_preview": numeric_count,
                "has_keyword": has_keyword,
                "size_bytes": len(content),
                "sha256": sha256_bytes(content),
                "created_utc": utc_now(),
            })
    return rows


def extract_archive(data: bytes, target: ArxivSourceTarget, outdir: pathlib.Path) -> tuple[str, list[dict[str, Any]]]:
    kind = classify_archive(data)
    if kind == "tar":
        return kind, extract_from_tar(data, target, outdir)
    if kind == "zip":
        return kind, extract_from_zip(data, target, outdir)
    if kind == "gzip_single_or_tar_gz":
        try:
            decompressed = gzip.decompress(data)
            nested_kind = classify_archive(decompressed)
            if nested_kind == "tar":
                return "gzip_tar", extract_from_tar(decompressed, target, outdir)
            # single gzipped text-like file
            ok, reason, numeric_count, has_keyword = should_extract_member(target.output_filename + ".decompressed", decompressed)
            target_dir = outdir / sanitize_path_component(target.target_id)
            target_dir.mkdir(parents=True, exist_ok=True)
            out = target_dir / sanitize_path_component(target.output_filename + ".decompressed.txt")
            if ok:
                out.write_bytes(decompressed)
            return "gzip_single", [{
                "target_id": target.target_id,
                "source_id": target.source_id,
                "member_name": target.output_filename + ".decompressed",
                "output_file": str(out) if ok else "",
                "extracted": ok,
                "reason": reason,
                "numeric_count_preview": numeric_count,
                "has_keyword": has_keyword,
                "size_bytes": len(decompressed),
                "sha256": sha256_bytes(decompressed),
                "created_utc": utc_now(),
            }]
        except Exception as exc:
            return "gzip_unreadable", [{"target_id": target.target_id, "source_id": target.source_id, "member_name": "", "output_file": "", "extracted": False, "reason": f"gzip_error:{exc}", "created_utc": utc_now()}]
    # plain tex or unknown: preserve if keyword/numeric enough
    ok, reason, numeric_count, has_keyword = should_extract_member(target.output_filename, data)
    target_dir = outdir / sanitize_path_component(target.target_id)
    target_dir.mkdir(parents=True, exist_ok=True)
    out = target_dir / sanitize_path_component(target.output_filename + ".txt")
    if ok:
        out.write_bytes(data)
    return kind, [{
        "target_id": target.target_id,
        "source_id": target.source_id,
        "member_name": target.output_filename,
        "output_file": str(out) if ok else "",
        "extracted": ok,
        "reason": reason,
        "numeric_count_preview": numeric_count,
        "has_keyword": has_keyword,
        "size_bytes": len(data),
        "sha256": sha256_bytes(data),
        "created_utc": utc_now(),
    }]


def run(args: argparse.Namespace) -> int:
    paths = locate_paths()
    for key in ("references_01", "archives_dir", "extracted_dir"):
        paths[key].mkdir(parents=True, exist_ok=True)

    target_registry_path = paths["references_01"] / f"strong_interaction_arxiv_source_targets_raw_{SCRIPT_VERSION}.csv"
    write_csv(target_registry_path, [asdict(t) | {"created_utc": utc_now()} for t in TARGETS], [
        "target_id", "source_id", "arxiv_id", "source_url", "output_filename", "expected_role", "priority", "notes", "created_utc"
    ])

    download_rows: list[dict[str, Any]] = []
    extraction_rows: list[dict[str, Any]] = []

    for target in TARGETS:
        started = utc_now()
        archive_path = paths["archives_dir"] / target.output_filename
        ok, data, error, status = safe_request(target.source_url, args.max_size_mb)
        if ok and data is not None:
            archive_path.write_bytes(data)
            digest = sha256_bytes(data)
            size = len(data)
            archive_kind, extracted = extract_archive(data, target, paths["extracted_dir"])
            extraction_rows.extend(extracted)
        else:
            digest = ""
            size = 0
            archive_kind = "not_downloaded"
        download_rows.append({
            "target_id": target.target_id,
            "source_id": target.source_id,
            "arxiv_id": target.arxiv_id,
            "source_url": target.source_url,
            "archive_file": str(archive_path) if ok else "",
            "success": ok,
            "http_status": status,
            "size_bytes": size,
            "sha256": digest,
            "archive_kind": archive_kind,
            "error": error,
            "started_utc": started,
            "finished_utc": utc_now(),
        })
        time.sleep(SLEEP_SECONDS)

    download_manifest = paths["references_01"] / f"strong_interaction_arxiv_source_download_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(download_manifest, download_rows, [
        "target_id", "source_id", "arxiv_id", "source_url", "archive_file", "success", "http_status",
        "size_bytes", "sha256", "archive_kind", "error", "started_utc", "finished_utc"
    ])

    extraction_manifest = paths["references_01"] / f"strong_interaction_arxiv_source_extraction_manifest_raw_{SCRIPT_VERSION}.csv"
    write_csv(extraction_manifest, extraction_rows, [
        "target_id", "source_id", "member_name", "output_file", "extracted", "reason", "numeric_count_preview",
        "has_keyword", "size_bytes", "sha256", "created_utc"
    ])

    summary_path = paths["references_01"] / f"strong_interaction_arxiv_source_summary_raw_{SCRIPT_VERSION}.txt"
    success_count = sum(1 for r in download_rows if r.get("success"))
    extracted_count = sum(1 for r in extraction_rows if str(r.get("extracted")).lower() == "true" or r.get("extracted") is True)
    summary_path.write_text(
        "Strong_interaction arXiv source archive acquisition summary\n"
        "==========================================================\n"
        f"Generated UTC: {utc_now()}\n"
        f"Script version: {SCRIPT_VERSION}\n\n"
        f"Downloaded archives: {success_count}/{len(TARGETS)}\n"
        f"Extracted candidate files: {extracted_count}\n\n"
        "Interpretation:\n"
        "- These archives and extracted candidates are raw fallback source materials.\n"
        "- They are not final numerical benchmark input.\n"
        "- Review extracted candidates for tables, data availability links, and actual numeric arrays.\n"
        "- A later cleaner must convert confirmed numeric candidates into cleaned_tables before derived/input.\n\n"
        f"Archives directory: {paths['archives_dir']}\n"
        f"Extracted candidates directory: {paths['extracted_dir']}\n"
        f"Download manifest: {download_manifest}\n"
        f"Extraction manifest: {extraction_manifest}\n",
        encoding="utf-8",
    )

    print(f"[OK] target registry: {target_registry_path}")
    print(f"[OK] download manifest: {download_manifest}")
    print(f"[OK] extraction manifest: {extraction_manifest}")
    print(f"[OK] summary: {summary_path}")
    print(f"[DONE] downloaded={success_count}/{len(TARGETS)} extracted_candidates={extracted_count}")
    return 0 if success_count > 0 else 1


def main() -> int:
    parser = argparse.ArgumentParser(description="Download arXiv source archives for Strong_interaction fallback numerical-source discovery.")
    parser.add_argument("--max-size-mb", type=int, default=MAX_SIZE_MB_DEFAULT, help="Maximum source archive size in MB. Default: 200.")
    args = parser.parse_args()
    return run(args)


if __name__ == "__main__":
    sys.exit(main())
