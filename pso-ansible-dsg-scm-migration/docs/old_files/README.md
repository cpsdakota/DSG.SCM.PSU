# SCM Device Register

CLI tool for registering Palo Alto Next Generation Firewalls in Strata Cloud Manager.

## Features

- List registered devices in SCM
- View available label groups
- Claim devices and add them to Cloud Managed Devices
- OAuth2 authentication with automatic token management

## Installation

### Using Poetry (recommended)

```bash
poetry install
poetry shell
```

### Using pip

```bash
pip install -e .
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` and add your SCM credentials:
   - `SCM_CLIENT_ID`: Your service account client ID
   - `SCM_CLIENT_SECRET`: Your service account client secret
   - `SCM_TSG_ID`: Your Tenant Service Group ID

These are the same credentials used in other SCM tools like `scm-auditing` and `airs-migration`.

## Usage

### Display configuration and test connection

```bash
scm-device-register info
```

### List registered devices

```bash
scm-device-register list
```

List with JSON output:
```bash
scm-device-register list --json
```

List with verbose output (shows all request/response details):
```bash
scm-device-register list --verbose
```

### List available label groups

```bash
scm-device-register labels
```

With JSON output:
```bash
scm-device-register labels --json
```

With verbose output:
```bash
scm-device-register labels --verbose
```

### Claim a device

Claim a single device:
```bash
scm-device-register claim 007958000744783
```

Claim multiple devices:
```bash
scm-device-register claim 007958000744783 007958000744784
```

Claim with labels:
```bash
scm-device-register claim 007958000744783 --labels label-id-1 --labels label-id-2
```

Claim with verbose output (useful for debugging):
```bash
scm-device-register claim 007958000744783 --verbose
```

## Development

### Install dependencies

```bash
poetry install
```

### Run tests

```bash
poetry run pytest
```

### Code formatting

```bash
poetry run black .
poetry run ruff check .
```

## API Endpoints

This tool uses the following SCM API endpoints:

- **List Devices**: `GET https://paas-11.prod.panorama.paloaltonetworks.com/ngfw/api/v1/devices?type=registered`
- **Get Label Groups**: `GET https://paas-11.prod.panorama.paloaltonetworks.com/api/sase/config/v1/device-config/label-groups`
- **Claim Device**: `POST https://admin.prod.panorama.paloaltonetworks.com/api/v2/device-registrations/claim`

All endpoints use the `x-auth-jwt` header for authentication with an OAuth2 bearer token.

## License

MIT
