import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest

from src.simulate_trial_data import simulate_all
from src.generate_tlfs import generate_all
from src.qc_framework import run_full_framework


@pytest.fixture(scope="module")
def data():
    return simulate_all()


@pytest.fixture(scope="module")
def paths(data, tmp_path_factory):
    outdir = str(tmp_path_factory.mktemp("tlfs"))
    return generate_all(data, outdir=outdir)


def test_at_least_25_outputs_generated(paths):
    assert len(paths) >= 25


def test_all_outputs_are_valid_files(paths):
    for p in paths:
        assert os.path.exists(p)
        assert os.path.getsize(p) > 100


def test_all_outputs_are_valid_rtf(paths):
    for p in paths:
        with open(p) as f:
            content = f.read()
        assert content.startswith(r"{\rtf1")
        assert content.count("{") == content.count("}")


def test_qc_framework_has_exactly_45_checks(paths, data):
    result = run_full_framework(paths, data)
    assert result["n_checks"] == 45


def test_qc_framework_covers_five_dimensions(paths, data):
    result = run_full_framework(paths, data)
    assert set(result["score_by_dimension"].keys()) == {
        "Structural Integrity", "Content Accuracy", "Formatting Compliance",
        "Traceability", "Regulatory Readiness",
    }


def test_overall_qc_score_in_realistic_band(paths, data):
    result = run_full_framework(paths, data)
    assert 80.0 <= result["overall_qc_score_pct"] <= 100.0


def test_sas_source_programs_exist():
    sas_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "sas")
    sas_files = [f for f in os.listdir(sas_dir) if f.endswith(".sas")]
    assert len(sas_files) >= 2
