// Auto-generated API tests by ai-api-test-generator

import io.restassured.RestAssured;
import io.restassured.http.ContentType;
import org.junit.jupiter.api.*;
import static io.restassured.RestAssured.*;
import static org.hamcrest.Matchers.*;

public class ApiTests {

    @BeforeAll
    public static void setup() {
        RestAssured.baseURI = System.getenv("API_BASE_URL") != null
            ? System.getenv("API_BASE_URL")
            : "https://petstore.example.com/api/v1";
    }

    // GET /pets
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

    @Test
    @DisplayName("Error handling: DELETE on this endpoint should fail")
    public void test_pets_method_not_allowed() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets")
        .then()
            .statusCode(405);
    }

    // POST /pets
    @Test
    @DisplayName("Happy path: Create a new pet")
    public void test_post_pets_success() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"name\": \"test_value\", \"species\": \"test_value\", \"status\": \"test_value\", \"tags\": [\"test_value\"]}")
        .when()
            .post("/pets")
        .then()
            .statusCode(201);
    }

    @Test
    @DisplayName("Auth: request without credentials returns 401")
    public void test_post_pets_unauthorized() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"name\": \"test_value\", \"species\": \"test_value\", \"status\": \"test_value\", \"tags\": [\"test_value\"]}")
        .when()
            .post("/pets")
        .then()
            .statusCode(401);
    }

    @Test
    @DisplayName("Validation: request with empty/invalid body")
    public void test_post_pets_invalid_body() {
        given()
            .contentType(ContentType.JSON)
            .body("{}")
        .when()
            .post("/pets")
        .then()
            .statusCode(400);
    }

    @Test
    @DisplayName("Error handling: DELETE on this endpoint should fail")
    public void test_pets_method_not_allowed() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets")
        .then()
            .statusCode(405);
    }

    // GET /pets/{petId}
    @Test
    @DisplayName("Happy path: Get a pet by ID")
    public void test_get_pets_petId_success() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .get("/pets/1")
        .then()
            .statusCode(200);
    }

    @Test
    @DisplayName("Error handling: resource not found with invalid ID")
    public void test_get_pets_petId_not_found() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .get("/pets/INVALID_99999")
        .then()
            .statusCode(404);
    }

    @Test
    @DisplayName("Error handling: DELETE on this endpoint should fail")
    public void test_pets_petId_method_not_allowed() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets/1")
        .then()
            .statusCode(405);
    }

    // PUT /pets/{petId}
    @Test
    @DisplayName("Happy path: Update an existing pet")
    public void test_put_pets_petId_success() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"name\": \"test_value\", \"species\": \"test_value\", \"status\": \"test_value\", \"tags\": [\"test_value\"]}")
        .when()
            .put("/pets/1")
        .then()
            .statusCode(200);
    }

    @Test
    @DisplayName("Error handling: resource not found with invalid ID")
    public void test_put_pets_petId_not_found() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"name\": \"test_value\", \"species\": \"test_value\", \"status\": \"test_value\", \"tags\": [\"test_value\"]}")
        .when()
            .put("/pets/INVALID_99999")
        .then()
            .statusCode(404);
    }

    @Test
    @DisplayName("Auth: request without credentials returns 401")
    public void test_put_pets_petId_unauthorized() {
        given()
            .contentType(ContentType.JSON)
            .body("{\"name\": \"test_value\", \"species\": \"test_value\", \"status\": \"test_value\", \"tags\": [\"test_value\"]}")
        .when()
            .put("/pets/1")
        .then()
            .statusCode(401);
    }

    @Test
    @DisplayName("Validation: request with empty/invalid body")
    public void test_put_pets_petId_invalid_body() {
        given()
            .contentType(ContentType.JSON)
            .body("{}")
        .when()
            .put("/pets/1")
        .then()
            .statusCode(400);
    }

    @Test
    @DisplayName("Error handling: DELETE on this endpoint should fail")
    public void test_pets_petId_method_not_allowed() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets/1")
        .then()
            .statusCode(405);
    }

    // DELETE /pets/{petId}
    @Test
    @DisplayName("Happy path: Delete a pet")
    public void test_delete_pets_petId_success() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets/1")
        .then()
            .statusCode(200);
    }

    @Test
    @DisplayName("Error handling: resource not found with invalid ID")
    public void test_delete_pets_petId_not_found() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets/INVALID_99999")
        .then()
            .statusCode(404);
    }

    @Test
    @DisplayName("Auth: request without credentials returns 401")
    public void test_delete_pets_petId_unauthorized() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .delete("/pets/1")
        .then()
            .statusCode(401);
    }

    @Test
    @DisplayName("Error handling: PATCH on this endpoint should fail")
    public void test_pets_petId_method_not_allowed() {
        given()
            .contentType(ContentType.JSON)
        .when()
            .patch("/pets/1")
        .then()
            .statusCode(405);
    }

}