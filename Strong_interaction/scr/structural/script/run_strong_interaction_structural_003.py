#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
run_strong_interaction_structural_003.py

Structural diagnostic pipeline for the strong-interaction note.

Author: Kwon Dominicus
Assistant-prepared implementation draft: 2026-06-02

Placement:
    scr/structural/script/run_strong_interaction_structural_003.py

Input policy:
    Use the SAME official input directory as the standard pipeline.

Default input:
    data/derived/input/

Default output:
    results/structural/<YYYYMMDD_HHMMSS>/

v003 fix:
    Keeps the v002 project-root auto-detection fix.
    Also fixes duplicate case_id insertion when the official standard input already
    contains a case_id column.

Interpretive status:
    This is not a QCD derivation, not a Standard Model replacement, and not a proof.
    It is a reproducible structural diagnostic layer built after the preserved standard baseline.
"""

from __future__ import annotations

import argparse
import json
import math
import sys
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Sequence, Tuple

import numpy as np
import pandas as pd

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


EPS = 1.0e-12

EXPECTED_INPUT_FILES = {
    "minimal": "strong_interaction_minimal_input.csv",
    "constants": "strong_interaction_selected_constants_input_001.csv",
    "particles": "strong_interaction_selected_particles_input_001.csv",
    "manifest": "strong_interaction_input_manifest_001.csv",
}

MAIN_CASE_INPUT_KEYS = ("minimal", "particles")

ID_HINTS = (
    "case_id",
    "case",
    "target",
    "label",
    "name",
    "particle",
    "particle_name",
    "process",
    "channel",
    "reaction",
    "observable",
)

EXCLUDE_NUMERIC_HINTS = (
    "index",
    "row",
    "id",
    "year",
    "doi",
    "reference",
    "source",
)

STANDARD_RESULT_HINTS = (
    "standard",
    "expected",
    "residual",
    "error",
    "difference",
    "ratio",
    "pass",
    "fail",
    "check",
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Run structural diagnostics using the same official input as the standard pipeline."
    )
    parser.add_argument(
        "--project-root",
        default=None,
        help=(
            "Project root. If omitted, the script auto-detects the root by walking upward "
            "from both the current working directory and the script location."
        ),
    )
    parser.add_argument(
        "--input-dir",
        default=None,
        help="Official input directory. Default: <detected-project-root>/data/derived/input.",
    )
    parser.add_argument(
        "--output-root",
        default=None,
        help="Output root. Default: <detected-project-root>/results/structural.",
    )
    parser.add_argument(
        "--near-threshold",
        type=float,
        default=0.15,
        help="Near-background threshold in robust sigma units. Default: 0.15.",
    )
    parser.add_argument(
        "--feature-weight-mode",
        choices=["derived", "equal"],
        default="derived",
        help="Feature weight mode. derived = completeness × robust variability. equal = equal weights.",
    )
    return parser.parse_args()


def timestamp() -> str:
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def ensure_dir(path: Path) -> Path:
    path.mkdir(parents=True, exist_ok=True)
    return path


def expected_input_paths(input_dir: Path) -> Dict[str, Path]:
    return {key: input_dir / filename for key, filename in EXPECTED_INPUT_FILES.items()}


def has_main_case_input(input_dir: Path) -> bool:
    paths = expected_input_paths(input_dir)
    return any(paths[key].exists() for key in MAIN_CASE_INPUT_KEYS)


def candidate_roots_from(path: Path) -> List[Path]:
    p = path.resolve()
    roots = [p]
    if p.is_file():
        roots.append(p.parent)
        roots.extend(p.parent.parents)
    else:
        roots.extend(p.parents)
    # preserve order and deduplicate
    out = []
    seen = set()
    for r in roots:
        key = str(r).lower()
        if key not in seen:
            out.append(r)
            seen.add(key)
    return out


def detect_project_root(explicit_project_root: Optional[str]) -> Tuple[Path, List[Path]]:
    """
    Detect project root by searching for:
        data/derived/input/<main case input>
    Legacy typo fallback:
        data/derivde/input/<main case input>
    """
    searched: List[Path] = []

    if explicit_project_root:
        root = Path(explicit_project_root).resolve()
        return root, [root / "data" / "derived" / "input"]

    script_path = Path(__file__).resolve()
    cwd = Path.cwd().resolve()

    root_candidates: List[Path] = []
    root_candidates.extend(candidate_roots_from(cwd))
    root_candidates.extend(candidate_roots_from(script_path))

    # Deduplicate.
    deduped = []
    seen = set()
    for r in root_candidates:
        key = str(r).lower()
        if key not in seen:
            deduped.append(r)
            seen.add(key)

    for root in deduped:
        for rel in (Path("data") / "derived" / "input", Path("data") / "derivde" / "input"):
            input_dir = root / rel
            searched.append(input_dir)
            if has_main_case_input(input_dir):
                return root, searched

    # If no input exists, prefer a plausible root:
    # script path .../scr/structural/script -> root is parents[2] from script dir.
    try:
        fallback_root = script_path.parents[3]
    except IndexError:
        fallback_root = cwd
    return fallback_root, searched


def resolve_input_dir(args: argparse.Namespace, project_root: Path, searched: List[Path]) -> Path:
    if args.input_dir:
        return Path(args.input_dir).resolve()

    preferred = project_root / "data" / "derived" / "input"
    if has_main_case_input(preferred):
        return preferred

    legacy = project_root / "data" / "derivde" / "input"
    if has_main_case_input(legacy):
        return legacy

    # Last chance: use any searched candidate containing the main input.
    for candidate in searched:
        if has_main_case_input(candidate):
            return candidate

    return preferred


def read_csv_if_exists(path: Path) -> Optional[pd.DataFrame]:
    if not path.exists():
        return None
    try:
        return pd.read_csv(path)
    except UnicodeDecodeError:
        return pd.read_csv(path, encoding="utf-8-sig")


def first_existing_column(df: pd.DataFrame, hints: Sequence[str]) -> Optional[str]:
    lower_map = {str(c).lower(): c for c in df.columns}
    for hint in hints:
        if hint.lower() in lower_map:
            return lower_map[hint.lower()]
    for c in df.columns:
        low = str(c).lower()
        if any(h in low for h in hints):
            return c
    return None


def clean_case_id_series(df: pd.DataFrame, prefix: str) -> pd.Series:
    id_col = first_existing_column(df, ID_HINTS)
    if id_col is not None:
        out = df[id_col].astype(str).str.strip()
        out = out.replace({"": np.nan, "nan": np.nan, "None": np.nan})
        if out.notna().any():
            fallback = pd.Series([f"{prefix}_{i:04d}" for i in range(len(df))], index=df.index)
            return out.where(out.notna(), fallback)
    return pd.Series([f"{prefix}_{i:04d}" for i in range(len(df))], index=df.index)


def ensure_case_id_column(df: pd.DataFrame, prefix: str) -> pd.DataFrame:
    """
    Ensure exactly one usable case_id column without blindly inserting a duplicate.

    v003 fix:
    - If the official standard input already contains case_id, reuse it.
    - If it contains a differently named identifier column, create case_id from that.
    - If no identifier exists, generate case_0000-style identifiers.
    """
    out = df.copy()
    series = clean_case_id_series(out, prefix)

    # Exact case_id already exists: reuse and sanitize it.
    if "case_id" in out.columns:
        out["case_id"] = series
        cols = ["case_id"] + [c for c in out.columns if c != "case_id"]
        return out.loc[:, cols]

    # Case-insensitive case_id exists under another capitalization.
    case_id_like = None
    for c in out.columns:
        if str(c).lower() == "case_id":
            case_id_like = c
            break

    if case_id_like is not None:
        out = out.rename(columns={case_id_like: "case_id"})
        out["case_id"] = series
        cols = ["case_id"] + [c for c in out.columns if c != "case_id"]
        return out.loc[:, cols]

    out.insert(0, "case_id", series)
    return out


def numeric_columns(df: pd.DataFrame) -> List[str]:
    cols: List[str] = []
    for c in df.columns:
        low = str(c).lower()
        if any(h in low for h in EXCLUDE_NUMERIC_HINTS):
            continue
        if any(h in low for h in STANDARD_RESULT_HINTS):
            continue
        s = pd.to_numeric(df[c], errors="coerce")
        valid_count = int(s.notna().sum())
        if valid_count >= max(2, min(3, len(df))):
            cols.append(c)
    return cols


def robust_minmax(s: pd.Series) -> pd.Series:
    x = pd.to_numeric(s, errors="coerce").astype(float)

    if x.notna().sum() == 0:
        return pd.Series(np.nan, index=s.index)

    median_value = float(np.nanmedian(x))
    x = x.fillna(median_value)

    q05 = float(np.nanquantile(x, 0.05))
    q95 = float(np.nanquantile(x, 0.95))

    if (not math.isfinite(q05)) or (not math.isfinite(q95)) or abs(q95 - q05) < EPS:
        xmin = float(np.nanmin(x))
        xmax = float(np.nanmax(x))
        if abs(xmax - xmin) < EPS:
            return pd.Series(np.full(len(x), 0.5), index=s.index)
        return (x - xmin) / (xmax - xmin + EPS)

    clipped = x.clip(lower=q05, upper=q95)
    return (clipped - q05) / (q95 - q05 + EPS)


def robust_variability(s: pd.Series) -> float:
    x = pd.to_numeric(s, errors="coerce").astype(float)
    x = x[np.isfinite(x)]
    if len(x) < 2:
        return 0.0

    q25, q75 = np.nanquantile(x, [0.25, 0.75])
    iqr = float(q75 - q25)

    if (not math.isfinite(iqr)) or iqr < EPS:
        return max(float(np.nanstd(x)), 0.0)

    return iqr


def load_inputs(input_dir: Path) -> Dict[str, Optional[pd.DataFrame]]:
    return {
        key: read_csv_if_exists(input_dir / filename)
        for key, filename in EXPECTED_INPUT_FILES.items()
    }


def build_main_case_table(inputs: Dict[str, Optional[pd.DataFrame]]) -> pd.DataFrame:
    """
    The structural layer uses the same official input as the standard layer.

    Priority:
    1. strong_interaction_minimal_input.csv
    2. strong_interaction_selected_particles_input_001.csv
    """
    minimal = inputs.get("minimal")
    particles = inputs.get("particles")

    if minimal is not None and len(minimal) > 0:
        df = ensure_case_id_column(minimal, "case")
        df["source_table"] = EXPECTED_INPUT_FILES["minimal"]
        return df

    if particles is not None and len(particles) > 0:
        df = ensure_case_id_column(particles, "particle")
        df["source_table"] = EXPECTED_INPUT_FILES["particles"]
        return df

    raise FileNotFoundError(
        "No usable main case input was found. Expected either "
        "strong_interaction_minimal_input.csv or "
        "strong_interaction_selected_particles_input_001.csv in the official input directory."
    )


def build_feature_matrix(case_df: pd.DataFrame, weight_mode: str) -> Tuple[pd.DataFrame, pd.DataFrame]:
    cols = numeric_columns(case_df)

    if not cols:
        raise ValueError(
            "No usable numeric feature columns were found in the official input. "
            "The structural layer needs at least one non-ID numeric column."
        )

    normalized = pd.DataFrame(index=case_df.index)
    rows = []

    for c in cols:
        raw = pd.to_numeric(case_df[c], errors="coerce")
        normalized[f"feature__{c}"] = robust_minmax(raw)

        completeness = float(raw.notna().mean())
        variability = robust_variability(raw)
        raw_weight_score = completeness * (variability + EPS)

        rows.append(
            {
                "feature": c,
                "completeness": completeness,
                "robust_variability": variability,
                "raw_weight_score": raw_weight_score,
            }
        )

    weights = pd.DataFrame(rows)

    if weight_mode == "equal":
        weights["weight"] = 1.0 / len(weights)
    else:
        total = float(weights["raw_weight_score"].sum())
        if total <= EPS:
            weights["weight"] = 1.0 / len(weights)
        else:
            weights["weight"] = weights["raw_weight_score"] / total

    return normalized, weights


def compute_structural_layer(
    case_df: pd.DataFrame,
    features_norm: pd.DataFrame,
    weights: pd.DataFrame,
    near_threshold: float,
) -> pd.DataFrame:
    out = case_df[["case_id", "source_table"]].copy()

    feature_cols = list(features_norm.columns)
    weight_map = {
        f"feature__{row['feature']}": float(row["weight"])
        for _, row in weights.iterrows()
    }

    mat = features_norm.copy()
    for c in mat.columns:
        fill_value = float(np.nanmedian(mat[c])) if mat[c].notna().any() else 0.5
        mat[c] = mat[c].fillna(fill_value)

    weighted_sum = np.zeros(len(mat), dtype=float)
    for c in feature_cols:
        weighted_sum += mat[c].to_numpy(dtype=float) * weight_map.get(c, 0.0)

    d_bg = float(np.nanmedian(weighted_sum))
    sigma = weighted_sum - d_bg
    sigma_std = float(np.nanstd(sigma))
    gamma = 1.0 / (sigma_std + EPS) if sigma_std > EPS else 1.0
    sigma_robust = gamma * sigma

    out["D_w_structural"] = weighted_sum
    out["D_bg_internal_median"] = d_bg
    out["sigma_structural"] = sigma
    out["gamma_internal"] = gamma
    out["sigma_structural_robust_units"] = sigma_robust

    def classify(value: float) -> str:
        if abs(value) <= near_threshold:
            return "near_background"
        if value > near_threshold:
            return "above_background_structural_response"
        return "below_background_structural_response"

    out["structural_response_flag"] = [classify(v) for v in sigma_robust]

    contribution_preview = []
    for i in range(len(mat)):
        contributions = []
        for c in feature_cols:
            original_feature = c.replace("feature__", "", 1)
            contribution = float(mat.iloc[i][c]) * weight_map.get(c, 0.0)
            contributions.append((original_feature, contribution))
        contributions.sort(key=lambda item: abs(item[1]), reverse=True)
        contribution_preview.append("; ".join(f"{name}:{value:.4g}" for name, value in contributions[:3]))

    out["top_weighted_feature_contributions"] = contribution_preview

    return out


def write_plots(structural_summary: pd.DataFrame, feature_weights: pd.DataFrame, plot_dir: Path) -> None:
    plot_cases = structural_summary.copy()
    plot_cases["case_id"] = plot_cases["case_id"].astype(str)

    if len(plot_cases) > 40:
        plot_cases = plot_cases.sort_values("D_w_structural", ascending=False).head(40)

    plt.figure(figsize=(max(8, min(16, len(plot_cases) * 0.45)), 5))
    plt.bar(plot_cases["case_id"], plot_cases["D_w_structural"])
    plt.xticks(rotation=75, ha="right")
    plt.ylabel("D_w structural")
    plt.title("Strong-interaction structural descriptor")
    plt.tight_layout()
    plt.savefig(plot_dir / "structural_Dw_001.png", dpi=180)
    plt.close()

    plt.figure(figsize=(max(8, min(16, len(plot_cases) * 0.45)), 5))
    plt.bar(plot_cases["case_id"], plot_cases["sigma_structural_robust_units"])
    plt.axhline(0.0, linewidth=1.0)
    plt.xticks(rotation=75, ha="right")
    plt.ylabel("sigma structural, robust units")
    plt.title("Structural contrast relative to internal background")
    plt.tight_layout()
    plt.savefig(plot_dir / "structural_sigma_001.png", dpi=180)
    plt.close()

    weights_plot = feature_weights.sort_values("weight", ascending=False).head(30)
    plt.figure(figsize=(max(8, min(16, len(weights_plot) * 0.5)), 5))
    plt.bar(weights_plot["feature"].astype(str), weights_plot["weight"])
    plt.xticks(rotation=75, ha="right")
    plt.ylabel("weight")
    plt.title("Derived structural feature weights")
    plt.tight_layout()
    plt.savefig(plot_dir / "structural_feature_weights_001.png", dpi=180)
    plt.close()


def write_run_manifest(
    output_dir: Path,
    project_root: Path,
    input_dir: Path,
    searched_input_dirs: List[Path],
    inputs: Dict[str, Optional[pd.DataFrame]],
    args: argparse.Namespace,
) -> None:
    rows = []
    rows.append(
        {
            "role": "detected_project_root",
            "filename": "",
            "path": str(project_root),
            "exists": project_root.exists(),
            "rows": None,
            "columns": None,
        }
    )

    for key, filename in EXPECTED_INPUT_FILES.items():
        path = input_dir / filename
        df = inputs.get(key)
        rows.append(
            {
                "role": key,
                "filename": filename,
                "path": str(path),
                "exists": path.exists(),
                "rows": None if df is None else int(len(df)),
                "columns": None if df is None else int(len(df.columns)),
            }
        )

    for n, candidate in enumerate(searched_input_dirs):
        rows.append(
            {
                "role": f"searched_input_dir_{n:03d}",
                "filename": "",
                "path": str(candidate),
                "exists": candidate.exists(),
                "rows": None,
                "columns": None,
            }
        )

    rows.append(
        {
            "role": "run_arguments",
            "filename": "",
            "path": json.dumps(vars(args), ensure_ascii=False),
            "exists": True,
            "rows": None,
            "columns": None,
        }
    )

    pd.DataFrame(rows).to_csv(
        output_dir / "structural_run_manifest_001.csv",
        index=False,
        encoding="utf-8-sig",
    )


def write_summary(
    output_dir: Path,
    project_root: Path,
    input_dir: Path,
    structural_summary: pd.DataFrame,
    feature_weights: pd.DataFrame,
) -> None:
    counts = structural_summary["structural_response_flag"].value_counts(dropna=False).to_dict()

    top_weights = feature_weights.sort_values("weight", ascending=False).head(10)
    top_weight_lines = [
        f"- {row['feature']}: weight={row['weight']:.6g}, completeness={row['completeness']:.3g}, variability={row['robust_variability']:.6g}"
        for _, row in top_weights.iterrows()
    ]

    text = f"""Strong-interaction structural pipeline summary
================================================

Run time:
- {datetime.now().isoformat(timespec='seconds')}

Detected project root:
- {project_root}

Input policy:
- Same official input directory as the standard pipeline.

Input directory:
- {input_dir}

Output directory:
- {output_dir}

Interpretive status
-------------------
This output is a structural diagnostic layer.

It does not claim:
- QCD derivation,
- Standard Model replacement,
- direct strong-interaction proof,
- final empirical validation.

It only computes an internally normalized structural descriptor from the same
official input used by the standard baseline.

Core quantities
---------------
D_w_structural:
- weighted structural descriptor computed from normalized numeric input features.

D_bg_internal_median:
- internal background level, defined as the median of D_w_structural.

sigma_structural:
- structural contrast relative to the internal background.

sigma_structural_robust_units:
- internally normalized contrast using gamma_internal = 1 / std(sigma_structural).

Structural response counts
--------------------------
{json.dumps(counts, ensure_ascii=False, indent=2)}

Top feature weights
-------------------
{chr(10).join(top_weight_lines) if top_weight_lines else '- no feature weights'}

Output files
------------
- structural_case_summary_001.csv
- structural_feature_weights_001.csv
- structural_numeric_features_001.csv
- structural_run_manifest_001.csv
- structural_summary_001.txt
- plots/structural_Dw_001.png
- plots/structural_sigma_001.png
- plots/structural_feature_weights_001.png

Recommended wording
-------------------
Use: "structural diagnostic layer after a preserved standard baseline."

Avoid: "QCD proof", "strong-interaction derivation", "Standard Model replacement",
or "final validation."
"""
    (output_dir / "structural_summary_001.txt").write_text(text, encoding="utf-8")


def write_error(
    output_dir: Path,
    project_root: Path,
    input_dir: Path,
    searched_input_dirs: List[Path],
    exc: Exception,
) -> None:
    searched_text = "\n".join(f"- {p}" for p in searched_input_dirs)
    error_text = f"""Strong-interaction structural pipeline failed
================================================

Error:
{type(exc).__name__}: {exc}

Detected project root:
{project_root}

Selected input directory:
{input_dir}

Expected official standard-input files:
{json.dumps(EXPECTED_INPUT_FILES, ensure_ascii=False, indent=2)}

Searched input directories:
{searched_text if searched_text else '- none'}

Immediate command workaround:
python scr\\structural\\script\\run_strong_interaction_structural_003.py --project-root <PROJECT_ROOT>

If running from scr\\structural\\script, the manual relative command is usually:
python run_strong_interaction_structural_003.py --project-root ..\\..\\..
"""
    (output_dir / "structural_error_001.txt").write_text(error_text, encoding="utf-8")
    print(error_text, file=sys.stderr)


def main() -> int:
    args = parse_args()

    project_root, searched_input_dirs = detect_project_root(args.project_root)
    input_dir = resolve_input_dir(args, project_root, searched_input_dirs)

    if args.output_root:
        output_root = Path(args.output_root).resolve()
    else:
        output_root = project_root / "results" / "structural"

    output_dir = ensure_dir(output_root / timestamp())
    plot_dir = ensure_dir(output_dir / "plots")

    inputs = load_inputs(input_dir)

    try:
        case_df = build_main_case_table(inputs)
        features_norm, feature_weights = build_feature_matrix(
            case_df=case_df,
            weight_mode=args.feature_weight_mode,
        )
        structural_summary = compute_structural_layer(
            case_df=case_df,
            features_norm=features_norm,
            weights=feature_weights,
            near_threshold=float(args.near_threshold),
        )
    except Exception as exc:
        write_error(output_dir, project_root, input_dir, searched_input_dirs, exc)
        return 1

    structural_summary.to_csv(
        output_dir / "structural_case_summary_001.csv",
        index=False,
        encoding="utf-8-sig",
    )
    feature_weights.to_csv(
        output_dir / "structural_feature_weights_001.csv",
        index=False,
        encoding="utf-8-sig",
    )

    numeric_features_out = pd.concat([case_df[["case_id"]], features_norm], axis=1)
    numeric_features_out.to_csv(
        output_dir / "structural_numeric_features_001.csv",
        index=False,
        encoding="utf-8-sig",
    )

    write_plots(structural_summary, feature_weights, plot_dir)
    write_run_manifest(output_dir, project_root, input_dir, searched_input_dirs, inputs, args)
    write_summary(output_dir, project_root, input_dir, structural_summary, feature_weights)

    print("[OK] Strong-interaction structural pipeline completed.")
    print(f"[PROJECT ROOT] {project_root}")
    print(f"[INPUT] {input_dir}")
    print(f"[OUTPUT] {output_dir}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
