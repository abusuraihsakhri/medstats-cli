# 🩺 MedStats CLI

> Diagnostic accuracy metrics from a 2×2 contingency table — with plain-English clinical interpretations.

[![Python 3.10+](https://img.shields.io/badge/python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)

Every clinician and med student has Googled "how to calculate sensitivity and specificity." Most calculators spit out numbers with zero explanation. **MedStats CLI** gives you all 13 diagnostic metrics, color-coded by quality, with plain-English interpretations for each — and an optional teaching mode that shows every derivation step.

---

## Features

- ✅ **13 metrics** — Sensitivity, Specificity, PPV, NPV, LR+, LR−, Accuracy, F1, Youden's J, DOR, RR, AUC (estimate), NNT
- 💬 **Plain-English interpretations** — not just numbers; tells you what each result *means* clinically
- 🎓 **Teaching mode** (`--teaching`) — step-by-step derivation for each metric
- 📄 **Markdown export** (`--export results.md`) — publication-ready table
- 🖥️ **Interactive mode** — guided prompts if you prefer not to use arguments
- 🎨 **Color-coded output** — green/yellow/red at a glance

---

## Installation

```bash
pip install medstats-cli
```

Or from source:

```bash
git clone https://github.com/your-username/medstats-cli
cd medstats-cli
pip install -e .
```

**Requirements:** Python 3.10+ | `typer` | `rich`

---

## Quick Start

Provide your 2×2 table values in order: **TP FP FN TN**

```
              Test +    Test −
Disease +  │  TP (a)  │  FN (c)  │
Disease −  │  FP (b)  │  TN (d)  │
```

```bash
medstats calc 90 10 5 95
```

### With teaching mode (step-by-step derivations)

```bash
medstats calc 90 10 5 95 --teaching
```

### Export results to Markdown

```bash
medstats calc 90 10 5 95 --export results.md
```

### Interactive mode (guided prompts)

```bash
medstats interactive
```

---

## Example Output

```
╔══════════════════════════════════════╗
║  MedStats CLI  — Diagnostic Accuracy Calculator  ║
╚══════════════════════════════════════╝

─────────────────── 2×2 Contingency Table ───────────────────

┌──────────────────┬──────────────────┬──────────────────┬──────────┐
│                  │  Test Positive   │  Test Negative   │  Total   │
├──────────────────┼──────────────────┼──────────────────┼──────────┤
│  Disease Present │  TP = 90         │  FN = 5          │  95      │
│  Disease Absent  │  FP = 10         │  TN = 95         │  105     │
│  Total           │  100             │  100             │  200     │
└──────────────────┴──────────────────┴──────────────────┴──────────┘
Prevalence: 47.5%  |  N = 200

───────────────── Diagnostic Accuracy Metrics ────────────────

  Metric                          Abbr    Value      Formula                 Interpretation
 ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
  Sensitivity                     Sn      94.7%      TP / (TP + FN)          Excellent. A negative result...
  Specificity                     Sp      90.5%      TN / (TN + FP)          Excellent. A positive result...
  Positive Predictive Value       PPV     90.0%      TP / (TP + FP)          Excellent. A positive test...
  Negative Predictive Value       NPV     95.0%      TN / (TN + FN)          Excellent. A negative result...
  Accuracy                        Acc     92.5%      (TP + TN) / Total       Excellent. Correctly classifies...
  Positive Likelihood Ratio       LR+     9.947      Sensitivity / (1-Sp)    LR+ = 9.95. Moderate-strong...
  Negative Likelihood Ratio       LR−     0.058      (1-Sn) / Specificity    LR− = 0.06. Excellent...
  Diagnostic Odds Ratio           DOR    171.000     (TP × TN) / (FP × FN)  Strong association...
  Relative Risk                   RR      9.947      [TP/(TP+FN)] / ...      Strong association...
  Youden's Index                  J       85.2%      Sn + Sp − 1             Excellent overall...
  F1 Score                        F1      92.3%      2×(PPV×Sn)/(PPV+Sn)    Excellent balance...
  AUC (balanced accuracy est.)    AUC     92.6%      (Sn + Sp) / 2          Excellent discrimination...
  Number Needed to Test           NNT     2.2        1 / (Sn × Prevalence)  2.2 patients to test...
```

---

## Metrics Reference

| Metric | Abbreviation | What it answers |
|--------|--------------|-----------------|
| Sensitivity | Sn | Of all with disease, how many test positive? |
| Specificity | Sp | Of all without disease, how many test negative? |
| Positive Predictive Value | PPV | If test is positive, how likely is disease? |
| Negative Predictive Value | NPV | If test is negative, how likely is no disease? |
| Accuracy | Acc | Overall proportion correctly classified |
| Positive Likelihood Ratio | LR+ | How much more likely is a positive in disease? |
| Negative Likelihood Ratio | LR− | How much more likely is a negative in no-disease? |
| Diagnostic Odds Ratio | DOR | Single summary of overall discriminative ability |
| Relative Risk | RR | Risk of testing positive: diseased vs healthy |
| Youden's Index | J | Combined Sn + Sp summary (0–1 scale) |
| F1 Score | F1 | Harmonic mean of PPV and Sensitivity |
| AUC estimate | AUC | Balanced accuracy (single-threshold estimate) |
| Number Needed to Test | NNT | Patients tested to detect one true positive |

> **Note on AUC:** This tool estimates AUC as `(Sensitivity + Specificity) / 2` (balanced accuracy). A full AUC requires ROC curve data across all thresholds. The warning is always shown in output.

---

## Teaching Mode

Run with `--teaching` to see step-by-step derivations like this:

```
Sensitivity (Sn)
  1. Sensitivity asks: 'Of all people WITH the disease, how many did the test correctly identify?'
  2. Disease-positive cases = TP + FN = 90 + 5 = 95
  3. Sensitivity = TP / (TP + FN) = 90 / 95 = 0.9474
  4. Memory aid: Sensitivity = 'PID' — Positive In Disease.
  5. High sensitivity → good for RULING OUT disease (SnNout).
```

---

## Project Structure

```
medstats-cli/
├── medstats/
│   ├── __init__.py
│   ├── cli.py          # Typer CLI entry point
│   ├── metrics.py      # Pure metric functions (no I/O)
│   └── display.py      # Rich terminal rendering
├── tests/
│   └── test_metrics.py
├── pyproject.toml
└── README.md
```

---

## Running Tests

```bash
pip install pytest
pytest tests/
```

---

## Contributing

Contributions welcome. Ideas for future versions:
- `--prevalence` flag to adjust PPV/NPV for a different population prevalence
- Fagan's nomogram ASCII art
- Batch mode: process multiple 2×2 tables from a CSV
- Confidence intervals (Wilson score) for each metric

---

## License

MIT — see [LICENSE](LICENSE)

---

*Built by Dr. Abu Suraih Sakhri · Part of the MedStats open-source toolkit*
