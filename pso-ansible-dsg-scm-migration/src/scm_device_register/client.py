"""SCM API client for device management."""

from typing import Any, Dict, List, Optional
import json

import requests
from requests.exceptions import RequestException
from rich.console import Console
from rich.syntax import Syntax
from rich.panel import Panel

from scm_device_register.auth import token_manager
from scm_device_register.config import settings

console = Console()


class SCMClientError(Exception):
    """Raised when an SCM API request fails."""

    pass


class SCMDeviceClient:
    """Client for interacting with SCM Device Management APIs."""

    def __init__(self, verbose: bool = False) -> None:
        """
        Initialize the SCM device client.

        Args:
            verbose: Enable verbose logging of requests and responses
        """
        self.session = requests.Session()
        self.session.verify = settings.verify_ssl
        self.verbose = verbose

    def _get_headers(self) -> Dict[str, str]:
        """
        Get headers with authentication token.

        Returns:
            Dict[str, str]: Headers with x-auth-jwt token
        """
        token = token_manager.get_token()
        return {
            "x-auth-jwt": token,
            "Content-Type": "application/json",
            "Accept": "application/json",
        }

    def _log_request(self, method: str, url: str, headers: Dict[str, str],
                     params: Optional[Dict] = None, payload: Optional[Dict] = None) -> None:
        """Log request details in verbose mode."""
        if not self.verbose:
            return

        console.print("\n[bold cyan]═══ REQUEST ═══[/bold cyan]")
        console.print(f"[yellow]{method}[/yellow] {url}")

        # Mask the token in headers for security
        masked_headers = headers.copy()
        if "x-auth-jwt" in masked_headers:
            token = masked_headers["x-auth-jwt"]
            masked_headers["x-auth-jwt"] = f"{token[:20]}...{token[-10:]}" if len(token) > 30 else "***"

        console.print("\n[bold]Headers:[/bold]")
        syntax = Syntax(json.dumps(masked_headers, indent=2), "json", theme="monokai")
        console.print(syntax)

        if params:
            console.print("\n[bold]Query Parameters:[/bold]")
            syntax = Syntax(json.dumps(params, indent=2), "json", theme="monokai")
            console.print(syntax)

        if payload:
            console.print("\n[bold]Payload:[/bold]")
            syntax = Syntax(json.dumps(payload, indent=2), "json", theme="monokai")
            console.print(syntax)

    def _log_response(self, response: requests.Response) -> None:
        """Log response details in verbose mode."""
        if not self.verbose:
            return

        console.print("\n[bold magenta]═══ RESPONSE ═══[/bold magenta]")
        console.print(f"[yellow]Status Code:[/yellow] {response.status_code}")
        console.print(f"[yellow]Status:[/yellow] {response.reason}")

        console.print("\n[bold]Response Headers:[/bold]")
        syntax = Syntax(json.dumps(dict(response.headers), indent=2), "json", theme="monokai")
        console.print(syntax)

        try:
            response_json = response.json()
            console.print("\n[bold]Response Body:[/bold]")
            syntax = Syntax(json.dumps(response_json, indent=2), "json", theme="monokai")
            console.print(syntax)
        except:
            console.print("\n[bold]Response Body:[/bold]")
            console.print(response.text[:1000])  # Limit to first 1000 chars

        console.print("[bold cyan]═══════════════[/bold cyan]\n")

    def list_devices(self, device_type: str = "registered") -> Dict[str, Any]:
        """
        List available devices in SCM.

        Args:
            device_type: Type of devices to list (default: "registered")

        Returns:
            Dict containing device list response

        Raises:
            SCMClientError: If the API request fails
        """
        url = f"{settings.device_api_base}/ngfw/api/v1/devices"
        params = {"type": device_type}
        headers = self._get_headers()

        self._log_request("GET", url, headers, params=params)

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )
            self._log_response(response)
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            raise SCMClientError(f"Failed to list devices: {e}") from e

    def get_label_groups(self, pagination: bool = False) -> Dict[str, Any]:
        """
        Get available label groups.

        Args:
            pagination: Whether to use pagination (default: False)

        Returns:
            Dict containing label groups response

        Raises:
            SCMClientError: If the API request fails
        """
        url = f"{settings.config_api_base}/api/sase/config/v1/device-config/label-groups"
        params = {"pagination": str(pagination).lower()}
        headers = self._get_headers()

        self._log_request("GET", url, headers, params=params)

        try:
            response = self.session.get(
                url,
                headers=headers,
                params=params,
                timeout=30,
            )
            self._log_response(response)
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            raise SCMClientError(f"Failed to get label groups: {e}") from e

    def claim_device(self, serial_numbers: List[str], labels: List[str] = None) -> Dict[str, Any]:
        """
        Claim devices and add them to Cloud Managed Devices.

        Args:
            serial_numbers: List of device serial numbers to claim
            labels: Optional list of label IDs to apply to devices

        Returns:
            Dict containing claim response

        Raises:
            SCMClientError: If the API request fails
        """
        url = f"{settings.admin_api_base}/api/v2/device-registrations/claim"
        headers = self._get_headers()

        payload = {
            "devices": serial_numbers,
            "labels": labels or []
        }

        self._log_request("POST", url, headers, payload=payload)

        try:
            response = self.session.post(
                url,
                headers=headers,
                json=payload,
                timeout=30,
            )
            self._log_response(response)
            response.raise_for_status()
            return response.json()

        except RequestException as e:
            # Try to get error details from response
            error_msg = str(e)
            if hasattr(e, 'response') and e.response is not None:
                try:
                    error_detail = e.response.json()
                    error_msg = f"{e} - Details: {error_detail}"
                except:
                    error_msg = f"{e} - Response: {e.response.text}"

            raise SCMClientError(f"Failed to claim device: {error_msg}") from e
