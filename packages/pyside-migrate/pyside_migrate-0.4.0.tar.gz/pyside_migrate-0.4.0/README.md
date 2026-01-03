# PySide Migrate

A command-line tool for migrating PySide2 code to PySide6, currently focusing on enum namespace changes.

## Overview

PySide6 introduced changes to how enums are accessed. In PySide2, many enums were accessed directly through the Qt namespace (e.g., `Qt.AlignCenter`). In PySide6, these enums have been moved to their specific enum classes (e.g., `Qt.AlignmentFlag.AlignCenter`).

This tool automates the migration process by transforming your PySide2 code to use the enum locations that are expected by PySide6. It supports transforming code that uses PySide2 or [Qt.py](https://github.com/mottosso/Qt.py).

## Usage

### Using uv (recommended)

```bash
uvx pyside-migrate ../path/to/code/
```

### Using pip

```bash
pip install pyside-migrate
pyside-migrate ../path/to/code/
```

## Examples

### Before migration:

```python
from PySide2.QtCore import Qt

alignment = Qt.AlignCenter
button = Qt.LeftButton
flags = Qt.AlignLeft | Qt.AlignTop
```

### After migration:

```python
from PySide2.QtCore import Qt

alignment = Qt.AlignmentFlag.AlignCenter
button = Qt.MouseButton.LeftButton
flags = Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop
```
## Development

### Running tests

Using uv:

```bash
uv run pytest
```

Or with pytest directly:

```bash
pytest
```

## Requirements

- Python 3.10 or higher
- libcst 1.0.0 or higher

## License

MIT

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## Known Limitations

- The tool currently focuses on enum migrations and does not handle other PySide2 to PySide6 breaking changes
- Only enums defined in `enum-mappings.json` will be transformed
- The tool preserves import statements; you'll still need to manually update `PySide2` imports to `PySide6` after running the enum migrations
