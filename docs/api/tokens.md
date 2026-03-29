# API Reference: Tokens

Manage My Tokens on programs and folders.

**Access:** `client.tokens`  
**Marketo docs:** [Assets — Tokens](https://developers.marketo.com/rest-api/assets/tokens/)

---

## Methods

### `get(folder_id, folder_type) → list[dict]`

Get all tokens for a folder or program.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_id` | `int` | *required* | The folder or program ID |
| `folder_type` | `str` | `"Program"` | `"Folder"` or `"Program"` |

**Returns:** List of token records.

```python
tokens = client.tokens.get(folder_id=1001, folder_type="Program")
for t in tokens:
    print(f"{t['name']} = {t['value']} ({t['type']})")
```

---

### `create(folder_id, folder_type, name, type, value) → dict`

Create or update a My Token. If a token with the same name exists, it is overwritten.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_id` | `int` | *required* | The folder or program ID |
| `folder_type` | `str` | `"Program"` | `"Folder"` or `"Program"` |
| `name` | `str` | `""` | Token name (e.g., `"{{my.event-date}}"`) |
| `type` | `str` | `"text"` | Token type |
| `value` | `str` | `""` | Token value |

**Token types:** `"text"`, `"date"`, `"rich text"`, `"score"`, `"number"`, `"sfdc campaign"`

**Returns:** API response with the created/updated token.

```python
# Simple text token
client.tokens.create(
    folder_id=1001,
    folder_type="Program",
    name="{{my.event-date}}",
    type="text",
    value="September 15, 2025"
)

# Rich text token
client.tokens.create(
    folder_id=1001,
    folder_type="Program",
    name="{{my.cta-button}}",
    type="rich text",
    value='<a href="https://example.com" style="...">Register Now</a>'
)
```

---

### `delete(folder_id, folder_type, name, type) → dict`

Delete a My Token.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `folder_id` | `int` | *required* | The folder or program ID |
| `folder_type` | `str` | `"Program"` | `"Folder"` or `"Program"` |
| `name` | `str` | `""` | Token name to delete |
| `type` | `str` | `"text"` | Token type |

**Returns:** API response confirming deletion.

```python
client.tokens.delete(
    folder_id=1001,
    folder_type="Program",
    name="{{my.event-date}}",
    type="text"
)
```

---

## Token Inheritance

Tokens follow Marketo's folder hierarchy. A token set at a folder level is inherited by all programs within that folder, unless overridden at the program level. Use `folder_type="Folder"` to set tokens at the folder level for broad inheritance.
