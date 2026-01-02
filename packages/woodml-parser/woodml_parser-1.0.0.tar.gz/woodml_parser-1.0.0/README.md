# WoodML Parser (Python)

Reference implementation of the WoodML parser for Python.

## Installation

```bash
pip install woodml-parser
```

Or install from source:

```bash
pip install -e .
```

## CLI Usage

After installation, the `woodml` command is available:

```bash
# Parse and display project info
woodml parse project.woodml

# Generate a cut list
woodml cutlist project.woodml -f table

# Validate a file
woodml validate project.woodml

# Show project information
woodml info project.woodml -f json
```

### CLI Options

- `-o, --output <file>` - Write output to file instead of stdout
- `-f, --format <fmt>` - Output format: json, text, table (default: text)
- `-v, --verbose` - Show detailed output
- `-h, --help` - Show help message

## Library Usage

```python
from woodml import parse_and_resolve, generate_cut_list, format_cut_list

# Parse a WoodML document
woodml_source = '''
woodml: "1.0"

project:
  name: "Simple Box"
  units: imperial

formulas:
  vars:
    length: 12"
    width: 8"

parts:
  - id: side
    dimensions:
      length: $length
      width: $width
      thickness: 1/2"
    quantity: 2
'''

# Parse and resolve all variables
doc = parse_and_resolve(woodml_source)

# Generate cut list
cut_list = generate_cut_list(doc)
print(format_cut_list(cut_list))
```

## API

### Parsing

- `parse(source)` - Parse WoodML string into document
- `parse_and_resolve(source)` - Parse and resolve all variables/formulas

### Units

- `parse_dimension(value)` - Parse dimension string (e.g., `"3-1/2\""`)
- `to_inches(dim)` - Convert dimension to inches
- `to_millimeters(dim)` - Convert dimension to millimeters
- `format_imperial(dim)` - Format as imperial string
- `format_metric(dim)` - Format as metric string

### Formulas

- `create_context(variables)` - Create formula evaluation context
- `evaluate_formula(expr, context)` - Evaluate formula expression
- `resolve_formulas(formulas)` - Resolve all formulas in a Formulas object

### Utilities

- `validate_document(doc)` - Validate document structure
- `calculate_board_feet(doc)` - Calculate total board feet
- `generate_cut_list(doc)` - Generate cut list from resolved document
- `format_cut_list(items)` - Format cut list as string table

## License

MIT
