"""
Deployment commands for Xenfra CLI.
"""

import os

import click
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from xenfra_sdk import XenfraClient
from xenfra_sdk.exceptions import XenfraAPIError, XenfraError
from xenfra_sdk.privacy import scrub_logs

from ..utils.auth import API_BASE_URL, get_auth_token
from ..utils.codebase import has_xenfra_config
from ..utils.config import apply_patch

console = Console()

# Maximum number of retry attempts for auto-healing
MAX_RETRY_ATTEMPTS = 3


def get_client() -> XenfraClient:
    """Get authenticated SDK client."""
    token = get_auth_token()
    if not token:
        console.print("[bold red]Not logged in. Run 'xenfra auth login' first.[/bold red]")
        raise click.Abort()

    return XenfraClient(token=token, api_url=API_BASE_URL)


def show_diagnosis_panel(diagnosis: str, suggestion: str):
    """Display diagnosis and suggestion in formatted panels."""
    console.print()
    console.print(Panel(diagnosis, title="[bold red]🔍 Diagnosis[/bold red]", border_style="red"))
    console.print()
    console.print(
        Panel(suggestion, title="[bold yellow]💡 Suggestion[/bold yellow]", border_style="yellow")
    )


def show_patch_preview(patch_data: dict):
    """Show a preview of the patch that will be applied."""
    console.print()
    console.print("[bold green]🔧 Automatic Fix Available[/bold green]")
    console.print(f"  [cyan]File:[/cyan] {patch_data.get('file')}")
    console.print(f"  [cyan]Operation:[/cyan] {patch_data.get('operation')}")
    console.print(f"  [cyan]Value:[/cyan] {patch_data.get('value')}")
    console.print()


def zen_nod_workflow(logs: str, client: XenfraClient, attempt: int) -> bool:
    """
    Execute the Zen Nod auto-healing workflow.

    Args:
        logs: Deployment error logs
        client: Authenticated SDK client
        attempt: Current attempt number

    Returns:
        True if patch was applied and user wants to retry, False otherwise
    """
    console.print()
    console.print(f"[cyan]🤖 Analyzing failure (attempt {attempt}/{MAX_RETRY_ATTEMPTS})...[/cyan]")

    # Scrub sensitive data from logs
    scrubbed_logs = scrub_logs(logs)

    # Diagnose with AI
    try:
        diagnosis_result = client.intelligence.diagnose(scrubbed_logs)
    except Exception as e:
        console.print(f"[yellow]Could not diagnose failure: {e}[/yellow]")
        return False

    # Show diagnosis
    show_diagnosis_panel(diagnosis_result.diagnosis, diagnosis_result.suggestion)

    # Check if there's an automatic patch
    if diagnosis_result.patch and diagnosis_result.patch.file:
        show_patch_preview(diagnosis_result.patch.model_dump())

        # Zen Nod confirmation
        if click.confirm("Apply this fix and retry deployment?", default=True):
            try:
                # Apply patch (with automatic backup)
                backup_path = apply_patch(diagnosis_result.patch.model_dump())
                console.print("[bold green]✓ Patch applied[/bold green]")
                if backup_path:
                    console.print(f"[dim]Backup saved: {backup_path}[/dim]")
                return True  # Signal to retry
            except Exception as e:
                console.print(f"[bold red]Failed to apply patch: {e}[/bold red]")
                return False
        else:
            console.print()
            console.print("[yellow]❌ Patch declined. Follow the manual steps above.[/yellow]")
            return False
    else:
        console.print()
        console.print(
            "[yellow]No automatic fix available. Please follow the manual steps above.[/yellow]"
        )
        return False


@click.command()
@click.option("--project-name", help="Project name (defaults to current directory name)")
@click.option("--git-repo", help="Git repository URL (if deploying from git)")
@click.option("--branch", default="main", help="Git branch (default: main)")
@click.option("--framework", help="Framework override (fastapi, flask, django)")
@click.option("--no-heal", is_flag=True, help="Disable auto-healing on failure")
def deploy(project_name, git_repo, branch, framework, no_heal):
    """
    Deploy current project to DigitalOcean with auto-healing.

    Deploys your application with zero configuration. The CLI will:
    1. Check for xenfra.yaml (or run init if missing)
    2. Create a deployment
    3. Auto-diagnose and fix failures (unless --no-heal is set or XENFRA_NO_AI=1)

    Set XENFRA_NO_AI=1 environment variable to disable all AI features.
    """
    # Check XENFRA_NO_AI environment variable
    no_ai = os.environ.get("XENFRA_NO_AI", "0") == "1"
    if no_ai:
        console.print("[yellow]XENFRA_NO_AI is set. Auto-healing disabled.[/yellow]")
        no_heal = True

    # Check for xenfra.yaml
    if not has_xenfra_config():
        console.print("[yellow]No xenfra.yaml found.[/yellow]")
        if click.confirm("Run 'xenfra init' to create configuration?", default=True):
            from .intelligence import init

            ctx = click.get_current_context()
            ctx.invoke(init, manual=no_ai, accept_all=False)
        else:
            console.print("[dim]Deployment cancelled.[/dim]")
            return

    # Default project name to current directory
    if not project_name:
        project_name = os.path.basename(os.getcwd())

    # Determine deployment source
    if git_repo:
        console.print(f"[cyan]Deploying {project_name} from git repository...[/cyan]")
    else:
        console.print(f"[cyan]Deploying {project_name} from local directory...[/cyan]")
        console.print(
            "[yellow]Local deployment requires code upload (not yet fully implemented).[/yellow]"
        )
        console.print("[dim]Please use --git-repo for now.[/dim]")
        return

    # Retry loop for auto-healing
    attempt = 0
    deployment_id = None

    try:
        with get_client() as client:
            while attempt < MAX_RETRY_ATTEMPTS:
                # Safety check to prevent infinite loops
                if attempt > MAX_RETRY_ATTEMPTS:
                    raise RuntimeError("Safety break: Retry loop exceeded MAX_RETRY_ATTEMPTS.")

                attempt += 1

                if attempt > 1:
                    console.print(
                        f"\n[cyan]🔄 Retrying deployment (attempt {attempt}/{MAX_RETRY_ATTEMPTS})...[/cyan]"
                    )
                else:
                    console.print("[cyan]Creating deployment...[/cyan]")

                # Detect framework if not provided
                if not framework:
                    console.print("[dim]Auto-detecting framework...[/dim]")
                    framework = "fastapi"  # Default for now

                # Create deployment
                try:
                    deployment = client.deployments.create(
                        project_name=project_name,
                        git_repo=git_repo,
                        branch=branch,
                        framework=framework,
                    )

                    deployment_id = deployment["deployment_id"]
                    console.print(
                        f"[bold green]✓[/bold green] Deployment created: [cyan]{deployment_id}[/cyan]"
                    )

                    # Show deployment details
                    details_table = Table(show_header=False, box=None)
                    details_table.add_column("Property", style="cyan")
                    details_table.add_column("Value", style="white")

                    details_table.add_row("Deployment ID", str(deployment_id))
                    details_table.add_row("Project", project_name)
                    if git_repo:
                        details_table.add_row("Repository", git_repo)
                        details_table.add_row("Branch", branch)
                    details_table.add_row("Framework", framework)
                    details_table.add_row("Status", deployment.get("status", "PENDING"))

                    panel = Panel(
                        details_table,
                        title="[bold green]Deployment Started[/bold green]",
                        border_style="green",
                    )
                    console.print(panel)

                    # Show next steps
                    console.print("\n[bold]Next steps:[/bold]")
                    console.print(f"  • Monitor status: [cyan]xenfra status {deployment_id}[/cyan]")
                    console.print(f"  • View logs: [cyan]xenfra logs {deployment_id}[/cyan]")
                    if not no_heal:
                        console.print(
                            f"  • Diagnose issues: [cyan]xenfra diagnose {deployment_id}[/cyan]"
                        )

                    # Success - break out of retry loop
                    break

                except XenfraAPIError as e:
                    # Deployment failed
                    console.print(f"[bold red]✗ Deployment failed: {e.detail}[/bold red]")

                    # Check if we should auto-heal
                    if no_heal or attempt >= MAX_RETRY_ATTEMPTS:
                        # No auto-healing or max retries reached
                        if attempt >= MAX_RETRY_ATTEMPTS:
                            console.print(
                                f"\n[bold red]❌ Maximum retry attempts ({MAX_RETRY_ATTEMPTS}) reached.[/bold red]"
                            )
                            console.print(
                                "[yellow]Unable to auto-fix the issue. Please review the errors above.[/yellow]"
                            )
                        raise
                    else:
                        # Try to get logs for diagnosis
                        error_logs = str(e.detail)
                        try:
                            if deployment_id:
                                # This should be a method in the SDK that returns a string
                                logs_response = client.deployments.get_logs(deployment_id)
                                if isinstance(logs_response, dict):
                                    error_logs = logs_response.get("logs", str(e.detail))
                                else:
                                    error_logs = str(logs_response)  # Assuming it can be a string
                        except Exception as log_err:
                            console.print(
                                f"[yellow]Warning: Could not fetch detailed logs for diagnosis: {log_err}[/yellow]"
                            )
                            # Fallback to the initial error detail
                            pass

                        # Run Zen Nod workflow
                        should_retry = zen_nod_workflow(error_logs, client, attempt)

                        if not should_retry:
                            # User declined patch or no patch available
                            console.print("\n[dim]Deployment cancelled.[/dim]")
                            raise click.Abort()

                        # Continue to next iteration (retry)
                        continue

    except XenfraAPIError as e:
        console.print(f"[bold red]API Error: {e.detail}[/bold red]")
    except XenfraError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except click.Abort:
        pass
    except Exception as e:
        console.print(f"[bold red]Unexpected error: {e}[/bold red]")


@click.command()
@click.argument("deployment-id")
@click.option("--follow", "-f", is_flag=True, help="Follow log output (stream)")
@click.option("--tail", type=int, help="Show last N lines")
def logs(deployment_id, follow, tail):
    """
    Stream deployment logs.

    Shows logs for a specific deployment. Use --follow to stream logs in real-time.
    """
    try:
        with get_client() as client:
            console.print(f"[cyan]Fetching logs for deployment {deployment_id}...[/cyan]")

            log_content = client.deployments.get_logs(deployment_id)

            if not log_content:
                console.print("[yellow]No logs available yet.[/yellow]")
                console.print("[dim]The deployment may still be starting up.[/dim]")
                return

            # Process logs
            log_lines = log_content.strip().split("\n")

            # Apply tail if specified
            if tail:
                log_lines = log_lines[-tail:]

            # Display logs with syntax highlighting
            console.print(f"\n[bold]Logs for deployment {deployment_id}:[/bold]\n")

            if follow:
                console.print(
                    "[yellow]Note: --follow flag not yet implemented (showing static logs)[/yellow]\n"
                )

            # Display logs
            for line in log_lines:
                # Color-code based on log level
                if "ERROR" in line or "FAILED" in line:
                    console.print(f"[red]{line}[/red]")
                elif "WARN" in line or "WARNING" in line:
                    console.print(f"[yellow]{line}[/yellow]")
                elif "SUCCESS" in line or "COMPLETED" in line:
                    console.print(f"[green]{line}[/green]")
                elif "INFO" in line:
                    console.print(f"[cyan]{line}[/cyan]")
                else:
                    console.print(line)

    except XenfraAPIError as e:
        console.print(f"[bold red]API Error: {e.detail}[/bold red]")
    except XenfraError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except click.Abort:
        pass


@click.command()
@click.argument("deployment-id", required=False)
@click.option("--watch", "-w", is_flag=True, help="Watch status updates")
def status(deployment_id, watch):
    """
    Show deployment status.

    Displays current status, progress, and details for a deployment.
    Use --watch to monitor status in real-time.
    """
    try:
        if not deployment_id:
            console.print("[yellow]No deployment ID provided.[/yellow]")
            console.print("[dim]Usage: xenfra status <deployment-id>[/dim]")
            return

        with get_client() as client:
            console.print(f"[cyan]Fetching status for deployment {deployment_id}...[/cyan]")

            deployment_status = client.deployments.get_status(deployment_id)

            if watch:
                console.print(
                    "[yellow]Note: --watch flag not yet implemented (showing current status)[/yellow]\n"
                )

            # Display status
            status_value = deployment_status.get("status", "UNKNOWN")
            state = deployment_status.get("state", "unknown")
            progress = deployment_status.get("progress", 0)

            # Status panel
            status_color = {
                "PENDING": "yellow",
                "IN_PROGRESS": "cyan",
                "SUCCESS": "green",
                "FAILED": "red",
                "CANCELLED": "dim",
            }.get(status_value, "white")

            # Create status table
            table = Table(show_header=False, box=None)
            table.add_column("Property", style="cyan")
            table.add_column("Value")

            table.add_row("Deployment ID", str(deployment_id))
            table.add_row("Status", f"[{status_color}]{status_value}[/{status_color}]")
            table.add_row("State", state)

            if progress > 0:
                table.add_row("Progress", f"{progress}%")

            if "project_name" in deployment_status:
                table.add_row("Project", deployment_status["project_name"])

            if "created_at" in deployment_status:
                table.add_row("Created", deployment_status["created_at"])

            if "finished_at" in deployment_status:
                table.add_row("Finished", deployment_status["finished_at"])

            if "url" in deployment_status:
                table.add_row("URL", f"[link]{deployment_status['url']}[/link]")

            if "ip_address" in deployment_status:
                table.add_row("IP Address", deployment_status["ip_address"])

            panel = Panel(table, title="[bold]Deployment Status[/bold]", border_style=status_color)
            console.print(panel)

            # Show error if failed
            if status_value == "FAILED" and "error" in deployment_status:
                error_panel = Panel(
                    deployment_status["error"],
                    title="[bold red]Error[/bold red]",
                    border_style="red",
                )
                console.print("\n", error_panel)

                console.print("\n[bold]Troubleshooting:[/bold]")
                console.print(f"  • View logs: [cyan]xenfra logs {deployment_id}[/cyan]")
                console.print(f"  • Diagnose: [cyan]xenfra diagnose {deployment_id}[/cyan]")

            # Show next steps based on status
            elif status_value == "SUCCESS":
                console.print("\n[bold green]Deployment successful! 🎉[/bold green]")
                if "url" in deployment_status:
                    console.print(f"  • Visit: [link]{deployment_status['url']}[/link]")

            elif status_value in ["PENDING", "IN_PROGRESS"]:
                console.print("\n[bold]Deployment in progress...[/bold]")
                console.print(f"  • View logs: [cyan]xenfra logs {deployment_id}[/cyan]")
                console.print(f"  • Check again: [cyan]xenfra status {deployment_id}[/cyan]")

    except XenfraAPIError as e:
        console.print(f"[bold red]API Error: {e.detail}[/bold red]")
    except XenfraError as e:
        console.print(f"[bold red]Error: {e}[/bold red]")
    except click.Abort:
        pass
