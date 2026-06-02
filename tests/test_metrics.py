"""
tests/test_metrics.py
~~~~~~~~~~~~~~~~~~~~~
Unit tests for medstats metric calculations.
Reference values computed by hand and cross-checked against established calculators.
"""

import pytest
from medstats.metrics import Table, compute_all
from medstats import metrics as m


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def standard_table() -> Table:
    """A well-balanced 2×2 table with known reference values."""
    return Table(tp=90, fp=10, fn=5, tn=95)


@pytest.fixture
def perfect_table() -> Table:
    return Table(tp=50, fp=0, fn=0, tn=50)


@pytest.fixture
def zero_fn_table() -> Table:
    """Sensitivity should be 1.0."""
    return Table(tp=100, fp=20, fn=0, tn=80)


@pytest.fixture
def zero_disease_table() -> Table:
    """No disease cases — sensitivity and NPV should be None."""
    return Table(tp=0, fp=10, fn=0, tn=90)


# ---------------------------------------------------------------------------
# Individual metric tests
# ---------------------------------------------------------------------------

class TestSensitivity:
    def test_standard(self, standard_table):
        r = m.sensitivity(standard_table)
        assert r.value == pytest.approx(90 / 95, rel=1e-4)

    def test_perfect(self, perfect_table):
        r = m.sensitivity(perfect_table)
        assert r.value == pytest.approx(1.0)

    def test_no_disease(self, zero_disease_table):
        r = m.sensitivity(zero_disease_table)
        assert r.value is None


class TestSpecificity:
    def test_standard(self, standard_table):
        r = m.specificity(standard_table)
        assert r.value == pytest.approx(95 / 105, rel=1e-4)

    def test_perfect(self, perfect_table):
        r = m.specificity(perfect_table)
        assert r.value == pytest.approx(1.0)


class TestPPV:
    def test_standard(self, standard_table):
        r = m.ppv(standard_table)
        assert r.value == pytest.approx(90 / 100, rel=1e-4)

    def test_no_test_positives(self):
        t = Table(tp=0, fp=0, fn=10, tn=90)
        r = m.ppv(t)
        assert r.value is None


class TestNPV:
    def test_standard(self, standard_table):
        r = m.npv(standard_table)
        assert r.value == pytest.approx(95 / 100, rel=1e-4)


class TestAccuracy:
    def test_standard(self, standard_table):
        r = m.accuracy(standard_table)
        assert r.value == pytest.approx(185 / 200, rel=1e-4)

    def test_perfect(self, perfect_table):
        r = m.accuracy(perfect_table)
        assert r.value == pytest.approx(1.0)


class TestLRPositive:
    def test_standard(self, standard_table):
        sn = 90 / 95
        sp = 95 / 105
        expected = sn / (1 - sp)
        r = m.lr_positive(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)

    def test_perfect_specificity(self, perfect_table):
        # sp = 1.0 → denominator = 0 → should be None
        r = m.lr_positive(perfect_table)
        assert r.value is None


class TestLRNegative:
    def test_standard(self, standard_table):
        sn = 90 / 95
        sp = 95 / 105
        expected = (1 - sn) / sp
        r = m.lr_negative(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)


class TestOddsRatio:
    def test_standard(self, standard_table):
        expected = (90 * 95) / (10 * 5)
        r = m.odds_ratio(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)

    def test_zero_cell(self):
        t = Table(tp=50, fp=0, fn=10, tn=40)
        r = m.odds_ratio(t)
        assert r.value is None


class TestYoudenIndex:
    def test_standard(self, standard_table):
        sn = 90 / 95
        sp = 95 / 105
        expected = sn + sp - 1
        r = m.youden_index(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)

    def test_perfect(self, perfect_table):
        r = m.youden_index(perfect_table)
        assert r.value == pytest.approx(1.0)


class TestF1:
    def test_standard(self, standard_table):
        ppv_val = 90 / 100
        sn_val = 90 / 95
        expected = 2 * ppv_val * sn_val / (ppv_val + sn_val)
        r = m.f1_score(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)


class TestAUC:
    def test_standard(self, standard_table):
        sn = 90 / 95
        sp = 95 / 105
        expected = (sn + sp) / 2
        r = m.auc_from_lr(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)


class TestNNT:
    def test_standard(self, standard_table):
        sn = 90 / 95
        prev = 95 / 200
        expected = 1 / (sn * prev)
        r = m.nnt(standard_table)
        assert r.value == pytest.approx(expected, rel=1e-4)


# ---------------------------------------------------------------------------
# Integration: compute_all returns 13 results
# ---------------------------------------------------------------------------

class TestComputeAll:
    def test_returns_all_metrics(self, standard_table):
        results = compute_all(standard_table)
        assert len(results) == 13

    def test_all_have_names(self, standard_table):
        for r in compute_all(standard_table):
            assert r.name
            assert r.abbreviation
            assert r.formula

    def test_all_have_teaching_steps(self, standard_table):
        for r in compute_all(standard_table):
            assert isinstance(r.teaching_steps, list)


# ---------------------------------------------------------------------------
# Table properties
# ---------------------------------------------------------------------------

class TestTableProperties:
    def test_prevalence(self, standard_table):
        assert standard_table.prevalence == pytest.approx(95 / 200)

    def test_totals(self, standard_table):
        assert standard_table.total == 200
        assert standard_table.disease_positive == 95
        assert standard_table.disease_negative == 105
        assert standard_table.test_positive == 100
        assert standard_table.test_negative == 100
