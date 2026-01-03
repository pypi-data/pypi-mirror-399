#!/usr/bin/env python3
"""
Generate transform.yaml files for all schemas in stock_examples.

This script reads JSON schema files and creates transform.yaml files
that convert all field names from camelCase to snake_case (Pythonic naming).
"""

import json
import re
from pathlib import Path
from typing import Dict, Any

PYCHARTER_PATH = Path(__file__).parent.parent
STOCK_EXAMPLES_DIR = PYCHARTER_PATH / "data" / "stock_examples"


def camel_to_snake(name: str) -> str:
    """Convert camelCase to snake_case."""
    # Insert an underscore before any uppercase letter that follows a lowercase letter or digit
    s1 = re.sub('(.)([A-Z][a-z]+)', r'\1_\2', name)
    # Insert an underscore before any uppercase letter that follows a lowercase letter
    s2 = re.sub('([a-z0-9])([A-Z])', r'\1_\2', s1)
    return s2.lower()


def extract_field_names(schema: Dict[str, Any]) -> Dict[str, str]:
    """
    Extract field names from JSON schema and create rename mappings.
    
    Handles both object schemas and array schemas (with items).
    
    Returns:
        Dictionary mapping original field names to snake_case names
    """
    rename_map = {}
    
    # Handle array schemas (type: "array" with items)
    if schema.get("type") == "array" and "items" in schema:
        items_schema = schema["items"]
        if isinstance(items_schema, dict) and "properties" in items_schema:
            for field_name in items_schema["properties"].keys():
                snake_name = camel_to_snake(field_name)
                rename_map[field_name] = snake_name
    
    # Handle object schemas
    elif "properties" in schema:
        for field_name in schema["properties"].keys():
            snake_name = camel_to_snake(field_name)
            rename_map[field_name] = snake_name
    
    return rename_map


def generate_transform_yaml(
    schema_name: str,
    provider: str,
    rename_map: Dict[str, str],
) -> str:
    """Generate transform.yaml content."""
    # Determine title and description
    if provider == "fmp":
        title = f"{schema_name}_transformation"
        description = f"Transformation rules for FMP {schema_name.replace('_', ' ').title()} dataset"
    else:
        title = f"{schema_name}_transformation"
        description = f"Transformation rules for {provider.upper()} {schema_name.replace('_', ' ').title()} dataset"
    
    yaml_content = f"""title: {title}
description: {description}
version: 1.0.0

# Transformation operations are organized by type, with fields listed underneath
# This makes it easier to see all fields affected by each transformation type
# and apply transformations in a logical order

# 1. RENAME: Change field names from camelCase (source) to snake_case (target)
# This converts all field names to Pythonic naming convention
rename:
"""
    
    # Add rename rules
    for original, snake_case in sorted(rename_map.items()):
        if original != snake_case:
            yaml_content += f"  {original}: {snake_case}\n"
        else:
            yaml_content += f"  {original}: {original}  # Already snake_case\n"
    
    yaml_content += """
# 2. DROP: Remove fields entirely (field won't appear in output)
# drop:
#   - old_field_name
#   - deprecated_field
#   - temporary_field

# 3. FILL_NULL: Replace null/empty values with defaults
# fill_null:
#   field_name:
#     default: "default_value"
#   numeric_field:
#     default: 0

# 4. DROP_NULL: Remove records where specified field is null
# drop_null:
#   - required_field_1
#   - required_field_2

# 5. REPLACE: Replace values based on patterns or exact matches
# replace:
#   # Pattern-based replacement (regex)
#   status:
#     pattern:
#       regex: "^OLD_"
#       replacement: "NEW_"
#   # Exact value replacement
#   code:
#     exact:
#       - from: "ACTIVE"
#         to: "active"
#       - from: "INACTIVE"
#         to: "inactive"

# 6. HASH: Hash field values (useful for PII, sensitive data)
# hash:
#   email:
#     algorithm: sha256
#     salt: "optional_salt"

# 7. FILTER: Filter records based on conditions
# filter:
#   # Keep records matching ALL conditions (AND logic)
#   and:
#     - field: symbol
#       operator: not_null
#     - field: status
#       operator: equals
#       value: "active"

# 8. DEDUP: Remove duplicate records
# dedup:
#   fields:
#     - symbol
#     - date
#   strategy: first

# TYPE CONVERSION: Convert field types (applied after rename)
# type:
#   symbol: string
#   date: datetime
#   price: float
#   count: integer
#   is_active: boolean
"""
    
    return yaml_content


def main():
    """Generate transform.yaml files for all schemas."""
    print("=" * 60)
    print("Generating transform.yaml Files")
    print("=" * 60)
    
    schema_dirs = sorted(STOCK_EXAMPLES_DIR.iterdir())
    
    for schema_dir in schema_dirs:
        if not schema_dir.is_dir():
            continue
        
        # Skip fmp_stock_list as it already has a transform.yaml
        if schema_dir.name == "fmp_stock_list":
            print(f"\n⏭ Skipping {schema_dir.name} (already has transform.yaml)")
            continue
        
        # Find schema JSON file
        schema_files = list(schema_dir.glob("*_schema.json"))
        if not schema_files:
            print(f"\n⚠ No schema file found in {schema_dir.name}")
            continue
        
        schema_file = schema_files[0]
        schema_name = schema_file.stem.replace("_schema", "")
        
        # Determine provider
        if schema_name.startswith("fmp_"):
            provider = "fmp"
            base_name = schema_name.replace("fmp_", "")
        elif schema_name.startswith("massive_"):
            provider = "massive"
            base_name = schema_name.replace("massive_", "")
        else:
            provider = "unknown"
            base_name = schema_name
        
        print(f"\nProcessing: {schema_name}")
        
        try:
            # Read schema
            with open(schema_file, 'r', encoding='utf-8') as f:
                schema = json.load(f)
            
            # Extract field names and create rename map
            rename_map = extract_field_names(schema)
            
            if not rename_map:
                print(f"  ⚠ No fields found in schema")
                continue
            
            # Count how many fields need renaming
            needs_rename = sum(1 for orig, snake in rename_map.items() if orig != snake)
            print(f"  Found {len(rename_map)} fields, {needs_rename} need renaming")
            
            # Generate transform.yaml
            transform_content = generate_transform_yaml(base_name, provider, rename_map)
            
            # Write transform.yaml
            transform_file = schema_dir / "transform.yaml"
            with open(transform_file, 'w', encoding='utf-8') as f:
                f.write(transform_content)
            
            print(f"  ✓ Created: {transform_file.relative_to(PYCHARTER_PATH)}")
            
        except Exception as e:
            print(f"  ❌ Error processing {schema_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✓ Transform file generation complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

