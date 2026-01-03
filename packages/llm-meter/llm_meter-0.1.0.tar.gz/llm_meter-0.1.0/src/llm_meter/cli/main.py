import asyncio
import csv
import io
import json
from datetime import datetime
from typing import Any

import typer
from pydantic import BaseModel
from rich.console import Console
from rich.table import Table

from llm_meter.storage import StorageManager
from llm_meter.storage.base import StorageEngine

app = typer.Typer(help="LLM Usage & Cost Tracking CLI")
usage_app = typer.Typer(help="Inspect LLM usage data")
app.add_typer(usage_app, name="usage")

console = Console()


class UsageExport(BaseModel):
    request_id: str
    endpoint: str | None
    user_id: str | None
    model: str
    provider: str
    total_tokens: int
    cost_estimate: float
    latency_ms: int
    timestamp: datetime


def get_storage(url: str) -> StorageEngine:
    return StorageManager(url)


@usage_app.command("summary")
def summary(
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s", help="Database URL"),
) -> None:
    """Show a high-level summary of LLM usage by model."""

    async def run() -> list[dict[str, Any]]:
        storage = get_storage(storage_url)
        data = await storage.get_usage_summary()
        await storage.close()
        return data

    data = asyncio.run(run())

    if not data:
        console.print("[yellow]No usage data found.[/yellow]")
        return

    table = Table(title="LLM Usage Summary")
    table.add_column("Model", style="cyan")
    table.add_column("Total Tokens", justify="right")
    table.add_column("Est. Cost ($)", justify="right", style="green")
    table.add_column("Call Count", justify="right")

    for row in data:
        table.add_row(str(row["model"]), f"{row['total_tokens']:,}", f"{row['total_cost']:.6f}", str(row["call_count"]))

    console.print(table)


@usage_app.command("by-endpoint")
def by_endpoint(
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s", help="Database URL"),
) -> None:
    """Show LLM usage aggregated by endpoint."""

    async def run() -> list[dict[str, Any]]:
        storage = get_storage(storage_url)
        data = await storage.get_usage_by_endpoint()
        await storage.close()
        return data

    data = asyncio.run(run())

    if not data:
        console.print("[yellow]No usage data found.[/yellow]")
        return

    table = Table(title="Usage by Endpoint")
    table.add_column("Endpoint", style="cyan")
    table.add_column("Total Tokens", justify="right")
    table.add_column("Est. Cost ($)", justify="right", style="green")

    for row in data:
        table.add_row(str(row["endpoint"] or "N/A"), f"{row['total_tokens']:,}", f"{row['total_cost']:.6f}")

    console.print(table)


@app.command("export")
def export(
    format: str = typer.Option("json", "--format", "-f", help="Export format (json, csv)"),
    output: str | None = typer.Option(None, "--output", "-o", help="Output file path"),
    storage_url: str = typer.Option("sqlite+aiosqlite:///llm_usage.db", "--storage-url", "-s", help="Database URL"),
) -> None:
    """Export raw usage data."""

    async def run() -> list[UsageExport]:
        storage = get_storage(storage_url)
        all_usage = await storage.get_all_usage()
        # Convert SQLAlchemy objects to Pydantic models
        rows = [UsageExport.model_validate(u, from_attributes=True) for u in all_usage]
        await storage.close()
        return rows

    data: list[UsageExport] = asyncio.run(run())

    if not data:
        console.print("[yellow]No data to export.[/yellow]")
        return

    if format == "json":
        # Serialize list of models to JSON
        json_content = json.dumps([row.model_dump(mode="json") for row in data], indent=2)
        if output:
            with open(output, "w") as f:
                f.write(json_content)
            console.print(f"[green]Data exported to {output}[/green]")
        else:
            console.print(json_content)
    elif format == "csv":
        keys = list(UsageExport.model_fields.keys())
        if output:
            with open(output, "w", newline="") as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                # Use model_dump(mode='json') for CSV to handle datetime properly
                writer.writerows([row.model_dump(mode="json") for row in data])
            console.print(f"[green]Data exported to {output}[/green]")
        else:
            output_buffer = io.StringIO()
            writer = csv.DictWriter(output_buffer, fieldnames=keys)
            writer.writeheader()
            for row in data:
                writer.writerow(row.model_dump(mode="json"))
            console.print(output_buffer.getvalue())


if __name__ == "__main__":  # pragma: no cover
    app()
