"""Tests for the OpenAPI parser."""

import json
from pathlib import Path

import pytest

from ai_api_test_generator.parser import OpenAPIParser, APISpec


FIXTURES_DIR = Path(__file__).parent.parent / "examples" / "specs"


class TestOpenAPIParser:
    """Test suite for OpenAPIParser."""

    def test_parse_yaml_spec(self):
        """Should parse a YAML OpenAPI spec correctly."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()

        assert isinstance(spec, APISpec)
        assert spec.title == "Petstore API"
        assert spec.version == "1.0.0"
        assert spec.base_url == "https://petstore.example.com/api/v1"

    def test_endpoint_count(self):
        """Should find all endpoints."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()
        assert len(spec.endpoints) == 5  # GET/POST /pets + GET/PUT/DELETE /pets/{petId}

    def test_endpoint_methods(self):
        """Should parse HTTP methods correctly."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()
        methods = {(ep.method, ep.path) for ep in spec.endpoints}
        assert ("GET", "/pets") in methods
        assert ("POST", "/pets") in methods
        assert ("GET", "/pets/{petId}") in methods
        assert ("PUT", "/pets/{petId}") in methods
        assert ("DELETE", "/pets/{petId}") in methods

    def test_parameters_parsed(self):
        """Should parse query and path parameters."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()

        get_pets = next(ep for ep in spec.endpoints if ep.method == "GET" and ep.path == "/pets")
        param_names = [p.name for p in get_pets.parameters]
        assert "limit" in param_names
        assert "status" in param_names

    def test_request_body_parsed(self):
        """Should parse request body with schema."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()

        post_pets = next(ep for ep in spec.endpoints if ep.method == "POST" and ep.path == "/pets")
        assert post_pets.request_body is not None
        assert post_pets.request_body.content_type == "application/json"
        assert "properties" in post_pets.request_body.schema

    def test_responses_parsed(self):
        """Should parse response definitions."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()

        get_pet = next(
            ep for ep in spec.endpoints
            if ep.method == "GET" and ep.path == "/pets/{petId}"
        )
        status_codes = {r.status_code for r in get_pet.responses}
        assert "200" in status_codes
        assert "404" in status_codes

    def test_security_schemes(self):
        """Should extract security schemes."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()
        assert "bearerAuth" in spec.security_schemes

    def test_prompt_context_generation(self):
        """Should generate a prompt context string."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()
        context = parser.to_prompt_context(spec)

        assert "Petstore API" in context
        assert "GET /pets" in context
        assert "POST /pets" in context

    def test_enum_values_parsed(self):
        """Should parse enum constraints."""
        parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
        spec = parser.parse()

        get_pets = next(ep for ep in spec.endpoints if ep.method == "GET" and ep.path == "/pets")
        status_param = next(p for p in get_pets.parameters if p.name == "status")
        assert status_param.enum == ["available", "pending", "sold"]
