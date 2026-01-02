#!/usr/bin/env python3
"""
WoodML Parser Example
Demonstrates parsing a WoodML file and generating a cut list
"""

from woodml import (
    parse_and_resolve,
    generate_cut_list,
    format_cut_list,
    calculate_board_feet,
    validate_document,
    parse,
)


def main():
    # Example WoodML document
    woodml_source = '''
woodml: "1.0"

project:
  name: "Simple Side Table"
  units: imperial

formulas:
  vars:
    table_height: 26"
    top_length: 20"
    top_width: 16"
    leg_size: 1-1/4"
    apron_width: 3-1/2"

  computed:
    leg_length: $table_height - 3/4"
    long_apron: $top_length - (2 * $leg_size)
    short_apron: $top_width - (2 * $leg_size)

materials:
  lumber:
    - id: cherry_4_4
      species: cherry
      thickness: 4/4
      board_feet: 6

parts:
  - id: top
    name: "Table Top"
    material: cherry_4_4
    dimensions:
      length: $top_length
      width: $top_width
      thickness: 3/4"

  - id: leg
    name: "Leg"
    material: cherry_4_4
    dimensions:
      length: $leg_length
      width: $leg_size
      thickness: $leg_size
    quantity: 4

  - id: long_apron
    name: "Long Apron"
    material: cherry_4_4
    dimensions:
      length: $long_apron
      width: $apron_width
      thickness: 3/4"
    quantity: 2

  - id: short_apron
    name: "Short Apron"
    material: cherry_4_4
    dimensions:
      length: $short_apron
      width: $apron_width
      thickness: 3/4"
    quantity: 2

joinery:
  - type: mortise_and_tenon
    parts: [leg, long_apron]
  - type: mortise_and_tenon
    parts: [leg, short_apron]
'''

    print("=" * 60)
    print("WoodML Parser Example")
    print("=" * 60)
    print()

    # Parse the document
    print("Parsing WoodML document...")
    doc = parse(woodml_source)
    print(f"Project: {doc.project.name}")
    print(f"WoodML Version: {doc.woodml}")
    print()

    # Validate
    print("Validating document...")
    errors = validate_document(doc)
    if errors:
        for error in errors:
            print(f"  [{error.severity.upper()}] {error.path}: {error.message}")
    else:
        print("  No validation errors found!")
    print()

    # Parse and resolve all formulas
    print("Resolving formulas and dimensions...")
    resolved = parse_and_resolve(woodml_source)

    print("\nResolved Variables:")
    for name, value in resolved.resolved_variables.items():
        if hasattr(value, 'original'):
            print(f"  ${name} = {value.original} ({value.value:.3f}\")")
        else:
            print(f"  ${name} = {value}")
    print()

    # Generate cut list
    print("Generating Cut List:")
    print("-" * 60)
    cut_list = generate_cut_list(resolved)
    print(format_cut_list(cut_list))
    print()

    # Calculate total board feet
    total_bf = calculate_board_feet(resolved)
    print(f"\nTotal Board Feet Required: {total_bf:.2f} BF")
    print(f"Add 20% waste factor: {total_bf * 1.2:.2f} BF")
    print()

    # Show parts breakdown
    print("Parts Breakdown:")
    print("-" * 60)
    for part in resolved.resolved_parts:
        dims = part.dimensions
        print(f"\n{part.name or part.id}:")
        print(f"  Material: {part.material}")
        print(f"  Dimensions: {dims.length.value:.2f}\" x {dims.width.value:.2f}\" x {dims.thickness.value:.2f}\"")
        print(f"  Quantity: {part.quantity}")


if __name__ == "__main__":
    main()
