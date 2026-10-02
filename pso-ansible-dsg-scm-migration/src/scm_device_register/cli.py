"""CLI interface for SCM Device Register tool."""

import click
from rich.console import Console
from rich.table import Table
from rich import print as rprint
import json

from scm_device_register import __version__
from scm_device_register.auth import AuthenticationError
from scm_device_register.client import SCMDeviceClient, SCMClientError
from scm_device_register.config import settings

console = Console()


@click.group()
@click.version_option(version=__version__)
def app() -> None:
    """CLI tool for registering Palo Alto NGFW devices in Strata Cloud Manager."""
    pass


@app.command()
@click.option(
    "--type",
    "-t",
    "device_type",
    default="registered",
    help="Device type to filter (default: registered)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON response",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with request/response details",
)
def list(device_type: str, output_json: bool, verbose: bool) -> None:
    """List available devices in SCM."""
    try:
        console.print("[bold blue]Fetching devices...[/bold blue]")

        client = SCMDeviceClient(verbose=verbose)
        response = client.list_devices(device_type=device_type)

        if output_json:
            rprint(json.dumps(response, indent=2))
            return

        # Display in table format
        # Response can be a list or dict with "devices" key
        devices = response if hasattr(response, '__iter__') and not hasattr(response, 'get') else response.get("devices", [])

        if devices:
            table = Table(title=f"Devices (Type: {device_type})")
            table.add_column("Serial Number", style="cyan")
            table.add_column("Hostname", style="white")
            table.add_column("Model", style="green")
            table.add_column("Status", style="yellow")

            for device in devices:
                table.add_row(
                    device.get("id", device.get("serial", "N/A")),
                    device.get("hostname", "N/A"),
                    device.get("model", "N/A"),
                    device.get("status", "N/A"),
                )

            console.print(table)
            console.print(f"\n[green]Total devices: {len(devices)}[/green]")
        else:
            console.print("[yellow]No devices found[/yellow]")

    except AuthenticationError as e:
        console.print(f"[bold red]Authentication failed:[/bold red] {e}")
        raise click.Abort()
    except SCMClientError as e:
        console.print(f"[bold red]API request failed:[/bold red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise click.Abort()


@app.command()
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON response",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with request/response details",
)
def labels(output_json: bool, verbose: bool) -> None:
    """List available label groups."""
    try:
        console.print("[bold blue]Fetching label groups...[/bold blue]")

        client = SCMDeviceClient(verbose=verbose)
        response = client.get_label_groups()

        if output_json:
            rprint(json.dumps(response, indent=2))
            return

        # Display in table format
        if "data" in response and response["data"]:
            table = Table(title="Label Groups")
            table.add_column("ID", style="cyan")
            table.add_column("Name", style="white")
            table.add_column("Description", style="green")

            for label in response["data"]:
                table.add_row(
                    label.get("id", "N/A"),
                    label.get("name", "N/A"),
                    label.get("description", "N/A"),
                )

            console.print(table)
            console.print(f"\n[green]Total label groups: {len(response['data'])}[/green]")
        else:
            console.print("[yellow]No label groups found[/yellow]")

    except AuthenticationError as e:
        console.print(f"[bold red]Authentication failed:[/bold red] {e}")
        raise click.Abort()
    except SCMClientError as e:
        console.print(f"[bold red]API request failed:[/bold red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise click.Abort()


@app.command()
@click.option(
    "--labels",
    "-l",
    multiple=True,
    help="Label IDs to apply to the device (can be used multiple times)",
)
@click.option(
    "--json",
    "output_json",
    is_flag=True,
    help="Output raw JSON response",
)
@click.option(
    "--verbose",
    "-v",
    is_flag=True,
    help="Enable verbose output with request/response details",
)
@click.argument("serial_numbers", nargs=-1, required=True)
def claim(serial_numbers: tuple, labels: tuple, output_json: bool, verbose: bool) -> None:
    """
    Claim one or more devices and add them to Cloud Managed Devices.

    SERIAL_NUMBERS: One or more device serial numbers to claim
    """
    try:
        from builtins import list as list_builtin
        serial_list = list_builtin(serial_numbers)
        label_list = list_builtin(labels) if labels else []

        console.print(f"[bold blue]Claiming {len(serial_list)} device(s)...[/bold blue]")
        console.print(f"[yellow]Serial numbers: {', '.join(serial_list)}[/yellow]")
        if label_list:
            console.print(f"[yellow]Labels: {', '.join(label_list)}[/yellow]")

        client = SCMDeviceClient(verbose=verbose)
        response = client.claim_device(serial_list, label_list)

        if output_json:
            rprint(json.dumps(response, indent=2))
            return

        console.print("[bold green]Device(s) claimed successfully![/bold green]")
        console.print("\n[cyan]Response:[/cyan]")
        rprint(json.dumps(response, indent=2))

    except AuthenticationError as e:
        console.print(f"[bold red]Authentication failed:[/bold red] {e}")
        raise click.Abort()
    except SCMClientError as e:
        console.print(f"[bold red]API request failed:[/bold red] {e}")
        raise click.Abort()
    except Exception as e:
        console.print(f"[bold red]Unexpected error:[/bold red] {e}")
        raise click.Abort()


@app.command()
def info() -> None:
    """Display configuration and connection information."""
    console.print(f"[bold blue]SCM Device Register v{__version__}[/bold blue]\n")

    # Configuration info
    table = Table(title="Configuration")
    table.add_column("Setting", style="cyan")
    table.add_column("Value", style="white")

    table.add_row("Client ID", settings.client_id)
    table.add_row("TSG ID", settings.tsg_id)
    table.add_row("Device API Base", settings.device_api_base)
    table.add_row("Admin API Base", settings.admin_api_base)
    table.add_row("Config API Base", settings.config_api_base)
    table.add_row("Auth URL", settings.auth_url)
    table.add_row("Verify SSL", str(settings.verify_ssl))

    console.print(table)

    # Test connection
    console.print("\n[yellow]Testing authentication...[/yellow]")
    try:
        client = SCMDeviceClient()
        # Try to fetch devices as a connection test
        client.list_devices()
        console.print("[bold green]Authentication successful![/bold green]")
    except AuthenticationError as e:
        console.print(f"[bold red]Authentication failed:[/bold red] {e}")
    except SCMClientError as e:
        console.print(f"[bold yellow]API test failed:[/bold yellow] {e}")
        console.print("[yellow]Authentication may be working, but API access failed.[/yellow]")


if __name__ == "__main__":
    app()
