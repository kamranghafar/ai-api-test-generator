"""AI-powered test scenario generator using OpenAI."""

from __future__ import annotations

import json
import os
from typing import Any

from openai import OpenAI
from rich.console import Console

from .parser import APISpec, Endpoint

console = Console()

SYSTEM_PROMPT = """You are an expert QA engineer specializing in API testing. Given an API specification,
generate comprehensive test scenarios covering:

1. **Happy Path**: Valid requests with expected successful responses
2. **Validation**: Invalid inputs, missing required fields, wrong types, boundary values
3. **Authentication/Authorization**: Missing auth, invalid tokens, expired credentials
4. **Edge Cases**: Empty strings, very long strings, special characters, unicode, null values
5. **Error Handling**: Server errors, not found, conflict states, rate limiting
6. **Business Logic**: Workflow tests, state transitions, data consistency

For each test, provide:
- Test name (descriptive, snake_case)
- Description of what it tests
- HTTP method and path
- Headers (including auth)
- Request body (if applicable)
- Query parameters (if applicable)
- Expected status code
- Expected response validation (key fields to check)
- Assertions to make

Return ONLY valid JSON in the specified format."""


def _build_test_generation_prompt(
    api_context: str,
    endpoint: Endpoint,
    base_url: str,
    auth_config: dict | None = None,
) -> str:
    """Build the prompt for generating tests for a specific endpoint."""
    auth_info = ""
    if auth_config:
        auth_info = f"\nAuthentication config: {json.dumps(auth_config)}"

    return f"""Generate comprehensive API test scenarios for the following endpoint.

API Context:
{api_context}
{auth_info}

Focus endpoint: {endpoint.method} {endpoint.path}
Summary: {endpoint.summary}
Description: {endpoint.description}

Return a JSON array of test objects with this structure:
{{
  "tests": [
    {{
      "name": "test_descriptive_name",
      "description": "What this test verifies",
      "method": "{endpoint.method}",
      "path": "{endpoint.path}",
      "headers": {{"Content-Type": "application/json"}},
      "query_params": {{}},
      "path_params": {{}},
      "body": null,
      "expected_status": 200,
      "assertions": [
        {{"type": "status_code", "value": 200}},
        {{"type": "response_has_key", "key": "id"}},
        {{"type": "response_type", "key": "data", "expected": "array"}}
      ]
    }}
  ]
}}

Generate 5-8 tests covering happy path, validation, error handling, and edge cases.
Return ONLY the JSON, no markdown or extra text."""


class AITestGenerator:
    """Generates test scenarios using OpenAI."""

    def __init__(
        self,
        api_key: str | None = None,
        model: str = "gpt-4o-mini",
        base_url_override: str | None = None,
    ):
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY", "")
        if not self.api_key:
            raise ValueError(
                "OpenAI API key required. Set OPENAI_API_KEY env var or pass --api-key."
            )
        self.client = OpenAI(api_key=self.api_key)
        self.model = model
        self.base_url_override = base_url_override

    def generate_tests(
        self,
        api_spec: APISpec,
        api_context: str,
        auth_config: dict | None = None,
        endpoints_filter: list[str] | None = None,
    ) -> dict[str, list[dict]]:
        """Generate test scenarios for all endpoints in the spec."""
        base_url = self.base_url_override or api_spec.base_url
        all_tests: dict[str, list[dict]] = {}

        endpoints = api_spec.endpoints
        if endpoints_filter:
            endpoints = [
                ep for ep in endpoints
                if any(f in f"{ep.method} {ep.path}" for f in endpoints_filter)
            ]

        for i, endpoint in enumerate(endpoints):
            key = f"{endpoint.method} {endpoint.path}"
            console.print(
                f"  [{i+1}/{len(endpoints)}] Generating tests for [cyan]{key}[/cyan]..."
            )

            try:
                tests = self._generate_for_endpoint(
                    api_context, endpoint, base_url, auth_config
                )
                all_tests[key] = tests
            except Exception as e:
                console.print(f"    [red]Error: {e}[/red]")
                all_tests[key] = []

        return all_tests

    def _generate_for_endpoint(
        self,
        api_context: str,
        endpoint: Endpoint,
        base_url: str,
        auth_config: dict | None,
    ) -> list[dict]:
        """Generate tests for a single endpoint using AI."""
        prompt = _build_test_generation_prompt(
            api_context, endpoint, base_url, auth_config
        )

        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": prompt},
            ],
            temperature=0.3,
            max_tokens=4000,
            response_format={"type": "json_object"},
        )

        content = response.choices[0].message.content or "{}"
        result = json.loads(content)
        return result.get("tests", [])


class OfflineTestGenerator:
    """Generates test scenarios without AI using rule-based heuristics.

    Useful when no OpenAI key is available or for deterministic output.
    """

    def generate_tests(
        self,
        api_spec: APISpec,
        auth_config: dict | None = None,
        endpoints_filter: list[str] | None = None,
    ) -> dict[str, list[dict]]:
        """Generate rule-based test scenarios for all endpoints."""
        base_url = api_spec.base_url
        all_tests: dict[str, list[dict]] = {}

        endpoints = api_spec.endpoints
        if endpoints_filter:
            endpoints = [
                ep for ep in endpoints
                if any(f in f"{ep.method} {ep.path}" for f in endpoints_filter)
            ]

        for endpoint in endpoints:
            key = f"{endpoint.method} {endpoint.path}"
            all_tests[key] = self._generate_for_endpoint(endpoint, base_url, auth_config)

        return all_tests

    def _generate_for_endpoint(
        self,
        endpoint: Endpoint,
        base_url: str,
        auth_config: dict | None,
    ) -> list[dict]:
        """Generate deterministic tests for one endpoint."""
        tests = []
        path = endpoint.path
        method = endpoint.method

        # Build default headers
        headers: dict[str, str] = {"Content-Type": "application/json"}
        if auth_config:
            headers.update(auth_config.get("headers", {}))

        # Path params placeholder values
        path_params = {}
        for p in endpoint.parameters:
            if p.location == "path":
                path_params[p.name] = p.example or self._sample_value(p.schema_type)

        # 1. Happy path
        body = self._build_sample_body(endpoint) if endpoint.request_body else None
        expected = 200 if method == "GET" else (201 if method == "POST" else 200)
        tests.append({
            "name": f"test_{method.lower()}_{self._slug(path)}_success",
            "description": f"Happy path: {endpoint.summary or method + ' ' + path}",
            "method": method,
            "path": path,
            "headers": headers,
            "query_params": {},
            "path_params": path_params,
            "body": body,
            "expected_status": expected,
            "assertions": [{"type": "status_code", "value": expected}],
        })

        # 2. Missing required params → 400/422
        for p in endpoint.parameters:
            if p.required and p.location == "query":
                tests.append({
                    "name": f"test_{method.lower()}_{self._slug(path)}_missing_{p.name}",
                    "description": f"Validation: missing required query param '{p.name}'",
                    "method": method,
                    "path": path,
                    "headers": headers,
                    "query_params": {},
                    "path_params": path_params,
                    "body": body,
                    "expected_status": 400,
                    "assertions": [{"type": "status_code", "value": 400}],
                })

        # 3. Invalid path param → 404
        if any(p.location == "path" for p in endpoint.parameters):
            bad_path_params = {k: "INVALID_99999" for k in path_params}
            tests.append({
                "name": f"test_{method.lower()}_{self._slug(path)}_not_found",
                "description": "Error handling: resource not found with invalid ID",
                "method": method,
                "path": path,
                "headers": headers,
                "query_params": {},
                "path_params": bad_path_params,
                "body": body,
                "expected_status": 404,
                "assertions": [{"type": "status_code", "value": 404}],
            })

        # 4. Auth missing → 401
        if endpoint.security or auth_config:
            tests.append({
                "name": f"test_{method.lower()}_{self._slug(path)}_unauthorized",
                "description": "Auth: request without credentials returns 401",
                "method": method,
                "path": path,
                "headers": {"Content-Type": "application/json"},
                "query_params": {},
                "path_params": path_params,
                "body": body,
                "expected_status": 401,
                "assertions": [{"type": "status_code", "value": 401}],
            })

        # 5. Invalid body → 400/422 (for POST/PUT/PATCH)
        if method in ("POST", "PUT", "PATCH") and endpoint.request_body:
            tests.append({
                "name": f"test_{method.lower()}_{self._slug(path)}_invalid_body",
                "description": "Validation: request with empty/invalid body",
                "method": method,
                "path": path,
                "headers": headers,
                "query_params": {},
                "path_params": path_params,
                "body": {},
                "expected_status": 400,
                "assertions": [{"type": "status_code", "value": 400}],
            })

        # 6. Wrong method → 405
        wrong_method = "DELETE" if method != "DELETE" else "PATCH"
        tests.append({
            "name": f"test_{self._slug(path)}_method_not_allowed",
            "description": f"Error handling: {wrong_method} on this endpoint should fail",
            "method": wrong_method,
            "path": path,
            "headers": headers,
            "query_params": {},
            "path_params": path_params,
            "body": None,
            "expected_status": 405,
            "assertions": [{"type": "status_code", "value": 405}],
        })

        return tests

    @staticmethod
    def _slug(path: str) -> str:
        return path.strip("/").replace("/", "_").replace("{", "").replace("}", "").replace("-", "_")

    @staticmethod
    def _sample_value(schema_type: str) -> Any:
        return {
            "integer": 1,
            "number": 1.0,
            "boolean": True,
            "string": "test_value",
            "array": [],
        }.get(schema_type, "test_value")

    def _build_sample_body(self, endpoint: Endpoint) -> dict | None:
        if not endpoint.request_body:
            return None
        schema = endpoint.request_body.schema
        if endpoint.request_body.example:
            return endpoint.request_body.example
        return self._schema_to_sample(schema)

    def _schema_to_sample(self, schema: dict) -> Any:
        if not schema:
            return {}
        stype = schema.get("type", "object")
        if stype == "object":
            props = schema.get("properties", {})
            return {k: self._schema_to_sample(v) for k, v in props.items()}
        if stype == "array":
            items = schema.get("items", {})
            return [self._schema_to_sample(items)]
        return self._sample_value(stype)
