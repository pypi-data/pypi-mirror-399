"""Main CLI application for n8n-flow-manager."""

import asyncio
import json
from pathlib import Path
from typing import List, Optional

import typer
from rich import print as rprint
from rich.console import Console
from rich.progress import Progress, SpinnerColumn, TextColumn
from rich.table import Table

from ..client import N8NClient
from ..exceptions import N8NError
from ..utils.templating import load_workflow_from_file, save_workflow_to_file

app = typer.Typer(
    name="n8n-py",
    help="🚀 n8n-flow-manager: DevOps CLI for n8n workflow automation",
    add_completion=False,
)
console = Console()


def get_client(
    api_key: Optional[str] = None,
    base_url: Optional[str] = None,
) -> N8NClient:
    """Create and return an N8N client instance."""
    return N8NClient(api_key=api_key, base_url=base_url)


@app.command()
def list_workflows(
    active: Optional[bool] = typer.Option(None, "--active", help="Filter by active status"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    List all workflows from n8n instance.
    """

    async def _list() -> None:
        try:
            async with get_client(api_key, base_url) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task(description="Fetching workflows...", total=None)
                    workflows = await client.workflows.list(active=active)

                if not workflows:
                    console.print("[yellow]No workflows found.[/yellow]")
                    return

                table = Table(title=f"Workflows ({len(workflows)} found)")
                table.add_column("ID", style="cyan")
                table.add_column("Name", style="green")
                table.add_column("Active", style="magenta")
                table.add_column("Nodes", style="blue")

                for wf in workflows:
                    table.add_row(
                        wf.id or "N/A",
                        wf.name,
                        "✓" if wf.active else "✗",
                        str(len(wf.nodes)),
                    )

                console.print(table)

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_list())


@app.command()
def get_workflow(
    workflow_id: str = typer.Argument(..., help="Workflow ID"),
    output: Optional[Path] = typer.Option(None, "--output", help="Save to file"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Get a specific workflow by ID.
    """

    async def _get() -> None:
        try:
            async with get_client(api_key, base_url) as client:
                workflow = await client.workflows.get(workflow_id)

                if output:
                    save_workflow_to_file(workflow, output)
                    console.print(f"[green]✓ Workflow saved to {output}[/green]")
                else:
                    rprint(workflow.model_dump(by_alias=True, exclude_none=True))

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_get())


@app.command()
def deploy(
    file: Path = typer.Argument(..., help="Workflow JSON file", exists=True),
    variables: Optional[List[str]] = typer.Option(
        None,
        "--var",
        help="Template variables (format: key=value)",
    ),
    activate: bool = typer.Option(False, "--activate", help="Activate after deployment"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Deploy a workflow from a JSON file (supports Jinja2 templates).
    """

    async def _deploy() -> None:
        try:
            # Parse variables
            vars_dict = {}
            if variables:
                for var in variables:
                    if "=" not in var:
                        console.print(f"[red]Invalid variable format: {var}[/red]")
                        raise typer.Exit(code=1)
                    key, value = var.split("=", 1)
                    vars_dict[key.strip()] = value.strip()

            # Load workflow
            console.print(f"[blue]Loading workflow from {file}...[/blue]")
            workflow = load_workflow_from_file(file, vars_dict if vars_dict else None)

            async with get_client(api_key, base_url) as client:
                # Create workflow
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task(description="Deploying workflow...", total=None)
                    created = await client.workflows.create(workflow)

                console.print(
                    f"[green]✓ Workflow deployed successfully![/green]\n"
                    f"  ID: {created.id}\n"
                    f"  Name: {created.name}"
                )

                # Activate if requested
                if activate:
                    await client.workflows.activate(created.id)  # type: ignore
                    console.print("[green]✓ Workflow activated[/green]")

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)
        except Exception as e:
            console.print(f"[red]Error: {str(e)}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_deploy())


@app.command()
def backup(
    output_dir: Path = typer.Option(
        "./backups",
        "--output",
        help="Output directory for backups",
    ),
    active_only: bool = typer.Option(False, "--active-only", help="Backup only active workflows"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Backup all workflows to local directory.
    """

    async def _backup() -> None:
        try:
            output_dir.mkdir(parents=True, exist_ok=True)

            async with get_client(api_key, base_url) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    task = progress.add_task(description="Fetching workflows...", total=None)
                    workflows = await client.workflows.list(active=active_only or None)
                    progress.update(task, completed=True)

                if not workflows:
                    console.print("[yellow]No workflows to backup.[/yellow]")
                    return

                console.print(f"[blue]Backing up {len(workflows)} workflows...[/blue]")

                for workflow in workflows:
                    # Sanitize filename
                    safe_name = "".join(
                        c if c.isalnum() or c in ("-", "_") else "_" for c in workflow.name
                    )
                    filename = f"{workflow.id}_{safe_name}.json"
                    filepath = output_dir / filename

                    save_workflow_to_file(workflow, filepath)
                    console.print(f"  [green]✓[/green] {workflow.name} → {filename}")

                console.print(
                    f"\n[green]✓ Successfully backed up {len(workflows)} workflows to {output_dir}[/green]"
                )

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_backup())


@app.command()
def execute(
    workflow_id: str = typer.Argument(..., help="Workflow ID to execute"),
    wait: bool = typer.Option(True, "--wait/--no-wait", help="Wait for execution to complete"),
    timeout: int = typer.Option(300, "--timeout", help="Execution timeout in seconds"),
    input_file: Optional[Path] = typer.Option(
        None,
        "--input",
        help="Input data JSON file",
    ),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Execute a workflow by ID.
    """

    async def _execute() -> None:
        try:
            # Load input data if provided
            input_data = None
            if input_file:
                with open(input_file) as f:
                    input_data = json.load(f)

            async with get_client(api_key, base_url) as client:
                console.print(f"[blue]Executing workflow {workflow_id}...[/blue]")

                if wait:
                    with Progress(
                        SpinnerColumn(),
                        TextColumn("[progress.description]{task.description}"),
                        console=console,
                    ) as progress:
                        progress.add_task(
                            description="Waiting for execution to complete...", total=None
                        )
                        execution = await client.executions.run_and_wait(
                            workflow_id,
                            input_data=input_data,
                            timeout=timeout,
                        )

                    console.print("\n[green]✓ Execution completed![/green]")
                    console.print(f"  Execution ID: {execution.id}")
                    console.print(f"  Status: {execution.status}")
                    console.print(f"  Finished: {execution.finished}")

                    if execution.is_successful:
                        console.print("[green]  Result: Success ✓[/green]")
                    elif execution.is_failed:
                        console.print("[red]  Result: Failed ✗[/red]")

                else:
                    execution = await client.executions.trigger_workflow(
                        workflow_id, input_data=input_data
                    )
                    console.print(
                        f"[green]✓ Workflow triggered![/green]\n" f"  Execution ID: {execution.id}"
                    )

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_execute())


@app.command()
def activate(
    workflow_id: str = typer.Argument(..., help="Workflow ID to activate"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Activate a workflow.
    """

    async def _activate() -> None:
        try:
            async with get_client(api_key, base_url) as client:
                workflow = await client.workflows.activate(workflow_id)
                console.print(f"[green]✓ Workflow '{workflow.name}' activated[/green]")

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_activate())


@app.command()
def deactivate(
    workflow_id: str = typer.Argument(..., help="Workflow ID to deactivate"),
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Deactivate a workflow.
    """

    async def _deactivate() -> None:
        try:
            async with get_client(api_key, base_url) as client:
                workflow = await client.workflows.deactivate(workflow_id)
                console.print(f"[green]✓ Workflow '{workflow.name}' deactivated[/green]")

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_deactivate())


@app.command()
def health(
    api_key: Optional[str] = typer.Option(None, "--api-key", envvar="N8N_API_KEY"),
    base_url: Optional[str] = typer.Option(None, "--base-url", envvar="N8N_BASE_URL"),
) -> None:
    """
    Check n8n API connection health.
    """

    async def _health() -> None:
        try:
            async with get_client(api_key, base_url) as client:
                with Progress(
                    SpinnerColumn(),
                    TextColumn("[progress.description]{task.description}"),
                    console=console,
                ) as progress:
                    progress.add_task(description="Checking connection...", total=None)
                    healthy = await client.health_check()

                if healthy:
                    console.print("[green]✓ Connection healthy![/green]")
                    console.print(f"  API URL: {client.base_url}")
                else:
                    console.print("[red]✗ Connection failed[/red]")
                    raise typer.Exit(code=1)

        except N8NError as e:
            console.print(f"[red]Error: {e.message}[/red]")
            raise typer.Exit(code=1)

    asyncio.run(_health())


if __name__ == "__main__":
    app()
