"""
Generic ETL Orchestrator - Runtime ETL pipeline execution from contract artifacts.

This orchestrator reads contract artifacts (schema, coercion rules, validation rules)
and ETL configuration files (extract, transform, load) and executes the ETL pipeline
dynamically using streaming mode for memory-efficient processing.
"""

import asyncio
import gc
import warnings
from datetime import date, datetime, timedelta
from pathlib import Path
from typing import Any, AsyncIterator, Callable, Dict, List, Optional, Tuple

import yaml

from pycharter.contract_parser import ContractMetadata, parse_contract_file
from pycharter.etl_generator.checkpoint import CheckpointManager
from pycharter.etl_generator.database import (
    get_database_connection,
    load_data,
)
from pycharter.etl_generator.extraction import extract_with_pagination_streaming
from pycharter.etl_generator.progress import ETLProgress, ProgressTracker
from pycharter.utils.value_injector import resolve_values

# Optional dependency for memory monitoring
try:
    import psutil
    PSUTIL_AVAILABLE = True
except ImportError:
    PSUTIL_AVAILABLE = False


# ============================================================================
# CONSTANTS
# ============================================================================

COMPUTED_DATETIME_NOW = "@now"
COMPUTED_DATETIME_UTC_NOW = "@utcnow"
COMPUTED_WEEK_START = "@week_start"
COMPUTED_WEEK_END = "@week_end"
DEFAULT_BATCH_SIZE = 1000
DEFAULT_MAX_DEPTH = 10
DEFAULT_SEPARATOR = "_"

# Datetime parsing formats (in order of preference)
DATETIME_FORMATS = [
    '%Y-%m-%dT%H:%M:%S',
    '%Y-%m-%d %H:%M:%S',
    '%Y-%m-%d'
]


class ETLOrchestrator:
    """
    Generic ETL Orchestrator that executes pipelines from contract artifacts and ETL configs.
    
    Processes data in streaming mode: Extract-Batch → Transform-Batch → Load-Batch.
    This ensures constant memory usage regardless of dataset size.
    
    Example:
        >>> from pycharter.etl_generator import ETLOrchestrator
        >>> orchestrator = ETLOrchestrator(contract_dir="data/examples/my_contract")
        >>> await orchestrator.run()
    """
    
    def __init__(
        self,
        contract_dir: Optional[str] = None,
        contract_file: Optional[str] = None,
        contract_dict: Optional[Dict[str, Any]] = None,
        contract_metadata: Optional[ContractMetadata] = None,
        checkpoint_dir: Optional[str] = None,
        progress_callback: Optional[Callable[[ETLProgress], None]] = None,
        verbose: bool = True,
        max_memory_mb: Optional[int] = None,
        config_context: Optional[Dict[str, Any]] = None,
        # ETL config options (alternative to loading from contract_dir)
        extract_config: Optional[Dict[str, Any]] = None,
        transform_config: Optional[Dict[str, Any]] = None,
        load_config: Optional[Dict[str, Any]] = None,
        extract_file: Optional[str] = None,
        transform_file: Optional[str] = None,
        load_file: Optional[str] = None,
    ):
        """
        Initialize the ETL orchestrator with contract artifacts.
        
        Args:
            contract_dir: Directory containing contract files and ETL configs
            contract_file: Path to complete contract file (YAML/JSON)
            contract_dict: Contract as dictionary
            contract_metadata: ContractMetadata object (from parse_contract)
            checkpoint_dir: Directory for checkpoint files (None = disabled)
            progress_callback: Optional callback for progress updates
            verbose: If True, print progress to stdout
            max_memory_mb: Maximum memory usage in MB (None = no limit)
            config_context: Optional context dictionary for value injection.
                          Values in this dict have highest priority when resolving
                          variables in config files (e.g., ${VAR}).
                          Useful for injecting application-level settings.
            extract_config: Optional extract configuration as dictionary.
                           If provided, overrides extract.yaml from contract_dir.
            transform_config: Optional transform configuration as dictionary.
                            If provided, overrides transform.yaml from contract_dir.
            load_config: Optional load configuration as dictionary.
                        If provided, overrides load.yaml from contract_dir.
            extract_file: Optional path to extract.yaml file.
                         If provided, overrides extract.yaml from contract_dir.
            transform_file: Optional path to transform.yaml file.
                           If provided, overrides transform.yaml from contract_dir.
            load_file: Optional path to load.yaml file.
                      If provided, overrides load.yaml from contract_dir.
        
        Note:
            ETL config priority: direct dict > file path > contract_dir
            If contract_dir is not provided, you must provide extract_config/transform_config/load_config
            or extract_file/transform_file/load_file.
        """
        self.contract_dir: Optional[Path] = None
        self.schema: Optional[Dict[str, Any]] = None
        self.coercion_rules: Dict[str, Any] = {}
        self.validation_rules: Dict[str, Any] = {}
        self.input_params: Dict[str, Dict[str, Any]] = {}
        
        # Configuration context for value injection
        self.config_context = config_context or {}
        
        # Store ETL config parameters for later loading
        self._extract_config_param = extract_config
        self._transform_config_param = transform_config
        self._load_config_param = load_config
        self._extract_file_param = extract_file
        self._transform_file_param = transform_file
        self._load_file_param = load_file
        
        # Enhanced features
        self.checkpoint_manager = CheckpointManager(checkpoint_dir)
        self.progress_tracker = ProgressTracker(progress_callback, verbose)
        self.max_memory_mb = max_memory_mb
        self.process = None
        if PSUTIL_AVAILABLE:
            self.process = psutil.Process()
        
        # Load contract artifacts
        if contract_metadata:
            self._load_from_metadata(contract_metadata)
        elif contract_dict:
            self._load_from_dict(contract_dict)
        elif contract_file:
            file_path = Path(contract_file)
            self.contract_dir = file_path.parent
            self._load_from_file(file_path)
        elif contract_dir:
            self.contract_dir = Path(contract_dir)
            self._load_from_directory(self.contract_dir)
        else:
            # If no contract source provided, we still need contract_dir for ETL configs
            # unless all ETL configs are provided directly
            if not (extract_config or extract_file) and not contract_dir:
                raise ValueError(
                    "Must provide one of: contract_dir, contract_file, contract_dict, "
                    "contract_metadata, or extract_config/extract_file"
                )
            # Set contract_dir to None if not provided (ETL configs will be loaded from params)
            self.contract_dir = None
        
        # Load ETL configurations (extract, transform, load)
        # Priority: direct dict > file path > contract_dir
        self._load_etl_configs()
    
    # ============================================================================
    # INITIALIZATION AND CONFIGURATION LOADING
    # ============================================================================
    
    def _load_from_metadata(self, metadata: ContractMetadata) -> None:
        """Load contract from ContractMetadata object."""
        self.schema = metadata.schema
        self.coercion_rules = metadata.coercion_rules or {}
        self.validation_rules = metadata.validation_rules or {}
    
    def _load_from_dict(self, contract: Dict[str, Any]) -> None:
        """Load contract from dictionary."""
        self.schema = contract.get("schema")
        if not self.schema:
            raise ValueError("Contract dictionary must contain 'schema'")
        
        self.coercion_rules = self._extract_rules(contract.get("coercion_rules", {}))
        self.validation_rules = self._extract_rules(contract.get("validation_rules", {}))
    
    @staticmethod
    def _extract_rules(rules_data: Any) -> Dict[str, Any]:
        """Extract rules from various formats."""
        if not isinstance(rules_data, dict):
            return {}
        
        if "rules" in rules_data:
            return rules_data["rules"]
        elif not any(k in rules_data for k in ["version", "description", "title"]):
            return rules_data
        else:
            return {}
    
    def _load_from_file(self, file_path: Path) -> None:
        """Load contract from file."""
        contract_metadata = parse_contract_file(str(file_path))
        self._load_from_metadata(contract_metadata)
    
    def _load_from_directory(self, contract_dir: Path) -> None:
        """Load contract components from directory."""
        if not contract_dir.exists():
            raise ValueError(f"Contract directory not found: {contract_dir}")
        
        # Load schema (required) - support both YAML and JSON
        schema_path_yaml = contract_dir / "schema.yaml"
        schema_path_json = contract_dir / "schema.json"
        
        schema_path = None
        if schema_path_yaml.exists():
            schema_path = schema_path_yaml
        elif schema_path_json.exists():
            schema_path = schema_path_json
        else:
            # Try to find JSON schema files with dataset name pattern
            dataset_name = contract_dir.name
            possible_json_schemas = [
                contract_dir / f"{dataset_name}_schema.json",
                contract_dir / f"{dataset_name}.schema.json",
                contract_dir / "schema.json",
            ]
            for possible_path in possible_json_schemas:
                if possible_path.exists():
                    schema_path = possible_path
                    break
        
        if schema_path and schema_path.exists():
            if schema_path.suffix == '.json':
                import json
                with open(schema_path, 'r', encoding='utf-8') as f:
                    self.schema = json.load(f)
            else:
                self.schema = self._load_yaml(schema_path)
        else:
            raise ValueError(
                f"Schema file not found in {contract_dir}. "
                f"Expected: schema.yaml, schema.json, or {contract_dir.name}_schema.json"
            )
        
        # Load coercion rules (optional)
        coercion_path = contract_dir / "coercion_rules.yaml"
        if coercion_path.exists():
            coercion_data = self._load_yaml(coercion_path)
            self.coercion_rules = self._extract_rules(coercion_data)
        
        # Load validation rules (optional)
        validation_path = contract_dir / "validation_rules.yaml"
        if validation_path.exists():
            validation_data = self._load_yaml(validation_path)
            self.validation_rules = self._extract_rules(validation_data)
    
    def _load_etl_configs(self) -> None:
        """
        Load ETL configuration files (extract, transform, load).
        
        Priority order:
        1. Direct dictionary parameters (extract_config, transform_config, load_config)
        2. File path parameters (extract_file, transform_file, load_file)
        3. Files in contract_dir (extract.yaml, transform.yaml, load.yaml)
        """
        # Load extract config (required)
        self.extract_config = self._load_single_config(
            config_param=self._extract_config_param,
            file_param=self._extract_file_param,
            default_filename="extract.yaml",
            required=True,
            config_name="Extract"
        )
        
        # Load transform config (optional)
        self.transform_config = self._load_single_config(
            config_param=self._transform_config_param,
            file_param=self._transform_file_param,
            default_filename="transform.yaml",
            required=False,
            config_name="Transform"
        )
        
        # Load load config (required)
        self.load_config = self._load_single_config(
            config_param=self._load_config_param,
            file_param=self._load_file_param,
            default_filename="load.yaml",
            required=True,
            config_name="Load"
        )
        
        # Parse input parameters from extract config
        self._parse_input_params()
        
        if not self.schema:
            raise ValueError("Schema not loaded")
    
    def _load_single_config(
        self,
        config_param: Optional[Dict[str, Any]],
        file_param: Optional[str],
        default_filename: str,
        required: bool,
        config_name: str,
    ) -> Dict[str, Any]:
        """
        Load a single ETL config following priority order.
        
        Args:
            config_param: Direct dictionary config (highest priority)
            file_param: File path to config (medium priority)
            default_filename: Default filename in contract_dir (lowest priority)
            required: Whether this config is required
            config_name: Name for error messages
            
        Returns:
            Loaded config dictionary (empty dict if not required and not found)
        """
        # Priority 1: Direct dictionary
        if config_param is not None:
            return config_param
        
        # Priority 2: File path
        if file_param:
            config_path = Path(file_param)
            if not config_path.exists():
                raise ValueError(f"{config_name} config file not found: {config_path}")
            config = self._load_yaml(config_path)
            # Set contract_dir from file if not already set
            if not self.contract_dir:
                self.contract_dir = config_path.parent
            return config
        
        # Priority 3: From contract_dir
        if self.contract_dir and self.contract_dir.exists():
            config_path = self.contract_dir / default_filename
            if config_path.exists():
                return self._load_yaml(config_path)
        
        # Handle missing config
        if required:
            raise ValueError(
                f"{config_name} configuration not found. Provide one of: "
                f"{config_name.lower()}_config (dict), {config_name.lower()}_file (path), "
                f"or contract_dir with {default_filename}"
            )
        
        return {}
    
    def _parse_input_params(self) -> None:
        """Parse input parameters from extract config."""
        input_params_config = self.extract_config.get('input_params', [])
        if isinstance(input_params_config, list):
            self.input_params = {name: {} for name in input_params_config}
        elif isinstance(input_params_config, dict):
            self.input_params = input_params_config
        else:
            self.input_params = {}
    
    def _load_yaml(self, file_path: Path) -> Dict[str, Any]:
        """Load YAML file, return empty dict if not found."""
        if not file_path.exists():
            return {}
        with open(file_path, 'r', encoding='utf-8') as f:
            return yaml.safe_load(f) or {}
    
    def _prepare_params(self, **kwargs) -> Tuple[Dict[str, Any], Dict[str, Any]]:
        """Prepare params and headers from config and kwargs."""
        params = self.extract_config.get('params', {}).copy()
        headers = self.extract_config.get('headers', {})
        
        # Get parameter mapping from extract config (maps input param names to API param names)
        param_mapping = self.extract_config.get('param_mapping', {})
        
        # Merge input arguments
        for param_name, param_value in kwargs.items():
            if param_name in self.input_params:
                # Check if there's a mapping for this parameter
                api_param_name = param_mapping.get(param_name, param_name)
                params[api_param_name] = param_value
            else:
                warnings.warn(
                    f"Unknown input parameter '{param_name}'. "
                    f"Available: {list(self.input_params.keys())}",
                    UserWarning
                )
        
        # Validate required input parameters and apply defaults for optional ones
        for param_name, param_meta in self.input_params.items():
            if param_meta.get('required', False):
                # Check if input parameter was provided in kwargs
                if param_name not in kwargs:
                    raise ValueError(
                        f"Required input parameter '{param_name}' not provided. "
                        f"Please provide: {param_name}=value"
                    )
            else:
                # Apply default value for optional parameters if not provided
                if param_name not in kwargs and 'default' in param_meta:
                    default_value = param_meta.get('default')
                    # Only add if default is not None (None means truly optional)
                    if default_value is not None:
                        api_param_name = param_mapping.get(param_name, param_name)
                        params[api_param_name] = default_value
        
        # Resolve values with config context
        source_file = str(self.contract_dir / "extract.yaml") if self.contract_dir else None
        params = resolve_values(params, context=self.config_context, source_file=source_file)
        headers = resolve_values(headers, context=self.config_context, source_file=source_file)
        
        return params, headers
    
    # ============================================================================
    # EXTRACTION
    # ============================================================================
    
    async def extract(
        self,
        batch_size: Optional[int] = None,
        max_records: Optional[int] = None,
        **kwargs
    ) -> AsyncIterator[List[Dict[str, Any]]]:
        """
        Extract data in batches using async generator.
        
        Yields batches of records for memory-efficient processing.
        
        Args:
            batch_size: Number of records per batch (defaults to extract.yaml config)
            max_records: Maximum total records to extract (None = all)
            **kwargs: Input parameters defined in extract.yaml's input_params section
        
        Yields:
            Batches of extracted records (lists of dictionaries)
        
        Example:
            >>> async for batch in orchestrator.extract(symbol="AAPL"):
            ...     print(f"Extracted {len(batch)} records")
        """
        if batch_size is None:
            batch_size = self.extract_config.get('batch_size', DEFAULT_BATCH_SIZE)
        
        params, headers = self._prepare_params(**kwargs)
        
        async for batch in extract_with_pagination_streaming(
            self.extract_config, params, headers, self.contract_dir, batch_size, max_records, config_context=self.config_context
        ):
            yield batch
    
    # ============================================================================
    # TRANSFORMATION
    # ============================================================================
    
    def transform(self, raw_data: List[Dict[str, Any]], **kwargs) -> List[Dict[str, Any]]:
        """
        Transform extracted data according to transformation rules.
        
        Transformation steps (in order):
        1. Rename fields (with optional flattening)
        2. Copy remaining fields (with optional flattening)
        3. Add computed fields from kwargs
        4. Apply type conversions
        5. Apply fill_null rules
        6. Drop specified fields
        
        Args:
            raw_data: Raw data from extraction
            **kwargs: Additional transformation parameters
        
        Returns:
            Transformed data
        """
        if not self.transform_config:
            return raw_data
        
        # Extract transformation rules once
        transform_rules = self._extract_transform_rules()
        
        transformed_data = []
        for record in raw_data:
            transformed_record = self._transform_single_record(
                record, transform_rules, **kwargs
            )
            transformed_data.append(transformed_record)
        
        return transformed_data
    
    def _extract_transform_rules(self) -> Dict[str, Any]:
        """Extract and return all transformation rules from config."""
        return {
            'rename': self.transform_config.get('rename', {}),
            'flatten': self.transform_config.get('flatten', {}),
            'type': self.transform_config.get('type', {}),
            'fill_null': self.transform_config.get('fill_null', {}),
            'drop': self.transform_config.get('drop', []),
        }
    
    def _transform_single_record(
        self,
        record: Dict[str, Any],
        transform_rules: Dict[str, Any],
        **kwargs
    ) -> Dict[str, Any]:
        """Transform a single record through all transformation steps."""
        rename_rules = transform_rules['rename']
        flatten_rules = transform_rules['flatten']
        type_rules = transform_rules['type']
        fill_null_rules = transform_rules['fill_null']
        drop_fields = transform_rules['drop']
        
        transformed_record = {}
        
        # Step 1: Apply rename transformations (with flattening if configured)
        transformed_record.update(
            self._apply_rename_transformations(record, rename_rules, flatten_rules)
        )
        
        # Step 2: Copy remaining fields (with flattening if configured)
        transformed_record.update(
            self._copy_remaining_fields(record, rename_rules, flatten_rules, drop_fields)
        )
        
        # Step 3: Add computed fields from kwargs
        self._add_computed_fields(transformed_record, **kwargs)
        
        # Step 4: Apply type conversions
        self._apply_type_conversions(transformed_record, type_rules)
        
        # Step 5: Apply fill_null rules
        self._apply_fill_null_rules(transformed_record, fill_null_rules)
        
        # Step 6: Drop specified fields
        self._drop_fields(transformed_record, drop_fields)
        
        return transformed_record
    
    def _apply_rename_transformations(
        self,
        record: Dict[str, Any],
        rename_rules: Dict[str, str],
        flatten_rules: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Apply rename transformations, handling flattening if configured."""
        transformed = {}
        
        for source_field, target_field in rename_rules.items():
            if source_field in record:
                value = record[source_field]
                flattened = self._maybe_flatten_field(source_field, value, flatten_rules)
                if flattened is not None:
                    transformed.update(flattened)
                else:
                    transformed[target_field] = value
            elif target_field in record:
                transformed[target_field] = record[target_field]
        
        return transformed
    
    def _copy_remaining_fields(
        self,
        record: Dict[str, Any],
        rename_rules: Dict[str, str],
        flatten_rules: Dict[str, Any],
        drop_fields: List[str]
    ) -> Dict[str, Any]:
        """Copy remaining fields not in rename rules, handling flattening if configured."""
        transformed = {}
        
        for key, value in record.items():
            if key not in rename_rules and key not in transformed:
                if key not in drop_fields:
                    flattened = self._maybe_flatten_field(key, value, flatten_rules)
                    if flattened is not None:
                        transformed.update(flattened)
                    else:
                        transformed[key] = value
        
        return transformed
    
    def _maybe_flatten_field(
        self,
        field_name: str,
        value: Any,
        flatten_rules: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Flatten a field if it's configured for flattening, otherwise return None.
        
        Returns:
            Flattened dictionary if field should be flattened, None otherwise
        """
        if field_name not in flatten_rules:
            return None
        
        flatten_config = flatten_rules[field_name]
        if not flatten_config.get('enabled', True):
            return None
        
        if isinstance(value, dict):
            return self._flatten_nested_object(value, field_name, flatten_config)
        elif isinstance(value, list):
            return self._flatten_array(value, field_name, flatten_config)
        
        return None
    
    def _add_computed_fields(self, transformed_record: Dict[str, Any], **kwargs) -> None:
        """Add computed fields from kwargs (e.g., direction from type parameter)."""
        if 'type' in kwargs:
            # Map type parameter to direction field
            # This is a common pattern for market movers pipelines
            type_value = kwargs['type']
            type_to_direction = {
                'gainers': 'gainers',
                'losers': 'losers',
                'most_active': 'most_active'
            }
            direction = type_to_direction.get(type_value, type_value)
            transformed_record['direction'] = direction
    
    def _apply_type_conversions(
        self,
        transformed_record: Dict[str, Any],
        type_rules: Dict[str, str]
    ) -> None:
        """Apply type conversions to fields."""
        for field, field_type in type_rules.items():
            if field in transformed_record:
                transformed_record[field] = self._convert_type(
                    transformed_record[field], field_type
                )
    
    def _apply_fill_null_rules(
        self,
        transformed_record: Dict[str, Any],
        fill_null_rules: Dict[str, Any]
    ) -> None:
        """Apply fill_null rules, handling computed datetime values."""
        for field, config in fill_null_rules.items():
            if field not in transformed_record or transformed_record[field] is None:
                default_value = config.get('default') if isinstance(config, dict) else config
                computed_value = self._compute_datetime_value(default_value)
                transformed_record[field] = computed_value if computed_value is not None else default_value
    
    def _compute_datetime_value(self, value: Any) -> Optional[datetime]:
        """
        Compute datetime value from special constants.
        
        Args:
            value: Value to check (may be a computed datetime constant)
            
        Returns:
            Computed datetime if value is a computed constant, None otherwise
        """
        if value == COMPUTED_DATETIME_NOW:
            return datetime.now()
        elif value == COMPUTED_DATETIME_UTC_NOW:
            return datetime.utcnow()
        elif value == COMPUTED_WEEK_START:
            return self._get_week_start()
        elif value == COMPUTED_WEEK_END:
            return self._get_week_end()
        return None
    
    def _get_week_start(self) -> datetime:
        """Calculate Monday of current week (00:00:00 UTC)."""
        now = datetime.utcnow()
        days_since_monday = now.weekday()
        week_start = now - timedelta(days=days_since_monday)
        return week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    
    def _get_week_end(self) -> datetime:
        """Calculate Sunday of current week (23:59:59.999999 UTC)."""
        week_start = self._get_week_start()
        return week_start + timedelta(days=6, hours=23, minutes=59, seconds=59, microseconds=999999)
    
    def _drop_fields(self, transformed_record: Dict[str, Any], drop_fields: List[str]) -> None:
        """Remove specified fields from the record."""
        for field in drop_fields:
            transformed_record.pop(field, None)
    
    def _flatten_nested_object(
        self, 
        nested_obj: Dict[str, Any], 
        field_name: str, 
        config: Dict[str, Any],
        depth: int = 0,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Flatten a nested object according to configuration.
        Supports simple key mapping, recursive flattening, and prefix patterns.
        
        Args:
            nested_obj: The nested dictionary to flatten
            field_name: Name of the field containing the nested object
            config: Flatten configuration from transform.yaml
            depth: Current recursion depth
            max_depth: Maximum recursion depth to prevent infinite loops
        
        Returns:
            Dictionary with flattened keys
        """
        if not isinstance(nested_obj, dict):
            return {field_name: nested_obj}
        
        flattened = {}
        strategy = config.get('strategy', 'simple')  # simple, recursive
        separator = config.get('separator', DEFAULT_SEPARATOR)
        max_depth_config = config.get('max_depth', max_depth)
        key_mapping = config.get('key_mapping', {})
        prefix = config.get('prefix', '')
        
        if depth >= max_depth_config:
            # Prevent infinite recursion
            return {field_name: nested_obj}
        
        if strategy == 'recursive':
            # Recursively flatten all nested objects
            for key, value in nested_obj.items():
                if isinstance(value, dict):
                    # Recursively flatten nested dict
                    nested_flattened = self._flatten_nested_object(
                        value, 
                        f"{field_name}{separator}{key}", 
                        config,
                        depth + 1,
                        max_depth_config
                    )
                    flattened.update(nested_flattened)
                elif isinstance(value, list):
                    # Handle arrays
                    array_config = config.get('array_fields', [])
                    flatten_arrays = config.get('flatten_arrays', False)
                    if key in array_config or flatten_arrays:
                        # Flatten array items
                        for idx, item in enumerate(value):
                            if isinstance(item, dict):
                                item_flattened = self._flatten_nested_object(
                                    item,
                                    f"{field_name}{separator}{key}{separator}{idx}",
                                    config,
                                    depth + 1,
                                    max_depth_config
                                )
                                flattened.update(item_flattened)
                            else:
                                flattened[f"{field_name}{separator}{key}{separator}{idx}"] = item
                    else:
                        # Keep array as-is
                        flattened[f"{field_name}{separator}{key}"] = value
                else:
                    # Simple value
                    flattened[f"{field_name}{separator}{key}"] = value
        else:  # strategy == 'simple' (default)
            # Simple flattening with key mapping or prefix
            for nested_key, nested_value in nested_obj.items():
                if isinstance(nested_value, dict):
                    # Nested dict - recursively flatten if recursive is enabled
                    if config.get('recursive', False):
                        nested_flattened = self._flatten_nested_object(
                            nested_value,
                            f"{field_name}{separator}{nested_key}",
                            config,
                            depth + 1,
                            max_depth_config
                        )
                        flattened.update(nested_flattened)
                    else:
                        # Keep as nested or use prefix
                        if prefix:
                            flattened[f"{prefix}{nested_key}"] = nested_value
                        else:
                            flattened[f"{field_name}{separator}{nested_key}"] = nested_value
                elif isinstance(nested_value, list):
                    # Array - handle if configured
                    if config.get('flatten_arrays', False):
                        for idx, item in enumerate(nested_value):
                            if isinstance(item, dict):
                                item_flattened = self._flatten_nested_object(
                                    item,
                                    f"{field_name}{separator}{nested_key}{separator}{idx}",
                                    config,
                                    depth + 1,
                                    max_depth_config
                                )
                                flattened.update(item_flattened)
                            else:
                                flattened[f"{field_name}{separator}{nested_key}{separator}{idx}"] = item
                    else:
                        # Keep array as-is
                        if key_mapping and nested_key in key_mapping:
                            flattened_key = key_mapping[nested_key]
                        elif prefix:
                            flattened_key = f"{prefix}{nested_key}"
                        else:
                            flattened_key = f"{field_name}{separator}{nested_key}"
                        flattened[flattened_key] = nested_value
                else:
                    # Simple value - use key mapping, prefix, or default
                    if key_mapping and nested_key in key_mapping:
                        # Use mapped key directly for simple strategy
                        # For array flattening, field_name will already include index (e.g., "orders_0")
                        mapped_key = key_mapping[nested_key]
                        # Only add field_name prefix if we're in array context (field_name contains separator)
                        if field_name and separator in field_name:
                            # This is from array flattening - preserve the indexed prefix
                            flattened_key = f"{field_name}{separator}{mapped_key}"
                        else:
                            # Simple strategy - use mapped key directly (no prefix)
                            flattened_key = mapped_key
                    elif prefix:
                        flattened_key = f"{prefix}{nested_key}"
                    else:
                        flattened_key = f"{field_name}{separator}{nested_key}"
                    flattened[flattened_key] = nested_value
        
        return flattened
    
    def _flatten_array(
        self,
        array_obj: List[Any],
        field_name: str,
        config: Dict[str, Any],
        depth: int = 0,
        max_depth: int = 10
    ) -> Dict[str, Any]:
        """
        Flatten an array of nested objects according to configuration.
        
        Args:
            array_obj: The array to flatten
            field_name: Name of the field containing the array
            config: Flatten configuration from transform.yaml
            depth: Current recursion depth
            max_depth: Maximum recursion depth
        
        Returns:
            Dictionary with flattened keys
        """
        if not isinstance(array_obj, list):
            return {field_name: array_obj}
        
        flattened = {}
        strategy = config.get('strategy', 'array_flatten')
        separator = config.get('separator', DEFAULT_SEPARATOR)
        max_depth_config = config.get('max_depth', max_depth)
        item_flatten = config.get('item_flatten', {})
        aggregate = config.get('aggregate', False)  # If True, aggregate all items into single keys
        
        if depth >= max_depth_config:
            return {field_name: array_obj}
        
        if strategy == 'array_flatten' or strategy == 'simple':
            # Flatten each item in the array
            for idx, item in enumerate(array_obj):
                if isinstance(item, dict):
                    # Use item_flatten config if provided, otherwise use parent config
                    item_config = item_flatten if item_flatten else config
                    
                    if aggregate:
                        # Aggregate: all items contribute to same keys (last wins or merge)
                        item_flattened = self._flatten_nested_object(
                            item,
                            field_name,  # Same base name for all items
                            item_config,
                            depth + 1,
                            max_depth_config
                        )
                        # Merge or overwrite (last item wins)
                        flattened.update(item_flattened)
                    else:
                        # Indexed: each item gets its own keys with index
                        # Create a new config that uses the indexed field name as base
                        indexed_config = item_config.copy()
                        indexed_config['_base_field'] = f"{field_name}{separator}{idx}"
                        
                        item_flattened = self._flatten_nested_object(
                            item,
                            f"{field_name}{separator}{idx}",
                            indexed_config,
                            depth + 1,
                            max_depth_config
                        )
                        flattened.update(item_flattened)
                else:
                    # Simple value in array
                    if aggregate:
                        # For aggregate, use field name directly (last value wins)
                        flattened[field_name] = item
                    else:
                        flattened[f"{field_name}{separator}{idx}"] = item
        else:
            # Keep array as-is
            flattened[field_name] = array_obj
        
        return flattened
    
    def _convert_type(self, value: Any, target_type: str) -> Any:
        """Convert value to target type."""
        if value is None:
            return None
        
        type_map = {
            'string': str,
            'integer': int,
            'int': int,
            'float': float,
            'double': float,
            'boolean': bool,
            'bool': bool,
            'datetime': self._parse_datetime,
            'timestamp': self._parse_datetime,
            'date': self._parse_date,
        }
        
        converter = type_map.get(target_type.lower())
        if converter:
            try:
                # Converter is either a type (callable) or a method (also callable)
                return converter(value)
            except (ValueError, TypeError):
                return value
        
        return value
    
    def _parse_datetime(self, value: Any) -> Any:
        """Parse datetime value from string or return datetime object."""
        if isinstance(value, datetime):
            return value
        if isinstance(value, str):
            for fmt in DATETIME_FORMATS:
                try:
                    return datetime.strptime(value, fmt)
                except ValueError:
                    continue
        return value
    
    def _parse_date(self, value: Any) -> Any:
        """Parse date value."""
        if isinstance(value, date):
            return value
        if isinstance(value, datetime):
            return value.date()
        if isinstance(value, str):
            try:
                return datetime.strptime(value, '%Y-%m-%d').date()
            except ValueError:
                pass
        return value
    
    # ============================================================================
    # LOADING
    # ============================================================================
    
    async def load(
        self,
        transformed_data: List[Dict[str, Any]],
        session: Any = None,
        **kwargs,
    ) -> Dict[str, Any]:
        """Load transformed data into the database."""
        target_table = self.load_config.get('target_table')
        schema_name = self.load_config.get('schema_name', 'scraper')
        write_method = self.load_config.get('write_method', 'upsert')
        primary_key = self.load_config.get('primary_key')
        unique_constraints = self.load_config.get('unique_constraints', [])
        # Keep primary_key as-is (can be string or list for composite keys)
        # The load functions now handle both single and composite primary keys
        batch_size = self.load_config.get('batch_size', 1000)
        
        # If primary_key is 'id' and not in the data, use unique constraints for conflict detection
        # This allows using UUID primary keys while upserting on natural keys
        conflict_key = primary_key
        if write_method == 'upsert' and transformed_data:
            incoming_columns = set(transformed_data[0].keys())
            # Check if primary_key is 'id' (string) or contains 'id' (list)
            pk_is_id = (isinstance(primary_key, str) and primary_key == 'id') or \
                       (isinstance(primary_key, list) and len(primary_key) == 1 and primary_key[0] == 'id')
            
            if pk_is_id and 'id' not in incoming_columns:
                # Use first unique constraint for conflict detection
                if unique_constraints:
                    # unique_constraints can be a list of lists or a list of strings
                    if isinstance(unique_constraints[0], list):
                        conflict_key = unique_constraints[0]  # First constraint (can be composite)
                    else:
                        conflict_key = unique_constraints[0] if isinstance(unique_constraints[0], str) else unique_constraints
                else:
                    # Fallback: if no unique constraints, can't do upsert
                    raise ValueError(
                        f"Cannot perform upsert: primary_key is 'id' (auto-generated) but no unique_constraints "
                        f"specified in load.yaml for conflict detection. Please specify unique_constraints."
                    )
        
        if not target_table:
            raise ValueError("target_table not specified in load configuration")
        
        tunnel = None
        if session is None:
            try:
                engine, db_session, db_type, tunnel = get_database_connection(
                    self.load_config, self.contract_dir, config_context=self.config_context
                )
                try:
                    result = load_data(
                        transformed_data,
                        db_session,
                        schema_name,
                        target_table,
                        write_method,
                        conflict_key,  # Use conflict_key (may be unique constraint instead of PK)
                        batch_size,
                        db_type,
                    )
                    return result
                finally:
                    db_session.close()
                    if tunnel:
                        tunnel.stop()
            except Exception as e:
                if tunnel:
                    try:
                        tunnel.stop()
                    except Exception:
                        pass
                raise
        else:
            from pycharter.etl_generator.database import detect_database_type
            from sqlalchemy.ext.asyncio import AsyncSession
            
            # Detect database type
            db_type = "postgresql"
            if hasattr(session, 'bind') and hasattr(session.bind, 'url'):
                db_url = str(session.bind.url)
                db_type = detect_database_type(db_url)
            
            # load_data is now async and expects AsyncSession
            if not isinstance(session, AsyncSession):
                raise ValueError(
                    f"load_data requires an AsyncSession, but got {type(session)}. "
                    "Please use an AsyncSession for database operations."
                )
            
            return await load_data(
                transformed_data,
                session,
                schema_name,
                target_table,
                write_method,
                conflict_key,  # Use conflict_key (may be unique constraint instead of PK)
                batch_size,
                db_type,
            )
    
    # ============================================================================
    # MEMORY MANAGEMENT
    # ============================================================================
    
    def _check_memory(self) -> Optional[float]:
        """Get current memory usage in MB, or None if psutil not available."""
        if not PSUTIL_AVAILABLE or not self.process:
            return None
        return self.process.memory_info().rss / 1024 / 1024
    
    def _enforce_memory_limit(self):
        """Check and enforce memory limits."""
        if self.max_memory_mb:
            current = self._check_memory()
            if current and current > self.max_memory_mb:
                gc.collect()
                current = self._check_memory()
                
                if current and current > self.max_memory_mb:
                    raise MemoryError(
                        f"Memory limit exceeded: {current:.1f}MB > {self.max_memory_mb}MB. "
                        f"Consider increasing batch_size."
                    )
    
    # ============================================================================
    # PIPELINE EXECUTION
    # ============================================================================
    
    async def run(
        self,
        dry_run: bool = False,
        session: Any = None,
        checkpoint_id: Optional[str] = None,
        resume: bool = False,
        batch_size: Optional[int] = None,
        max_retries: int = 3,
        error_threshold: float = 0.1,
        **kwargs,
    ) -> Dict[str, Any]:
        """
        Run the complete ETL pipeline in streaming mode.
        
        Processes data incrementally: Extract-Batch → Transform-Batch → Load-Batch.
        This ensures constant memory usage regardless of dataset size.
        
        Args:
            dry_run: If True, skip database operations
            session: Optional database session
            checkpoint_id: Optional checkpoint ID for resume capability
            resume: If True, resume from checkpoint
            batch_size: Batch size for processing (defaults to extract.yaml config)
            max_retries: Maximum retries for failed batches
            error_threshold: Error rate threshold (0.0-1.0) before aborting
            **kwargs: Additional parameters passed to extract()
            
        Returns:
            Pipeline execution results dictionary
        """
        if batch_size is None:
            batch_size = self.extract_config.get('batch_size', DEFAULT_BATCH_SIZE)
        
        results = {
            'extraction': {'batches_processed': 0, 'total_records': 0},
            'transformation': {'batches_processed': 0, 'total_records': 0},
            'loading': {'batches_processed': 0, 'total_records': 0, 'inserted': 0, 'updated': 0},
            'success': False,
            'failed_batches': [],
        }
        
        # Load checkpoint if resuming
        start_batch = 0
        if resume and checkpoint_id:
            checkpoint_state = self.checkpoint_manager.load(checkpoint_id)
            if checkpoint_state:
                kwargs.update(checkpoint_state.last_processed_params)
                start_batch = checkpoint_state.batch_num
        
        self.progress_tracker.start()
        batch_num = 0
        total_records = 0
        failed_batches = []
        
        try:
            async for batch in self.extract(batch_size=batch_size, **kwargs):
                batch_num += 1
                
                # Skip batches if resuming
                if batch_num <= start_batch:
                    continue
                
                batch_start_time = datetime.now()
                
                try:
                    self._enforce_memory_limit()
                    
                    # Transform batch
                    transformed_batch = self.transform(batch, **kwargs)
                    
                    # Load batch
                    if not dry_run:
                        load_result = await self.load(transformed_batch, session=session, **kwargs)
                        results['loading']['inserted'] += load_result.get('inserted', 0)
                        results['loading']['updated'] += load_result.get('updated', 0)
                        results['loading']['total_records'] += load_result.get('total', 0)
                    
                    # Update counters
                    total_records += len(batch)
                    results['extraction']['total_records'] += len(batch)
                    results['extraction']['batches_processed'] = batch_num
                    results['transformation']['total_records'] += len(transformed_batch)
                    results['transformation']['batches_processed'] = batch_num
                    results['loading']['batches_processed'] = batch_num
                    
                    # Report progress
                    memory_usage = self._check_memory()
                    batch_time = (datetime.now() - batch_start_time).total_seconds()
                    self.progress_tracker.record_batch_time(batch_time)
                    self.progress_tracker.report(
                        'extract',
                        batch_num,
                        total_records,
                        memory_usage_mb=memory_usage,
                    )
                    
                    # Save checkpoint
                    if checkpoint_id:
                        self.checkpoint_manager.save(
                            checkpoint_id,
                            'extract',
                            batch_num,
                            total_records,
                            kwargs,
                        )
                    
                    # Cleanup
                    del batch, transformed_batch
                    gc.collect()
                    
                except Exception as e:
                    failed_batches.append({
                        'batch_num': batch_num,
                        'error': str(e),
                        'records': len(batch),
                    })
                    
                    # Check error rate
                    error_rate = len(failed_batches) / batch_num if batch_num > 0 else 1.0
                    if error_rate > error_threshold:
                        raise RuntimeError(
                            f"Error rate too high: {error_rate:.1%} > {error_threshold:.1%}. "
                            f"Aborting pipeline."
                        )
                    
                    # Retry logic
                    if len(failed_batches) <= max_retries:
                        await asyncio.sleep(2 ** len(failed_batches))
                        continue
                    else:
                        self.progress_tracker.report(
                            'extract',
                            batch_num,
                            total_records,
                            error_count=len(failed_batches),
                        )
            
            results['failed_batches'] = failed_batches
            results['success'] = len(failed_batches) < batch_num * error_threshold
            
            # Delete checkpoint on success
            if checkpoint_id and results['success']:
                self.checkpoint_manager.delete(checkpoint_id)
            
        except Exception as e:
            # Save error checkpoint
            if checkpoint_id:
                self.checkpoint_manager.save(
                    checkpoint_id,
                    'error',
                    batch_num,
                    total_records,
                    kwargs,
                    error=str(e),
                )
            results['error'] = str(e)
            results['success'] = False
            raise
        
        return results
    
    async def run_multiple(
        self,
        param_name: Optional[str] = None,
        param_values: Optional[List[Any]] = None,
        param_sets: Optional[List[Dict[str, Any]]] = None,
        batch_size: int = 5,
        delay_between_runs: float = 1.0,
        dry_run: bool = False,
        session: Any = None,
        **kwargs,
    ) -> List[Dict[str, Any]]:
        """
        Run ETL pipeline multiple times with different parameter sets.
        
        This method allows you to efficiently run the same ETL pipeline multiple times
        with varying parameters. You can either:
        1. Provide a single parameter name and list of values (simple case)
        2. Provide a list of parameter dictionaries (complex case with multiple varying params)
        
        Args:
            param_name: Name of the parameter to vary (e.g., 'symbol', 'ticker', 'date')
                       Required if using param_values.
            param_values: List of values for the specified parameter.
                         Each value will be passed as {param_name: value} to run().
            param_sets: List of parameter dictionaries. Each dict will be unpacked
                       and passed to run() as **params. Use this when multiple
                       parameters vary between runs.
            batch_size: Number of runs to process before a brief pause (for rate limiting)
            delay_between_runs: Delay in seconds between individual runs (for rate limiting)
            dry_run: If True, skip database operations
            session: Optional database session
            **kwargs: Additional parameters passed to each run() call (common to all runs)
        
        Returns:
            List of result dictionaries, each containing:
            - 'params': The parameters used for this run
            - 'success': Whether the run succeeded
            - 'records': Number of records processed (if successful)
            - 'result': Full result dictionary from run() (if successful)
            - 'error': Error message (if failed)
        
        Examples:
            # Simple case: vary a single parameter
            >>> results = await orchestrator.run_multiple(
            ...     param_name='symbol',
            ...     param_values=['AAPL', 'MSFT', 'GOOGL'],
            ...     batch_size=5,
            ...     delay_between_runs=1.0
            ... )
            
            # Complex case: vary multiple parameters
            >>> results = await orchestrator.run_multiple(
            ...     param_sets=[
            ...         {'symbol': 'AAPL', 'date': '2024-01-01'},
            ...         {'symbol': 'MSFT', 'date': '2024-01-02'},
            ...     ],
            ...     batch_size=3,
            ...     delay_between_runs=0.5
            ... )
        """
        # Validate inputs
        if param_sets is not None:
            if param_name is not None or param_values is not None:
                raise ValueError(
                    "Cannot use both param_sets and param_name/param_values. "
                    "Use either param_sets OR param_name+param_values."
                )
            if not isinstance(param_sets, list) or len(param_sets) == 0:
                raise ValueError("param_sets must be a non-empty list of dictionaries")
            # Convert param_sets to list of dicts
            runs = [dict(params) for params in param_sets]
        elif param_name is not None and param_values is not None:
            if not isinstance(param_values, list) or len(param_values) == 0:
                raise ValueError("param_values must be a non-empty list")
            # Convert param_name + param_values to list of dicts
            runs = [{param_name: value} for value in param_values]
        else:
            raise ValueError(
                "Must provide either (param_name + param_values) OR param_sets"
            )
        
        results = []
        
        for i in range(0, len(runs), batch_size):
            run_batch = runs[i:i + batch_size]
            
            for run_params in run_batch:
                try:
                    # Merge run_params with common kwargs
                    merged_params = {**kwargs, **run_params}
                    result = await self.run(
                        dry_run=dry_run,
                        session=session,
                        **merged_params
                    )
                    results.append({
                        'params': run_params,
                        'success': result['success'],
                        'records': result.get('loading', {}).get('total_records', 0),
                        'result': result,
                    })
                except Exception as e:
                    results.append({
                        'params': run_params,
                        'success': False,
                        'error': str(e),
                    })
                
                # Rate limiting
                if i + batch_size < len(runs) or run_params != run_batch[-1]:
                    await asyncio.sleep(delay_between_runs)
        
        return results


def create_orchestrator(
    contract_dir: Optional[str] = None,
    **kwargs,
) -> ETLOrchestrator:
    """
    Create an ETL orchestrator instance.
    
    Args:
        contract_dir: Directory containing contract files and ETL configs
        **kwargs: Additional arguments passed to ETLOrchestrator
    
    Returns:
        ETLOrchestrator instance
    """
    return ETLOrchestrator(contract_dir=contract_dir, **kwargs)
