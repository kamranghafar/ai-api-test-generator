<div align="center">

# 🤖 AI API Test Generator

[![Python 3.9+](https://img.shields.io/badge/python-3.9+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](https://opensource.org/licenses/MIT)
[![PyPI](https://img.shields.io/badge/pypi-v1.0.0-blue.svg)](https://pypi.org/project/ai-api-test-generator/)
[![Tests](https://img.shields.io/badge/tests-24%20passed-brightgreen.svg)]()

**Generate comprehensive API tests from OpenAPI/Swagger specs using AI.**

Outputs production-ready test suites in **Postman**, **pytest**, **Jest**, and **REST Assured** formats.

[Quick Start](#-quick-start) · [Features](#-features) · [Output Formats](#-output-formats) · [Examples](#-examples) · [Contributing](#-contributing)

</div>

---

## ✨ Features

- 📄 **Parse OpenAPI 3.x & Swagger 2.0** — YAML or JSON, local files or URLs
- 🤖 **AI-Powered Test Generation** — Uses OpenAI to create intelligent test scenarios
- 🔧 **Offline Mode** — Rule-based generation without AI (no API key needed)
- 📦 **4 Output Formats** — Postman Collection, pytest, Jest, REST Assured
- 🎯 **Comprehensive Coverage** — Happy path, validation, auth, edge cases, error handling
- ⚙️ **Configurable** — Custom base URLs, auth headers, endpoint filtering
- 🖥️ **Beautiful CLI** — Rich terminal output with progress tracking

## 📦 Installation

```bash
pip install ai-api-test-generator
```

Or install from source:

```bash
git clone https://github.com/kamranghafar/ai-api-test-generator.git
cd ai-api-test-generator
pip install -e .
```

## 🚀 Quick Start

### With AI (OpenAI)

```bash
export OPENAI_API_KEY="sk-..."
ai-test-gen openapi.yaml
```

### Offline (no API key needed)

```bash
ai-test-gen openapi.yaml --offline
```

### From URL

```bash
ai-test-gen https://petstore3.swagger.io/api/v3/openapi.json --offline -f pytest
```

## 📖 Usage

```
ai-test-gen [OPTIONS] SPEC

Arguments:
  SPEC  OpenAPI spec file path or URL

Options:
  -f, --format [postman|pytest|jest|rest-assured|all]
                                  Output format (default: all)
  -o, --output-dir TEXT           Output directory (default: ./generated_tests)
  --base-url TEXT                 Override the base URL from the spec
  --api-key TEXT                  OpenAI API key (or set OPENAI_API_KEY)
  --model TEXT                    OpenAI model (default: gpt-4o-mini)
  --auth-token TEXT               Bearer token for the target API
  --auth-header TEXT              Custom auth header (Name:Value)
  --offline                       Generate tests without AI (rule-based)
  --endpoint TEXT                 Filter to specific endpoints (repeatable)
  --version                       Show version
  --help                          Show this message and exit
```

## 🎯 Output Formats

### Postman Collection (v2.1)

Import directly into Postman with pre-built test scripts:

```bash
ai-test-gen spec.yaml -f postman -o ./tests
# → tests/postman_collection.json
```

### pytest + requests

Production-ready Python tests:

```bash
ai-test-gen spec.yaml -f pytest -o ./tests
# → tests/test_api.py
```

```python
"""Auto-generated API tests by ai-api-test-generator."""

import os
import requests

BASE_URL = os.getenv("API_BASE_URL", "https://petstore.example.com/api/v1")
AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")

def test_get_pets_success():
    """Happy path: List all pets"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    response = requests.get(url, headers=headers)
    assert response.status_code == 200
```

### Jest + axios

JavaScript tests for Node.js projects:

```bash
ai-test-gen spec.yaml -f jest -o ./tests
# → tests/api.test.js
```

```javascript
describe('GET /pets', () => {
  it('Happy path: List all pets', async () => {
    const response = await axios({
      method: 'get',
      url: `${BASE_URL}/pets`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(200);
  });
});
```

### REST Assured (Java)

JUnit 5 tests for Java projects:

```bash
ai-test-gen spec.yaml -f rest-assured -o ./tests
# → tests/ApiTests.java
```

```java
@Test
@DisplayName("Happy path: List all pets")
public void test_get_pets_success() {
    given()
        .contentType(ContentType.JSON)
    .when()
        .get("/pets")
    .then()
        .statusCode(200);
}
```

## 📋 Examples

### Petstore API (included)

```bash
# Generate all formats with offline mode
ai-test-gen examples/specs/petstore.yaml --offline -o examples/generated

# Generate only pytest with AI
export OPENAI_API_KEY="sk-..."
ai-test-gen examples/specs/petstore.yaml -f pytest --model gpt-4o

# Filter to specific endpoints
ai-test-gen examples/specs/petstore.yaml --offline --endpoint "GET /pets" --endpoint "POST /pets"
```

### With Authentication

```bash
# Bearer token
ai-test-gen spec.yaml --auth-token "your-jwt-token"

# Custom header
ai-test-gen spec.yaml --auth-header "X-API-Key:your-api-key"
```

### Override Base URL

```bash
ai-test-gen spec.yaml --base-url "http://localhost:8080/api"
```

## 🧪 Test Types Generated

| Category | Tests Generated |
|---|---|
| **Happy Path** | Valid requests with expected responses |
| **Validation** | Missing required fields, invalid types, boundary values |
| **Authentication** | Missing/invalid credentials, expired tokens |
| **Edge Cases** | Empty strings, special characters, null values |
| **Error Handling** | 404 not found, 405 method not allowed, invalid IDs |
| **Business Logic** | State transitions, data consistency (AI mode) |

## 🏗️ Architecture

```
ai_api_test_generator/
├── cli.py          # Click CLI entry point
├── parser.py       # OpenAPI 3.x / Swagger 2.0 parser
├── generator.py    # AI (OpenAI) + offline test generators
└── formatters.py   # Postman, pytest, Jest, REST Assured output
```

## 🤝 Contributing

Contributions are welcome! Here's how to get started:

1. Fork the repository
2. Create a feature branch: `git checkout -b feature/amazing-feature`
3. Install dev dependencies: `pip install -e ".[dev]"`
4. Run tests: `pytest tests/ -v`
5. Make your changes and add tests
6. Submit a pull request

### Development Setup

```bash
git clone https://github.com/kamranghafar/ai-api-test-generator.git
cd ai-api-test-generator
pip install -e ".[dev]"
pytest tests/ -v
```

### Ideas for Contribution

- Add support for gRPC/GraphQL specs
- New output formats (Karate, k6, Artillery)
- Test data generation from JSON Schema
- CI/CD integration templates
- OpenAPI spec validation before generation

## 📄 License

MIT License — see [LICENSE](LICENSE) for details.

## 👨‍💻 Author

**Kamran Ghaffar** — Senior QA Engineer specializing in API testing and AI-powered automation.

- GitHub: [@kamranghafar](https://github.com/kamranghafar)
