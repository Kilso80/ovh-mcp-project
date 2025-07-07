// handlers/users_integration_test.go
package handlers_test

import (
	"net/http"
	"net/http/httptest"
	"testing"

	"go-api/handlers"
	"go-api/utils"

	"github.com/gin-gonic/gin"
	"github.com/stretchr/testify/assert"
)

func TestMain(m *testing.M) {
	// Initialize the database connection
	db, err := utils.InitDB("user=goapi password=tatatoto dbname=todolist sslmode=disable")
	if err != nil {
		panic("Failed to connect to database: " + err.Error())
	}
	defer db.Close()
	utils.Db = db

	// Run the tests
	m.Run()
}

func TestUserSearch(t *testing.T) {
	// Insert test user
	_, err := utils.Db.Exec("INSERT INTO USERS (name, password) VALUES ($1, $2)", "testuser", "$2a$10$KwTBMV7Lb94DyRlGjZP2COYhJzFtQ.6J8G2p6UZD6rN4XV8sWJ0kO")
	if err != nil {
		t.Fatalf("Failed to insert test user: %v", err)
	}
	defer utils.Db.Exec("DELETE FROM USERS WHERE name = $1", "testuser")

	t.Run("With existing user", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("GET", "/users?search=testuser", nil)

		c.Request = req
		handlers.UserSearcher(c)

		assert.Equal(t, http.StatusOK, w.Code, "Response Code was %d. Expected %d. Response body: %s", w.Code, http.StatusOK, w.Body.String())
		assert.Contains(t, w.Body.String(), "testuser")
	})

	t.Run("Without search parameter", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("GET", "/users", nil)

		c.Request = req
		handlers.UserSearcher(c)

		assert.Equal(t, http.StatusBadRequest, w.Code, "Response Code was %d. Expected %d. Response body: %s", w.Code, http.StatusBadRequest, w.Body.String())
	})

	t.Run("With non-existing user", func(t *testing.T) {
		w := httptest.NewRecorder()
		c, _ := gin.CreateTestContext(w)
		req, _ := http.NewRequest("GET", "/users?search=nouser", nil)

		c.Request = req
		handlers.UserSearcher(c)

		assert.Equal(t, http.StatusOK, w.Code, "Response Code was %d. Expected %d. Response body: %s", w.Code, http.StatusNotFound, w.Body.String())
		assert.Contains(t, w.Body.String(), "[]")
	})
}

