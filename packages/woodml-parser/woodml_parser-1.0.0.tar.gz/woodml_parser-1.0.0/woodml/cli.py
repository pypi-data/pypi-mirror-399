#!/usr/bin/env python3
"""
WoodML CLI Tool
Command-line interface for parsing and processing WoodML files
"""

import argparse
import json
import sys
from pathlib import Path
from typing import Optional

from .parser import (
    WoodMLParser,
    validate_document,
    generate_cut_list,
    format_cut_list,
    calculate_board_feet,
    ValidationError,
)
from .types import ResolvedDocument, Dimension
from .svg import generate_svg, SVGOptions, ColorScheme, DiagramType
from .cost import estimate_cost, format_cost_estimate, CostEstimateOptions


def format_errors(errors: list[ValidationError]) -> str:
    """Format validation errors for display"""
    return "\n".join(
        f"[{e.severity.upper()}] {e.path}: {e.message}"
        for e in errors
    )


def write_output(content: str, output_file: Optional[str]) -> None:
    """Write content to file or stdout"""
    if output_file:
        Path(output_file).write_text(content)
        print(f"Output written to: {output_file}")
    else:
        print(content)


def cmd_parse(args: argparse.Namespace) -> int:
    """Parse and display a WoodML file"""
    source = Path(args.file).read_text()
    parser = WoodMLParser()

    try:
        resolved = parser.parse_and_resolve(source)

        if args.format == "json":
            # Convert to JSON-serializable dict
            output = {
                "woodml": resolved.woodml,
                "project": {
                    "name": resolved.project.name if resolved.project else None,
                    "units": resolved.project.units.value if resolved.project else "imperial",
                } if resolved.project else None,
                "parts": [
                    {
                        "id": p.id,
                        "name": p.name,
                        "material": p.material,
                        "dimensions": {
                            "length": p.dimensions.length.value,
                            "width": p.dimensions.width.value,
                            "thickness": p.dimensions.thickness.value,
                        },
                        "quantity": p.quantity,
                    }
                    for p in resolved.resolved_parts
                ],
                "totalBoardFeet": round(calculate_board_feet(resolved), 2),
            }
            write_output(json.dumps(output, indent=2), args.output)
        else:
            lines = [
                f"Project: {resolved.project.name if resolved.project else 'Untitled'}",
                f"Version: {resolved.woodml}",
                f"Units: {resolved.project.units.value if resolved.project else 'imperial'}",
                "",
                f"Parts: {len(resolved.resolved_parts)}",
                f"Total Board Feet: {calculate_board_feet(resolved):.2f}",
            ]

            if args.verbose:
                lines.append("")
                lines.append("Resolved Variables:")
                for name, value in resolved.resolved_variables.items():
                    if isinstance(value, Dimension):
                        lines.append(f"  ${name} = {value.original} ({value.value})")
                    else:
                        lines.append(f"  ${name} = {value}")

            write_output("\n".join(lines), args.output)
        return 0

    except Exception as e:
        print(f"Parse error: {e}", file=sys.stderr)
        return 1


def cmd_cutlist(args: argparse.Namespace) -> int:
    """Generate a cut list from a WoodML file"""
    source = Path(args.file).read_text()
    parser = WoodMLParser()

    try:
        resolved = parser.parse_and_resolve(source)
        cut_list = generate_cut_list(resolved)

        if args.format == "json":
            output = [
                {
                    "partId": item.part_id,
                    "partName": item.part_name,
                    "material": item.material,
                    "length": item.length,
                    "width": item.width,
                    "thickness": item.thickness,
                    "quantity": item.quantity,
                    "grain": item.grain,
                    "boardFeet": item.board_feet,
                }
                for item in cut_list
            ]
            write_output(json.dumps(output, indent=2), args.output)
        elif args.format == "table":
            write_output(format_cut_list(cut_list), args.output)
        else:
            # Text format - simple list
            lines = ["Cut List:", ""]
            for item in cut_list:
                lines.append(f"{item.part_name} ({item.material})")
                lines.append(f"  {item.length} x {item.width} x {item.thickness}")
                lines.append(f"  Quantity: {item.quantity}, Board Feet: {item.board_feet}")
                lines.append("")
            lines.append(f"Total Board Feet: {sum(i.board_feet for i in cut_list):.2f}")
            write_output("\n".join(lines), args.output)
        return 0

    except Exception as e:
        print(f"Error generating cut list: {e}", file=sys.stderr)
        return 1


def cmd_validate(args: argparse.Namespace) -> int:
    """Validate a WoodML file"""
    source = Path(args.file).read_text()
    parser = WoodMLParser()

    try:
        doc = parser.parse(source)
        errors = validate_document(doc)

        if args.format == "json":
            output = {
                "valid": len(errors) == 0,
                "errors": [
                    {"path": e.path, "message": e.message, "severity": e.severity}
                    for e in errors
                ],
            }
            write_output(json.dumps(output, indent=2), args.output)
        else:
            if len(errors) == 0:
                write_output("✓ Document is valid", args.output)
            else:
                error_count = sum(1 for e in errors if e.severity == "error")
                warn_count = sum(1 for e in errors if e.severity == "warning")
                write_output(
                    f"Found {error_count} error(s) and {warn_count} warning(s):\n\n{format_errors(errors)}",
                    args.output,
                )
                return 1
        return 0

    except Exception as e:
        print(f"Validation failed: {e}", file=sys.stderr)
        return 1


def cmd_info(args: argparse.Namespace) -> int:
    """Show project information"""
    source = Path(args.file).read_text()
    parser = WoodMLParser()

    try:
        resolved = parser.parse_and_resolve(source)

        info = {
            "file": Path(args.file).name,
            "project": resolved.project.name if resolved.project else "Untitled",
            "author": resolved.project.author if resolved.project and resolved.project.author else "Unknown",
            "version": resolved.woodml,
            "units": resolved.project.units.value if resolved.project else "imperial",
            "description": resolved.project.description if resolved.project else "",
            "statistics": {
                "parts": len(resolved.resolved_parts),
                "materials": {
                    "lumber": len(resolved.materials.lumber) if resolved.materials else 0,
                    "hardware": len(resolved.materials.hardware) if resolved.materials else 0,
                    "sheetGoods": len(resolved.materials.sheet_goods) if resolved.materials else 0,
                },
                "joinery": len(resolved.joinery) if resolved.joinery else 0,
                "assemblySteps": len(resolved.assembly) if resolved.assembly else 0,
                "totalBoardFeet": round(calculate_board_feet(resolved), 2),
            },
        }

        if args.format == "json":
            write_output(json.dumps(info, indent=2), args.output)
        else:
            lines = [
                f"File: {info['file']}",
                f"Project: {info['project']}",
                f"Author: {info['author']}",
                f"WoodML Version: {info['version']}",
                f"Units: {info['units']}",
                "",
                "Statistics:",
                f"  Parts: {info['statistics']['parts']}",
                f"  Lumber types: {info['statistics']['materials']['lumber']}",
                f"  Hardware items: {info['statistics']['materials']['hardware']}",
                f"  Sheet goods: {info['statistics']['materials']['sheetGoods']}",
                f"  Joinery connections: {info['statistics']['joinery']}",
                f"  Assembly steps: {info['statistics']['assemblySteps']}",
                f"  Total board feet: {info['statistics']['totalBoardFeet']}",
            ]

            if info["description"]:
                lines.extend(["", f"Description: {info['description']}"])

            write_output("\n".join(lines), args.output)
        return 0

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1


def cmd_diagram(args: argparse.Namespace) -> int:
    """Generate SVG diagram from a WoodML file"""
    source = Path(args.file).read_text()
    parser = WoodMLParser()

    try:
        resolved = parser.parse_and_resolve(source)

        # Map string to enum
        diagram_type_map = {
            "parts": DiagramType.PARTS,
            "exploded": DiagramType.EXPLODED,
            "cutlist": DiagramType.CUTLIST,
        }
        color_scheme_map = {
            "default": ColorScheme.DEFAULT,
            "blueprint": ColorScheme.BLUEPRINT,
            "monochrome": ColorScheme.MONOCHROME,
        }

        options = SVGOptions(
            width=args.width,
            height=args.height,
            color_scheme=color_scheme_map[args.color],
            show_dimensions=True,
            show_names=True,
            show_grain=True,
        )

        diagram_type = diagram_type_map[args.type]
        svg = generate_svg(resolved, diagram_type, options)

        # Default output to file
        output_file = args.output or f"{Path(args.file).stem}.svg"
        write_output(svg, output_file)

        if args.verbose:
            print(f"Generated {args.type} diagram with {len(resolved.resolved_parts)} parts")

        return 0

    except Exception as e:
        print(f"Error generating diagram: {e}", file=sys.stderr)
        return 1


def cmd_cost(args: argparse.Namespace) -> int:
    """Estimate project cost from a WoodML file"""
    source = Path(args.file).read_text()
    parser = WoodMLParser()

    try:
        resolved = parser.parse_and_resolve(source)

        options = CostEstimateOptions(
            waste_percentage=args.waste / 100,
            labor_rate=args.labor_rate,
            include_labor=args.include_labor,
        )

        estimate = estimate_cost(resolved, options)

        if args.format == "json":
            output = {
                "lumber": {
                    "items": [
                        {
                            "material": item.material,
                            "boardFeet": item.board_feet,
                            "pricePerBF": item.price_per_bf,
                            "cost": item.cost,
                            "parts": item.parts,
                        }
                        for item in estimate.lumber_items
                    ],
                    "subtotal": estimate.lumber_subtotal,
                },
                "hardware": {
                    "items": [
                        {
                            "name": item.name,
                            "type": item.type,
                            "size": item.size,
                            "quantity": item.quantity,
                            "unitPrice": item.unit_price,
                            "cost": item.cost,
                        }
                        for item in estimate.hardware_items
                    ],
                    "subtotal": estimate.hardware_subtotal,
                },
                "finishing": {
                    "items": [
                        {
                            "product": item.product,
                            "coverage": item.coverage,
                            "unitsNeeded": item.units_needed,
                            "unitPrice": item.unit_price,
                            "cost": item.cost,
                        }
                        for item in estimate.finishing_items
                    ],
                    "subtotal": estimate.finishing_subtotal,
                },
                "labor": {
                    "hours": estimate.labor_hours,
                    "rate": estimate.labor_rate,
                    "subtotal": estimate.labor_subtotal,
                },
                "total": estimate.total,
                "boardFeetTotal": estimate.board_feet_total,
                "squareFeetTotal": estimate.square_feet_total,
                "wastePercentage": estimate.waste_percentage,
                "notes": estimate.notes,
            }
            write_output(json.dumps(output, indent=2), args.output)
        else:
            write_output(format_cost_estimate(estimate), args.output)

        return 0

    except Exception as e:
        print(f"Error estimating cost: {e}", file=sys.stderr)
        return 1


def main() -> int:
    """Main entry point for CLI"""
    parser = argparse.ArgumentParser(
        prog="woodml",
        description="WoodML CLI - Parse and process WoodML files",
    )
    parser.add_argument(
        "--version",
        action="version",
        version="woodml 1.0.0",
    )

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # Common arguments
    def add_common_args(subparser: argparse.ArgumentParser) -> None:
        subparser.add_argument("file", help="WoodML file to process")
        subparser.add_argument(
            "-o", "--output",
            help="Write output to file instead of stdout",
        )
        subparser.add_argument(
            "-f", "--format",
            choices=["json", "text", "table"],
            default="text",
            help="Output format (default: text)",
        )
        subparser.add_argument(
            "-v", "--verbose",
            action="store_true",
            help="Show detailed output",
        )

    # Parse command
    parse_parser = subparsers.add_parser("parse", help="Parse and validate a WoodML file")
    add_common_args(parse_parser)
    parse_parser.set_defaults(func=cmd_parse)

    # Cutlist command
    cutlist_parser = subparsers.add_parser("cutlist", help="Generate a cut list")
    add_common_args(cutlist_parser)
    cutlist_parser.set_defaults(func=cmd_cutlist)

    # Validate command
    validate_parser = subparsers.add_parser("validate", help="Validate a WoodML file")
    add_common_args(validate_parser)
    validate_parser.set_defaults(func=cmd_validate)

    # Info command
    info_parser = subparsers.add_parser("info", help="Show project information")
    add_common_args(info_parser)
    info_parser.set_defaults(func=cmd_info)

    # Diagram command
    diagram_parser = subparsers.add_parser("diagram", help="Generate SVG diagram")
    diagram_parser.add_argument("file", help="WoodML file to process")
    diagram_parser.add_argument(
        "-o", "--output",
        help="Write output to file (default: <input>.svg)",
    )
    diagram_parser.add_argument(
        "-t", "--type",
        choices=["parts", "exploded", "cutlist"],
        default="parts",
        help="Diagram type (default: parts)",
    )
    diagram_parser.add_argument(
        "-c", "--color",
        choices=["default", "blueprint", "monochrome"],
        default="default",
        help="Color scheme (default: default)",
    )
    diagram_parser.add_argument(
        "-w", "--width",
        type=int,
        default=800,
        help="SVG width in pixels (default: 800)",
    )
    diagram_parser.add_argument(
        "--height",
        type=int,
        default=600,
        help="SVG height in pixels (default: 600)",
    )
    diagram_parser.add_argument(
        "-v", "--verbose",
        action="store_true",
        help="Show detailed output",
    )
    diagram_parser.set_defaults(func=cmd_diagram)

    # Cost command
    cost_parser = subparsers.add_parser("cost", help="Estimate project cost")
    cost_parser.add_argument("file", help="WoodML file to process")
    cost_parser.add_argument(
        "-o", "--output",
        help="Write output to file instead of stdout",
    )
    cost_parser.add_argument(
        "-f", "--format",
        choices=["json", "text"],
        default="text",
        help="Output format (default: text)",
    )
    cost_parser.add_argument(
        "--waste",
        type=int,
        default=15,
        help="Waste percentage (default: 15)",
    )
    cost_parser.add_argument(
        "--labor-rate",
        type=float,
        default=25.0,
        help="Labor rate per hour (default: 25)",
    )
    cost_parser.add_argument(
        "--include-labor",
        action="store_true",
        help="Include labor cost estimate",
    )
    cost_parser.set_defaults(func=cmd_cost)

    args = parser.parse_args()

    if not args.command:
        parser.print_help()
        return 0

    if not Path(args.file).exists():
        print(f"Error: File not found: {args.file}", file=sys.stderr)
        return 1

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
