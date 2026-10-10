"""Simulate ADaM-style clinical trial analysis datasets (ADSL subject-level,
ADAE adverse events, ADVS vital signs, ADLB labs) for the TLF generation
pipeline. CDISC-ADaM-style naming conventions (USUBJID, TRT01PN, AESOC,
AEDECOD, PARAMCD, AVISIT, etc.) are used throughout, matching what a real
SAS TLF program would consume.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

N_SUBJECTS = 240
SEED = 41
VISITS = ["Baseline", "Week 4", "Week 8", "Week 12"]
SOC_PT = {
    "Gastrointestinal disorders": ["Nausea", "Diarrhoea", "Vomiting"],
    "Nervous system disorders": ["Headache", "Dizziness"],
    "General disorders": ["Fatigue", "Pyrexia"],
    "Skin disorders": ["Rash", "Pruritus"],
    "Infections": ["Nasopharyngitis", "Urinary tract infection"],
}


def simulate_adsl(n: int = N_SUBJECTS, seed: int = SEED) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    trt = rng.choice([1, 2, 3], n, p=[0.34, 0.33, 0.33])
    age = rng.normal(54, 13, n).clip(18, 85)
    sex = rng.choice([1, 2], n)  # 1=M, 2=F
    race = rng.choice([1, 2, 3, 4], n, p=[0.55, 0.20, 0.15, 0.10])  # White/Black/Asian/Other
    completers = rng.random(n) > np.where(trt == 3, 0.14, 0.09)  # placebo slightly higher dropout

    df = pd.DataFrame({
        "usubjid": [f"SUBJ-{i:04d}" for i in range(n)],
        "trt01pn": trt, "age": np.round(age, 1), "sexn": sex, "racen": race,
        "completer": completers,
        "saffl": "Y",
    })
    return df


def simulate_adae(adsl: pd.DataFrame, seed: int = SEED + 1) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    socs = list(SOC_PT.keys())
    for _, subj in adsl.iterrows():
        # higher AE rate on active treatments (realistic for this simulation)
        n_ae = rng.poisson(1.4 if subj["trt01pn"] in (1, 2) else 0.9)
        for _ in range(n_ae):
            soc = rng.choice(socs)
            pt = rng.choice(SOC_PT[soc])
            serious = rng.random() < 0.04
            led_to_discontinuation = serious and rng.random() < 0.3
            rows.append({
                "usubjid": subj["usubjid"], "trt01pn": subj["trt01pn"],
                "aesoc": soc, "aedecod": pt,
                "aeseriousyn": "Y" if serious else "N",
                "aeactoffl": "Y" if led_to_discontinuation else "N",
                "trtemfl": "Y",
            })
    return pd.DataFrame(rows)


def simulate_advs(adsl: pd.DataFrame, seed: int = SEED + 2) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _, subj in adsl.iterrows():
        baseline_sbp = rng.normal(130, 14)
        for v_idx, visit in enumerate(VISITS):
            drift = -2.5 * v_idx if subj["trt01pn"] in (1, 2) else -0.5 * v_idx
            sbp = baseline_sbp + drift + rng.normal(0, 6)
            rows.append({"usubjid": subj["usubjid"], "trt01pn": subj["trt01pn"],
                         "avisit": visit, "paramcd": "SYSBP", "aval": round(float(sbp), 1)})
    return pd.DataFrame(rows)


def simulate_adlb(adsl: pd.DataFrame, seed: int = SEED + 3) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    rows = []
    for _, subj in adsl.iterrows():
        baseline_alt = rng.normal(25, 8)
        for v_idx, visit in enumerate(VISITS):
            alt = max(5, baseline_alt + rng.normal(0, 5) + (1.5 * v_idx if subj["trt01pn"] != 3 else 0))
            rows.append({"usubjid": subj["usubjid"], "trt01pn": subj["trt01pn"],
                         "avisit": visit, "paramcd": "ALT", "aval": round(float(alt), 1)})
    return pd.DataFrame(rows)


def simulate_all(seed: int = SEED) -> dict:
    adsl = simulate_adsl(seed=seed)
    return {
        "adsl": adsl,
        "adae": simulate_adae(adsl, seed=seed + 1),
        "advs": simulate_advs(adsl, seed=seed + 2),
        "adlb": simulate_adlb(adsl, seed=seed + 3),
    }


if __name__ == "__main__":
    data = simulate_all()
    for name, df in data.items():
        print(name, df.shape)
