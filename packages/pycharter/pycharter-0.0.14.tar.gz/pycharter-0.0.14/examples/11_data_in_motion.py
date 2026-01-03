"""
Example: Validating Data in Motion

This example demonstrates PyCharter's capabilities for validating data
as it flows through pipelines before it reaches persistent storage.

Features demonstrated:
1. Streaming validation with iterators
2. Async validation for non-blocking operations
3. Validation decorators for easy integration
4. Callback-based validation for real-time processing
5. Parallel batch validation for high throughput
6. Kafka integration for message validation
"""

from pycharter import (
    AsyncStreamingValidator,
    StreamingValidator,
    get_model_from_contract,
    validate_async,
    validate_batch_async,
    validate_batch_parallel,
    validate_input,
    validate_output,
    validate_stream,
    validate_with_contract_decorator,
)


def example_streaming_validation():
    """Example 1: Streaming validation with iterators."""
    print("=" * 70)
    print("Example 1: Streaming Validation")
    print("=" * 70)

    # Create a simple contract inline
    from pycharter import from_dict
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "isbn": {"type": "string", "minLength": 10},
            "title": {"type": "string", "minLength": 1},
            "author": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        },
        "required": ["isbn", "title", "author"]
    }
    
    BookModel = from_dict(schema, "Book")

    # Create a data generator (simulating streaming data)
    def data_generator():
        yield {"isbn": "1234567890", "title": "Book 1", "author": {"name": "Author 1"}}
        yield {"isbn": "0987654321", "title": "Book 2", "author": {"name": "Author 2"}}
        yield {"isbn": "invalid", "title": ""}  # Invalid data

    # Validate stream
    print("\nValidating data stream:")
    for result in validate_stream(BookModel, data_generator(), yield_invalid=True):
        if result.is_valid:
            print(f"  ✓ Valid: {result.data.title}")
        else:
            print(f"  ✗ Invalid: {result.errors[:1]}")


def example_async_validation():
    """Example 2: Async validation for non-blocking operations."""
    print("\n" + "=" * 70)
    print("Example 2: Async Validation")
    print("=" * 70)

    import asyncio

    async def async_example():
        from pycharter import from_dict
        
        schema = {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "isbn": {"type": "string", "minLength": 10},
                "title": {"type": "string", "minLength": 1},
                "author": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"]
                }
            },
            "required": ["isbn", "title", "author"]
        }
        
        BookModel = from_dict(schema, "Book")

        # Validate single record asynchronously
        result = await validate_async(
            BookModel, {"isbn": "1234567890", "title": "Book 1", "author": {"name": "Author 1"}}
        )
        print(f"\nAsync validation result: {'Valid' if result.is_valid else 'Invalid'}")

        # Validate batch asynchronously
        data_list = [
            {"isbn": "1234567890", "title": "Book 1", "author": {"name": "Author 1"}},
            {"isbn": "0987654321", "title": "Book 2", "author": {"name": "Author 2"}},
        ]
        results = await validate_batch_async(BookModel, data_list)
        print(f"Async batch validation: {sum(1 for r in results if r.is_valid)}/{len(results)} valid")

    asyncio.run(async_example())


def example_validation_decorators():
    """Example 3: Validation decorators for easy integration."""
    print("\n" + "=" * 70)
    print("Example 3: Validation Decorators")
    print("=" * 70)

    from pycharter import from_dict
    
    # Create a simple contract inline
    contract = {
        "schema": {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "isbn": {"type": "string", "minLength": 10},
                "title": {"type": "string", "minLength": 1},
                "author": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"]
                }
            },
            "required": ["isbn", "title", "author"]
        }
    }
    
    # Generate model for decorators
    BookModel = from_dict(contract["schema"], "Book")

    # Decorator for input validation
    @validate_input(BookModel, param_name="book_data")
    def process_book(book_data):
        """Process a book - input is automatically validated."""
        print(f"  Processing book: {book_data.title}")
        return {"processed": True, "isbn": book_data.isbn}

    # Decorator for output validation
    @validate_output(BookModel)
    def get_book() -> dict:
        """Get a book - output is automatically validated."""
        return {"isbn": "1234567890", "title": "Valid Book", "author": {"name": "Author"}}

    # Decorator for both input and output
    @validate_with_contract_decorator(contract)
    def transform_book(book_data) -> dict:
        """Transform a book - both input and output are validated."""
        return {"isbn": book_data.isbn, "title": book_data.title.upper(), "author": book_data.author}

    print("\nTesting input validation:")
    try:
        process_book({"isbn": "1234567890", "title": "Test Book", "author": {"name": "Author"}})
        print("  ✓ Input validation successful")
    except Exception as e:
        print(f"  ✗ Error: {e}")

    print("\nTesting output validation:")
    try:
        result = get_book()
        print(f"  ✓ Output validation successful: {result.get('isbn')}")
    except Exception as e:
        print(f"  ✗ Error: {e}")


def example_callback_validation():
    """Example 4: Callback-based validation for real-time processing."""
    print("\n" + "=" * 70)
    print("Example 4: Callback-Based Validation")
    print("=" * 70)

    from pycharter import from_dict
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "isbn": {"type": "string", "minLength": 10},
            "title": {"type": "string", "minLength": 1},
            "author": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        },
        "required": ["isbn", "title", "author"]
    }
    
    BookModel = from_dict(schema, "Book")

    # Define callbacks
    def handle_valid(data):
        print(f"  ✓ Valid record: {data.title} - sending to database")

    def handle_invalid(result):
        print(f"  ✗ Invalid record: {result.errors[:1]} - sending to DLQ")

    # Create streaming validator with callbacks
    validator = StreamingValidator(
        BookModel, on_valid=handle_valid, on_invalid=handle_invalid
    )

    # Validate data with callbacks
    print("\nValidating with callbacks:")
    data_list = [
        {"isbn": "1234567890", "title": "Book 1", "author": {"name": "Author 1"}},
        {"isbn": "invalid", "title": ""},  # Invalid
        {"isbn": "0987654321", "title": "Book 2", "author": {"name": "Author 2"}},
    ]

    for data in data_list:
        validator.validate_record(data)

    print(f"\nValidator stats:")
    print(f"  Total validations: {validator.validation_count}")
    print(f"  Valid: {validator.valid_count}")
    print(f"  Invalid: {validator.invalid_count}")
    print(f"  Success rate: {validator.success_rate:.2%}")


def example_parallel_validation():
    """Example 5: Parallel batch validation for high throughput."""
    print("\n" + "=" * 70)
    print("Example 5: Parallel Batch Validation")
    print("=" * 70)

    from pycharter import from_dict
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "isbn": {"type": "string", "minLength": 10},
            "title": {"type": "string", "minLength": 1},
            "author": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        },
        "required": ["isbn", "title", "author"]
    }
    
    BookModel = from_dict(schema, "Book")

    # Create large dataset
    large_data = [
        {"isbn": f"{i:010d}", "title": f"Book {i}", "author": {"name": f"Author {i}"}}
        for i in range(100)
    ]  # Reduced from 1000 for faster example execution

    print(f"\nValidating {len(large_data)} records in parallel...")
    results = validate_batch_parallel(
        BookModel, large_data, max_workers=4, chunk_size=25
    )

    valid_count = sum(1 for r in results if r.is_valid)
    print(f"  Valid: {valid_count}/{len(results)}")
    print(f"  Invalid: {len(results) - valid_count}/{len(results)}")


def example_streaming_validator():
    """Example 6: Using StreamingValidator for optimized streaming."""
    print("\n" + "=" * 70)
    print("Example 6: StreamingValidator (Optimized)")
    print("=" * 70)

    from pycharter import from_dict
    
    schema = {
        "type": "object",
        "version": "1.0.0",
        "properties": {
            "isbn": {"type": "string", "minLength": 10},
            "title": {"type": "string", "minLength": 1},
            "author": {
                "type": "object",
                "properties": {"name": {"type": "string"}},
                "required": ["name"]
            }
        },
        "required": ["isbn", "title", "author"]
    }
    
    BookModel = from_dict(schema, "Book")

    # Create streaming validator (model is cached)
    validator = StreamingValidator(BookModel)

    def data_stream():
        for i in range(10):
            yield {"isbn": f"{i:010d}", "title": f"Book {i}", "author": {"name": f"Author {i}"}}

    print("\nValidating stream with cached model:")
    valid_count = 0
    for result in validator.validate_stream(data_stream()):
        if result.is_valid:
            valid_count += 1

    print(f"  Valid records: {valid_count}")
    print(f"  Total validations: {validator.validation_count}")


def example_kafka_integration():
    """Example 7: Kafka integration (requires kafka-python)."""
    print("\n" + "=" * 70)
    print("Example 7: Kafka Integration")
    print("=" * 70)

    try:
        from pycharter.integrations import KafkaValidator
        from pycharter import from_dict
        
        # Create a simple contract inline
        schema = {
            "type": "object",
            "version": "1.0.0",
            "properties": {
                "isbn": {"type": "string", "minLength": 10},
                "title": {"type": "string", "minLength": 1},
                "author": {
                    "type": "object",
                    "properties": {"name": {"type": "string"}},
                    "required": ["name"]
                }
            },
            "required": ["isbn", "title", "author"]
        }
        
        BookModel = from_dict(schema, "Book")

        print("\nKafka validator created (not connecting in example):")
        # KafkaValidator expects a contract (file path, dict, or ContractMetadata), not a model
        contract_dict = {
            "schema": schema
        }
        validator = KafkaValidator(
            contract=contract_dict,
            kafka_config={"bootstrap_servers": "localhost:9092"},
        )
        print("  ✓ KafkaValidator initialized")

        print("\n  In real usage:")
        print("    for result in validator.consume_and_validate('book-topic'):")
        print("        if result.is_valid:")
        print("            process(result.data)")
        print("        else:")
        print("            send_to_dlq(result)")

    except ImportError:
        print("\n  ⚠ Kafka integration not available.")
        print("  Install with: pip install kafka-python")
    except Exception as e:
        print(f"\n  ⚠ Error: {e}")
        print("  Kafka integration may require additional setup")


if __name__ == "__main__":
    print("\n" + "=" * 70)
    print("PyCharter: Data in Motion Validation Examples")
    print("=" * 70)

    try:
        example_streaming_validation()
        example_async_validation()
        example_validation_decorators()
        example_callback_validation()
        example_parallel_validation()
        example_streaming_validator()
        example_kafka_integration()

        print("\n" + "=" * 70)
        print("✓ All examples completed!")
        print("=" * 70)

    except Exception as e:
        print(f"\n✗ Error running examples: {e}")
        import traceback

        traceback.print_exc()

