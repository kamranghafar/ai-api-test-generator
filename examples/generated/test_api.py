"""Auto-generated API tests by ai-api-test-generator."""

import os
import pytest
import requests


BASE_URL = os.getenv("API_BASE_URL", "https://petstore.example.com/api/v1")
AUTH_TOKEN = os.getenv("API_AUTH_TOKEN", "")


def _headers(extra=None):
    h = {"Content-Type": "application/json"}
    if AUTH_TOKEN:
        h["Authorization"] = f"Bearer {AUTH_TOKEN}"
    if extra:
        h.update(extra)
    return h


# ======================================================================
# GET /pets
# ======================================================================

def test_get_pets_success():
    """Happy path: List all pets"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    response = requests.get(url, headers=headers)
    assert response.status_code == 200

def test_pets_method_not_allowed():
    """Error handling: DELETE on this endpoint should fail"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 405


# ======================================================================
# POST /pets
# ======================================================================

def test_post_pets_success():
    """Happy path: Create a new pet"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
}
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 201

def test_post_pets_unauthorized():
    """Auth: request without credentials returns 401"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
}
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 401

def test_post_pets_invalid_body():
    """Validation: request with empty/invalid body"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    payload = {}
    response = requests.post(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_pets_method_not_allowed():
    """Error handling: DELETE on this endpoint should fail"""
    url = f"{BASE_URL}/pets"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 405


# ======================================================================
# GET /pets/{petId}
# ======================================================================

def test_get_pets_petId_success():
    """Happy path: Get a pet by ID"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    response = requests.get(url, headers=headers)
    assert response.status_code == 200

def test_get_pets_petId_not_found():
    """Error handling: resource not found with invalid ID"""
    url = f"{BASE_URL}/pets/INVALID_99999"
    headers = _headers()
    response = requests.get(url, headers=headers)
    assert response.status_code == 404

def test_pets_petId_method_not_allowed():
    """Error handling: DELETE on this endpoint should fail"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 405


# ======================================================================
# PUT /pets/{petId}
# ======================================================================

def test_put_pets_petId_success():
    """Happy path: Update an existing pet"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
}
    response = requests.put(url, headers=headers, json=payload)
    assert response.status_code == 200

def test_put_pets_petId_not_found():
    """Error handling: resource not found with invalid ID"""
    url = f"{BASE_URL}/pets/INVALID_99999"
    headers = _headers()
    payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
}
    response = requests.put(url, headers=headers, json=payload)
    assert response.status_code == 404

def test_put_pets_petId_unauthorized():
    """Auth: request without credentials returns 401"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
}
    response = requests.put(url, headers=headers, json=payload)
    assert response.status_code == 401

def test_put_pets_petId_invalid_body():
    """Validation: request with empty/invalid body"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    payload = {}
    response = requests.put(url, headers=headers, json=payload)
    assert response.status_code == 400

def test_pets_petId_method_not_allowed():
    """Error handling: DELETE on this endpoint should fail"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 405


# ======================================================================
# DELETE /pets/{petId}
# ======================================================================

def test_delete_pets_petId_success():
    """Happy path: Delete a pet"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 200

def test_delete_pets_petId_not_found():
    """Error handling: resource not found with invalid ID"""
    url = f"{BASE_URL}/pets/INVALID_99999"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 404

def test_delete_pets_petId_unauthorized():
    """Auth: request without credentials returns 401"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    response = requests.delete(url, headers=headers)
    assert response.status_code == 401

def test_pets_petId_method_not_allowed():
    """Error handling: PATCH on this endpoint should fail"""
    url = f"{BASE_URL}/pets/1"
    headers = _headers()
    response = requests.patch(url, headers=headers)
    assert response.status_code == 405
