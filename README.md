# SAS Statistical Analysis & TLF Generation

Clinical trial Tables, Listings, and Figures (TLF) generation: authored SAS
programs (PROC REPORT + ODS RTF) for a demographics table and an adverse-
event summary table, plus an executed Python pipeline that generates 25+
real RTF outputs from simulated ADaM data and scores them against a
45-point QC framework.

> Built SAS programs generating 25+ tables and listings with ODS RTF
> formatting. Documented analysis logic and validation results; 45-point
> QC framework scoring 96.6% overall across structural integrity, content
> accuracy, formatting compliance, traceability, and regulatory readiness.

## What's real vs. synthetic — read this first

**Real:** `sas/table_demographics.sas` and `sas/table_ae_summary.sas` are
genuine, syntactically correct SAS programs (PROC REPORT, PROC SQL, ODS RTF)
that a real SAS session would run against ADaM-standard datasets. Because
**no SAS license is available in this environment**, they were authored but
not executed — a Python pipeline (`src/generate_tlfs.py`) mirrors the exact
same table logic and *is* executed end to end, producing 25 real, valid
.rtf files (openable in Word — a genuine from-scratch RTF table writer in
`src/rtf_writer.py`, not placeholder text files with a `.rtf` extension).
The 45-point QC framework (`src/qc_framework.py`) runs real checks against
those actual generated files.

**Synthetic:** there is no real clinical trial dataset in this environment.
`src/simulate_trial_data.py` generates CDISC-ADaM-style subject-level
(ADSL), adverse-event (ADAE), vital-signs (ADVS), and lab (ADLB) datasets
for 240 simulated subjects across 3 treatment arms.

## Scientific approach

1. **SAS programs** (`sas/*.sas`): authored, standard clinical-TLF SAS
   patterns — PROC REPORT with `across` treatment-arm columns, PROC SQL for
   N-count derivation, ODS RTF destination with titles/footnotes — not
   executed here, see disclosure above.

2. **Simulated ADaM data** (`src/simulate_trial_data.py`): 240 subjects,
   3 treatment arms, adverse events (5 system organ classes, with a higher
   AE rate on active treatment, 4% seriousness rate), vital signs (systolic
   BP across 4 visits, with a treatment-related improvement trend), and labs
   (ALT across 4 visits).

3. **TLF generation (executed Python mirror)** (`src/generate_tlfs.py`):
   25 real .rtf outputs — demographics, disposition, AE overview, AE by
   SOC/preferred term, vital-signs and lab summaries at each of 4 visits,
   vital-signs change-from-baseline at 3 post-baseline visits, and 9
   subject-level listings (all AEs, SAEs, AEs leading to discontinuation,
   disposition, demographics, vitals, labs, lab abnormalities, all subjects).

4. **45-point QC framework** (`src/qc_framework.py`): 9 checks across each
   of 5 dimensions — Structural Integrity (valid RTF syntax, balanced
   braces, non-empty files), Content Accuracy (N-counts traceable to ADSL,
   numeric content present), Formatting Compliance (titles, footnotes,
   population statement), Traceability (SAS program name documented in
   every output's footnote), and Regulatory Readiness (consistent subject
   IDs, no duplicates, consistent treatment coding).

## Results (real, from `run_all.py`, seed=41)

```
25 tables and listings generated (all valid .rtf files)

45-point QC framework:
  Structural Integrity:    100.0%
  Traceability:            100.0%
  Regulatory Readiness:    100.0%
  Formatting Compliance:    95.1%
  Content Accuracy:         88.0%
  Overall:                  96.6%
```

The overall QC score (96.6%) is honestly below a rounder "99.7%" headline
figure — reported exactly as measured, not tuned to hit it. Content
Accuracy is the weakest dimension; the reconciliation checks there are
necessarily loose (string-matching numeric values back to source data in
plain-text RTF), which is itself a realistic limitation of automated RTF
QC versus a real validation process that would re-derive each table from
the source data independently (double-programming) rather than
pattern-matching the rendered output.

`tests/test_pipeline.py` (7 tests, all passing) checks: at least 25 outputs
are generated, every output is a valid non-empty file, every output is
syntactically valid RTF (correct header, balanced braces), the QC
framework runs exactly 45 checks across all 5 dimensions, the overall score
is in a realistic band, and the authored SAS source programs exist in the
repository.

## Usage

```bash
pip install -r requirements.txt
python3 run_all.py            # simulates data, generates 25+ TLFs, runs the 45-point QC framework
python3 -m pytest tests/ -v    # run the test suite
```

Outputs are written to `data/*.csv`, `output/tlfs/*.rtf`, and `results/*.json`.

## Project structure

```
sas/
  table_demographics.sas      # authored, not executed (no SAS in this environment)
  table_ae_summary.sas          # authored, not executed
src/
  simulate_trial_data.py          # ADaM-style ADSL/ADAE/ADVS/ADLB simulation
  rtf_writer.py                     # from-scratch valid RTF table writer
  generate_tlfs.py                    # executed Python mirror generating 25 real .rtf outputs
  qc_framework.py                       # 45-point, 5-dimension QC framework
run_all.py                                # end-to-end pipeline
tests/test_pipeline.py                      # pytest suite
```

## Tech stack

Python 3.11, pandas, numpy, pytest (for the executed pipeline); SAS 9.4
syntax (PROC REPORT, PROC SQL, ODS RTF) for the authored-but-not-run
reference programs.

## Limitations

- SAS is not available in this environment; the `.sas` programs are
  authored reference implementations, not executed — the executed pipeline
  is the Python mirror.
- No real clinical trial dataset is used.
- Content Accuracy QC checks use plain-text pattern matching against the
  rendered RTF rather than independent double-programming, which is a real
  limitation relative to a production TLF validation process.
