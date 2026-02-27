#!/usr/bin/env python3
"""
validate_xml.py — Validate LROI PROMs XML against XSD schema.

Usage:
    python validate_xml.py <xml_file> <xsd_file>

Example:
    python validate_xml.py output.xml XSD_LROI_PROMs_v9_2-20210608.xsd
"""

import sys
from pathlib import Path


def validate_xml(xml_path: str, xsd_path: str) -> int:
    """
    Validate XML file against XSD schema.
    
    Returns:
        0 if valid
        1 if validation failed
        2 if error (file not found, parse error, etc.)
    """
    try:
        from lxml import etree
    except ImportError:
        print("Error: lxml not installed. Install with: pip install lxml")
        return 2
    
    xml_file = Path(xml_path)
    xsd_file = Path(xsd_path)
    
    # Check files exist
    if not xml_file.exists():
        print(f"Error: XML file not found: {xml_path}")
        return 2
    
    if not xsd_file.exists():
        print(f"Error: XSD file not found: {xsd_path}")
        return 2
    
    try:
        # Load schema
        schema_doc = etree.parse(str(xsd_file))
        schema = etree.XMLSchema(schema_doc)
        
        # Load and validate XML
        xml_doc = etree.parse(str(xml_file))
        
        if schema.validate(xml_doc):
            print(f"✓ {xml_path} is VALID")
            return 0
        else:
            print(f"✗ {xml_path} validation FAILED:")
            print()
            for error in schema.error_log:
                print(f"  Line {error.line}, Column {error.column}:")
                print(f"    {error.message}")
            print()
            print(f"Total errors: {len(schema.error_log)}")
            return 1
    
    except etree.XMLSyntaxError as e:
        print(f"✗ XML parsing error: {e}")
        return 2
    
    except Exception as e:
        print(f"✗ Unexpected error: {e}")
        return 2


def main():
    if len(sys.argv) != 3:
        print(__doc__)
        print("Error: Requires exactly 2 arguments")
        return 2
    
    xml_file = sys.argv[1]
    xsd_file = sys.argv[2]
    
    return validate_xml(xml_file, xsd_file)


if __name__ == "__main__":
    sys.exit(main())
