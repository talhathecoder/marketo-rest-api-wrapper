# API Reference: Lists

Manage Marketo static lists — browse, add/remove leads, check membership.

**Access:** `client.lists`  
**Marketo docs:** [Lead Database — Static Lists](https://developers.marketo.com/rest-api/lead-database/static-lists/)

---

## Methods

### `get(list_ids, names, program_names, workspace_names) → list[dict]`

Get static lists with optional filters.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_ids` | `list[int] \| None` | `None` | Filter by list IDs |
| `names` | `list[str] \| None` | `None` | Filter by list names |
| `program_names` | `list[str] \| None` | `None` | Filter by parent program names |
| `workspace_names` | `list[str] \| None` | `None` | Filter by workspace names |

**Returns:** List of static list records.

```python
all_lists = client.lists.get()
specific = client.lists.get(names=["Target Accounts", "VIP Leads"])
```

---

### `get_by_id(list_id) → dict | None`

Get a single static list by ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_id` | `int` | *required* | The static list ID |

**Returns:** List record dict, or `None` if not found.

---

### `get_leads(list_id, fields, batch_size) → list[dict]`

Get all leads in a static list. Automatically paginates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_id` | `int` | *required* | The static list ID |
| `fields` | `list[str] \| None` | `None` | Fields to return |
| `batch_size` | `int` | `300` | Results per page (max 300) |

**Returns:** List of lead records.

```python
leads = client.lists.get_leads(100, fields=["email", "firstName", "company"])
print(f"{len(leads)} leads in list")
```

---

### `add_leads(list_id, lead_ids) → dict`

Add leads to a static list.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_id` | `int` | *required* | The static list ID |
| `lead_ids` | `list[int]` | *required* | Lead IDs to add |

**Returns:** API response with status per lead (`"added"` or `"skipped"`).

```python
result = client.lists.add_leads(100, lead_ids=[5, 10, 15, 20])
```

**Limit:** Up to 300 lead IDs per call.

---

### `remove_leads(list_id, lead_ids) → dict`

Remove leads from a static list.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_id` | `int` | *required* | The static list ID |
| `lead_ids` | `list[int]` | *required* | Lead IDs to remove |

**Returns:** API response with status per lead.

```python
client.lists.remove_leads(100, lead_ids=[15, 20])
```

---

### `is_member(list_id, lead_ids) → list[dict]`

Check if leads are members of a static list.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `list_id` | `int` | *required* | The static list ID |
| `lead_ids` | `list[int]` | *required* | Lead IDs to check |

**Returns:** List of membership status records.

```python
statuses = client.lists.is_member(100, lead_ids=[5, 10, 99])
for s in statuses:
    print(f"Lead {s['id']}: member={s['membership']}")
```
