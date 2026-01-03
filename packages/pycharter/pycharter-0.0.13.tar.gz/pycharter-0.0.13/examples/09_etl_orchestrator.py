"""
Example: Using the Generic ETL Orchestrator

This example demonstrates how to use the ETLOrchestrator class
to run ETL pipelines from configuration files.
"""

import asyncio
from pycharter.etl_generator import ETLOrchestrator, create_orchestrator


async def example_standalone():
    """Example: Run orchestrator standalone."""
    print("=" * 60)
    print("Example: Standalone ETL Orchestrator")
    print("=" * 60)

    # Create orchestrator from config directory
    orchestrator = ETLOrchestrator(
        config_dir="data/examples/fmp_stock_list"
    )

    # Run the pipeline
    results = await orchestrator.run(dry_run=True)
    
    print(f"\n✓ Pipeline Results:")
    print(f"  Success: {results['success']}")
    print(f"  Extracted: {results['extraction']['records']} records")
    print(f"  Transformed: {results['transformation']['records']} records")
    if 'loading' in results:
        print(f"  Loaded: {results['loading'].get('total', 0)} records")


async def example_airflow():
    """Example: Use orchestrator in Airflow DAG."""
    print("\n" + "=" * 60)
    print("Example: Airflow Integration")
    print("=" * 60)

    # In Airflow DAG:
    code_example = '''
from airflow import DAG
from airflow.operators.python import PythonOperator
from pycharter.etl_generator import ETLOrchestrator
import asyncio

def run_etl_pipeline():
    """Run ETL pipeline from config files."""
    orchestrator = ETLOrchestrator(
        config_dir="/path/to/config"
    )
    asyncio.run(orchestrator.run(dry_run=False))

# In DAG definition:
etl_task = PythonOperator(
    task_id="fmp_stock_list_etl",
    python_callable=run_etl_pipeline,
    dag=dag,
)
'''
    print(code_example)


async def example_docker():
    """Example: Use orchestrator in Docker container."""
    print("\n" + "=" * 60)
    print("Example: Docker Container")
    print("=" * 60)

    # Dockerfile example
    dockerfile_example = '''
FROM python:3.11-slim

WORKDIR /app

# Install pycharter
RUN pip install pycharter

# Copy config files
COPY config/ /app/config/

# Entrypoint script
COPY run_etl.py /app/

CMD ["python", "run_etl.py"]
'''
    
    # run_etl.py example
    script_example = '''
import asyncio
import sys
from pycharter.etl_generator import ETLOrchestrator

async def main():
    config_dir = sys.argv[1] if len(sys.argv) > 1 else "/app/config"
    orchestrator = ETLOrchestrator(config_dir=config_dir)
    await orchestrator.run(dry_run=False)

if __name__ == "__main__":
    asyncio.run(main())
'''
    
    print("Dockerfile:")
    print(dockerfile_example)
    print("\nrun_etl.py:")
    print(script_example)


async def example_custom_config():
    """Example: Use orchestrator with custom config file paths."""
    print("\n" + "=" * 60)
    print("Example: Custom Configuration Files")
    print("=" * 60)

    orchestrator = ETLOrchestrator(
        config_dir="data/examples/fmp_stock_list",
        extract_file="custom_extract.yaml",  # Override default
        load_file="custom_load.yaml",  # Override default
    )

    print("✓ Orchestrator created with custom config files")


if __name__ == "__main__":
    print("\n" + "=" * 60)
    print("ETL Orchestrator Examples")
    print("=" * 60)

    # Run examples
    asyncio.run(example_standalone())
    asyncio.run(example_airflow())
    asyncio.run(example_docker())
    asyncio.run(example_custom_config())

    print("\n" + "=" * 60)
    print("Key Benefits:")
    print("=" * 60)
    print("  ✓ No code generation needed")
    print("  ✓ Runtime configuration reading")
    print("  ✓ Reusable across different pipelines")
    print("  ✓ Easy integration with Airflow/Prefect")
    print("  ✓ Docker-friendly")
    print("  ✓ Can be imported as part of pycharter package")

