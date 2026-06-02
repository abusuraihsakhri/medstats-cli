"""
medstats.metrics
~~~~~~~~~~~~~~~~
Pure-function calculations for all 2×2 contingency table diagnostic metrics.
Each function is intentionally standalone for testability and reuse.
"""

from __future__ import annotations
import math
from dataclasses import dataclass


@dataclass
class Table:
    """A 2×2 diagnostic contingency table.

    Attributes:
        tp: True Positives  — disease present, test positive
        fp: False Positives — disease absent,  test positive
        fn: False Negatives — disease present, test negative
        tn: True Negatives  — disease absent,  test negative
    """
    tp: float
    fp: float
    fn: float
    tn: float

    @property
    def total(self) -> float:
        return self.tp + self.fp + self.fn + self.tn

    @property
    def disease_positive(self) -> float:
        """Total with disease (condition positive)."""
        return self.tp + self.fn

    @property
    def disease_negative(self) -> float:
        """Total without disease (condition negative)."""
        return self.fp + self.tn

    @property
    def test_positive(self) -> float:
        return self.tp + self.fp

    @property
    def test_negative(self) -> float:
        return self.fn + self.tn

    @property
    def prevalence(self) -> float:
        return self.disease_positive / self.total if self.total else 0.0


@dataclass
class MetricResult:
    """A single computed metric with its value, interpretation, and derivation steps."""
    name: str
    abbreviation: str
    value: float | None
    formula: str
    interpretation: str
    teaching_steps: list[str]
    unit: str = ""
    warning: str = ""


def _safe_divide(numerator: float, denominator: float) -> float | None:
    """Return numerator/denominator, or None if denominator is zero."""
    if denominator == 0:
        return None
    return numerator / denominator


def sensitivity(t: Table) -> MetricResult:
    val = _safe_divide(t.tp, t.disease_positive)
    if val is None:
        interp = "Cannot compute — no disease-positive cases."
    elif val >= 0.90:
        interp = f"Excellent ({val:.1%}). A negative result effectively rules OUT the disease (SnNout mnemonic). Useful as a screening test."
    elif val >= 0.80:
        interp = f"Good ({val:.1%}). Most true cases are detected, but some are missed."
    elif val >= 0.60:
        interp = f"Moderate ({val:.1%}). A meaningful proportion of true cases are missed — consider as part of a diagnostic workup, not standalone."
    else:
        interp = f"Poor ({val:.1%}). Many true cases are missed. This test alone is insufficient to rule out disease."

    return MetricResult(
        name="Sensitivity",
        abbreviation="Sn",
        value=val,
        formula="TP / (TP + FN)",
        interpretation=interp,
        teaching_steps=[
            "Sensitivity asks: 'Of all people WITH the disease, how many did the test correctly identify?'",
            f"Disease-positive cases = TP + FN = {t.tp:.0f} + {t.fn:.0f} = {t.disease_positive:.0f}",
            f"Sensitivity = TP / (TP + FN) = {t.tp:.0f} / {t.disease_positive:.0f} = {val:.4f}" if val is not None else "Cannot compute.",
            "Memory aid: Sensitivity = 'PID' — Positive In Disease.",
            "High sensitivity → good for RULING OUT disease (SnNout).",
        ],
    )


def specificity(t: Table) -> MetricResult:
    val = _safe_divide(t.tn, t.disease_negative)
    if val is None:
        interp = "Cannot compute — no disease-negative cases."
    elif val >= 0.90:
        interp = f"Excellent ({val:.1%}). A positive result effectively rules IN the disease (SpPin mnemonic). Useful as a confirmatory test."
    elif val >= 0.80:
        interp = f"Good ({val:.1%}). Most healthy individuals are correctly identified as negative."
    elif val >= 0.60:
        interp = f"Moderate ({val:.1%}). Substantial false-positive rate — positive results need further confirmation."
    else:
        interp = f"Poor ({val:.1%}). High false-positive rate. Positive results are unreliable without confirmatory testing."

    return MetricResult(
        name="Specificity",
        abbreviation="Sp",
        value=val,
        formula="TN / (TN + FP)",
        interpretation=interp,
        teaching_steps=[
            "Specificity asks: 'Of all people WITHOUT the disease, how many did the test correctly identify as negative?'",
            f"Disease-negative cases = TN + FP = {t.tn:.0f} + {t.fp:.0f} = {t.disease_negative:.0f}",
            f"Specificity = TN / (TN + FP) = {t.tn:.0f} / {t.disease_negative:.0f} = {val:.4f}" if val is not None else "Cannot compute.",
            "Memory aid: Specificity = 'NIH' — Negative In Health.",
            "High specificity → good for RULING IN disease (SpPin).",
        ],
    )


def ppv(t: Table) -> MetricResult:
    val = _safe_divide(t.tp, t.test_positive)
    if val is None:
        interp = "Cannot compute — no test-positive cases."
    elif val >= 0.90:
        interp = f"Excellent ({val:.1%}). A positive test result is highly likely to represent true disease at this prevalence."
    elif val >= 0.70:
        interp = f"Good ({val:.1%}). Most positive results represent true disease, but confirmatory testing may be warranted."
    elif val >= 0.50:
        interp = f"Moderate ({val:.1%}). About half of positive results are false positives at this prevalence — interpret with caution."
    else:
        interp = f"Poor ({val:.1%}). Most positive results are false positives at this prevalence. High false-alarm rate."

    return MetricResult(
        name="Positive Predictive Value",
        abbreviation="PPV",
        value=val,
        formula="TP / (TP + FP)",
        interpretation=interp,
        teaching_steps=[
            "PPV asks: 'If a patient tests POSITIVE, what is the probability they truly have the disease?'",
            f"Test-positive cases = TP + FP = {t.tp:.0f} + {t.fp:.0f} = {t.test_positive:.0f}",
            f"PPV = TP / (TP + FP) = {t.tp:.0f} / {t.test_positive:.0f} = {val:.4f}" if val is not None else "Cannot compute.",
            "CRITICAL: PPV is heavily influenced by disease prevalence.",
            "The same test will have a lower PPV in a low-prevalence population (more false positives relative to true positives).",
        ],
    )


def npv(t: Table) -> MetricResult:
    val = _safe_divide(t.tn, t.test_negative)
    if val is None:
        interp = "Cannot compute — no test-negative cases."
    elif val >= 0.95:
        interp = f"Excellent ({val:.1%}). A negative result virtually rules out disease at this prevalence."
    elif val >= 0.85:
        interp = f"Good ({val:.1%}). A negative result is reassuring but not definitive."
    elif val >= 0.70:
        interp = f"Moderate ({val:.1%}). Meaningful false-negative rate — negative results should be interpreted in clinical context."
    else:
        interp = f"Poor ({val:.1%}). Many true disease cases would be missed. A negative result is not reassuring."

    return MetricResult(
        name="Negative Predictive Value",
        abbreviation="NPV",
        value=val,
        formula="TN / (TN + FN)",
        interpretation=interp,
        teaching_steps=[
            "NPV asks: 'If a patient tests NEGATIVE, what is the probability they truly do NOT have the disease?'",
            f"Test-negative cases = TN + FN = {t.tn:.0f} + {t.fn:.0f} = {t.test_negative:.0f}",
            f"NPV = TN / (TN + FN) = {t.tn:.0f} / {t.test_negative:.0f} = {val:.4f}" if val is not None else "Cannot compute.",
            "Like PPV, NPV varies with disease prevalence.",
            "NPV is HIGHER in low-prevalence settings (fewer true cases to miss).",
        ],
    )


def accuracy(t: Table) -> MetricResult:
    val = _safe_divide(t.tp + t.tn, t.total)
    if val is None:
        interp = "Cannot compute — no cases."
    elif val >= 0.90:
        interp = f"Excellent ({val:.1%}). The test correctly classifies the vast majority of subjects."
    elif val >= 0.80:
        interp = f"Good ({val:.1%}). Generally reliable, but consider performance in specific subgroups."
    else:
        interp = f"Suboptimal ({val:.1%}). Accuracy alone is misleading — check sensitivity/specificity separately, especially in imbalanced datasets."

    return MetricResult(
        name="Accuracy",
        abbreviation="Acc",
        value=val,
        formula="(TP + TN) / Total",
        interpretation=interp,
        teaching_steps=[
            "Accuracy = overall proportion of correct classifications.",
            f"Correct = TP + TN = {t.tp:.0f} + {t.tn:.0f} = {t.tp + t.tn:.0f}",
            f"Accuracy = {t.tp + t.tn:.0f} / {t.total:.0f} = {val:.4f}" if val is not None else "Cannot compute.",
            "WARNING: Accuracy is misleading when disease prevalence is very high or very low.",
            "Example: A test that always says 'negative' achieves 99% accuracy in a 1%-prevalence disease.",
        ],
    )


def lr_positive(t: Table) -> MetricResult:
    sn = _safe_divide(t.tp, t.disease_positive)
    sp = _safe_divide(t.tn, t.disease_negative)
    if sn is None or sp is None or sp == 1.0:
        val = None
        interp = "Cannot compute — insufficient data or specificity = 1.0."
    else:
        val = sn / (1 - sp)
        if val >= 10:
            interp = f"LR+ = {val:.2f}. Very strong positive shift. A positive test result makes disease ~{val:.0f}× more likely. Highly confirmatory."
        elif val >= 5:
            interp = f"LR+ = {val:.2f}. Moderate-strong positive shift. Substantially increases post-test probability."
        elif val >= 2:
            interp = f"LR+ = {val:.2f}. Weak-moderate positive shift. Some value but limited confirmatory power."
        else:
            interp = f"LR+ = {val:.2f}. Minimal positive shift. A positive result barely changes the probability of disease."

    return MetricResult(
        name="Positive Likelihood Ratio",
        abbreviation="LR+",
        value=val,
        formula="Sensitivity / (1 − Specificity)",
        interpretation=interp,
        teaching_steps=[
            "LR+ asks: 'How much more likely is a positive test result in someone WITH disease vs. WITHOUT?'",
            f"LR+ = Sensitivity / (1 − Specificity) = {sn:.4f} / (1 − {sp:.4f})" if (sn and sp) else "Cannot compute.",
            f"     = {sn:.4f} / {1 - sp:.4f} = {val:.4f}" if val is not None else "",
            "Interpretation guide: LR+ >10 = strong; 5–10 = moderate; 2–5 = weak; <2 = negligible.",
            "Use Fagan's nomogram to convert pre-test → post-test probability using LR+.",
        ],
    )


def lr_negative(t: Table) -> MetricResult:
    sn = _safe_divide(t.tp, t.disease_positive)
    sp = _safe_divide(t.tn, t.disease_negative)
    if sn is None or sp is None or sp == 0.0:
        val = None
        interp = "Cannot compute — insufficient data."
    else:
        val = (1 - sn) / sp
        if val <= 0.1:
            interp = f"LR− = {val:.3f}. Excellent. A negative test result makes disease ~{1/val:.0f}× less likely. Highly reassuring."
        elif val <= 0.2:
            interp = f"LR− = {val:.3f}. Good. A negative result substantially reduces post-test probability of disease."
        elif val <= 0.5:
            interp = f"LR− = {val:.3f}. Moderate. A negative result reduces disease probability somewhat."
        else:
            interp = f"LR− = {val:.3f}. Poor. A negative result barely rules out disease."

    return MetricResult(
        name="Negative Likelihood Ratio",
        abbreviation="LR−",
        value=val,
        formula="(1 − Sensitivity) / Specificity",
        interpretation=interp,
        teaching_steps=[
            "LR− asks: 'How much more likely is a negative test result in someone WITHOUT disease vs. WITH?'",
            f"LR− = (1 − Sensitivity) / Specificity = (1 − {sn:.4f}) / {sp:.4f}" if (sn and sp) else "Cannot compute.",
            f"     = {1 - sn:.4f} / {sp:.4f} = {val:.4f}" if val is not None else "",
            "Interpretation guide: LR− <0.1 = strong; 0.1–0.2 = moderate; 0.2–0.5 = weak; >0.5 = negligible.",
            "Lower LR− = better at ruling OUT disease.",
        ],
    )


def odds_ratio(t: Table) -> MetricResult:
    denom = t.fp * t.fn
    val = _safe_divide(t.tp * t.tn, denom)
    if val is None:
        interp = "Cannot compute — zero cell(s) in table."
    elif val >= 10:
        interp = f"OR = {val:.2f}. Strong association. Disease dramatically increases the odds of a positive test."
    elif val >= 3:
        interp = f"OR = {val:.2f}. Moderate association."
    elif val >= 1:
        interp = f"OR = {val:.2f}. Weak positive association."
    else:
        interp = f"OR = {val:.2f}. Negative association — test positive is less likely with disease (check data)."

    return MetricResult(
        name="Diagnostic Odds Ratio",
        abbreviation="DOR",
        value=val,
        formula="(TP × TN) / (FP × FN)",
        interpretation=interp,
        teaching_steps=[
            "DOR = single summary of overall test discriminative ability.",
            f"DOR = (TP × TN) / (FP × FN) = ({t.tp:.0f} × {t.tn:.0f}) / ({t.fp:.0f} × {t.fn:.0f})",
            f"    = {t.tp * t.tn:.0f} / {t.fp * t.fn:.0f} = {val:.4f}" if val is not None else "Cannot compute (zero cell).",
            "DOR = 1 means the test has no discriminative value.",
            "Note: DOR does not distinguish between high-sensitivity and high-specificity tests.",
        ],
    )


def relative_risk(t: Table) -> MetricResult:
    # RR of test-positive in disease-positive vs disease-negative
    risk_diseased = _safe_divide(t.tp, t.disease_positive)
    risk_healthy = _safe_divide(t.fp, t.disease_negative)
    val = _safe_divide(risk_diseased, risk_healthy) if (risk_diseased is not None and risk_healthy is not None) else None

    if val is None:
        interp = "Cannot compute — insufficient data."
    elif val >= 5:
        interp = f"RR = {val:.2f}. Disease is strongly associated with a positive test — {val:.1f}× more likely to test positive if diseased."
    elif val >= 2:
        interp = f"RR = {val:.2f}. Moderate association."
    elif val > 1:
        interp = f"RR = {val:.2f}. Weak positive association."
    else:
        interp = f"RR = {val:.2f}. No positive association (check data)."

    return MetricResult(
        name="Relative Risk",
        abbreviation="RR",
        value=val,
        formula="[TP/(TP+FN)] / [FP/(FP+TN)]",
        interpretation=interp,
        teaching_steps=[
            "RR here = risk of testing positive in disease-positive vs disease-negative groups.",
            f"Risk in diseased  = TP / (TP + FN) = {t.tp:.0f} / {t.disease_positive:.0f} = {risk_diseased:.4f}" if risk_diseased is not None else "",
            f"Risk in healthy   = FP / (FP + TN) = {t.fp:.0f} / {t.disease_negative:.0f} = {risk_healthy:.4f}" if risk_healthy is not None else "",
            f"RR = {risk_diseased:.4f} / {risk_healthy:.4f} = {val:.4f}" if val is not None else "Cannot compute.",
            "RR > 1 means testing positive is more common in diseased individuals — as expected for a good test.",
        ],
    )


def youden_index(t: Table) -> MetricResult:
    sn_r = sensitivity(t)
    sp_r = specificity(t)
    if sn_r.value is None or sp_r.value is None:
        val = None
        interp = "Cannot compute — missing sensitivity or specificity."
    else:
        val = sn_r.value + sp_r.value - 1
        if val >= 0.80:
            interp = f"J = {val:.3f}. Excellent overall discriminative performance."
        elif val >= 0.60:
            interp = f"J = {val:.3f}. Good overall performance."
        elif val >= 0.40:
            interp = f"J = {val:.3f}. Moderate — acceptable for screening but not confirmatory use."
        elif val > 0:
            interp = f"J = {val:.3f}. Poor — the test adds little diagnostic value over chance."
        else:
            interp = f"J = {val:.3f}. No value (≤ 0) — test performs no better than random."

    return MetricResult(
        name="Youden's Index",
        abbreviation="J",
        value=val,
        formula="Sensitivity + Specificity − 1",
        interpretation=interp,
        teaching_steps=[
            "Youden's J summarizes overall test performance on a 0–1 scale.",
            f"J = Sensitivity + Specificity − 1 = {sn_r.value:.4f} + {sp_r.value:.4f} − 1" if (sn_r.value and sp_r.value) else "",
            f"  = {val:.4f}" if val is not None else "Cannot compute.",
            "J = 0 → no discriminative value (like flipping a coin).",
            "J = 1 → perfect test (100% sensitivity AND 100% specificity).",
            "Youden's J is equivalent to the vertical distance from the ROC curve point to the diagonal chance line.",
        ],
    )


def f1_score(t: Table) -> MetricResult:
    p = _safe_divide(t.tp, t.test_positive)       # precision = PPV
    r = _safe_divide(t.tp, t.disease_positive)    # recall    = sensitivity
    val = _safe_divide(2 * p * r, p + r) if (p is not None and r is not None) else None

    if val is None:
        interp = "Cannot compute — zero denominator."
    elif val >= 0.90:
        interp = f"F1 = {val:.3f}. Excellent balance of precision (PPV) and recall (sensitivity)."
    elif val >= 0.75:
        interp = f"F1 = {val:.3f}. Good. Useful in imbalanced datasets where accuracy is misleading."
    else:
        interp = f"F1 = {val:.3f}. Suboptimal balance — check PPV and sensitivity individually."

    return MetricResult(
        name="F1 Score",
        abbreviation="F1",
        value=val,
        formula="2 × (PPV × Sensitivity) / (PPV + Sensitivity)",
        interpretation=interp,
        teaching_steps=[
            "F1 = harmonic mean of PPV (precision) and Sensitivity (recall).",
            f"PPV        = {p:.4f}" if p is not None else "PPV: cannot compute.",
            f"Sensitivity = {r:.4f}" if r is not None else "Sensitivity: cannot compute.",
            f"F1 = 2 × ({p:.4f} × {r:.4f}) / ({p:.4f} + {r:.4f}) = {val:.4f}" if val is not None else "Cannot compute.",
            "F1 = 1 is perfect; F1 = 0 is worst.",
            "Use F1 when you care equally about false positives and false negatives.",
        ],
    )


def auc_from_lr(t: Table) -> MetricResult:
    """
    Approximate AUC from LR+ and LR− using the formula:
    AUC ≈ (LR+ − 1) / (LR+ − LR−)   [Pepe 2003 approximation]
    More commonly: AUC = (Sensitivity + Specificity) / 2  (= balanced accuracy)
    We use the balanced accuracy as a conservative AUC estimate.
    """
    sn_r = sensitivity(t)
    sp_r = specificity(t)
    if sn_r.value is None or sp_r.value is None:
        val = None
        interp = "Cannot compute."
    else:
        val = (sn_r.value + sp_r.value) / 2
        if val >= 0.90:
            interp = f"AUC ≈ {val:.3f}. Excellent discrimination between diseased and healthy subjects."
        elif val >= 0.80:
            interp = f"AUC ≈ {val:.3f}. Good discrimination."
        elif val >= 0.70:
            interp = f"AUC ≈ {val:.3f}. Fair discrimination."
        elif val >= 0.60:
            interp = f"AUC ≈ {val:.3f}. Poor discrimination — marginal clinical utility."
        else:
            interp = f"AUC ≈ {val:.3f}. No discrimination — test is no better than chance."

    return MetricResult(
        name="AUC (balanced accuracy estimate)",
        abbreviation="AUC",
        value=val,
        formula="(Sensitivity + Specificity) / 2",
        interpretation=interp,
        warning="This is a single-threshold AUC estimate (balanced accuracy). True AUC requires full ROC curve data.",
        teaching_steps=[
            "True AUC requires data across all thresholds; from a 2×2 table we estimate it as balanced accuracy.",
            f"AUC ≈ (Sensitivity + Specificity) / 2 = ({sn_r.value:.4f} + {sp_r.value:.4f}) / 2" if (sn_r.value and sp_r.value) else "",
            f"    ≈ {val:.4f}" if val is not None else "Cannot compute.",
            "AUC = 0.5 → test is no better than random.",
            "AUC = 1.0 → perfect test.",
            "Standard thresholds: >0.9 excellent, 0.8–0.9 good, 0.7–0.8 fair, 0.6–0.7 poor, <0.6 fail.",
        ],
    )


def nnt(t: Table) -> MetricResult:
    """
    NNT in diagnostic context = number needed to test to detect one true positive.
    = 1 / (Sensitivity × Prevalence)
    """
    sn_r = sensitivity(t)
    prev = t.prevalence
    if sn_r.value is None or prev == 0:
        val = None
        interp = "Cannot compute — no disease cases or zero sensitivity."
    else:
        tp_rate = sn_r.value * prev   # proportion of all subjects who are true positives
        val = _safe_divide(1.0, tp_rate)
        if val is not None:
            interp = (
                f"NNT = {val:.1f}. On average, {val:.1f} patients must be tested to correctly identify "
                f"one true positive case at a prevalence of {prev:.1%}."
            )
        else:
            interp = "Cannot compute."

    return MetricResult(
        name="Number Needed to Test",
        abbreviation="NNT",
        value=val,
        formula="1 / (Sensitivity × Prevalence)",
        interpretation=interp,
        unit="patients",
        teaching_steps=[
            "NNT (diagnostic) = how many patients to test to find one true positive.",
            f"Prevalence = {prev:.4f} ({prev:.1%} of study population had disease)",
            f"Sensitivity = {sn_r.value:.4f}" if sn_r.value is not None else "",
            f"TP rate in population = Sensitivity × Prevalence = {sn_r.value:.4f} × {prev:.4f} = {sn_r.value * prev:.4f}" if sn_r.value else "",
            f"NNT = 1 / {sn_r.value * prev:.4f} = {val:.2f}" if val is not None else "Cannot compute.",
            "NNT depends heavily on prevalence — it rises steeply in low-prevalence settings.",
        ],
    )


def compute_all(t: Table) -> list[MetricResult]:
    """Compute all metrics for a given 2×2 table."""
    return [
        sensitivity(t),
        specificity(t),
        ppv(t),
        npv(t),
        accuracy(t),
        lr_positive(t),
        lr_negative(t),
        odds_ratio(t),
        relative_risk(t),
        youden_index(t),
        f1_score(t),
        auc_from_lr(t),
        nnt(t),
    ]
