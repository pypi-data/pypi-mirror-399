"""Command-line interface for Beacon."""

from pathlib import Path
from typing import Annotated

import typer
from rich.console import Console
from rich.table import Table

from beacon import __version__
from beacon.config import create_sample_config, load_config
from beacon.models import BenchmarkResult
from beacon.runner import run_benchmark

app = typer.Typer(
    name="beacon",
    help="RAG Chunking Strategy Benchmarking Toolkit",
    add_completion=False,
)
console = Console()


def version_callback(value: bool) -> None:
    """Print version and exit."""
    if value:
        console.print(f"beacon version {__version__}")
        raise typer.Exit()


@app.callback()
def main(
    version: Annotated[
        bool | None,
        typer.Option("--version", "-v", callback=version_callback, is_eager=True),
    ] = None,
) -> None:
    """Beacon - RAG Chunking Strategy Benchmarking Toolkit."""
    pass


@app.command()
def run(
    config: Annotated[
        Path,
        typer.Argument(help="Path to benchmark configuration file (YAML or JSON)"),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output directory for results"),
    ] = None,
    no_report: Annotated[
        bool,
        typer.Option("--no-report", help="Skip HTML report generation"),
    ] = False,
    quiet: Annotated[
        bool,
        typer.Option("--quiet", "-q", help="Suppress progress output"),
    ] = False,
) -> None:
    """Run a benchmark with the specified configuration."""
    console.print(f"[bold blue]Beacon[/bold blue] v{__version__}")
    console.print()

    # Load configuration
    try:
        benchmark_config = load_config(config)
    except Exception as e:
        console.print(f"[red]Error loading configuration:[/red] {e}")
        raise typer.Exit(1) from None

    # Override output directory if specified
    if output:
        benchmark_config.output_dir = output

    # Override report generation
    if no_report:
        benchmark_config.generate_html_report = False

    # Run benchmark
    console.print(f"[bold]Running benchmark:[/bold] {benchmark_config.name}")
    console.print(f"[dim]Documents:[/dim] {len(benchmark_config.documents)} files")
    console.print(f"[dim]Strategies:[/dim] {len(benchmark_config.strategies)}")
    console.print()

    try:
        result = run_benchmark(benchmark_config, verbose=not quiet)
    except Exception as e:
        console.print(f"[red]Error running benchmark:[/red] {e}")
        raise typer.Exit(1) from None

    # Display results
    display_results(result)

    console.print()
    console.print(f"[green]Results saved to:[/green] {benchmark_config.output_dir}")


@app.command()
def init(
    output: Annotated[
        Path,
        typer.Option("--output", "-o", help="Output path for sample config"),
    ] = Path("beacon.yaml"),
) -> None:
    """Create a sample configuration file."""
    if output.exists():
        overwrite = typer.confirm(f"{output} already exists. Overwrite?")
        if not overwrite:
            raise typer.Exit(0)

    create_sample_config(output)
    console.print(f"[green]Sample configuration created:[/green] {output}")
    console.print()
    console.print("Next steps:")
    console.print("  1. Edit the configuration file with your documents and queries")
    console.print("  2. Create a queries.jsonl file with your test queries")
    console.print("  3. Run: beacon run beacon.yaml")


@app.command()
def strategies() -> None:
    """List available chunking strategies."""
    table = Table(title="Available Chunking Strategies")
    table.add_column("Type", style="cyan")
    table.add_column("Description", style="white")
    table.add_column("Default Size", style="green")

    strategies_info = [
        ("fixed_size", "Split by fixed token/character count", "512 tokens"),
        ("sentence", "Split by sentence boundaries", "~512 tokens"),
        ("paragraph", "Split by paragraph boundaries", "~1024 tokens"),
        ("semantic", "Split by semantic similarity", "512 tokens"),
        ("recursive", "Recursively split with multiple separators", "512 tokens"),
    ]

    for strategy_type, description, default_size in strategies_info:
        table.add_row(strategy_type, description, default_size)

    console.print(table)
    console.print()
    console.print("[dim]Use 'beacon init' to create a config file with these strategies.[/dim]")


@app.command()
def compare(
    result_files: Annotated[
        list[Path],
        typer.Argument(help="Paths to benchmark result JSON files to compare"),
    ],
    output: Annotated[
        Path | None,
        typer.Option("--output", "-o", help="Output path for comparison report"),
    ] = None,
) -> None:
    """Compare results from multiple benchmark runs."""
    import json

    if len(result_files) < 2:
        console.print("[red]Please provide at least 2 result files to compare.[/red]")
        raise typer.Exit(1)

    results = []
    for result_file in result_files:
        if not result_file.exists():
            console.print(f"[red]File not found:[/red] {result_file}")
            raise typer.Exit(1)
        with open(result_file) as f:
            results.append(json.load(f))

    # Display comparison table
    table = Table(title="Benchmark Comparison")
    table.add_column("Benchmark", style="cyan")
    table.add_column("Best Strategy", style="green")
    table.add_column("MRR", justify="right")
    table.add_column("Recall@5", justify="right")
    table.add_column("NDCG@10", justify="right")

    for result in results:
        best = result.get("best_strategy", "N/A")
        # Find metrics for best strategy
        for sr in result.get("strategy_results", []):
            if sr["strategy"]["name"] == best:
                metrics = sr["metrics"]
                table.add_row(
                    result.get("config", {}).get("name", "Unknown"),
                    best,
                    f"{metrics.get('mrr', 0):.3f}",
                    f"{metrics.get('recall@5', 0):.3f}",
                    f"{metrics.get('ndcg@10', 0):.3f}",
                )
                break

    console.print(table)


def display_results(result: "BenchmarkResult") -> None:
    """Display benchmark results in a formatted table."""

    table = Table(title="Benchmark Results")
    table.add_column("Strategy", style="cyan")
    table.add_column("Chunks", justify="right")
    table.add_column("MRR", justify="right", style="green")
    table.add_column("R@1", justify="right")
    table.add_column("R@5", justify="right")
    table.add_column("R@10", justify="right")
    table.add_column("NDCG@10", justify="right")
    table.add_column("Latency", justify="right")

    for sr in result.strategy_results:
        is_best = sr.strategy.name == result.best_strategy
        style = "bold green" if is_best else None
        prefix = "★ " if is_best else "  "

        table.add_row(
            f"{prefix}{sr.strategy.name}",
            str(sr.metrics.num_chunks),
            f"{sr.metrics.mrr:.3f}",
            f"{sr.metrics.recall_at_1:.3f}",
            f"{sr.metrics.recall_at_5:.3f}",
            f"{sr.metrics.recall_at_10:.3f}",
            f"{sr.metrics.ndcg_at_10:.3f}",
            f"{sr.metrics.avg_latency_ms:.1f}ms",
            style=style,
        )

    console.print(table)
    console.print()
    console.print(f"[bold green]Best Strategy:[/bold green] {result.best_strategy}")
    console.print(f"[dim]{result.recommendation}[/dim]")


if __name__ == "__main__":
    app()
