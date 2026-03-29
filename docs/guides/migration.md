# Migrating from Other Libraries

If you're coming from another Marketo API library, this guide maps the key differences.

---

## From `marketorestpython`

The most common existing library. Here's how the API maps:

### Client Initialization

```python
# OLD (marketorestpython)
from marketorestpython.client import MarketoClient
mc = MarketoClient(munchkin_id, client_id, client_secret)

# NEW (marketo-rest-api-wrapper)
from marketo_api import MarketoClient
client = MarketoClient(munchkin_id="...", client_id="...", client_secret="...")
```

### Lead Operations

```python
# OLD
lead = mc.execute(method="get_lead_by_id", id=12345)
leads = mc.execute(method="get_multiple_leads_by_filter_type",
                   filterType="email", filterValues=["a@b.com"], fields=["email"])
mc.execute(method="create_update_leads", leads=[{...}], action="createOrUpdate")

# NEW
lead = client.leads.get_by_id(12345)
leads = client.leads.get_by_filter(filter_type="email", filter_values=["a@b.com"], fields=["email"])
client.leads.create_or_update(leads=[{...}], action="createOrUpdate")
```

### Key Differences

| Feature | `marketorestpython` | `marketo-rest-api-wrapper` |
|---------|--------------------|-----------------------------|
| API style | `mc.execute(method=...)` | `client.resource.method()` |
| Rate limiting | Manual | Automatic (built-in) |
| Pagination | Manual | Automatic |
| Retries | None | Exponential backoff |
| Token refresh | Manual | Automatic |
| Bulk API | Limited | Full support |
| Type hints | No | Yes |
| Error handling | Generic exceptions | Structured hierarchy |

---

## From Direct `requests` Calls

If you've been calling the Marketo API directly:

### Before

```python
import requests
import time

# Manual token management
def get_token(munchkin_id, client_id, client_secret):
    url = f"https://{munchkin_id}.mktorest.com/identity/oauth/token"
    params = {
        "grant_type": "client_credentials",
        "client_id": client_id,
        "client_secret": client_secret
    }
    resp = requests.get(url, params=params)
    return resp.json()["access_token"]

token = get_token(MUNCHKIN_ID, CLIENT_ID, CLIENT_SECRET)

# Manual API call with no retry, no rate limiting
headers = {"Authorization": f"Bearer {token}"}
url = f"https://{MUNCHKIN_ID}.mktorest.com/rest/v1/leads.json"
resp = requests.get(url, params={
    "filterType": "email",
    "filterValues": "test@example.com"
}, headers=headers)

data = resp.json()
if not data["success"]:
    print(f"Error: {data['errors']}")
else:
    leads = data["result"]

# Manual pagination
all_leads = []
while True:
    resp = requests.get(url, params=params, headers=headers)
    data = resp.json()
    all_leads.extend(data.get("result", []))
    if not data.get("moreResult"):
        break
    params["nextPageToken"] = data["nextPageToken"]
```

### After

```python
from marketo_api import MarketoClient

client = MarketoClient(
    munchkin_id=MUNCHKIN_ID,
    client_id=CLIENT_ID,
    client_secret=CLIENT_SECRET
)

# One line — auth, pagination, rate limiting, retries all handled
leads = client.leads.get_by_filter(
    filter_type="email",
    filter_values=["test@example.com"]
)
```

Everything you had to handle manually — token refresh, error parsing, pagination loops, rate limit sleeps, retry backoff — is now built in.

---

## From Node.js / JavaScript Libraries

If you're migrating a Node.js Marketo integration to Python:

```javascript
// Node.js (typical pattern)
const Marketo = require('node-marketo-rest');
const marketo = new Marketo({endpoint, identity, clientId, clientSecret});

const lead = await marketo.lead.find('email', ['test@example.com']);
await marketo.lead.createOrUpdate([{email: 'new@test.com', firstName: 'Test'}]);
```

```python
# Python equivalent
from marketo_api import MarketoClient

client = MarketoClient(munchkin_id="...", client_id="...", client_secret="...")

lead = client.leads.get_by_email("test@example.com")
client.leads.create_or_update([{"email": "new@test.com", "firstName": "Test"}])
```

The resource-based structure (`client.leads`, `client.campaigns`, etc.) is similar to most modern API client patterns regardless of language.

---

## Migration Checklist

1. **Install the package:** `pip install marketo-rest-api-wrapper`
2. **Replace credentials setup** — use `MarketoClient(...)` or `MarketoClient.from_env()`
3. **Replace API calls** — map old method names to new resource methods (see table above)
4. **Remove manual token management** — delete token acquisition and refresh code
5. **Remove manual pagination loops** — all list methods auto-paginate
6. **Remove manual rate limiting** — delete sleep/throttle logic
7. **Update error handling** — use the structured exception hierarchy
8. **Remove manual retry logic** — built-in exponential backoff handles transient errors
9. **Test** — run your integration tests against a Marketo sandbox
