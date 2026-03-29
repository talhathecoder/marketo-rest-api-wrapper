# API Reference: Programs

Manage Marketo programs — browse, create, update, clone, and get members.

**Access:** `client.programs`  
**Marketo docs:** [Assets — Programs](https://developers.marketo.com/rest-api/assets/programs/)

---

## Methods

### `get(max_return, offset, status, workspace) → list[dict]`

Browse programs with optional filters. Automatically paginates.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `max_return` | `int` | `200` | Results per page |
| `offset` | `int` | `0` | Starting offset |
| `status` | `str \| None` | `None` | Filter by status (e.g., `"active"`) |
| `workspace` | `str \| None` | `None` | Filter by workspace name |

**Returns:** List of program records.

```python
programs = client.programs.get()
active = client.programs.get(status="active", workspace="Default")
```

---

### `get_by_id(program_id) → dict | None`

Get a program by ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `program_id` | `int` | *required* | The program ID |

**Returns:** Program record dict, or `None` if not found.

```python
program = client.programs.get_by_id(1001)
```

---

### `get_by_name(name) → dict | None`

Get a program by exact name.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Exact program name |

**Returns:** Program record dict, or `None` if not found.

```python
program = client.programs.get_by_name("Q3-Webinar-Sept")
```

---

### `create(name, folder, program_type, channel, description) → dict`

Create a new program.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Program name |
| `folder` | `dict` | *required* | Folder dict, e.g., `{"id": 50, "type": "Folder"}` |
| `program_type` | `str` | *required* | `"Default"`, `"Event"`, `"Email"`, `"Engagement"`, `"Nurture"` |
| `channel` | `str` | *required* | Channel name (e.g., `"Webinar"`, `"Content"`, `"Email Blast"`) |
| `description` | `str` | `""` | Optional description |

**Returns:** Created program record.

```python
program = client.programs.create(
    name="Q4-Product-Launch",
    folder={"id": 50, "type": "Folder"},
    program_type="Default",
    channel="Content",
    description="Q4 product launch campaign"
)
```

---

### `update(program_id, **kwargs) → dict`

Update a program's metadata.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `program_id` | `int` | *required* | The program ID |
| `**kwargs` | | | Fields to update (e.g., `name`, `description`) |

```python
client.programs.update(1001, description="Updated description")
```

---

### `clone(program_id, name, folder, description) → dict`

Clone a program with all its assets.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `program_id` | `int` | *required* | Source program ID |
| `name` | `str` | *required* | Name for the clone |
| `folder` | `dict` | *required* | Target folder dict |
| `description` | `str` | `""` | Optional description |

**Returns:** Cloned program record.

```python
clone = client.programs.clone(
    program_id=1001,
    name="Q3-Webinar-Clone",
    folder={"id": 50, "type": "Folder"}
)
print(f"Cloned to program ID: {clone['id']}")
```

---

### `get_members(program_id, max_return, fields) → list[dict]`

Get all members of a program.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `program_id` | `int` | *required* | The program ID |
| `max_return` | `int` | `200` | Results per page |
| `fields` | `list[str] \| None` | `None` | Fields to return |

**Returns:** List of program member records.

```python
members = client.programs.get_members(
    program_id=1001,
    fields=["email", "firstName", "programStatus"]
)
```

---

## Return Value Shapes

### Program Record

```python
{
    "id": 1001,
    "name": "Q3-Webinar-Sept",
    "description": "September webinar program",
    "type": "Default",
    "channel": "Webinar",
    "status": "active",
    "workspace": "Default",
    "folder": {"type": "Folder", "value": 50, "folderName": "Marketing Programs"},
    "createdAt": "2025-01-15T10:00:00Z",
    "updatedAt": "2025-06-20T14:30:00Z"
}
```
