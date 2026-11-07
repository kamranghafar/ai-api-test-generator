"""Output formatters for different test frameworks."""

from __future__ import annotations

import json
import re
from typing import Any


def _resolve_path(path: str, path_params: dict) -> str:
    """Replace path placeholders with values."""
    result = path
    for key, value in path_params.items():
        result = result.replace(f"{{{key}}}", str(value))
    return result


def _safe_name(name: str) -> str:
    """Sanitize a test name."""
    return re.sub(r"[^a-zA-Z0-9_]", "_", name)


# ---------------------------------------------------------------------------
# Postman Collection v2.1
# ---------------------------------------------------------------------------

def to_postman_collection(
    api_title: str,
    base_url: str,
    all_tests: dict[str, list[dict]],
) -> dict:
    """Convert tests to a Postman Collection v2.1 JSON structure."""
    items = []

    for endpoint_key, tests in all_tests.items():
        folder_items = []
        for test in tests:
            method = test["method"]
            path = _resolve_path(test["path"], test.get("path_params", {}))
            url_raw = f"{base_url.rstrip('/')}{path}"

            # Query params
            query = []
            for k, v in test.get("query_params", {}).items():
                query.append({"key": k, "value": str(v)})

            # Headers
            header = []
            for k, v in test.get("headers", {}).items():
                header.append({"key": k, "value": v})

            # Build Postman test script
            pm_tests = []
            for assertion in test.get("assertions", []):
                if assertion["type"] == "status_code":
                    pm_tests.append(
                        f'pm.test("Status code is {assertion["value"]}", function () {{\n'
                        f'    pm.response.to.have.status({assertion["value"]});\n'
                        f'}});'
                    )
                elif assertion["type"] == "response_has_key":
                    pm_tests.append(
                        f'pm.test("Response has key {assertion["key"]}", function () {{\n'
                        f'    var jsonData = pm.response.json();\n'
                        f'    pm.expect(jsonData).to.have.property("{assertion["key"]}");\n'
                        f'}});'
                    )
                elif assertion["type"] == "response_type":
                    expected = assertion.get("expected", "object")
                    pm_tests.append(
                        f'pm.test("{assertion["key"]} is {expected}", function () {{\n'
                        f'    var jsonData = pm.response.json();\n'
                        f'    pm.expect(typeof jsonData.{assertion["key"]}).to.eql("{expected}");\n'
                        f'}});'
                    )

            body_obj: dict | None = None
            if test.get("body") is not None:
                body_obj = {
                    "mode": "raw",
                    "raw": json.dumps(test["body"], indent=2),
                    "options": {"raw": {"language": "json"}},
                }

            request_obj: dict[str, Any] = {
                "method": method,
                "header": header,
                "url": {
                    "raw": url_raw,
                    "host": [base_url.rstrip("/")],
                    "path": [p for p in path.strip("/").split("/") if p],
                    "query": query,
                },
            }
            if body_obj:
                request_obj["body"] = body_obj

            item = {
                "name": test.get("description", test["name"]),
                "event": [
                    {
                        "listen": "test",
                        "script": {
                            "type": "text/javascript",
                            "exec": pm_tests,
                        },
                    }
                ],
                "request": request_obj,
            }
            folder_items.append(item)

        items.append({"name": endpoint_key, "item": folder_items})

    return {
        "info": {
            "name": f"{api_title} - AI Generated Tests",
            "schema": "https://schema.getpostman.com/json/collection/v2.1.0/collection.json",
        },
        "item": items,
    }


# ---------------------------------------------------------------------------
# Python pytest + requests
# ---------------------------------------------------------------------------

def to_pytest(
    base_url: str,
    all_tests: dict[str, list[dict]],
) -> str:
    """Generate pytest + requests test code."""
    lines = [
        '"""Auto-generated API tests by ai-api-test-generator."""',
        "",
        "import os",
        "import pytest",
        "import requests",
        "",
        "",
        f'BASE_URL = os.getenv("API_BASE_URL", "{base_url.rstrip("/")}")',
        'AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")',
        "",
        "",
        "def _headers(extra=None):",
        '    h = {"Content-Type": "application/json"}',
        "    if AUTH_TOKEN:",
        '        h["Authorization"] = f"Bearer {AUTH_TOKEN}"',
        "    if extra:",
        "        h.update(extra)",
        "    return h",
        "",
    ]

    for endpoint_key, tests in all_tests.items():
        lines.append("")
        lines.append(f"# {'=' * 70}")
        lines.append(f"# {endpoint_key}")
        lines.append(f"# {'=' * 70}")
        lines.append("")

        for test in tests:
            name = _safe_name(test["name"])
            if not name.startswith("test_"):
                name = f"test_{name}"

            method = test["method"].lower()
            path = test["path"]
            path_params = test.get("path_params", {})
            resolved = _resolve_path(path, path_params)
            body = test.get("body")
            query = test.get("query_params", {})
            expected_status = test.get("expected_status", 200)
            desc = test.get("description", "")

            lines.append(f"def {name}():")
            lines.append(f'    """{desc}"""')
            lines.append(f'    url = f"{{BASE_URL}}{resolved}"')

            if test.get("headers") and "Authorization" not in str(test["headers"]):
                lines.append(f"    headers = _headers()")
            else:
                custom = {k: v for k, v in test.get("headers", {}).items() if k != "Content-Type"}
                if custom:
                    lines.append(f"    headers = _headers({custom!r})")
                else:
                    lines.append("    headers = _headers()")

            args = ["url", "headers=headers"]
            if body is not None:
                lines.append(f"    payload = {json.dumps(body, indent=4)}")
                args.append("json=payload")
            if query:
                lines.append(f"    params = {json.dumps(query)}")
                args.append("params=params")

            lines.append(f"    response = requests.{method}({', '.join(args)})")
            lines.append(f"    assert response.status_code == {expected_status}")

            for assertion in test.get("assertions", []):
                if assertion["type"] == "response_has_key":
                    lines.append(f'    assert "{assertion["key"]}" in response.json()')
                elif assertion["type"] == "response_type" and assertion.get("expected") == "array":
                    lines.append(f'    assert isinstance(response.json().get("{assertion["key"]}"), list)')

            lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# JavaScript / Jest + axios
# ---------------------------------------------------------------------------

def to_jest(
    base_url: str,
    all_tests: dict[str, list[dict]],
) -> str:
    """Generate Jest + axios test code."""
    lines = [
        "/**",
        " * Auto-generated API tests by ai-api-test-generator",
        " */",
        "",
        "const axios = require('axios');",
        "",
        f"const BASE_URL = process.env.API_BASE_URL || '{base_url.rstrip('/')}';",
        "const AUTH_TOKEN = process.env.API_AUTH_TOKEN || '';",
        "",
        "const headers = () => ({",
        "  'Content-Type': 'application/json',",
        "  ...(AUTH_TOKEN ? { Authorization: `Bearer ${AUTH_TOKEN}` } : {}),",
        "});",
        "",
    ]

    for endpoint_key, tests in all_tests.items():
        safe_desc = endpoint_key.replace("'", "\\'")
        lines.append(f"describe('{safe_desc}', () => {{")

        for test in tests:
            method = test["method"].lower()
            path = test["path"]
            path_params = test.get("path_params", {})
            resolved = _resolve_path(path, path_params)
            body = test.get("body")
            expected_status = test.get("expected_status", 200)
            desc = test.get("description", test["name"]).replace("'", "\\'")

            lines.append(f"  it('{desc}', async () => {{")

            if body is not None:
                body_json = json.dumps(body, indent=4)
                lines.append(f"    const payload = {body_json};")

            lines.append("    const response = await axios({")
            lines.append(f"      method: '{method}',")
            lines.append(f"      url: `${{BASE_URL}}{resolved}`,")
            lines.append(f"      headers: headers(),")

            if body is not None:
                lines.append("      data: payload,")

            query = test.get("query_params", {})
            if query:
                lines.append(f"      params: {json.dumps(query)},")

            lines.append("      validateStatus: () => true,")
            lines.append("    });")
            lines.append(f"    expect(response.status).toBe({expected_status});")

            for assertion in test.get("assertions", []):
                if assertion["type"] == "response_has_key":
                    lines.append(
                        f"    expect(response.data).toHaveProperty('{assertion['key']}');"
                    )

            lines.append("  });")
            lines.append("")

        lines.append("});")
        lines.append("")

    return "\n".join(lines)


# ---------------------------------------------------------------------------
# REST Assured (Java)
# ---------------------------------------------------------------------------

def to_rest_assured(
    base_url: str,
    all_tests: dict[str, list[dict]],
    class_name: str = "ApiTests",
) -> str:
    """Generate REST Assured (Java) test code."""
    lines = [
        "// Auto-generated API tests by ai-api-test-generator",
        "",
        "import io.restassured.RestAssured;",
        "import io.restassured.http.ContentType;",
        "import org.junit.jupiter.api.*;",
        "import static io.restassured.RestAssured.*;",
        "import static org.hamcrest.Matchers.*;",
        "",
        f"public class {class_name} {{",
        "",
        "    @BeforeAll",
        "    public static void setup() {",
        f'        RestAssured.baseURI = System.getenv("API_BASE_URL") != null',
        f'            ? System.getenv("API_BASE_URL")',
        f'            : "{base_url.rstrip("/")}";',
        "    }",
        "",
    ]

    for endpoint_key, tests in all_tests.items():
        lines.append(f"    // {endpoint_key}")

        for test in tests:
            method = test["method"].lower()
            path = test["path"]
            path_params = test.get("path_params", {})
            resolved = _resolve_path(path, path_params)
            body = test.get("body")
            expected_status = test.get("expected_status", 200)
            desc = test.get("description", test["name"])
            java_name = _safe_name(test["name"])

            lines.append("    @Test")
            lines.append(f'    @DisplayName("{desc}")')
            lines.append(f"    public void {java_name}() {{")
            lines.append("        given()")
            lines.append("            .contentType(ContentType.JSON)")

            if body is not None:
                body_str = json.dumps(body).replace('"', '\\"')
                lines.append(f'            .body("{body_str}")')

            query = test.get("query_params", {})
            for k, v in query.items():
                lines.append(f'            .queryParam("{k}", "{v}")')

            lines.append(f"        .when()")
            lines.append(f'            .{method}("{resolved}")')
            lines.append(f"        .then()")
            lines.append(f"            .statusCode({expected_status});")
            lines.append("    }")
            lines.append("")

    lines.append("}")
    return "\n".join(lines)
