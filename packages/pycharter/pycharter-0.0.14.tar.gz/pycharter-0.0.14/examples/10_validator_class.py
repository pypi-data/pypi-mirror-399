"""
Example: Using the Validator Class

This example demonstrates how to use the Validator class
to perform validation from contract artifacts.
"""

from pycharter.runtime_validator import Validator, create_validator


def example_standalone():
    """Example: Use validator standalone."""
    print("=" * 60)
    print("Example: Standalone Validator")
    print("=" * 60)

    # Create validator from contract directory
    validator = Validator(
        contract_dir="data/examples/fmp_stock_list"
    )

    # Validate single record
    result = validator.validate({
        "symbol": "AAPL",
        "company_name": "Apple Inc.",
    })
    
    print(f"\n✓ Validation Result:")
    print(f"  Valid: {result.is_valid}")
    if result.is_valid:
        print(f"  Data: {result.data}")
    else:
        print(f"  Errors: {result.errors}")


def example_batch_validation():
    """Example: Validate batch of records."""
    print("\n" + "=" * 60)
    print("Example: Batch Validation")
    print("=" * 60)

    validator = create_validator("data/examples/fmp_stock_list")
    
    records = [
        {"symbol": "AAPL", "company_name": "Apple Inc."},
        {"symbol": "MSFT", "company_name": "Microsoft Corporation"},
        {"symbol": "", "company_name": "Invalid"},  # Invalid: empty symbol
    ]
    
    results = validator.validate_batch(records)
    
    valid_count = sum(1 for r in results if r.is_valid)
    invalid_count = sum(1 for r in results if not r.is_valid)
    
    print(f"\n✓ Batch Validation Results:")
    print(f"  Total: {len(results)}")
    print(f"  Valid: {valid_count}")
    print(f"  Invalid: {invalid_count}")
    
    for i, result in enumerate(results):
        status = "✓" if result.is_valid else "✗"
        print(f"  {status} Record {i+1}: {result.is_valid}")


def example_airflow_integration():
    """Example: Use validator in Airflow DAG."""
    print("\n" + "=" * 60)
    print("Example: Airflow Integration")
    print("=" * 60)

    code_example = '''
from airflow.operators.python import PythonOperator
from pycharter.runtime_validator import Validator

def validate_data():
    """Validate data in Airflow task."""
    validator = Validator(contract_dir="/path/to/contract")
    
    # Get data from previous task
    data = get_data_from_previous_task()
    
    # Validate
    result = validator.validate(data)
    if not result.is_valid:
        raise ValueError(f"Validation failed: {result.errors}")
    
    return result.data

task = PythonOperator(
    task_id="validate_data",
    python_callable=validate_data,
    dag=dag,
)
'''
    print(code_example)


def example_docker_integration():
    """Example: Use validator in Docker container."""
    print("\n" + "=" * 60)
    print("Example: Docker Integration")
    print("=" * 60)

    code_example = '''
# In your validation service
from pycharter.runtime_validator import Validator

# Initialize validator once (can be reused)
validator = Validator(contract_dir="/app/contracts/fmp_stock_list")

# Validate incoming data
@app.post("/validate")
async def validate_endpoint(data: dict):
    result = validator.validate(data)
    return {
        "valid": result.is_valid,
        "data": result.data if result.is_valid else None,
        "errors": result.errors if not result.is_valid else None,
    }
'''
    print(code_example)


def example_custom_contract_files():
    """Example: Use validator with custom contract file paths."""
    print("\n" + "=" * 60)
    print("Example: Custom Contract Files")
    print("=" * 60)

    validator = Validator(
        contract_dir="data/examples/fmp_stock_list",
        schema_file="custom_schema.yaml",  # Override default
        validation_rules_file="custom_validation.yaml",  # Override default
    )

    print("✓ Validator created with custom contract files")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("Validator Class Examples")
    print("=" * 60)

    # Run examples
    example_standalone()
    example_batch_validation()
    example_airflow_integration()
    example_docker_integration()
    example_custom_contract_files()

    print("\n" + "=" * 60)
    print("Key Benefits:")
    print("=" * 60)
    print("  ✓ No code generation needed")
    print("  ✓ Runtime contract loading")
    print("  ✓ Reusable across different contracts")
    print("  ✓ Easy integration with Airflow/Prefect")
    print("  ✓ Docker-friendly")
    print("  ✓ Can be imported as part of pycharter package")
    print("  ✓ Supports single and batch validation")

