"""
Feature extraction utility for extracting feature definitions from FeatureView savers.

This module provides utilities to analyze a project's FeatureView classes and extract
feature information from the saver's schema configuration.
"""

import ast
import importlib.util
import os
import sys
from typing import List, Optional, Dict, Any, Literal


# Cook API value types
ValueType = Literal[
    "integer", "string", "float", "boolean",
    "date", "date_time", "uuid", "vector", "list"
]

# Mapping from pandas/python dtypes to Cook API ValueType
DTYPE_TO_VALUE_TYPE: Dict[str, ValueType] = {
    # Integer types
    "int": "integer",
    "int8": "integer",
    "int16": "integer",
    "int32": "integer",
    "int64": "integer",
    "Int8": "integer",
    "Int16": "integer",
    "Int32": "integer",
    "Int64": "integer",
    "uint8": "integer",
    "uint16": "integer",
    "uint32": "integer",
    "uint64": "integer",
    # Float types
    "float": "float",
    "float16": "float",
    "float32": "float",
    "float64": "float",
    "Float32": "float",
    "Float64": "float",
    "double": "float",
    # String types
    "str": "string",
    "string": "string",
    "object": "string",
    # Boolean types
    "bool": "boolean",
    "boolean": "boolean",
    # Date/DateTime types
    "date": "date",
    "datetime": "date_time",
    "datetime64": "date_time",
    "datetime64[ns]": "date_time",
    "timestamp": "date_time",
    # UUID
    "uuid": "uuid",
    # Vector/List types
    "vector": "vector",
    "list": "list",
    "array": "list",
}


def map_dtype_to_value_type(dtype: Optional[str]) -> ValueType:
    """
    Map a pandas/python dtype to Cook API ValueType.

    Parameters
    ----------
    dtype : str, optional
        The pandas or python dtype string.

    Returns
    -------
    ValueType
        The corresponding Cook API value type.
    """
    if dtype is None:
        return "string"

    # Normalize dtype string
    dtype_lower = dtype.lower().strip()

    # Handle datetime variations
    if dtype_lower.startswith("datetime"):
        return "date_time"

    # Direct lookup
    if dtype_lower in DTYPE_TO_VALUE_TYPE:
        return DTYPE_TO_VALUE_TYPE[dtype_lower]

    # Default to string for unknown types
    return "string"


def extract_features_from_saver(saver, version: str = "1.0.0") -> List[Dict[str, Any]]:
    """
    Extract feature definitions from a Saver's SaveConfigs and Schemas.

    Parameters
    ----------
    saver : Saver
        A Saver instance containing save_configs with schema definitions.
    version : str
        Version string for the features.

    Returns
    -------
    List[Dict[str, Any]]
        List of feature dictionaries ready for Cook API submission.
        Each feature has: name, label, description, version, has_limited_values, type
    """
    features = []

    if saver is None or not hasattr(saver, 'save_configs'):
        return features

    for config in saver.save_configs:
        schema = config.schema

        for col in schema.cols:
            # Skip ID columns from features (they're identifiers, not features)
            if col.is_id:
                continue

            feature_name = col.to or col.original

            feature = {
                "name": feature_name,
                "label": feature_name.replace("_", " ").title(),
                "description": "",
                "version": version,
                "has_limited_values": False,
                "type": map_dtype_to_value_type(col.dtype),
            }
            features.append(feature)

    return features


def find_feature_views_in_file(file_path: str) -> List[str]:
    """
    Parse a Python file and find all classes that inherit from FeatureView.

    Parameters
    ----------
    file_path : str
        Path to the Python file to analyze.

    Returns
    -------
    List[str]
        List of class names that inherit from FeatureView.
    """
    with open(file_path, 'r') as f:
        try:
            tree = ast.parse(f.read(), filename=file_path)
        except SyntaxError:
            return []

    feature_view_classes = []

    for node in ast.walk(tree):
        if isinstance(node, ast.ClassDef):
            for base in node.bases:
                base_name = None
                if isinstance(base, ast.Name):
                    base_name = base.id
                elif isinstance(base, ast.Attribute):
                    base_name = base.attr

                if base_name == 'FeatureView':
                    feature_view_classes.append(node.name)
                    break

    return feature_view_classes


def load_module_from_path(module_path: str, module_name: str = None):
    """
    Dynamically load a Python module from a file path.

    Parameters
    ----------
    module_path : str
        Path to the Python file.
    module_name : str, optional
        Name to use for the module. If not provided, uses the file name.

    Returns
    -------
    module
        The loaded module.
    """
    if module_name is None:
        module_name = os.path.splitext(os.path.basename(module_path))[0]

    spec = importlib.util.spec_from_file_location(module_name, module_path)
    module = importlib.util.module_from_spec(spec)
    sys.modules[module_name] = module
    spec.loader.exec_module(module)

    return module


def extract_features_from_directory(
    directory: str,
    main_file: str = None,
    version: str = "1.0.0",
    echo_func=None,
) -> List[Dict[str, Any]]:
    """
    Extract features from all FeatureView classes in a project directory.

    Parameters
    ----------
    directory : str
        Path to the project directory.
    main_file : str, optional
        Path to the main entry file. If provided, only this file is analyzed.
    version : str
        Version string for the features.
    echo_func : callable, optional
        Function to use for printing messages.

    Returns
    -------
    List[Dict[str, Any]]
        List of feature dictionaries ready for Cook API submission.
    """
    all_features = []

    def echo(msg):
        if echo_func:
            echo_func(msg)

    # Add directory to Python path for imports
    original_path = sys.path.copy()
    if directory not in sys.path:
        sys.path.insert(0, directory)

    try:
        # Find Python files to analyze
        files_to_analyze = []

        if main_file:
            main_path = os.path.join(directory, main_file)
            if os.path.exists(main_path) and main_path.endswith('.py'):
                files_to_analyze.append(main_path)
        else:
            for root, _, files in os.walk(directory):
                for file in files:
                    if file.endswith('.py') and not file.startswith('__'):
                        files_to_analyze.append(os.path.join(root, file))

        # First pass: find files with FeatureView classes
        files_with_feature_views = []
        for file_path in files_to_analyze:
            feature_view_classes = find_feature_views_in_file(file_path)
            if feature_view_classes:
                files_with_feature_views.append((file_path, feature_view_classes))

        # Second pass: load modules and extract features
        for file_path, class_names in files_with_feature_views:
            try:
                module = load_module_from_path(file_path)

                for class_name in class_names:
                    if hasattr(module, class_name):
                        feature_view_class = getattr(module, class_name)

                        # Get the saver from the class (class attribute, not instance)
                        saver = getattr(feature_view_class, 'saver', None)

                        if saver is not None:
                            echo(f"Found FeatureView: {class_name}")
                            features = extract_features_from_saver(saver, version)
                            all_features.extend(features)
                            echo(f"  Extracted {len(features)} features")
            except Exception as e:
                # Log but continue if a file fails to load
                echo(f"Warning: Could not extract features from {file_path}: {e}")
                continue
    finally:
        # Restore original path
        sys.path = original_path

    return all_features
