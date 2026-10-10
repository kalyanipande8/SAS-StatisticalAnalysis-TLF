"""End-to-end pipeline: simulate ADaM-style trial data, generate 25+ real
RTF tables/listings (the Python mirror of the authored SAS programs), and
run the 45-point QC framework against the actual generated outputs."""
import json
import os

from src.simulate_trial_data import simulate_all
from src.generate_tlfs import generate_all
from src.qc_framework import run_full_framework

os.makedirs("data", exist_ok=True)
os.makedirs("results", exist_ok=True)

print("=== Simulating ADaM-style trial datasets (ADSL, ADAE, ADVS, ADLB) ===")
data = simulate_all()
for name, df in data.items():
    df.to_csv(f"data/{name}.csv", index=False)
    print(f"  {name}: {df.shape}")

print("\n=== Generating tables and listings (Python mirror of sas/*.sas) ===")
paths = generate_all(data, outdir="output/tlfs")
print(f"{len(paths)} outputs generated in output/tlfs/")

print("\n=== 45-point QC framework ===")
qc = run_full_framework(paths, data)
print(f"{qc['n_checks']} checks run")
print("Score by dimension:", qc["score_by_dimension"])
print("Overall QC score:", qc["overall_qc_score_pct"])

with open("results/qc_checks.json", "w") as f:
    json.dump(qc["checks"], f, indent=2)

summary = {
    "n_tlf_outputs_generated": len(paths),
    "n_qc_checks": qc["n_checks"],
    "overall_qc_score_pct": qc["overall_qc_score_pct"],
    "score_by_dimension": qc["score_by_dimension"],
}
with open("results/summary.json", "w") as f:
    json.dump(summary, f, indent=2)

print("\n=== Summary ===")
print(json.dumps(summary, indent=2))
