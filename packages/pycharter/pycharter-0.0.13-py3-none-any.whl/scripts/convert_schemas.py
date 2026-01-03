#!/usr/bin/env python3
"""
Convert Pydantic schemas from statfyi-scraper-api to JSON Schema files in pycharter.

This script reads Pydantic models from statfyi-scraper-api/app/schemas/external/
and converts them to JSON Schema format, saving them in pycharter/data/stock_examples/
"""

import json
import sys
from pathlib import Path
from typing import Any, Dict, List

# Add paths for imports
SCRAPER_API_PATH = Path(__file__).parent.parent.parent / "statfyi-scraper-api"
PYCHARTER_PATH = Path(__file__).parent.parent

if SCRAPER_API_PATH.exists():
    sys.path.insert(0, str(SCRAPER_API_PATH))

sys.path.insert(0, str(PYCHARTER_PATH))

from pycharter.json_schema_converter.converter import model_to_schema


def get_model_classes_from_module(module_path: Path) -> List[tuple]:
    """
    Import a module and extract all Pydantic BaseModel classes.
    
    Returns:
        List of (class_name, class_object) tuples
    """
    import importlib.util
    
    module_name = module_path.stem
    spec = importlib.util.spec_from_file_location(module_name, module_path)
    if spec is None or spec.loader is None:
        return []
    
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    
    from pydantic import BaseModel
    
    models = []
    for name in dir(module):
        obj = getattr(module, name)
        if (
            isinstance(obj, type)
            and issubclass(obj, BaseModel)
            and obj is not BaseModel
            and not name.startswith("_")
        ):
            # Prefer Item classes over Response classes
            if "Item" in name or "Response" not in name:
                models.append((name, obj))
    
    return models


def convert_schema_to_json(
    model_class: Any,
    schema_name: str,
    provider: str,
) -> Dict[str, Any]:
    """Convert a Pydantic model to JSON Schema."""
    # Extract title and description from model
    title = getattr(model_class, "__name__", schema_name)
    description = model_class.__doc__ or f"JSON Schema for {provider.upper()} {schema_name}"
    
    # Convert to JSON Schema
    schema = model_to_schema(
        model_class,
        title=title,
        description=description,
        version="1.0.0",
    )
    
    # If the model represents an array response, wrap it
    # Check if the model has a 'data' field that's a list
    if "properties" in schema and "data" in schema["properties"]:
        data_prop = schema["properties"]["data"]
        if data_prop.get("type") == "array" and "items" in data_prop:
            # Extract the items schema and make it the root
            schema = {
                "$schema": "https://json-schema.org/draft/2020-12/schema",
                "title": schema.get("title", title),
                "description": schema.get("description", description),
                "version": schema.get("version", "1.0.0"),
                "type": "array",
                "items": data_prop["items"],
            }
    
    return schema


def main():
    """Convert all schemas from scraper-api to pycharter."""
    if not SCRAPER_API_PATH.exists():
        print(f"Error: statfyi-scraper-api not found at {SCRAPER_API_PATH}")
        return
    
    output_base = PYCHARTER_PATH / "data" / "stock_examples"
    output_base.mkdir(parents=True, exist_ok=True)
    
    # Process FMP schemas
    fmp_schemas_dir = SCRAPER_API_PATH / "app" / "schemas" / "external" / "fmp"
    fmp_output_dir = output_base
    
    print("=" * 60)
    print("Converting FMP Schemas")
    print("=" * 60)
    
    for schema_file in sorted(fmp_schemas_dir.glob("*.py")):
        if schema_file.name == "__init__.py":
            continue
        
        schema_name = schema_file.stem
        print(f"\nProcessing: {schema_name}")
        
        try:
            models = get_model_classes_from_module(schema_file)
            if not models:
                print(f"  ⚠ No Pydantic models found in {schema_file.name}")
                continue
            
            # Use the first model (usually the Item model)
            model_name, model_class = models[0]
            if len(models) > 1:
                # Prefer Item models
                item_models = [(n, m) for n, m in models if "Item" in n]
                if item_models:
                    model_name, model_class = item_models[0]
                    print(f"  Using: {model_name} (from {len(models)} models)")
            
            # Convert to JSON Schema
            json_schema = convert_schema_to_json(model_class, schema_name, "fmp")
            
            # Create output directory
            output_dir = fmp_output_dir / f"fmp_{schema_name}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save JSON schema
            output_file = output_dir / f"fmp_{schema_name}_schema.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(json_schema, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Created: {output_file.relative_to(PYCHARTER_PATH)}")
            
        except Exception as e:
            print(f"  ❌ Error processing {schema_name}: {e}")
            import traceback
            traceback.print_exc()
    
    # Process Massive schemas
    massive_schemas_dir = SCRAPER_API_PATH / "app" / "schemas" / "external" / "massive"
    
    print("\n" + "=" * 60)
    print("Converting Massive Schemas")
    print("=" * 60)
    
    for schema_file in sorted(massive_schemas_dir.glob("*.py")):
        if schema_file.name == "__init__.py":
            continue
        
        schema_name = schema_file.stem
        print(f"\nProcessing: {schema_name}")
        
        try:
            models = get_model_classes_from_module(schema_file)
            if not models:
                print(f"  ⚠ No Pydantic models found in {schema_file.name}")
                continue
            
            # Use the first model
            model_name, model_class = models[0]
            if len(models) > 1:
                item_models = [(n, m) for n, m in models if "Item" in n]
                if item_models:
                    model_name, model_class = item_models[0]
                    print(f"  Using: {model_name} (from {len(models)} models)")
            
            # Convert to JSON Schema
            json_schema = convert_schema_to_json(model_class, schema_name, "massive")
            
            # Create output directory
            output_dir = fmp_output_dir / f"massive_{schema_name}"
            output_dir.mkdir(parents=True, exist_ok=True)
            
            # Save JSON schema
            output_file = output_dir / f"massive_{schema_name}_schema.json"
            with open(output_file, "w", encoding="utf-8") as f:
                json.dump(json_schema, f, indent=2, ensure_ascii=False)
            
            print(f"  ✓ Created: {output_file.relative_to(PYCHARTER_PATH)}")
            
        except Exception as e:
            print(f"  ❌ Error processing {schema_name}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("✓ Conversion complete!")
    print("=" * 60)


if __name__ == "__main__":
    main()

