"""
medstats.display
~~~~~~~~~~~~~~~~
Rich-powered terminal rendering for MedStats CLI output.
"""

from __future__ import annotations
from rich.console import Console
from rich.table import Table as RichTable
from rich.panel import Panel
from rich.text import Text
from rich.rule import Rule
from rich import box
from rich.columns import Columns
from rich.padding import Padding

from medstats.metrics import MetricResult, Table, compute_all

console = Console()


def _fmt_value(result: MetricResult) -> str:
    """Format a metric value for display."""
    if result.value is None:
        return "[dim]N/A[/dim]"
    # Percentage metrics
    pct_metrics = {"Sn", "Sp", "PPV", "NPV", "Acc", "AUC", "J", "F1"}
    if result.abbreviation in pct_metrics:
        return f"[bold]{result.value:.1%}[/bold]"
    elif result.abbreviation == "NNT":
        return f"[bold]{result.value:.1f}[/bold]"
    else:
        return f"[bold]{result.value:.3f}[/bold]"


def _value_color(result: MetricResult) -> str:
    """Assign a color based on metric value quality."""
    if result.value is None:
        return "dim"
    abbr = result.abbreviation
    v = result.value

    if abbr in ("Sn", "Sp", "PPV", "NPV", "Acc", "F1", "AUC", "J"):
        if v >= 0.85:
            return "green"
        elif v >= 0.70:
            return "yellow"
        else:
            return "red"
    elif abbr == "LR+":
        if v >= 10:
            return "green"
        elif v >= 5:
            return "yellow"
        else:
            return "red"
    elif abbr == "LR−":
        if v <= 0.1:
            return "green"
        elif v <= 0.2:
            return "yellow"
        else:
            return "red"
    elif abbr in ("DOR", "RR"):
        if v >= 5:
            return "green"
        elif v >= 2:
            return "yellow"
        else:
            return "red"
    return "white"


def render_table_summary(t: Table) -> None:
    """Print the 2×2 contingency table."""
    console.print()
    console.print(Rule("[bold cyan]2×2 Contingency Table[/bold cyan]", style="cyan"))
    console.print()

    grid = RichTable(box=box.ROUNDED, show_header=True, header_style="bold white on dark_blue")
    grid.add_column("", style="bold", width=20)
    grid.add_column("Test Positive (+)", justify="center", width=18)
    grid.add_column("Test Negative (−)", justify="center", width=18)
    grid.add_column("Total", justify="center", style="dim", width=12)

    grid.add_row(
        "[green]Disease Present[/green]",
        f"[green bold]TP = {t.tp:.0f}[/green bold]",
        f"[red]FN = {t.fn:.0f}[/red]",
        f"{t.disease_positive:.0f}",
    )
    grid.add_row(
        "[yellow]Disease Absent[/yellow]",
        f"[red]FP = {t.fp:.0f}[/red]",
        f"[green bold]TN = {t.tn:.0f}[/green bold]",
        f"{t.disease_negative:.0f}",
    )
    grid.add_row(
        "[dim]Total[/dim]",
        f"[dim]{t.test_positive:.0f}[/dim]",
        f"[dim]{t.test_negative:.0f}[/dim]",
        f"[bold]{t.total:.0f}[/bold]",
    )

    console.print(grid)
    console.print(
        f"  [dim]Prevalence: {t.prevalence:.1%}  |  "
        f"N = {t.total:.0f}  |  "
        f"TP={t.tp:.0f}  FP={t.fp:.0f}  FN={t.fn:.0f}  TN={t.tn:.0f}[/dim]"
    )
    console.print()


def render_results(results: list[MetricResult], teaching: bool = False) -> None:
    """Print all metric results in a rich table."""
    console.print(Rule("[bold cyan]Diagnostic Accuracy Metrics[/bold cyan]", style="cyan"))
    console.print()

    tbl = RichTable(
        box=box.SIMPLE_HEAVY,
        show_header=True,
        header_style="bold white",
        expand=True,
    )
    tbl.add_column("Metric", style="bold", min_width=30)
    tbl.add_column("Abbr", justify="center", width=6)
    tbl.add_column("Value", justify="center", width=12)
    tbl.add_column("Formula", style="dim italic", min_width=22)
    tbl.add_column("Interpretation", min_width=40)

    for r in results:
        color = _value_color(r)
        val_str = _fmt_value(r)
        warning_str = f"\n  [dim orange1]⚠ {r.warning}[/dim orange1]" if r.warning else ""
        interp_text = r.interpretation + warning_str

        tbl.add_row(
            r.name,
            f"[{color}]{r.abbreviation}[/{color}]",
            f"[{color}]{val_str}[/{color}]",
            r.formula,
            interp_text,
        )

    console.print(tbl)

    if teaching:
        render_teaching(results)


def render_teaching(results: list[MetricResult]) -> None:
    """Print step-by-step derivation for each metric."""
    console.print()
    console.print(Rule("[bold magenta]Teaching Mode — Step-by-Step Derivations[/bold magenta]", style="magenta"))

    for r in results:
        if not r.teaching_steps:
            continue
        console.print()
        header = Text(f"  {r.name} ({r.abbreviation})", style="bold underline magenta")
        console.print(header)
        for i, step in enumerate(r.teaching_steps, 1):
            if step:  # skip empty strings
                console.print(f"    [dim]{i}.[/dim] {step}")


def render_export_markdown(t: Table, results: list[MetricResult]) -> str:
    """Generate a markdown string of the full results table."""
    lines: list[str] = []
    lines.append("# MedStats CLI — Diagnostic Accuracy Report\n")
    lines.append("## 2×2 Contingency Table\n")
    lines.append("| | Test Positive | Test Negative | Total |")
    lines.append("|---|---|---|---|")
    lines.append(f"| **Disease Present** | TP = {t.tp:.0f} | FN = {t.fn:.0f} | {t.disease_positive:.0f} |")
    lines.append(f"| **Disease Absent**  | FP = {t.fp:.0f} | TN = {t.tn:.0f} | {t.disease_negative:.0f} |")
    lines.append(f"| **Total**           | {t.test_positive:.0f} | {t.test_negative:.0f} | {t.total:.0f} |")
    lines.append(f"\nPrevalence: {t.prevalence:.1%} | N = {t.total:.0f}\n")
    lines.append("\n## Metrics\n")
    lines.append("| Metric | Abbreviation | Value | Formula | Interpretation |")
    lines.append("|---|---|---|---|---|")
    for r in results:
        if r.value is not None:
            if r.abbreviation in ("Sn", "Sp", "PPV", "NPV", "Acc", "AUC", "J", "F1"):
                val_str = f"{r.value:.1%}"
            elif r.abbreviation == "NNT":
                val_str = f"{r.value:.1f}"
            else:
                val_str = f"{r.value:.3f}"
        else:
            val_str = "N/A"
        lines.append(f"| {r.name} | {r.abbreviation} | {val_str} | `{r.formula}` | {r.interpretation} |")

    lines.append("\n---")
    lines.append("*Generated by [MedStats CLI](https://github.com/your-username/medstats-cli)*")
    return "\n".join(lines)
