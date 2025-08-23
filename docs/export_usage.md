# Calibre Library Export and Registry Monitoring

This document provides usage examples and documentation for the Calibre library export and Windows Registry monitoring features.

## Table of Contents
- [Calibre Library Export](#calibre-library-export)
  - [Export Formats](#export-formats)
  - [Usage Examples](#usage-examples)
  - [Error Handling](#error-handling)
- [Registry Monitoring](#registry-monitoring)
  - [Starting Monitoring](#starting-monitoring)
  - [Stopping Monitoring](#stopping-monitoring)
  - [Webhook Integration](#webhook-integration)

## Calibre Library Export

The `export_calibre_library` function allows you to export your Calibre library to various formats.

### Export Formats

1. **JSON** - Structured JSON format with all book metadata
2. **CSV** - Comma-separated values, suitable for spreadsheets
3. **SQLite** - A lightweight SQL database file

### Usage Examples

#### Export to JSON
```python
result = export_calibre_library(
    library_path="/path/to/calibre/library",
    output_path="/output/books.json",
    format="json",
    include_metadata=True
)
```

#### Export to CSV
```python
result = export_calibre_library(
    library_path="/path/to/calibre/library",
    output_path="/output/books.csv",
    format="csv"
)
```

#### Export to SQLite
```python
result = export_calibre_library(
    library_path="/path/to/calibre/library",
    output_path="/output/books.db",
    format="sqlite"
)
```

### Error Handling

The function returns a dictionary with the following structure:
```python
{
    'status': 'success' | 'error',
    'message': 'Description of the result',
    'export_path': '/path/to/exported/file',
    'book_count': 42,  # Number of books exported
    'format': 'json'   # The export format used
}
```

## Registry Monitoring

The `monitor_registry` function allows you to monitor changes to Windows Registry keys.

### Starting Monitoring

```python
# Start monitoring a registry key
result = monitor_registry(
    path=r"HKEY_CURRENT_USER\Software\MyApp",
    action="start",
    callback_url="https://example.com/webhook"
)
```

### Stopping Monitoring

```python
# Stop monitoring a registry key
result = monitor_registry(
    path=r"HKEY_CURRENT_USER\Software\MyApp",
    action="stop"
)
```

### Webhook Integration

When a change is detected in the monitored registry key, a POST request will be sent to the specified callback URL with the following JSON payload:

```json
{
    "path": "HKEY_CURRENT_USER\\Software\\MyApp",
    "change_type": "created|deleted|modified",
    "key": "Settings",
    "value": "New Value",
    "value_type": "REG_SZ",
    "timestamp": "2023-01-01T12:00:00Z"
}
```

## Error Codes

| Status Code | Description |
|-------------|-------------|
| 400 | Invalid request parameters |
| 404 | Library path not found |
| 500 | Internal server error |

## Troubleshooting

- **Missing Dependencies**: Ensure all required packages are installed
- **Permissions**: The application needs appropriate permissions to access the registry and filesystem
- **Network Connectivity**: For webhook callbacks, ensure the server is accessible
