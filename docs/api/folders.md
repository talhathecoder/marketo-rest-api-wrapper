# API Reference: Folders

Navigate and manage the Marketo folder tree.

**Access:** `client.folders`  
**Marketo docs:** [Assets — Folders](https://developers.marketo.com/rest-api/assets/folders/)

---

## Methods

### `get_by_id(folder_id, folder_type) → dict | None`

Get a folder by ID.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_id` | `int` | *required* | The folder ID |
| `folder_type` | `str` | `"Folder"` | `"Folder"` or `"Program"` |

**Returns:** Folder record dict, or `None` if not found.

```python
folder = client.folders.get_by_id(50)
program_as_folder = client.folders.get_by_id(1001, folder_type="Program")
```

---

### `get_by_name(name, folder_type, root_folder_id, workspace) → dict | None`

Get a folder by name.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Exact folder name |
| `folder_type` | `str \| None` | `None` | Filter by type |
| `root_folder_id` | `int \| None` | `None` | Search within this root folder |
| `workspace` | `str \| None` | `None` | Workspace name |

**Returns:** Folder record dict, or `None` if not found.

```python
folder = client.folders.get_by_name("Marketing Programs", workspace="Default")
```

---

### `get_contents(folder_id, max_return) → list[dict]`

Get the contents of a folder (sub-folders, programs, assets).

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_id` | `int` | *required* | The folder ID |
| `max_return` | `int` | `200` | Results per page |

**Returns:** List of folder content records.

```python
contents = client.folders.get_contents(50)
for item in contents:
    print(f"{item['type']}: {item['name']} (ID: {item['id']})")
```

---

### `create(name, parent_id, parent_type, description) → dict`

Create a new folder.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `name` | `str` | *required* | Folder name |
| `parent_id` | `int` | *required* | Parent folder ID |
| `parent_type` | `str` | `"Folder"` | Parent type |
| `description` | `str` | `""` | Optional description |

**Returns:** Created folder record.

```python
folder = client.folders.create(
    name="Q4 Campaigns",
    parent_id=50,
    description="All Q4 2025 campaign assets"
)
```

---

### `delete(folder_id) → dict`

Delete an empty folder.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_id` | `int` | *required* | The folder ID |

**Returns:** API response confirming deletion.

**Note:** The folder must be empty. Move or delete contents first.
