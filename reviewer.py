import os
import sys
from pathlib import Path
import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn
from google import genai
from google.genai import types

from schemas import CodeReviewReport

app = typer.Typer(help="Code Reviewer & Bug Explainer CLI")
console = Console()


def extract_text(file_path: str) -> str:
    path = Path(file_path)
    if not path.exists():
        console.print(f"[bold red]Error: File not found -> {file_path}[/bold red]")
        raise typer.Exit(1)

    try:
        return path.read_text(encoding="utf-8")
    except Exception as e:
        console.print(f"[bold red]Failed to read file: {e}[/bold red]")
        raise typer.Exit(1)


@app.command()
def review(
    diff_input: str = typer.Argument(
        ...,
        help="Path to diff file (e.g., git diff output text file) or raw diff string",
    ),
):
    """Analyze a code diff or patch file, identify bugs, code smells, and provide refactoring suggestions."""

    if not os.environ.get("GEMINI_API_KEY"):
        console.print(
            "[bold red]Error: GEMINI_API_KEY environment variable is not set.[/bold red]"
        )
        raise typer.Exit(1)

    # Handle input being a file path or inline text
    if Path(diff_input).exists():
        diff_text = extract_text(diff_input)
    else:
        diff_text = diff_input

    client = genai.Client()

    prompt = f"""
You are an expert principal software engineer and automated code reviewer. 
Analyze the following code diff or patch. Identify logical bugs, security vulnerabilities, performance anti-patterns, and code smells. Provide a structured review report with code health score, detected issues, and refactored code suggestions.

=== CODE DIFF / PATCH ===
{diff_text}
"""

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        transient=True,
    ) as progress:
        progress.add_task(
            description="Reviewing code diff & analyzing patterns with Gemini...",
            total=None,
        )

        try:
            # Temporarily suppress stderr to keep terminal output clean
            original_stderr = sys.stderr
            sys.stderr = open(os.devnull, "w")
            try:
                response = client.models.generate_content(
                    model="gemini-2.5-flash",
                    contents=prompt,
                    config=types.GenerateContentConfig(
                        response_mime_type="application/json",
                        response_schema=CodeReviewReport,
                        temperature=0.1,
                    ),
                )
            finally:
                sys.stderr.close()
                sys.stderr = original_stderr

            result = CodeReviewReport.model_validate_json(response.text)
        except Exception as e:
            console.print(f"[bold red]Code review failed: {e}[/bold red]")
            raise typer.Exit(1)

    # Render Dashboard using Rich
    console.print("\n")
    console.print(
        Panel.fit(
            f"[bold cyan]🔍 Code Review & Bug Explainer Report[/bold cyan]",
            title="AI Code Reviewer",
            border_style="cyan",
        )
    )

    # Health Score Table
    score_table = Table(show_header=True, header_style="bold magenta")
    score_table.add_column("Review Metric", style="dim")
    score_table.add_column("Score / Status", justify="right")

    score_color = (
        "green"
        if result.overall_health_score >= 80
        else ("yellow" if result.overall_health_score >= 50 else "red")
    )
    score_table.add_row(
        "Code Health Score",
        f"[{score_color} bold]{result.overall_health_score}/100[/{score_color} bold]",
    )
    score_table.add_row("Total Issues Detected", str(len(result.issues)))
    console.print(score_table)

    # Executive Summary Panel
    console.print(
        Panel(
            result.summary,
            title="[bold yellow]📋 Executive Summary[/bold yellow]",
            border_style="yellow",
        )
    )

    # Issues Breakdown
    if result.issues:
        console.print("\n[bold red]🚨 Detected Issues & Bug Explanations:[/bold red]")
        for idx, issue in enumerate(result.issues, 1):
            sev_color = (
                "red"
                if issue.severity.lower() == "critical"
                else ("yellow" if issue.severity.lower() == "warning" else "blue")
            )
            issue_panel_text = f"[bold]Type:[/bold] {issue.issue_type}\n[bold]Approx. Line:[/bold] {issue.line_number_approximate or 'N/A'}\n\n{issue.description}"
            console.print(
                Panel(
                    issue_panel_text,
                    title=f"[{sev_color}]Issue #{idx} [{issue.severity}][/{sev_color}]",
                    border_style=sev_color,
                )
            )

    # Refactoring Suggestions
    if result.refactorings:
        console.print(
            "\n[bold green]💡 Refactoring Suggestions & Improved Code:[/bold green]"
        )
        for idx, ref in enumerate(result.refactorings, 1):
            ref_syntax = Syntax(
                ref.improved_code, "python", theme="monokai", line_numbers=True
            )
            ref_content = f"[bold]Rationale:[/bold] {ref.rationale}\n\n"
            console.print(
                Panel(
                    ref_content,
                    title=f"[green]Refactor #{idx}: {ref.title}[/green]",
                    border_style="green",
                )
            )
            console.print(
                Panel(
                    ref_syntax,
                    title="[yellow]Suggested Code Patch[/yellow]",
                    border_style="yellow",
                )
            )

    console.print("\n")


if __name__ == "__main__":
    app()
