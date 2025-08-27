#!/usr/bin/env python3
"""
Generate Swagger/OpenAPI JSON file for frontend integration
"""

import json
import subprocess
import sys
from pathlib import Path

def generate_swagger_json():
    """Generate Swagger JSON from the FastAPI application"""

    # Add the current directory to Python path
    current_dir = Path(__file__).parent
    sys.path.insert(0, str(current_dir))

    try:
        # Import the FastAPI app
        from app.main import app

        # Generate OpenAPI schema
        openapi_schema = app.openapi()

        # Save to file
        output_file = current_dir / "swagger.json"
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(openapi_schema, f, indent=2, ensure_ascii=False)

        print(f"✅ Swagger JSON generated successfully: {output_file}")
        print(f"📊 API endpoints documented: {len(openapi_schema.get('paths', {}))}")

        # Print summary of endpoints
        paths = openapi_schema.get('paths', {})
        print("\n📋 API Endpoints Summary:")
        for path, methods in paths.items():
            for method, details in methods.items():
                print(f"  {method.upper()} {path} - {details.get('summary', 'No summary')}")

        return True

    except ImportError as e:
        print(f"❌ Import error: {e}")
        print("Make sure all dependencies are installed and the app can be imported")
        return False
    except Exception as e:
        print(f"❌ Error generating Swagger JSON: {e}")
        return False

if __name__ == "__main__":
    success = generate_swagger_json()
    sys.exit(0 if success else 1)
