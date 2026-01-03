#!/usr/bin/env python3
"""
Example 8: Quality Assurance Pipeline

Demonstrates how to use PyCharter's quality assurance module to:
1. Run quality checks against data contracts
2. Calculate quality metrics
3. Track violations
4. Profile data characteristics
5. Check quality thresholds
6. Persist metrics and violations to database
7. Generate quality reports
"""

from pycharter import (
    QualityCheck,
    QualityCheckOptions,
    QualityThresholds,
    DataProfiler,
    InMemoryMetadataStore,
)


def example_basic_quality_check():
    """Basic quality check example."""
    print("=" * 70)
    print("Example 8a: Basic Quality Check")
    print("=" * 70)

    # Define a simple contract
    contract = {
        "schema": {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "user_id": {"type": "string"},
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
                "age": {"type": "integer", "minimum": 0, "maximum": 150},
            },
            "required": ["user_id", "name", "email"],
        }
    }

    # Sample data with some quality issues
    data = [
        {"user_id": "1", "name": "Alice", "email": "alice@example.com", "age": 30},  # Valid
        {"user_id": "2", "name": "Bob", "email": "invalid-email", "age": 25},  # Invalid email
        {"user_id": "3", "name": "", "email": "charlie@example.com", "age": 200},  # Invalid: empty name, age > 150
        {"user_id": "4", "email": "dave@example.com"},  # Missing required field: name
    ]

    # Create quality check instance
    check = QualityCheck()

    # Run quality check
    report = check.run(
        contract=contract,
        data=data,
        options=QualityCheckOptions(
            calculate_metrics=True,
            record_violations=True,
            include_field_metrics=True,
        ),
    )

    # Display results
    print(f"\nQuality Check Results:")
    print(f"  Records Checked: {report.record_count}")
    print(f"  Valid Records: {report.valid_count}")
    print(f"  Invalid Records: {report.invalid_count}")
    print(f"  Violations: {report.violation_count}")

    if report.quality_score:
        print(f"\nQuality Metrics:")
        print(f"  Overall Score: {report.quality_score.overall_score:.2f}/100")
        print(f"  Accuracy: {report.quality_score.accuracy:.2%}")
        print(f"  Completeness: {report.quality_score.completeness:.2%}")
        print(f"  Violation Rate: {report.quality_score.violation_rate:.2%}")

        if report.field_metrics:
            print(f"\nField-Level Metrics:")
            for field_name, metrics in report.field_metrics.items():
                print(f"  {field_name}:")
                print(f"    Completeness: {metrics.completeness:.2%}")
                print(f"    Violation Rate: {metrics.violation_rate:.2%}")

    print(f"\nPassed: {'✓ Yes' if report.passed else '✗ No'}")


def example_quality_check_with_thresholds():
    """Quality check with threshold monitoring."""
    print("\n" + "=" * 70)
    print("Example 8b: Quality Check with Thresholds")
    print("=" * 70)

    contract = {
        "schema": {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "product_id": {"type": "string"},
                "name": {"type": "string", "minLength": 1},
                "price": {"type": "number", "minimum": 0},
            },
            "required": ["product_id", "name", "price"],
        }
    }

    data = [
        {"product_id": "p1", "name": "Product 1", "price": 10.99},
        {"product_id": "p2", "name": "Product 2", "price": 20.50},
        {"product_id": "p3", "name": "", "price": -5.0},  # Invalid
    ]

    # Define quality thresholds
    thresholds = QualityThresholds(
        min_overall_score=95.0,
        max_violation_rate=0.05,  # 5%
        min_completeness=0.95,  # 95%
        min_accuracy=0.95,  # 95%
    )

    check = QualityCheck()
    report = check.run(
        contract=contract,
        data=data,
        options=QualityCheckOptions(
            calculate_metrics=True,
            check_thresholds=True,
            thresholds=thresholds,
        ),
    )

    print(f"\nQuality Score: {report.quality_score.overall_score:.2f}/100")
    print(f"Threshold Breaches: {len(report.threshold_breaches)}")

    if report.threshold_breaches:
        print("\n⚠ Threshold Breaches Detected:")
        for breach in report.threshold_breaches:
            print(f"  - {breach}")
    else:
        print("\n✓ All thresholds met")

    print(f"Passed: {'✓ Yes' if report.passed else '✗ No'}")


def example_quality_check_with_store():
    """Quality check using metadata store."""
    print("\n" + "=" * 70)
    print("Example 8c: Quality Check with Metadata Store")
    print("=" * 70)

    # Create in-memory store
    store = InMemoryMetadataStore()
    store.connect()

    # Store a schema
    schema_id = store.store_schema(
        schema_name="user",
        schema={
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "user_id": {"type": "string"},
                "name": {"type": "string", "minLength": 1},
                "email": {"type": "string", "format": "email"},
            },
            "required": ["user_id", "name", "email"],
        },
        version="1.0.0",
    )

    data = [
        {"user_id": "1", "name": "Alice", "email": "alice@example.com"},
        {"user_id": "2", "name": "Bob", "email": "invalid"},
    ]

    check = QualityCheck(store=store)
    report = check.run(
        schema_id=schema_id,
        data=data,
        options=QualityCheckOptions(
            calculate_metrics=True,
            record_violations=True,
        ),
    )

    print(f"\nQuality Score: {report.quality_score.overall_score:.2f}/100")
    print(f"Valid: {report.valid_count}/{report.record_count}")

    # Query violations
    violations = check.violation_tracker.get_violations(schema_id=schema_id)
    print(f"\nViolations Found: {len(violations)}")
    for violation in violations:
        print(f"  - Record {violation.record_id}: {violation.field_violations[0]['error_message']}")

    store.disconnect()


def example_data_profiling():
    """Standalone data profiling example."""
    print("\n" + "=" * 70)
    print("Example 8d: Data Profiling")
    print("=" * 70)

    data = [
        {"name": "Alice", "age": 30, "score": 95.5, "active": True},
        {"name": "Bob", "age": 25, "score": 87.2, "active": True},
        {"name": "Charlie", "age": None, "score": 92.0, "active": False},
        {"name": "David", "age": 35, "score": None, "active": True},
    ]

    profiler = DataProfiler()
    profile = profiler.profile(data)

    print(f"\nProfile Results:")
    print(f"  Record Count: {profile['record_count']}")
    print(f"  Average Completeness: {profile['overall_stats']['average_completeness']:.2%}")

    print(f"\nField Profiles:")
    for field_name, field_profile in profile['field_profiles'].items():
        print(f"\n  {field_name}:")
        print(f"    Type: {field_profile['type']}")
        print(f"    Completeness: {field_profile['completeness']:.2%}")
        print(f"    Null Count: {field_profile['null_count']}")
        if 'mean' in field_profile:
            print(f"    Mean: {field_profile['mean']:.2f}")
        if 'min' in field_profile:
            print(f"    Range: {field_profile['min']} - {field_profile['max']}")


def example_quality_check_with_deduplication():
    """Quality check with data version tracking and deduplication."""
    print("\n" + "=" * 70)
    print("Example 8e: Quality Check with Deduplication")
    print("=" * 70)

    contract = {
        "schema": {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "id": {"type": "string"},
                "value": {"type": "number"},
            },
            "required": ["id", "value"],
        }
    }

    data = [
        {"id": "1", "value": 10},
        {"id": "2", "value": 20},
    ]

    check = QualityCheck()
    
    # First check
    print("\nRunning first quality check...")
    report1 = check.run(
        contract=contract,
        data=data,
        options=QualityCheckOptions(
            calculate_metrics=True,
            record_violations=True,
            data_version="v1.0.0",
            data_source="test_data.json",
            deduplicate_violations=True,
        ),
    )
    print(f"  Quality Score: {report1.quality_score.overall_score:.2f}/100")
    print(f"  Violations: {report1.violation_count}")

    # Second check with same data (should deduplicate)
    print("\nRunning second check with same data...")
    report2 = check.run(
        contract=contract,
        data=data,  # Same data
        options=QualityCheckOptions(
            calculate_metrics=True,
            record_violations=True,
            data_version="v1.0.0",  # Same version
            data_source="test_data.json",
            deduplicate_violations=True,
            skip_if_unchanged=True,  # Skip if data unchanged
        ),
    )
    print(f"  Quality Score: {report2.quality_score.overall_score:.2f}/100")
    print(f"  Violations: {report2.violation_count}")
    print(f"  Note: With skip_if_unchanged=True, metrics won't be duplicated")


if __name__ == "__main__":
    example_basic_quality_check()
    example_quality_check_with_thresholds()
    example_quality_check_with_store()
    example_data_profiling()
    example_quality_check_with_deduplication()

