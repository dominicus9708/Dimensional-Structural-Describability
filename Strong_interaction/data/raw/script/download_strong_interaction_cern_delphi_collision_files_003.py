#!/usr/bin/env python3
# -*- coding: utf-8 -*-
from __future__ import annotations

import argparse
import csv
import datetime as dt
import pathlib
import urllib.parse
from typing import Any, Iterable

RAW_BATCH = "03"
SCRIPT_VERSION = "003"


def utc_now() -> str:
    return dt.datetime.now(dt.timezone.utc).isoformat(timespec="seconds")


def locate_paths() -> dict[str, pathlib.Path]:
    script_path = pathlib.Path(__file__).resolve()
    strong_root = script_path.parents[3]
    return {
        "references": strong_root / "data" / "raw" / "references" / RAW_BATCH,
        "source_tables": strong_root / "data" / "raw" / "source_tables" / RAW_BATCH,
        "shortlist": strong_root / "data" / "raw" / "references" / RAW_BATCH / "strong_interaction_cern_delphi_record_file_candidates_collision_shortlist_raw_003.csv",
        "download