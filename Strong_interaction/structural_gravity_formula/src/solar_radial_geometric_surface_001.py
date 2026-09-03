from pathlib import Path
import pandas as pd

BASE = Path(__file__).resolve().parents[1]
INPUT = BASE / "data" / "solar_bp2004_radial_points_001.csv"
OUTPUT = BASE / "results" / "solar_radial_geometric_surface_001.csv"


def main():
    df = pd.read_csv(INPUT)
    df["slope_rel_surface"] = df["Mfrac"] / (df["Rfrac"] ** 2)
    df["enclosed_depth_proxy_rel_surface"] = df["Mfrac"] / df["Rfrac"]
    df["mean_density_proxy_rel_solar_mean"] = df["Mfrac"] / (df["Rfrac"] ** 3)
    df["rho_kg_m3"] = df["rho_g_cm3"] * 1000.0
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT, index=False)
    print(f"wrote {OUTPUT}")


if __name__ == "__main__":
    main()
