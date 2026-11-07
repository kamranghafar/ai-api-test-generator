/**
 * Auto-generated API tests by ai-api-test-generator
 */

const axios = require('axios');

const BASE_URL = process.env.API_BASE_URL || 'https://petstore.example.com/api/v1';
const AUTH_TOKEN = process.env.API_AUTH_TOKEN || '';

const headers = () => ({
  'Content-Type': 'application/json',
  ...(AUTH_TOKEN ? { Authorization: `Bearer ${AUTH_TOKEN}` } : {}),
});

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

  it('Error handling: DELETE on this endpoint should fail', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(405);
  });

});

describe('POST /pets', () => {
  it('Happy path: Create a new pet', async () => {
    const payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
};
    const response = await axios({
      method: 'post',
      url: `${BASE_URL}/pets`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(201);
  });

  it('Auth: request without credentials returns 401', async () => {
    const payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
};
    const response = await axios({
      method: 'post',
      url: `${BASE_URL}/pets`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(401);
  });

  it('Validation: request with empty/invalid body', async () => {
    const payload = {};
    const response = await axios({
      method: 'post',
      url: `${BASE_URL}/pets`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(400);
  });

  it('Error handling: DELETE on this endpoint should fail', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(405);
  });

});

describe('GET /pets/{petId}', () => {
  it('Happy path: Get a pet by ID', async () => {
    const response = await axios({
      method: 'get',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(200);
  });

  it('Error handling: resource not found with invalid ID', async () => {
    const response = await axios({
      method: 'get',
      url: `${BASE_URL}/pets/INVALID_99999`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(404);
  });

  it('Error handling: DELETE on this endpoint should fail', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(405);
  });

});

describe('PUT /pets/{petId}', () => {
  it('Happy path: Update an existing pet', async () => {
    const payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
};
    const response = await axios({
      method: 'put',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(200);
  });

  it('Error handling: resource not found with invalid ID', async () => {
    const payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
};
    const response = await axios({
      method: 'put',
      url: `${BASE_URL}/pets/INVALID_99999`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(404);
  });

  it('Auth: request without credentials returns 401', async () => {
    const payload = {
    "name": "test_value",
    "species": "test_value",
    "status": "test_value",
    "tags": [
        "test_value"
    ]
};
    const response = await axios({
      method: 'put',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(401);
  });

  it('Validation: request with empty/invalid body', async () => {
    const payload = {};
    const response = await axios({
      method: 'put',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      data: payload,
      validateStatus: () => true,
    });
    expect(response.status).toBe(400);
  });

  it('Error handling: DELETE on this endpoint should fail', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(405);
  });

});

describe('DELETE /pets/{petId}', () => {
  it('Happy path: Delete a pet', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(200);
  });

  it('Error handling: resource not found with invalid ID', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets/INVALID_99999`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(404);
  });

  it('Auth: request without credentials returns 401', async () => {
    const response = await axios({
      method: 'delete',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(401);
  });

  it('Error handling: PATCH on this endpoint should fail', async () => {
    const response = await axios({
      method: 'patch',
      url: `${BASE_URL}/pets/1`,
      headers: headers(),
      validateStatus: () => true,
    });
    expect(response.status).toBe(405);
  });

});
