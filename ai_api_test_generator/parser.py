"""OpenAPI/Swagger specification parser."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any
from dataclasses import dataclass, field

import yaml
import requests


@dataclass
class Parameter:
    """Represents an API parameter."""
    name: str
    location: str  # query, path, header, cookie
    required: bool = False
    schema_type: str = "string"
    description: str = ""
    enum: list[str] = field(default_factory=list)
    example: Any = None


@dataclass
class RequestBody:
    """Represents a request body."""
    content_type: str = "application/json"
    schema: dict = field(default_factory=dict)
    required: bool = False
    example: Any = None


@dataclass
class Response:
    """Represents an API response."""
    status_code: str
    description: str = ""
    schema: dict = field(default_factory=dict)


@dataclass
class Endpoint:
    """Represents a single API endpoint."""
    path: str
    method: str
    operation_id: str = ""
    summary: str = ""
    description: str = ""
    tags: list[str] = field(default_factory=list)
    parameters: list[Parameter] = field(default_factory=list)
    request_body: RequestBody | None = None
    responses: list[Response] = field(default_factory=list)
    security: list[dict] = field(default_factory=list)


@dataclass
class APISpec:
    """Parsed API specification."""
    title: str
    version: str
    description: str
    base_url: str
    endpoints: list[Endpoint] = field(default_factory=list)
    security_schemes: dict = field(default_factory=dict)
    schemas: dict = field(default_factory=dict)


class OpenAPIParser:
    """Parses OpenAPI 3.x and Swagger 2.0 specifications."""

    def __init__(self, source: str):
        self.source = source
        self.raw: dict = {}
        self._resolved_refs: dict[str, Any] = {}

    def parse(self) -> APISpec:
        """Parse the specification from file path or URL."""
        self.raw = self._load_spec()
        return self._build_api_spec()

    def _load_spec(self) -> dict:
        """Load spec from file or URL."""
        if self.source.startswith(("http://", "https://")):
            resp = requests.get(self.source, timeout=30)
            resp.raise_for_status()
            content = resp.text
        else:
            content = Path(self.source).read_text(encoding="utf-8")

        # Try JSON first, then YAML
        try:
            return json.loads(content)
        except json.JSONDecodeError:
            return yaml.safe_load(content)

    def _resolve_ref(self, obj: Any) -> Any:
        """Resolve $ref references recursively."""
        if not isinstance(obj, dict):
            return obj

        if "$ref" in obj:
            ref_path = obj["$ref"]
            if ref_path in self._resolved_refs:
                return self._resolved_refs[ref_path]

            # Navigate the ref path (e.g., #/components/schemas/Pet)
            parts = ref_path.lstrip("#/").split("/")
            resolved = self.raw
            for part in parts:
                resolved = resolved.get(part, {})

            self._resolved_refs[ref_path] = resolved
            return self._resolve_ref(resolved)

        # Recursively resolve nested objects
        result = {}
        for key, value in obj.items():
            if isinstance(value, dict):
                result[key] = self._resolve_ref(value)
            elif isinstance(value, list):
                result[key] = [
                    self._resolve_ref(item) if isinstance(item, dict) else item
                    for item in value
                ]
            else:
                result[key] = value
        return result

    def _build_api_spec(self) -> APISpec:
        """Build APISpec from raw parsed data."""
        spec = self.raw

        # Determine OpenAPI version
        is_swagger2 = spec.get("swagger", "").startswith("2")

        # Extract info
        info = spec.get("info", {})
        title = info.get("title", "API")
        version = info.get("version", "1.0.0")
        description = info.get("description", "")

        # Extract base URL
        base_url = self._extract_base_url(spec, is_swagger2)

        # Extract security schemes
        if is_swagger2:
            security_schemes = spec.get("securityDefinitions", {})
        else:
            security_schemes = spec.get("components", {}).get("securitySchemes", {})

        # Extract schemas
        if is_swagger2:
            schemas = spec.get("definitions", {})
        else:
            schemas = spec.get("components", {}).get("schemas", {})

        # Parse endpoints
        endpoints = self._parse_endpoints(spec, is_swagger2)

        return APISpec(
            title=title,
            version=version,
            description=description,
            base_url=base_url,
            endpoints=endpoints,
            security_schemes=security_schemes,
            schemas=schemas,
        )

    def _extract_base_url(self, spec: dict, is_swagger2: bool) -> str:
        """Extract the base URL from the spec."""
        if is_swagger2:
            host = spec.get("host", "localhost")
            base_path = spec.get("basePath", "/")
            schemes = spec.get("schemes", ["https"])
            return f"{schemes[0]}://{host}{base_path}"

        servers = spec.get("servers", [])
        if servers:
            return servers[0].get("url", "http://localhost")
        return "http://localhost"

    def _parse_endpoints(self, spec: dict, is_swagger2: bool) -> list[Endpoint]:
        """Parse all endpoint definitions."""
        endpoints = []
        paths = spec.get("paths", {})

        for path, path_item in paths.items():
            if not isinstance(path_item, dict):
                continue

            # Path-level parameters
            path_params = path_item.get("parameters", [])

            for method in ("get", "post", "put", "patch", "delete", "head", "options"):
                operation = path_item.get(method)
                if not operation or not isinstance(operation, dict):
                    continue

                endpoint = self._parse_operation(
                    path, method, operation, path_params, is_swagger2
                )
                endpoints.append(endpoint)

        return endpoints

    def _parse_operation(
        self,
        path: str,
        method: str,
        operation: dict,
        path_params: list,
        is_swagger2: bool,
    ) -> Endpoint:
        """Parse a single operation into an Endpoint."""
        # Merge path-level and operation-level parameters
        all_params = path_params + operation.get("parameters", [])
        parameters = []
        request_body = None

        for param_raw in all_params:
            param = self._resolve_ref(param_raw)

            # In Swagger 2.0, body params are special
            if is_swagger2 and param.get("in") == "body":
                schema = self._resolve_ref(param.get("schema", {}))
                request_body = RequestBody(
                    content_type="application/json",
                    schema=schema,
                    required=param.get("required", False),
                    example=schema.get("example"),
                )
                continue

            schema = self._resolve_ref(param.get("schema", {}))
            parameters.append(
                Parameter(
                    name=param.get("name", ""),
                    location=param.get("in", "query"),
                    required=param.get("required", False),
                    schema_type=schema.get("type", param.get("type", "string")),
                    description=param.get("description", ""),
                    enum=schema.get("enum", param.get("enum", [])),
                    example=schema.get("example", param.get("example")),
                )
            )

        # OpenAPI 3.x request body
        if not is_swagger2 and "requestBody" in operation:
            rb = self._resolve_ref(operation["requestBody"])
            content = rb.get("content", {})
            for ct, ct_data in content.items():
                schema = self._resolve_ref(ct_data.get("schema", {}))
                request_body = RequestBody(
                    content_type=ct,
                    schema=schema,
                    required=rb.get("required", False),
                    example=ct_data.get("example") or schema.get("example"),
                )
                break  # Use first content type

        # Parse responses
        responses = []
        for status_code, resp_data in operation.get("responses", {}).items():
            resp = self._resolve_ref(resp_data)
            schema = {}
            if is_swagger2:
                schema = self._resolve_ref(resp.get("schema", {}))
            else:
                content = resp.get("content", {})
                for ct_data in content.values():
                    schema = self._resolve_ref(ct_data.get("schema", {}))
                    break

            responses.append(
                Response(
                    status_code=str(status_code),
                    description=resp.get("description", ""),
                    schema=schema,
                )
            )

        return Endpoint(
            path=path,
            method=method.upper(),
            operation_id=operation.get("operationId", ""),
            summary=operation.get("summary", ""),
            description=operation.get("description", ""),
            tags=operation.get("tags", []),
            parameters=parameters,
            request_body=request_body,
            responses=responses,
            security=operation.get("security", []),
        )

    def to_prompt_context(self, api_spec: APISpec) -> str:
        """Convert parsed spec to a concise prompt context for AI."""
        lines = [
            f"API: {api_spec.title} v{api_spec.version}",
            f"Base URL: {api_spec.base_url}",
            f"Description: {api_spec.description}",
            "",
            "Security Schemes:",
        ]

        for name, scheme in api_spec.security_schemes.items():
            scheme_type = scheme.get("type", "unknown")
            lines.append(f"  - {name}: {scheme_type}")

        lines.append("")
        lines.append("Endpoints:")

        for ep in api_spec.endpoints:
            lines.append(f"\n  {ep.method} {ep.path}")
            if ep.summary:
                lines.append(f"    Summary: {ep.summary}")

            if ep.parameters:
                lines.append("    Parameters:")
                for p in ep.parameters:
                    req = " (required)" if p.required else ""
                    lines.append(f"      - {p.name} [{p.location}] {p.schema_type}{req}")
                    if p.enum:
                        lines.append(f"        Enum: {p.enum}")

            if ep.request_body:
                lines.append(f"    Request Body ({ep.request_body.content_type}):")
                schema_str = json.dumps(ep.request_body.schema, indent=6, default=str)
                # Truncate very large schemas
                if len(schema_str) > 500:
                    schema_str = schema_str[:500] + "\n      ..."
                lines.append(f"      {schema_str}")

            if ep.responses:
                lines.append("    Responses:")
                for r in ep.responses:
                    lines.append(f"      {r.status_code}: {r.description}")

        return "\n".join(lines)
