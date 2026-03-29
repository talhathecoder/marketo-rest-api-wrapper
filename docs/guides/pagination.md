# Pagination

Marketo uses two pagination styles depending on the endpoint. The wrapper handles both transparently — you get complete result sets without manual page management.

## Pagination Styles

### Token-based Pagination

Used by most lead database endpoints (leads, activities, list members).

Marketo includes `"moreResult": true` and a `nextPageToken` in the response when more pages exist. The wrapper follows these tokens automatically.

**Endpoints using token pagination:** leads (GET by filter), activities, list leads, custom objects.

### Offset-based Pagination

Used by asset and metadata endpoints (programs, campaigns, folders).

Marketo accepts `offset` and `maxReturn` parameters. The wrapper increments the offset automatically until a partial page (fewer results than `maxReturn`) signals the end.

**Endpoints using offset pagination:** programs, campaigns, lists, folder contents.

## Automatic Pagination (Default)

By default, all resource methods collect every page and return a complete list:

```python
# This fetches ALL matching leads, across however many pages it takes
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp"],
    fields=["email", "firstName"]
)
print(f"Total leads: {len(leads)}")
```

```python
# This fetches ALL programs across all pages
programs = client.programs.get()
print(f"Total programs: {len(programs)}")
```

## Controlling Page Size

Set `batch_size` (token-based) or `max_return` (offset-based) to control how many records each API call fetches:

```python
# 300 is the maximum for lead endpoints
leads = client.leads.get_by_filter(
    filter_type="company",
    filter_values=["Acme Corp"],
    batch_size=300  # max: 300
)

# 200 is typical for asset endpoints
programs = client.programs.get(max_return=200)
```

Larger page sizes mean fewer API calls but larger response payloads. For most use cases, use the maximum.

## Manual Pagination with Generators

For very large result sets where you don't want to load everything into memory, use the pagination utilities directly:

```python
from marketo_api.utils.pagination import paginate_with_token

# Returns a generator — records are fetched lazily as you iterate
for lead in paginate_with_token(
    client._transport.get,
    "/rest/v1/leads.json",
    params={
        "filterType": "company",
        "filterValues": "Acme Corp",
        "fields": "email,firstName",
        "batchSize": 300,
    },
):
    process_lead(lead)
    # Pages are fetched on demand as the generator advances
```

## Limiting Results

Collect a specific number of results and stop:

```python
from marketo_api.utils.pagination import paginate_with_token, collect_all

# Get only the first 50 leads
leads = collect_all(
    paginate_with_token(
        client._transport.get,
        "/rest/v1/leads.json",
        params={"filterType": "company", "filterValues": "Acme Corp"},
    ),
    limit=50
)
```

## Safety Limits

To prevent runaway pagination (e.g., a filter that matches millions of records), both pagination functions accept a `max_pages` parameter:

```python
from marketo_api.utils.pagination import paginate_with_token, collect_all

leads = collect_all(
    paginate_with_token(
        client._transport.get,
        "/rest/v1/leads.json",
        params={"filterType": "company", "filterValues": "Acme Corp"},
        max_pages=10  # Stop after 10 pages (default: 100)
    )
)
```

If the page limit is hit, a warning is logged:

```
WARNING: Reached max_pages=10 for endpoint=/rest/v1/leads.json. There may be more results.
```

## Activity Pagination

Activities use a special paging token mechanism. The wrapper handles this — just provide a `since_datetime`:

```python
activities = client.activities.get(
    activity_type_ids=[1, 12],
    since_datetime="2025-01-01T00:00:00Z"
)
```

Behind the scenes:
1. The wrapper calls `/rest/v1/activities/pagingtoken.json` to get an initial token
2. Uses that token to fetch the first page of activities
3. Follows `nextPageToken` values across all subsequent pages

## Pagination and Rate Limits

Every page fetch counts as one API call against your rate limits. The rate limiter applies to each page individually, so large paginated queries are automatically throttled:

```
Page 1  ──→ rate_limiter.wait_if_needed() → fetch → 300 records
Page 2  ──→ rate_limiter.wait_if_needed() → fetch → 300 records
  ...
Page 34 ──→ rate_limiter.wait_if_needed() → fetch → 150 records (done)
```

For very large exports (100k+ records), consider using the [Bulk Extract API](../api/bulk-extract.md) instead, which uses a single API call to create a job and another to download the file.
