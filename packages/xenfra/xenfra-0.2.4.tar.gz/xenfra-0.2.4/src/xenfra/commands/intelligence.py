"""
AI-powered intelligence commands for Xenfra CLI.
Includes smart initialization, deployment diagnosis, and codebase analysis.
"""
import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Confirm, Prompt
from rich.table import Table
from xenfra_sdk import XenfraClient
from xenfra_sdk.exceptions import XenfraAPIError, XenfraError
from xenfra_sdk.privacy import scrub_logs

from ..utils.auth import API_BASE_URL, get_auth_token
from ..utils.codebase import has_xenfra_config, scan_codebase
from ..utils.config import apply_patch, generate_xenfra_yaml, manual_prompt_for_config, read_xenfra_yaml

console = Console()


def get_client() -> XenfraClient:
    """Get authenticated SDK client."""
    token = get_auth_token()
    if not token:
        console.print("[bold red]Not logged in. Run 'xenfra login' first.[/bold red]")
        raise click.Abort()

    return XenfraClient(token=token, api_url=API_BASE_URL)


@click.command()
@click.option('--manual', is_flag=True, help='Skip AI detection, use interactive mode')
@click.option('--accept-all', is_flag=True, help='Accept AI suggestions without confirmation')
def init(manual, accept_all):
    """
    Initialize Xenfra configuration (AI-powered by default).

    Scans your codebase, detects framework and dependencies,
    and generates xenfra.yaml automatically.

    Use --manual to skip AI and configure interactively.
    Set XENFRA_NO_AI=1 environment variable to force manual mode globally.
    """
    # Check if config already exists
    if has_xenfra_config():
        console.print("[yellow]xenfra.yaml already exists.[/yellow]")
        if not Confirm.ask("Overwrite existing configuration?"):
            console.print("[dim]Cancelled.[/dim]")
            return

    # Check for XENFRA_NO_AI environment variable
    no_ai = os.environ.get('XENFRA_NO_AI', '0') == '1'
    if no_ai and not manual:
        console.print("[yellow]XENFRA_NO_AI is set. Using manual mode.[/yellow]")
        manual = True

    # Manual mode - interactive prompts
    if manual:
        console.print("[cyan]Manual configuration mode[/cyan]\n")
        try:
            filename = manual_prompt_for_config()
            console.print(f"\n[bold green]✓ xenfra.yaml created successfully![/bold green]")
            console.print(f"[dim]Run 'xenfra deploy' to deploy your project.[/dim]")
        except KeyboardInterrupt:
            console.print("\n[dim]Cancelled.[/dim]")
        except Exception as e:
            console.print(f"[bold red]Error: {e}[/bold red]")
        return

    # AI-powered detection (default)
    try:
        # Use context manager for SDK client
        with get_client() as client:
            # Scan codebase
            console.print("[cyan]Analyzing your codebase...[/cyan]")
            code_snippets = scan_codebase()

            if not code_snippets:
                console.print("[bold red]No code files found to analyze.[/bold red]")
                console.print("[dim]Make sure you're in a Python project directory.[/dim]")
                return

            console.print(f"[dim]Found {len(code_snippets)} files to analyze[/dim]")

            # Call Intelligence Service
            analysis = client.intelligence.analyze_codebase(code_snippets)

        # Display results
        console.print("\n[bold green]Analysis Complete![/bold green]\n")

        # Handle package manager conflict
        selected_package_manager = analysis.package_manager
        selected_dependency_file = analysis.dependency_file

        if analysis.has_conflict and analysis.detected_package_managers:
            console.print("[yellow]Multiple package managers detected![/yellow]\n")

            # Show options
            for i, option in enumerate(analysis.detected_package_managers, 1):
                console.print(f"  {i}. [cyan]{option.manager}[/cyan] ({option.file})")

            console.print(f"\n[dim]Recommended: {analysis.package_manager} (most modern)[/dim]")

            # Prompt user to select
            choice = Prompt.ask(
                "\nWhich package manager do you want to use?",
                choices=[str(i) for i in range(1, len(analysis.detected_package_managers) + 1)],
                default="1"
            )

            # Update selection based on user choice
            selected_option = analysis.detected_package_managers[int(choice) - 1]
            selected_package_manager = selected_option.manager
            selected_dependency_file = selected_option.file

            console.print(f"\n[green]Using {selected_package_manager} ({selected_dependency_file})[/green]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Framework", analysis.framework)
        table.add_row("Port", str(analysis.port))
        table.add_row("Database", analysis.database)
        if analysis.cache:
            table.add_row("Cache", analysis.cache)
        if analysis.workers:
            table.add_row("Workers", ", ".join(analysis.workers))
        table.add_row("Package Manager", selected_package_manager)
        table.add_row("Dependency File", selected_dependency_file)
        table.add_row("Instance Size", analysis.instance_size)
        table.add_row("Estimated Cost", f"${analysis.estimated_cost_monthly:.2f}/month")
        table.add_row("Confidence", f"{analysis.confidence:.0%}")

        console.print(Panel(table, title="[bold]Detected Configuration[/bold]"))

        if analysis.notes:
            console.print(f"\n[dim]{analysis.notes}[/dim]")

        # Confirm or edit
        if accept_all:
            confirmed = True
        else:
            confirmed = Confirm.ask("\nCreate xenfra.yaml with this configuration?", default=True)

        if confirmed:
            filename = generate_xenfra_yaml(analysis)
            console.print(f"[bold green]xenfra.yaml created successfully![/bold green]")
            console.print(f"[dim]Run 'xenfra deploy' to deploy your project.[/dim]")
        else:
            console.print("[yellow]Configuration cancelled.[/yellow]")

    except XenfraAPIError as e:
        console.print(f"[bold red]API Error: {e.detail}[/bold red]")
    except XenfraError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except click.Abort:
        pass
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/bold red]")


@click.command()
@click.argument('deployment-id', required=False)
@click.option('--apply', is_flag=True, help='Auto-apply suggested patch (with confirmation)')
@click.option('--logs', type=click.File('r'), help='Diagnose from log file instead of deployment')
def diagnose(deployment_id, apply, logs):
    """
    Diagnose deployment failures using AI.

    Analyzes logs and provides diagnosis, suggestions, and optionally
    an automatic patch to fix the issue.
    """
    try:
        # Use context manager for all SDK operations
        with get_client() as client:
            # Get logs
            if logs:
                log_content = logs.read()
                console.print(f"[cyan]Analyzing logs from file...[/cyan]")
            elif deployment_id:
                console.print(f"[cyan]Fetching logs for deployment {deployment_id}...[/cyan]")
                log_content = client.deployments.get_logs(deployment_id)

                if not log_content:
                    console.print("[yellow]No logs found for this deployment.[/yellow]")
                    return
            else:
                console.print("[bold red]Please specify a deployment ID or use --logs <file>[/bold red]")
                console.print("[dim]Usage: xenfra diagnose <deployment-id> or xenfra diagnose --logs error.log[/dim]")
                return

            # Scrub sensitive data
            scrubbed_logs = scrub_logs(log_content)

            # Try to read package manager context from xenfra.yaml
            package_manager = None
            dependency_file = None
            try:
                config = read_xenfra_yaml()
                package_manager = config.get('package_manager')
                dependency_file = config.get('dependency_file')

                if package_manager and dependency_file:
                    console.print(f"[dim]Using context: {package_manager} ({dependency_file})[/dim]")
            except FileNotFoundError:
                # No config file - diagnosis will infer from logs
                console.print("[dim]No xenfra.yaml found - inferring package manager from logs[/dim]")

            # Diagnose with context
            console.print("[cyan]Analyzing failure...[/cyan]")
            result = client.intelligence.diagnose(
                logs=scrubbed_logs,
                package_manager=package_manager,
                dependency_file=dependency_file
            )

        # Display diagnosis
        console.print("\n")
        console.print(Panel(result.diagnosis, title="[bold red]Diagnosis[/bold red]", border_style="red"))
        console.print(Panel(result.suggestion, title="[bold yellow]Suggestion[/bold yellow]", border_style="yellow"))

        # Handle patch
        if result.patch and result.patch.file:
            console.print("\n[bold green]Automatic fix available![/bold green]")
            console.print(f"  File: [cyan]{result.patch.file}[/cyan]")
            console.print(f"  Operation: [yellow]{result.patch.operation}[/yellow]")
            console.print(f"  Value: [white]{result.patch.value}[/white]")

            if apply or Confirm.ask("\nApply this patch?", default=False):
                try:
                    apply_patch(result.patch.model_dump())
                    console.print("[bold green]Patch applied successfully![/bold green]")
                    console.print("[cyan]Run 'xenfra deploy' to retry deployment.[/cyan]")
                except FileNotFoundError as e:
                    console.print(f"[bold red]Error: {e}[/bold red]")
                except Exception as e:
                    console.print(f"[bold red]Failed to apply patch: {e}[/bold red]")
            else:
                console.print("[dim]Patch not applied. Follow manual steps above.[/dim]")
        else:
            console.print("\n[yellow]No automatic fix available.[/yellow]")
            console.print("[dim]Please follow the manual steps in the suggestion above.[/dim]")

    except XenfraAPIError as e:
        console.print(f"[bold red]API Error: {e.detail}[/bold red]")
    except XenfraError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except click.Abort:
        pass
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/bold red]")


@click.command()
def analyze():
    """
    Analyze codebase without creating configuration.

    Shows what AI would detect, useful for previewing before running init.
    """
    try:
        # Use context manager for SDK client
        with get_client() as client:
            # Scan codebase
            console.print("[cyan]Analyzing your codebase...[/cyan]")
            code_snippets = scan_codebase()

            if not code_snippets:
                console.print("[bold red]No code files found to analyze.[/bold red]")
                return

            # Call Intelligence Service
            analysis = client.intelligence.analyze_codebase(code_snippets)

        # Display results
        console.print("\n[bold green]Analysis Results:[/bold green]\n")

        table = Table(show_header=False, box=None)
        table.add_column("Property", style="cyan")
        table.add_column("Value", style="white")

        table.add_row("Framework", analysis.framework)
        table.add_row("Port", str(analysis.port))
        table.add_row("Database", analysis.database)
        if analysis.cache:
            table.add_row("Cache", analysis.cache)
        if analysis.workers:
            table.add_row("Workers", ", ".join(analysis.workers))
        if analysis.env_vars:
            table.add_row("Environment Variables", ", ".join(analysis.env_vars))
        table.add_row("Instance Size", analysis.instance_size)
        table.add_row("Estimated Cost", f"${analysis.estimated_cost_monthly:.2f}/month")
        table.add_row("Confidence", f"{analysis.confidence:.0%}")

        console.print(table)

        if analysis.notes:
            console.print(f"\n[dim]Notes: {analysis.notes}[/dim]")

        console.print(f"\n[dim]Run 'xenfra init' to create xenfra.yaml with this configuration.[/dim]")

    except XenfraAPIError as e:
        console.print(f"[bold red]API Error: {e.detail}[/bold red]")
    except XenfraError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except click.Abort:
        pass
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/bold red]")
