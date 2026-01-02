"""
CLI entry point for autoapi-validator

Run with: python -m autoapi_validator
"""

import sys
import argparse
from pathlib import Path
from .loader import load_openapi
from .errors import OpenAPIError


def main():
    """Main CLI entry point"""
    parser = argparse.ArgumentParser(
        description="AutoAPI Validator - Validate API responses against OpenAPI specs",
        prog="autoapi-validator"
    )
    
    parser.add_argument(
        "spec",
        nargs="?",
        help="Path to OpenAPI specification file (YAML or JSON)"
    )
    
    parser.add_argument(
        "--version",
        action="version",
        version="autoapi-validator 0.1.0"
    )
    
    parser.add_argument(
        "--info",
        action="store_true",
        help="Display OpenAPI spec information"
    )
    
    args = parser.parse_args()
    
    # If no spec provided, show help
    if not args.spec:
        parser.print_help()
        print("\n[OK] AutoAPI Validator is ready!")
        print("  Usage: python -m autoapi_validator <spec_file.yaml>")
        return 0
    
    # Load and display spec info
    try:
        spec = load_openapi(args.spec)
        print(f"[OK] Successfully loaded OpenAPI spec: {args.spec}")
        
        if args.info:
            print("\n--- Specification Info:")
            print(f"  OpenAPI Version: {spec.get('openapi', spec.get('swagger', 'Unknown'))}")
            print(f"  Title: {spec.get('info', {}).get('title', 'N/A')}")
            print(f"  Version: {spec.get('info', {}).get('version', 'N/A')}")
            
            if 'paths' in spec:
                print(f"  Endpoints: {len(spec['paths'])}")
                print("\n  Available paths:")
                for path in list(spec['paths'].keys())[:10]:  # Show first 10
                    print(f"    - {path}")
                if len(spec['paths']) > 10:
                    print(f"    ... and {len(spec['paths']) - 10} more")
        
        return 0
        
    except OpenAPIError as e:
        print(f"[ERROR] {e}", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"[ERROR] Unexpected error: {e}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
