# 🚀 AutoAPI Validator

**Automatic OpenAPI request & response validator**

A Python package that automatically validates API requests & responses using an OpenAPI (Swagger) file.

## ✨ Features

✔ Load OpenAPI JSON/YAML specifications  
✔ Validate API responses against schemas  
✔ Clear, detailed error messages  
✔ CLI command for quick validation  
✔ Framework-independent  

## 📦 Installation

```bash
pip install autoapi-validator
```

### Development Installation

```bash
git clone https://github.com/santhosh/autoapi-validator.git
cd autoapi-validator
pip install -e .
```

## 🔧 Usage

### As a Library

```python
from autoapi_validator import load_openapi, validate_response

# Load OpenAPI specification
spec = load_openapi("openapi.yaml")

# Get schema for a specific component
schema = spec["components"]["schemas"]["User"]

# Validate API response
response = {
    "id": 1,
    "name": "Santhosh"
}

is_valid, message = validate_response(response, schema)
print(is_valid, message)
```

### FastAPI Integration 🚀

**NEW!** Automatic validation middleware for FastAPI applications:

```python
from fastapi import FastAPI
from autoapi_validator.integrations.fastapi import configure_validation

app = FastAPI()

# Enable automatic response validation
configure_validation(app, validate_responses=True)

# That's it! All responses are now validated against your OpenAPI schema
```

**Installation with FastAPI support:**
```bash
pip install autoapi-validator[fastapi]
```

**Features:**
- ✅ Automatic response validation using FastAPI's generated OpenAPI schema
- ✅ No duplicate schema definitions needed
- ✅ Validation warnings logged for debugging
- ✅ Non-blocking (responses still sent even if validation fails)

**Full example:**
```python
from fastapi import FastAPI
from pydantic import BaseModel
from autoapi_validator.integrations.fastapi import configure_validation

app = FastAPI()
configure_validation(app)

class User(BaseModel):
    id: int
    name: str
    email: str

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    return {"id": user_id, "name": "John", "email": "john@example.com"}
```

See [examples/fastapi_example.py](examples/fastapi_example.py) for a complete working example.


### Flask Integration 🍶

**NEW!** Validation decorators for Flask applications:

```python
from flask import Flask
from autoapi_validator.integrations.flask import setup_flask_validation

app = Flask(__name__)

# Setup validation with your OpenAPI spec
validator = setup_flask_validation(app, "openapi.yaml")

@app.post("/users")
@validator.validate_request_decorator("/users", "POST")
def create_user():
    # Request is automatically validated!
    return jsonify(request.json)

@app.get("/users/<int:user_id>")
@validator.validate_response_decorator("/users/{userId}", "GET")
def get_user(user_id):
    # Response is automatically validated!
    return jsonify({"id": user_id, "name": "John"})
```

**Installation with Flask support:**
```bash
pip install autoapi-validator[flask]
```

**Features:**
- ✅ Request validation decorators
- ✅ Response validation decorators
- ✅ Flexible per-endpoint validation
- ✅ Full OpenAPI schema support

See [examples/flask_example.py](examples/flask_example.py) for a complete working example.


### Django Integration 🎯

**NEW!** Middleware and decorators for Django applications:

```python
# settings.py
MIDDLEWARE = [
    ...
    'autoapi_validator.integrations.django.ValidationMiddleware',
]

OPENAPI_SPEC_PATH = 'path/to/openapi.yaml'
OPENAPI_VALIDATE_REQUESTS = False  # Optional
OPENAPI_VALIDATE_RESPONSES = True  # Optional

# views.py
from django.http import JsonResponse
from autoapi_validator.integrations.django import validate_api

@validate_api("/users", "POST")
def create_user(request):
    # Request automatically validated!
    data = json.loads(request.body)
    return JsonResponse({"id": 1, **data})

@validate_api("/users/{id}", "GET")
def get_user(request, id):
    # Response automatically validated!
    return JsonResponse({"id": id, "name": "John"})
```

**Installation with Django support:**
```bash
pip install autoapi-validator[django]
```

**Features:**
- ✅ Middleware for automatic validation
- ✅ View decorators for per-endpoint control
- ✅ Django & Django REST Framework support
- ✅ Full OpenAPI schema support

See [examples/django_example/](examples/django_example/) for complete examples.


### CI/CD Integration 🔄

**GitHub Actions Example:**
```yaml
- name: Validate OpenAPI Spec
  run: |
    pip install autoapi-validator
    python -m autoapi_validator openapi.yaml --info
```

**Pre-commit Hook:**
```yaml
repos:
  - repo: local
    hooks:
      - id: validate-openapi
        name: Validate OpenAPI Specification
        entry: python -m autoapi_validator
        args: ['openapi.yaml', '--info']
        language: system
```

See [examples/ci_cd/](examples/ci_cd/) for complete configurations.


### CLI Usage

```bash
# Display help
python -m autoapi_validator

# Load and validate OpenAPI spec
python -m autoapi_validator openapi.yaml

# Show spec information
python -m autoapi_validator openapi.yaml --info
```

## 📋 Example

If your API response should be:

```json
{
  "id": 1,
  "name": "Santhosh"
}
```

But the API returns:

```json
{
  "id": "one",
  "fullname": "Santhosh"
}
```

➡️ AutoAPI Validator will **detect the error automatically** and provide detailed feedback!

## 🛠️ Requirements

- Python >= 3.8
- pyyaml >= 6.0
- jsonschema >= 4.0.0
- requests >= 2.28.0

## 🗺️ Roadmap

### Version 0.1.0
- ✅ Load OpenAPI JSON/YAML
- ✅ Validate API responses
- ✅ Clear error messages
- ✅ Basic CLI

### Version 0.2.0
- ✅ FastAPI integration middleware
- ✅ Automatic response validation
- ✅ FastAPI example application

### Version 0.3.0
- ✅ FastAPI request validation
- ✅ Flask integration with decorators
- ✅ Flask example application
- ✅ CI/CD tools (GitHub Actions, pre-commit hooks)

### Version 0.4.0 (Current)
- ✅ Django integration with middleware
- ✅ Django view decorators
- ✅ Django example application

### Future Versions
- [ ] Auto test generation from OpenAPI specs
- [ ] Request body validation improvements  
- [ ] Real-time API monitoring
- [ ] Validation reporting and metrics

## 📄 License

MIT License - see LICENSE file for details

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## 👤 Author

**Santhosh**

---

⭐ Star this repo if you find it useful!
