# Konnektr Graph SDK for Python

A powerful, Python SDK for [Konnektr Graph](https://konnektr.io), fully compatible with the Azure Digital Twins API but optimized for the Konnektr ecosystem.

## Features

- **Azure-Free**: No dependencies on Azure libraries.
- **Synchronous & Asynchronous**: High-performance clients for both threaded and async workflows.
- **Modular Auth**: Supports OAuth 2.0 Client Credentials, Device Code Flow, and Static Tokens.
- **Auto-Pagination**: Seamlessly iterate through large query results and resource lists.
- **Data Models**: Typed dataclasses for Digital Twins, Models, Relationships, and Jobs.

## Installation

```bash
pip install konnektr-graph
```

## Quick Start

### Synchronous Client

```python
from konnektr_graph import KonnektrGraphClient
from konnektr_graph.auth import ClientSecretCredential

# Authenticate
cred = ClientSecretCredential(
    domain="auth.konnektr.io",
    audience="https://graph.konnektr.io",
    client_id="YOUR_CLIENT_ID",
    client_secret="YOUR_CLIENT_SECRET"
)

# Initialize Client
client = KonnektrGraphClient("https://your-graph-endpoint.konnektr.io", cred)

# Get a Digital Twin
twin = client.get_digital_twin("my-twin-id")
print(twin)

# Query Twins with auto-pagination
for twin in client.query_twins("SELECT * FROM digitaltwins"):
    print(twin)
```

### Asynchronous Client

```python
import asyncio
from konnektr_graph.aio import KonnektrGraphClient
from konnektr_graph.auth import AsyncClientSecretCredential

async def main():
    cred = AsyncClientSecretCredential(
        domain="auth.konnektr.io",
        audience="https://graph.konnektr.io",
        client_id="...",
        client_secret="..."
    )
    
    async with KonnektrGraphClient("https://your-graph-endpoint.konnektr.io", cred) as client:
        twin = await client.get_digital_twin("my-twin-id")
        print(twin)

asyncio.run(main())
```

## Authentication Options

- `ClientSecretCredential` / `AsyncClientSecretCredential`: Ideal for server-to-server scenarios.
- `DeviceCodeCredential` / `AsyncDeviceCodeCredential`: Best for interactive CLI tools.
- `StaticTokenCredential`: Use when you already have a valid access token.

## License

This project is licensed under the MIT License - see the LICENSE file for details.
