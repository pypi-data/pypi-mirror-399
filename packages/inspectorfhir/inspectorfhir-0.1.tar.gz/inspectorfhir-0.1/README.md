# Inspector FHIR 

A command-line utility and Python module for discovering FHIR endpoints and related API metadata.

## Overview

`ifhir.py` searches for FHIR and related endpoints on a given URL/host, including:
- FHIR metadata (CapabilityStatement)
- SMART-on-FHIR discovery endpoints
- OIDC discovery endpoints
- OAuth2 discovery endpoints
- Swagger/OpenAPI documentation
- API documentation UIs

## Installation

```bash
pip install inspectorfhir
```

## Command Line Usage

### Basic Usage

```bash
python ifhir.py --url https://example.com/fhir
```

### Options

- `--url, -U, -u`: Full FHIR URL where metadata should be found (e.g., `https://example.com/fhir`)
- `--hostname, -H`: Target server hostname (e.g., `https://example.com`)
- `--fhir_prefix, -F`: FHIR API prefix (e.g., `/fhir`) - used with `--hostname`
- `--all, -A`: Include full details of each endpoint check in the output

### Examples

**Using a full URL:**
```bash
python ifhir.py --url https://example.com/fhir/metadata
```

**Using hostname and prefix separately:**
```bash
python ifhir.py --hostname https://example.com --fhir_prefix /fhir
```

**Include detailed results:**
```bash
python ifhir.py --url https://example.com/fhir --all
```

## Using as a Python Module

### Import the Module

```python
from inspectorfhir.ifhir import fhir_recognizer
```

### Function: `fhir_recognizer(url, include_details=True)`

**Parameters:**
- `url` (str): The FHIR endpoint URL to check
- `include_details` (bool): Whether to include detailed response data (default: `True`)

**Returns:** Dictionary containing discovery results

### Example Usage

```python
from inspectorfhir.ifhir import fhir_recognizer
import json

# Check a FHIR endpoint with full details
result = fhir_recognizer('https://example.com/fhir', include_details=True)
print(json.dumps(result, indent=2))

# Check without detailed response data
result = fhir_recognizer('https://example.com/fhir', include_details=False)
print(json.dumps(result, indent=2))
```

### Response Structure

The response includes a `report` section with discovery results:

```json
{
    "report": {
        "fhir_metadata": {"url": "...", "found": true},
        "oidc_discovery": {"url": "...", "found": false},
        "oauth2_discovery": {"url": "...", "found": false},
        "smart_discovery_1": {"url": "...", "found": true},
        "smart_discovery_2": {"url": "...", "found": false},
        "documentation_ui": {"found": true, "https://...": true},
        "swagger_json": {"found": true, "https://...": true}
    }
}
```

When `include_details=True`, a `details` section contains full HTTP responses and data from each endpoint.
