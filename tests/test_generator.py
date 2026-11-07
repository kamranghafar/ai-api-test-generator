"""Tests for the offline test generator and output formatters."""

import json
from pathlib import Path

import pytest

from ai_api_test_generator.parser import OpenAPIParser
from ai_api_test_generator.generator import OfflineTestGenerator
from ai_api_test_generator.formatters import (
    to_postman_collection,
    to_pytest,
    to_jest,
    to_rest_assured,
)


FIXTURES_DIR = Path(__file__).parent.parent / "examples" / "specs"


@pytest.fixture
def petstore_spec():
    parser = OpenAPIParser(str(FIXTURES_DIR / "petstore.yaml"))
    return parser.parse()


@pytest.fixture
def generated_tests(petstore_spec):
    gen = OfflineTestGenerator()
    return gen.generate_tests(petstore_spec)


class TestOfflineGenerator:
    def test_generates_tests_for_all_endpoints(self, petstore_spec):
        gen = OfflineTestGenerator()
        tests = gen.generate_tests(petstore_spec)
        assert len(tests) == 5  # 5 endpoints

    def test_happy_path_always_present(self, generated_tests):
        for key, tests in generated_tests.items():
            names = [t["name"] for t in tests]
            assert any("success" in n for n in names), f"No happy-path test for {key}"

    def test_auth_test_for_secured_endpoints(self, generated_tests):
        post_key = "POST /pets"
        tests = generated_tests[post_key]
        assert any("unauthorized" in t["name"] for t in tests)

    def test_not_found_for_path_params(self, generated_tests):
        get_key = "GET /pets/{petId}"
        tests = generated_tests[get_key]
        assert any("not_found" in t["name"] for t in tests)

    def test_invalid_body_for_post(self, generated_tests):
        post_key = "POST /pets"
        tests = generated_tests[post_key]
        assert any("invalid_body" in t["name"] for t in tests)

    def test_filter_endpoints(self, petstore_spec):
        gen = OfflineTestGenerator()
        tests = gen.generate_tests(petstore_spec, endpoints_filter=["GET /pets"])
        assert "GET /pets" in tests
        assert "POST /pets" not in tests


class TestPostmanFormatter:
    def test_valid_collection_structure(self, petstore_spec, generated_tests):
        collection = to_postman_collection(
            petstore_spec.title, petstore_spec.base_url, generated_tests
        )
        assert "info" in collection
        assert "item" in collection
        assert collection["info"]["name"] == "Petstore API - AI Generated Tests"

    def test_collection_has_items(self, petstore_spec, generated_tests):
        collection = to_postman_collection(
            petstore_spec.title, petstore_spec.base_url, generated_tests
        )
        assert len(collection["item"]) > 0

    def test_serializable_to_json(self, petstore_spec, generated_tests):
        collection = to_postman_collection(
            petstore_spec.title, petstore_spec.base_url, generated_tests
        )
        serialized = json.dumps(collection, indent=2)
        assert len(serialized) > 100


class TestPytestFormatter:
    def test_generates_valid_python(self, petstore_spec, generated_tests):
        code = to_pytest(petstore_spec.base_url, generated_tests)
        assert "import requests" in code
        assert "def test_" in code
        assert "BASE_URL" in code

    def test_compilable_python(self, petstore_spec, generated_tests):
        code = to_pytest(petstore_spec.base_url, generated_tests)
        compile(code, "<generated>", "exec")


class TestJestFormatter:
    def test_generates_valid_js(self, petstore_spec, generated_tests):
        code = to_jest(petstore_spec.base_url, generated_tests)
        assert "require('axios')" in code
        assert "describe(" in code
        assert "it(" in code

    def test_contains_assertions(self, petstore_spec, generated_tests):
        code = to_jest(petstore_spec.base_url, generated_tests)
        assert "expect(" in code


class TestRestAssuredFormatter:
    def test_generates_valid_java(self, petstore_spec, generated_tests):
        code = to_rest_assured(petstore_spec.base_url, generated_tests)
        assert "import io.restassured" in code
        assert "public class ApiTests" in code
        assert "@Test" in code

    def test_custom_class_name(self, petstore_spec, generated_tests):
        code = to_rest_assured(
            petstore_spec.base_url, generated_tests, class_name="PetstoreTests"
        )
        assert "public class PetstoreTests" in code
