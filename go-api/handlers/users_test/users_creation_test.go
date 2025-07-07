package handlers_test

import (
	"bytes"
	"encoding/json"
	"io"
	"net/http"
	"net/http/httptest"
	"testing"

	"go-api/handlers"
	"go-api/utils"

	"github.com/gin-gonic/gin"
	"github.com/jmoiron/sqlx"
	"github.com/stretchr/testify/assert"
)

func TestUserCreation(t *testing.T) {
	t.Run("Successful User Creation", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("POST", "/users", nil)
		reqBody := map[string]string{"name": "newuser", "password": "securepassword"}
		reqBodyJSON, _ := json.Marshal(reqBody)
		req.Body = io.NopCloser(bytes.NewBuffer(reqBodyJSON))
		req.Header.Set("Content-Type", "application/json")

		c.Request = req
		handlers.UserCreator(c)

		assert.Equal(t, http.StatusCreated, w.Code, "Expected Status Created, got %d. Response body: %s", w.Code, w.Body.String())
	})

	t.Run("Missing Username", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("POST", "/users", nil)
		reqBody := map[string]string{"password": "securepassword"}
		reqBodyJSON, _ := json.Marshal(reqBody)
		req.Body = io.NopCloser(bytes.NewBuffer(reqBodyJSON))
		req.Header.Set("Content-Type", "application/json")

		c.Request = req
		handlers.UserCreator(c)

		assert.Equal(t, http.StatusBadRequest, w.Code, "Expected Bad Request, got %d", w.Code)
		assert.Contains(t, w.Body.String(), "Username and password are required")
	})

	t.Run("Missing Password", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("POST", "/users", nil)
		reqBody := map[string]string{"name": "newuser"}
		reqBodyJSON, _ := json.Marshal(reqBody)
		req.Body = io.NopCloser(bytes.NewBuffer(reqBodyJSON))
		req.Header.Set("Content-Type", "application/json")

		c.Request = req
		handlers.UserCreator(c)

		assert.Equal(t, http.StatusBadRequest, w.Code, "Expected Bad Request, got %d", w.Code)
		assert.Contains(t, w.Body.String(), "Username and password are required")
	})

	t.Run("Database Insertion Failure", func(t *testing.T) {
		// Temporarily change the Db to a mock that fails on insert
		oldDb := utils.Db
		utils.Db, _ = sqlx.Open("bad_driver", "invalid_dsn")
		defer func() { utils.Db = oldDb }()

		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("POST", "/users", nil)
		reqBody := map[string]string{"name": "newuser", "password": "securepassword"}
		reqBodyJSON, _ := json.Marshal(reqBody)
		req.Body = io.NopCloser(bytes.NewBuffer(reqBodyJSON))
		req.Header.Set("Content-Type", "application/json")

		c.Request = req
		handlers.UserCreator(c)

		assert.Equal(t, http.StatusInternalServerError, w.Code, "Expected Internal Server Error, got %d", w.Code)
	})
}
