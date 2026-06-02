"""
medstats.cli
~~~~~~~~~~~~
Command-line interface for MedStats — diagnostic accuracy calculator.

Usage examples:
    medstats calc 90 10 5 95
    medstats calc --tp 90 --fp 10 --fn 5 --tn 95 --teaching
    medstats calc 90 10 5 95 --export results.md
    medstats interactive
"""

from __future__ import annotations

import typer
from pathlib import Path
from typing import Optional
from rich.console import Console
from rich.panel import Panel
from rich.prompt import IntPrompt
from rich import box

from medstats.metrics import Table, compute_all
from medstats.display import (
    render_table_summary,
    render_results,
    render_export_markdown,
    console,
)

app = typer.Typer(
    name="medstats",
    help="🩺 MedStats CLI — Diagnostic accuracy metrics from a 2×2 contingency table.",
    add_completion=False,
    rich_markup_mode="rich",
)


def _validate_positive(name: str, value: float) -> None:
    """Raise a user-friendly error if value is negative."""
    if value < 0:
        console.print(f"[red]Error:[/red] {name} cannot be negative. Got: {value}")
        raise typer.Exit(code=1)


def _run_analysis(
    tp: float,
    fp: float,
    fn: float,
    tn: float,
    teaching: bool,
    export: Optional[Path],
) -> None:
    """Core logic shared by `calc` and `interactive` commands."""
    for name, val in [("TP", tp), ("FP", fp), ("FN", fn), ("TN", tn)]:
        _validate_positive(name, val)

    if tp + fp + fn + tn == 0:
        console.print("[red]Error:[/red] All values are zero — nothing to compute.")
        raise typer.Exit(code=1)

    table = Table(tp=tp, fp=fp, fn=fn, tn=tn)
    results = compute_all(table)

    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]MedStats CLI[/bold cyan]  [dim]— Diagnostic Accuracy Calculator[/dim]",
            box=box.DOUBLE,
            border_style="cyan",
            padding=(0, 2),
        )
    )

    render_table_summary(table)
    render_results(results, teaching=teaching)

    if export:
        try:
            abs_export = export.resolve()
            cwd = Path.cwd().resolve()
            # Ensure the resolved path is within the current working directory
            if not str(abs_export).startswith(str(cwd)):
                console.print(f"\n[red]Security Error:[/red] Export path must be within the current directory to prevent traversal. Got: {abs_export}")
                raise typer.Exit(code=1)
        except Exception as e:
             console.print(f"\n[red]Error:[/red] Invalid file path: {e}")
             raise typer.Exit(code=1)

        md = render_export_markdown(table, results)
        abs_export.write_text(md, encoding="utf-8")
        console.print(f"\n[green]✓[/green] Results securely exported to [bold]{abs_export}[/bold]\n")


@app.command()
def calc(
    tp: float = typer.Argument(..., help="True Positives  (disease present, test positive)"),
    fp: float = typer.Argument(..., help="False Positives (disease absent,  test positive)"),
    fn: float = typer.Argument(..., help="False Negatives (disease present, test negative)"),
    tn: float = typer.Argument(..., help="True Negatives  (disease absent,  test negative)"),
    teaching: bool = typer.Option(
        False,
        "--teaching", "-t",
        help="Show step-by-step derivation for each metric.",
    ),
    export: Optional[Path] = typer.Option(
        None,
        "--export", "-e",
        help="Export results to a Markdown file (e.g. results.md).",
        writable=True,
    ),
) -> None:
    """
    Calculate diagnostic accuracy metrics from a 2×2 table.

    Provide four values in order: [bold]TP FP FN TN[/bold]

    \b
                     Test +    Test −
    Disease +  │  TP (a)  │  FN (c)  │
    Disease −  │  FP (b)  │  TN (d)  │

    [dim]Example:[/dim]  medstats calc 90 10 5 95
    """
    _run_analysis(tp, fp, fn, tn, teaching, export)


@app.command()
def interactive() -> None:
    """
    Enter values interactively with prompts (no arguments needed).
    """
    console.print()
    console.print(
        Panel.fit(
            "[bold cyan]MedStats CLI[/bold cyan]  [dim]— Interactive Mode[/dim]\n\n"
            "Enter your 2×2 table values below.\n"
            "[dim]TP = true positives | FP = false positives | FN = false negatives | TN = true negatives[/dim]",
            box=box.ROUNDED,
            border_style="cyan",
            padding=(1, 2),
        )
    )
    console.print()

    try:
        tp = float(IntPrompt.ask("  True Positives  (TP) — disease present, test positive"))
        fp = float(IntPrompt.ask("  False Positives (FP) — disease absent,  test positive"))
        fn = float(IntPrompt.ask("  False Negatives (FN) — disease present, test negative"))
        tn = float(IntPrompt.ask("  True Negatives  (TN) — disease absent,  test negative"))

        teaching = typer.confirm("\n  Show teaching mode (step-by-step derivations)?", default=False)
        export_str = typer.prompt(
            "  Export to Markdown file? (leave blank to skip)",
            default="",
            show_default=False,
        )
    except (KeyboardInterrupt, EOFError):
        console.print("\n\n[yellow]Operation cancelled by user. Exiting securely.[/yellow]")
        raise typer.Exit(code=0)

    export = Path(export_str) if export_str.strip() else None

    _run_analysis(tp, fp, fn, tn, teaching, export)


def main() -> None:
    app()


if __name__ == "__main__":
    main()
