"""
OpenAPI specification loader module

Handles loading and parsing of OpenAPI/Swagger files in YAML or JSON format.
"""

import yaml
import json
from pathlib import Path
from .errors import OpenAPILoadError


def load_openapi(path):
    """
    Load OpenAPI specification from a YAML or JSON file.
    
    Args:
        path (str or Path): Path to the OpenAPI specification file
        
    Returns:
        dict: Parsed OpenAPI specification
        
    Raises:
        OpenAPILoadError: If file cannot be loaded or parsed
        
    Examples:
        >>> spec = load_openapi("openapi.yaml")
        >>> spec = load_openapi("swagger.json")
    """
    path = Path(path)
    
    if not path.exists():
        raise OpenAPILoadError(f"OpenAPI file not found: {path}")
    
    try:
        with open(path, "r", encoding="utf-8") as f:
            if path.suffix in [".yaml", ".yml"]:
                return yaml.safe_load(f)
            elif path.suffix == ".json":
                return json.load(f)
            else:
                raise OpenAPILoadError(
                    f"Unsupported file format: {path.suffix}. "
                    "Use .yaml, .yml, or .json"
                )
    except yaml.YAMLError as e:
        raise OpenAPILoadError(f"Invalid YAML format: {e}")
    except json.JSONDecodeError as e:
        raise OpenAPILoadError(f"Invalid JSON format: {e}")
    except Exception as e:
        raise OpenAPILoadError(f"Error loading OpenAPI file: {e}")
