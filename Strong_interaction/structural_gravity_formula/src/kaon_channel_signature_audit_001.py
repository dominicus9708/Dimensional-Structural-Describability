from pathlib import Path
import csv
import math

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "data" / "kaon_channel_signature_inputs_001.csv"
OUTPUT = BASE / "results" / "kaon_channel_signature_audit_001.csv"

by_candidate = {}
with INPUT.open("r", encoding="utf-8", newline="") as f:
    for row in csv.DictReader(f):
        by_candidate.setdefault(row["candidate"], []).append(row)


def summarize(weights):
    total = sum(weights)
    p = [w / total for w in weights]
    n = len(p)
    H = -sum(x * math.log(x) for x in p if x > 0.0)
    H_norm = H / math.log(n) if n > 1 else 0.0
    N_exp = math.exp(H)
    N_ipr = 1.0 / sum(x * x for x in p)
    l1_asym = sum(abs(x - 1.0 / n) for x in p)
    return H, H_norm, N_exp, N_ipr, l1_asym

rows = []
for candidate, group in by_candidate.items():
    A = [float(r["A_share"]) for r in group]
    D = [float(r["D_component_abs"]) for r in group]
    A_metrics = summarize(A)
    D_metrics = summarize(D)
    rows.append({
        "candidate": candidate,
        "A_entropy": f"{A_metrics[0]:.12e}",
        "A_entropy_normalized": f"{A_metrics[1]:.12e}",
        "A_effective_channels_expH": f"{A_metrics[2]:.12e}",
        "A_effective_channels_IPR": f"{A_metrics[3]:.12e}",
        "A_L1_asymmetry": f"{A_metrics[4]:.12e}",
        "D_entropy": f"{D_metrics[0]:.12e}",
        "D_entropy_normalized": f"{D_metrics[1]:.12e}",
        "D_effective_channels_expH": f"{D_metrics[2]:.12e}",
        "D_effective_channels_IPR": f"{D_metrics[3]:.12e}",
        "D_L1_asymmetry": f"{D_metrics[4]:.12e}",
    })

lookup = {r["candidate"]: r for r in rows}
if "pion" in lookup and "kaon" in lookup:
    pi, k = lookup["pion"], lookup["kaon"]
    for key in [
        "A_entropy_normalized",
        "A_effective_channels_expH",
        "A_effective_channels_IPR",
        "D_entropy_normalized",
        "D_effective_channels_expH",
        "D_effective_channels_IPR",
    ]:
        ratio = float(k[key]) / float(pi[key])
        for r in (pi, k):
            r[f"K_over_pi_{key}"] = f"{ratio:.12e}"

OUTPUT.parent.mkdir(parents=True, exist_ok=True)
fieldnames = list(rows[0].keys())
for r in rows:
    for key in r.keys():
        if key not in fieldnames:
            fieldnames.append(key)

with OUTPUT.open("w", encoding="utf-8", newline="") as f:
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(rows)

print(f"Wrote {OUTPUT}")
