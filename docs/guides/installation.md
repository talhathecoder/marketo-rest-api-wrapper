# Installation & Setup

## Requirements

- Python 3.9 or higher
- A Marketo instance with REST API access enabled
- API credentials (Client ID, Client Secret, Munchkin ID)

## Install from PyPI

```bash
pip install marketo-rest-api-wrapper
```

## Install from Source

```bash
git clone https://github.com/yourusername/marketo-rest-api-wrapper.git
cd marketo-rest-api-wrapper
pip install -e .
```

For development (includes testing and linting tools):

```bash
pip install -e ".[dev]"
```

## Obtaining API Credentials

You need three values to connect to your Marketo instance:

### 1. Munchkin Account ID

Your Munchkin ID is the unique identifier for your Marketo subscription. It follows the pattern `XXX-XXX-XXX` (e.g., `123-ABC-456`).

**Where to find it:**
- Go to **Admin** → **Integration** → **Munchkin** in your Marketo instance
- Or check your Marketo login URL: `https://app-{MUNCHKIN_ID}.marketo.com`

### 2. Client ID and Client Secret

These come from a LaunchPoint custom service:

1. Go to **Admin** → **Integration** → **LaunchPoint**
2. Click **New** → **New Service**
3. Set:
   - **Display Name**: `REST API Wrapper` (or your preferred name)
   - **Service**: `Custom`
   - **API Only User**: Select or create a dedicated API-only user
4. Click **Create**
5. Click **View Details** on the new service to get the **Client ID** and **Client Secret**

### 3. API-Only User (Required)

If you don't have one yet:

1. Go to **Admin** → **Users & Roles**
2. Create a new role with the API permissions you need:
   - **Read-Only Lead** — for reading leads and activities
   - **Read-Write Lead** — for creating/updating leads
   - **Read-Only Assets** — for reading programs, folders, tokens
   - **Read-Write Assets** — for creating/modifying programs
   - **Execute Campaign** — for triggering smart campaigns
3. Create a new user with **API Only** checked and assign the role above

### Permissions Reference

| Operation | Required Permission |
|-----------|-------------------|
| Read leads, activities | Read-Only Lead |
| Create/update/delete leads | Read-Write Lead |
| Merge leads | Read-Write Lead |
| Read programs, folders, tokens | Read-Only Assets |
| Create/modify programs, tokens | Read-Write Assets |
| Trigger/schedule campaigns | Execute Campaign |
| Bulk import | Read-Write Lead (or Read-Write Custom Object) |
| Bulk export | Read-Only Lead (or Read-Only Activity) |

## Verify Your Setup

```python
from marketo_api import MarketoClient

client = MarketoClient(
    munchkin_id="123-ABC-456",
    client_id="your-client-id",
    client_secret="your-client-secret"
)

# If this works without error, you're connected
schema = client.leads.describe()
print(f"Connected! Found {len(schema)} lead fields.")
```

## Next Steps

- [Quick Start Guide](quickstart.md) — Your first API calls
- [Configuration](configuration.md) — Advanced client settings
