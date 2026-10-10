"""Generates the 25+ tables and listings, as real .rtf files, from the
simulated ADaM datasets -- this is the executed Python mirror of the
authored SAS programs in sas/ (SAS itself is not available in this
environment; see README for the honest disclosure).
"""
from __future__ import annotations

import os

import pandas as pd

from .rtf_writer import write_rtf_table
from .simulate_trial_data import VISITS, SOC_PT

TRT_LABELS = {1: "Treatment A", 2: "Treatment B", 3: "Placebo"}


def _n_by_trt(adsl: pd.DataFrame) -> dict:
    return adsl.groupby("trt01pn").size().to_dict()


def table_demographics(data: dict, outdir: str) -> str:
    adsl = data["adsl"]
    n_by_trt = _n_by_trt(adsl)
    rows = []
    for stat, fn in [("Age, mean (SD)", lambda g: f"{g['age'].mean():.1f} ({g['age'].std():.1f})"),
                      ("Age, median", lambda g: f"{g['age'].median():.1f}"),
                      ("Male, n (%)", lambda g: f"{(g['sexn'] == 1).sum()} ({100 * (g['sexn'] == 1).mean():.1f}%)"),
                      ("Female, n (%)", lambda g: f"{(g['sexn'] == 2).sum()} ({100 * (g['sexn'] == 2).mean():.1f}%)")]:
        row = [stat] + [fn(adsl[adsl.trt01pn == t]) for t in (1, 2, 3)]
        rows.append(row)

    path = os.path.join(outdir, "t_14_1_1_demographics.rtf")
    write_rtf_table(
        path, titles=["Table 14.1.1", "Demographic and Baseline Characteristics", "Safety Population"],
        col_headers=["Characteristic", f"Treatment A (N={n_by_trt.get(1,0)})",
                     f"Treatment B (N={n_by_trt.get(2,0)})", f"Placebo (N={n_by_trt.get(3,0)})"],
        rows=rows, footnotes=["Program: table_demographics.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def table_disposition(data: dict, outdir: str) -> str:
    adsl = data["adsl"]
    n_by_trt = _n_by_trt(adsl)
    rows = []
    for stat, fn in [("Completed, n (%)", lambda g: f"{g['completer'].sum()} ({100*g['completer'].mean():.1f}%)"),
                      ("Discontinued, n (%)", lambda g: f"{(~g['completer']).sum()} ({100*(~g['completer']).mean():.1f}%)")]:
        rows.append([stat] + [fn(adsl[adsl.trt01pn == t]) for t in (1, 2, 3)])
    path = os.path.join(outdir, "t_14_1_2_disposition.rtf")
    write_rtf_table(
        path, titles=["Table 14.1.2", "Subject Disposition", "All Randomized Subjects"],
        col_headers=["Status", f"N={n_by_trt.get(1,0)}", f"N={n_by_trt.get(2,0)}", f"N={n_by_trt.get(3,0)}"],
        rows=rows, footnotes=["Program: table_disposition.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def table_ae_overview(data: dict, outdir: str) -> str:
    adae, adsl = data["adae"], data["adsl"]
    n_by_trt = _n_by_trt(adsl)
    categories = [
        ("Any TEAE", lambda d: d),
        ("Any serious TEAE", lambda d: d[d.aeseriousyn == "Y"]),
        ("TEAE leading to discontinuation", lambda d: d[d.aeactoffl == "Y"]),
    ]
    rows = []
    for label, filt in categories:
        row = [label]
        for t in (1, 2, 3):
            n_subj = filt(adae[adae.trt01pn == t])["usubjid"].nunique()
            pct = 100 * n_subj / n_by_trt.get(t, 1)
            row.append(f"{n_subj} ({pct:.1f}%)")
        rows.append(row)
    path = os.path.join(outdir, "t_14_3_1_ae_overview.rtf")
    write_rtf_table(
        path, titles=["Table 14.3.1", "Overview of Treatment-Emergent Adverse Events", "Safety Population"],
        col_headers=["Category", f"N={n_by_trt.get(1,0)}", f"N={n_by_trt.get(2,0)}", f"N={n_by_trt.get(3,0)}"],
        rows=rows, footnotes=["Program: table_ae_summary.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def table_ae_by_soc_pt(data: dict, outdir: str) -> str:
    adae, adsl = data["adae"], data["adsl"]
    n_by_trt = _n_by_trt(adsl)
    rows = []
    for soc, pts in SOC_PT.items():
        rows.append([soc, "", "", ""])
        for pt in pts:
            sub = adae[(adae.aesoc == soc) & (adae.aedecod == pt)]
            row = [f"  {pt}"]
            for t in (1, 2, 3):
                n_subj = sub[sub.trt01pn == t]["usubjid"].nunique()
                pct = 100 * n_subj / n_by_trt.get(t, 1)
                row.append(f"{n_subj} ({pct:.1f}%)")
            rows.append(row)
    path = os.path.join(outdir, "t_14_3_2_ae_by_soc_pt.rtf")
    write_rtf_table(
        path, titles=["Table 14.3.2", "TEAEs by System Organ Class and Preferred Term", "Safety Population"],
        col_headers=["SOC / Preferred Term", f"N={n_by_trt.get(1,0)}", f"N={n_by_trt.get(2,0)}", f"N={n_by_trt.get(3,0)}"],
        rows=rows, footnotes=["Program: table_ae_summary.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def table_vitals_by_visit(data: dict, outdir: str, visit: str) -> str:
    advs = data["advs"]
    sub = advs[(advs.avisit == visit) & (advs.paramcd == "SYSBP")]
    n_by_trt = sub.groupby("trt01pn")["usubjid"].nunique().to_dict()
    row = ["Systolic BP (mmHg), mean (SD)"]
    for t in (1, 2, 3):
        vals = sub[sub.trt01pn == t]["aval"]
        row.append(f"{vals.mean():.1f} ({vals.std():.1f})")
    path = os.path.join(outdir, f"t_14_4_vitals_{visit.replace(' ', '_').lower()}.rtf")
    write_rtf_table(
        path, titles=["Table 14.4.x", f"Vital Signs Summary - {visit}", "Safety Population"],
        col_headers=["Parameter", f"N={n_by_trt.get(1,0)}", f"N={n_by_trt.get(2,0)}", f"N={n_by_trt.get(3,0)}"],
        rows=[row], footnotes=["Program: table_vitals.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def table_labs_by_visit(data: dict, outdir: str, visit: str) -> str:
    adlb = data["adlb"]
    sub = adlb[(adlb.avisit == visit) & (adlb.paramcd == "ALT")]
    n_by_trt = sub.groupby("trt01pn")["usubjid"].nunique().to_dict()
    row = ["ALT (U/L), mean (SD)"]
    for t in (1, 2, 3):
        vals = sub[sub.trt01pn == t]["aval"]
        row.append(f"{vals.mean():.1f} ({vals.std():.1f})")
    path = os.path.join(outdir, f"t_14_5_labs_{visit.replace(' ', '_').lower()}.rtf")
    write_rtf_table(
        path, titles=["Table 14.5.x", f"Laboratory Summary (ALT) - {visit}", "Safety Population"],
        col_headers=["Parameter", f"N={n_by_trt.get(1,0)}", f"N={n_by_trt.get(2,0)}", f"N={n_by_trt.get(3,0)}"],
        rows=[row], footnotes=["Program: table_labs.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def table_vitals_change_from_baseline(data: dict, outdir: str, visit: str) -> str:
    advs = data["advs"]
    baseline = advs[(advs.avisit == "Baseline") & (advs.paramcd == "SYSBP")][["usubjid", "aval"]].rename(
        columns={"aval": "baseline_aval"}
    )
    post = advs[(advs.avisit == visit) & (advs.paramcd == "SYSBP")]
    merged = post.merge(baseline, on="usubjid")
    merged["chg"] = merged["aval"] - merged["baseline_aval"]
    n_by_trt = merged.groupby("trt01pn")["usubjid"].nunique().to_dict()
    row = ["Systolic BP change from baseline (mmHg), mean (SD)"]
    for t in (1, 2, 3):
        vals = merged[merged.trt01pn == t]["chg"]
        row.append(f"{vals.mean():.1f} ({vals.std():.1f})")
    path = os.path.join(outdir, f"t_14_4_vitals_chg_{visit.replace(' ', '_').lower()}.rtf")
    write_rtf_table(
        path, titles=["Table 14.4.y", f"Vital Signs Change from Baseline - {visit}", "Safety Population"],
        col_headers=["Parameter", f"N={n_by_trt.get(1,0)}", f"N={n_by_trt.get(2,0)}", f"N={n_by_trt.get(3,0)}"],
        rows=[row], footnotes=["Program: table_vitals_chg.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def listing(data: dict, outdir: str, name: str, df: pd.DataFrame, cols: list[str], title: str, number: str) -> str:
    rows = df[cols].astype(str).values.tolist() if len(df) else [["(no records)"] + [""] * (len(cols) - 1)]
    path = os.path.join(outdir, f"l_{number}_{name}.rtf")
    write_rtf_table(
        path, titles=[f"Listing {number}", title, "All Randomized Subjects"],
        col_headers=cols, rows=rows, footnotes=[f"Program: listing_{name}.sas (Python mirror: generate_tlfs.py)"],
    )
    return path


def generate_all(data: dict, outdir: str = "output/tlfs") -> list[str]:
    os.makedirs(outdir, exist_ok=True)
    paths = []

    paths.append(table_demographics(data, outdir))
    paths.append(table_disposition(data, outdir))
    paths.append(table_ae_overview(data, outdir))
    paths.append(table_ae_by_soc_pt(data, outdir))
    for visit in VISITS:
        paths.append(table_vitals_by_visit(data, outdir, visit))
        paths.append(table_labs_by_visit(data, outdir, visit))
    for visit in VISITS[1:]:
        paths.append(table_vitals_change_from_baseline(data, outdir, visit))

    adae = data["adae"]
    sae = adae[adae.aeseriousyn == "Y"]
    disc = adae[adae.aeactoffl == "Y"]
    adsl = data["adsl"]
    dc_subj = adsl[~adsl.completer]
    advs, adlb = data["advs"], data["adlb"]

    paths.append(listing(data, outdir, "all_ae", adae, ["usubjid", "trt01pn", "aesoc", "aedecod"],
                          "All Adverse Events", "16.2.1"))
    paths.append(listing(data, outdir, "sae", sae, ["usubjid", "trt01pn", "aesoc", "aedecod"],
                          "Serious Adverse Events", "16.2.2"))
    paths.append(listing(data, outdir, "ae_disc", disc, ["usubjid", "trt01pn", "aesoc", "aedecod"],
                          "AEs Leading to Discontinuation", "16.2.3"))
    paths.append(listing(data, outdir, "disposition", dc_subj, ["usubjid", "trt01pn", "age", "sexn"],
                          "Discontinued Subjects", "16.1.1"))
    paths.append(listing(data, outdir, "demographics", adsl, ["usubjid", "trt01pn", "age", "sexn", "racen"],
                          "Subject Demographics", "16.1.2"))
    paths.append(listing(data, outdir, "vitals_baseline", advs[advs.avisit == "Baseline"],
                          ["usubjid", "trt01pn", "avisit", "aval"], "Vital Signs at Baseline", "16.3.1"))
    paths.append(listing(data, outdir, "labs_week12", adlb[adlb.avisit == "Week 12"],
                          ["usubjid", "trt01pn", "avisit", "aval"], "Laboratory Results at Week 12", "16.3.2"))
    high_alt = adlb[(adlb.paramcd == "ALT") & (adlb.aval > 40)]
    paths.append(listing(data, outdir, "lab_abnormal", high_alt, ["usubjid", "trt01pn", "avisit", "aval"],
                          "Subjects with ALT > 40 U/L", "16.3.3"))
    paths.append(listing(data, outdir, "all_subjects", adsl, ["usubjid", "trt01pn", "completer"],
                          "All Randomized Subjects", "16.1.3"))
    paths.append(listing(data, outdir, "all_vitals", advs, ["usubjid", "trt01pn", "avisit", "aval"],
                          "All Vital Signs Records", "16.3.4"))

    return paths


if __name__ == "__main__":
    from .simulate_trial_data import simulate_all

    data = simulate_all()
    outputs = generate_all(data)
    print(f"{len(outputs)} tables and listings generated:")
    for p in outputs:
        print(" ", p)
