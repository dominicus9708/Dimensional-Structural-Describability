#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import re
import shutil
import subprocess
import urllib.parse
import urllib.request
import hashlib

RAW_BATCH = "03"
SCRIPT_VERSION = "003"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "strong_root": strong_root,
        "shortlist": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_cern_delphi_record_file_candidates_collision_shortlist_raw_003.csv",
        "references_03": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "download_dir": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH / "collision_file_downloads",
    }


def read_csv(path: pathlib.Path) -> list[dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def write_csv(path: pathlib.Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8-sig", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(rows)


def safe_name(value: str) -> str:
    parsed = urllib.parse.urlparse(value)
    name = pathlib.PurePosixPath(parsed.path).name or "collision_candidate.dat"
    name = re.sub(r"[^A-Za-z0-9_.-]+", "_", name).strip("._")
    return name[:180] or "collision_candidate.dat"


def sha256_file(path: pathlib.Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1024 * 1024), b""):
            h.update(block)
    return h.hexdigest()


def root_to_https_candidates(url: str) -> list[str]:
    if not url.startswith("root://eospublic.cern.ch/"):
        return []
    path = url.replace("root://eospublic.cern.ch/", "")
    while path.startswith("/"):
        path = path[1:]
    if path.startswith("eos/opendata/"):
        suffix = path[len("eos/opendata/"):]
        return [
            "https://eospublichttp.cern.ch/eos/opendata/" + suffix,
            "https://opendata.cern.ch/eos/opendata/" + suffix,
        ]
    return []


def try_http_download(url: str, output_path: pathlib.Path, max_size_mb: int) -> tuple[bool, str, int]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "DSD-Strong-interaction-pipeline/003"})
        with urllib.request.urlopen(req, timeout=180) as res:
            length = res.headers.get("Content-Length")
            if length and int(length) > max_size_mb * 1024 * 1024:
                return False, "blocked_by_size_limit", 0
            data = res.read(max_size_mb * 1024 * 1024 + 1)
            if len(data) > max_size_mb * 1024 * 1024:
                return False, "blocked_by_size_limit_after_read", 0
            output_path.write_bytes(data)
            return True, "downloaded_http", len(data)
    except Exception as exc:
        return False, type(exc).__name__ + ": " + str(exc), 0


def try_xrdcp_download(url: str, output_path: pathlib.Path, max_size_mb: int) -> tuple[bool, str, int]:
    xrdcp = shutil.which("xrdcp")
    if not xrdcp:
        return False, "xrdcp_not_found", 0
    cmd = [xrdcp, "-f", url, str(output_path)]
    try:
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=1800)
        if result.returncode != 0:
            return False, "xrdcp_failed: " + (result.stderr or result.stdout)[-1000:], 0
        size = output_path.stat().st_size if output_path.exists() else 0
        if size > max_size_mb * 1024 * 1024:
            output_path.unlink(missing_ok=True)
            return False, "blocked_by_size_limit_after_xrdcp", 0
        return True, "downloaded_xrdcp", size
    except Exception as exc:
        return False, type(exc).__name__ + ": " + str(exc), 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--limit", type=int, default=5)
    parser.add_argument("--max-size-mb", type=int, default=500)
    parser.add_argument("--try-download", action="store_true")
    args = parser.parse_args()

    paths = locate_paths()
    paths["download_dir"].mkdir(parents=True, exist_ok=True)

    rows = read_csv(paths["shortlist"])
    if not rows:
        print("[ERROR] shortlist missing or empty:", paths["shortlist"])
        return 1

    targets = rows[: args.limit] if args.limit and args.limit > 0 else rows
    manifest = []

    for i, row in enumerate(targets, start=1):
        url = row.get("candidate_url", "")
        fid = row.get("file_candidate_id", "candidate_" + str(i))
        out_name = fid + "__" + safe_name(url)
        out_path = paths["download_dir"] / out_name

        scheme = urllib.parse.urlparse(url).scheme
        success = False
        status = "not_attempted"
        size = 0
        sha256 = ""
        output_file = ""

        if scheme == "root":
            if args.try_download:
                success, status, size = try_xrdcp_download(url, out_path, args.max_size_mb)
                if not success:
                    for alt in root_to_https_candidates(url):
                        success, status, size = try_http_download(alt, out_path, args.max_size_mb)
                        if success:
                            break
            else:
                status = "root_scheme_requires_xrootd_use_try_download_to_attempt"
        elif scheme in {"http", "https"}:
            if args.try_download:
                success, status, size = try_http_download(url, out_path, args.max_size_mb)
            else:
                status = "http_candidate_not_downloaded_without_try_download"
        else:
            status = "unsupported_url_scheme"

        if success and out_path.exists():
            sha256 = sha256_file(out_path)
            output_file = str(out_path)

        manifest.append({
            "file_candidate_id": fid,
            "recid": row.get("recid", ""),
            "record_title": row.get("record_title", ""),
            "filename": row.get("filename", ""),
            "file_extension": row.get("file_extension", ""),
            "size_metadata": row.get("size_metadata", ""),
            "candidate_url": url,
            "url_scheme": scheme,
            "attempted_download": bool(args.try_download),
            "success": success,
            "status": status,
            "size_bytes": size,
            "sha256": sha256,
            "output_file": output_file,
            "created_utc": utc_now(),
        })

    manifest_path = paths["references_03"] / "strong_interaction_cern_delphi_collision_file_download_manifest_raw_003.csv"
    summary_path = paths["references_03"] / "strong_interaction_cern_delphi_collision_file_download_summary_raw_003.txt"

    fields = [
        "file_candidate_id", "recid", "record_title", "filename", "file_extension",
        "size_metadata", "candidate_url", "url_scheme", "attempted_download",
        "success", "status", "size_bytes", "sha256", "output_file", "created_utc"
    ]
    write_csv(manifest_path, manifest, fields)

    attempted = len(manifest)
    success_count = sum(1 for r in manifest if r["success"])
    root_count = sum(1 for r in manifest if r["url_scheme"] == "root")
    total_bytes = sum(int(r["size_bytes"]) for r in manifest)

    summary_lines = [
        "Strong_interaction CERN DELPHI collision file download summary",
        "============================================================",
        "Generated UTC: " + utc_now(),
        "Script version: " + SCRIPT_VERSION,
        "",
        "Rows attempted: " + str(attempted),
        "Successful downloads: " + str(success_count),
        "Root-scheme candidates: " + str(root_count),
        "Total downloaded bytes: " + str(total_bytes),
        "Try-download enabled: " + str(bool(args.try_download)),
        "",
        "Interpretation:",
        "- Without --try-download this script only records whether candidates require XRootD.",
        "- root:// URLs normally require xrdcp or an HTTP gateway.",
        "- Use small --limit values before any larger acquisition.",
        "Manifest: " + str(manifest_path),
    ]
    summary_path.write_text(chr(10).join(summary_lines), encoding="utf-8")

    print("[OK] manifest:", manifest_path)
    print("[OK] summary:", summary_path)
    print("[DONE] attempted=" + str(attempted) + " success=" + str(success_count) + " root_required=" + str(root_count) + " bytes=" + str(total_bytes))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
