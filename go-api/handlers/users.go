package handlers

import (
	"database/sql"
	"log"
	"net/http"

	"go-api/models"
	"go-api/utils"

	"github.com/gin-gonic/gin"
	"golang.org/x/crypto/bcrypt"
)

func UserCreator(c *gin.Context) {
	if utils.Db == nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Database connection is not initialized"})
		return
	}

	// Parse JSON body into a struct
	var user credentials
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	username := user.Username
	password := user.Password

	if username == "" || password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Username and password are required"})
		return
	}

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	var userID int64
	err = utils.Db.QueryRow(`
		INSERT INTO USERS (name, password) VALUES ($1, $2) RETURNING id;
	`, username, hashedPassword).Scan(&userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": userID})
}

func UserUpdater(c *gin.Context) {
	// Ensure AuthMiddleware has set the user_id in the context
	userIDInterface, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "User ID not found"})
		return
	}
	userID, ok := userIDInterface.(int)
	if !ok {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Invalid User ID type"})
		return
	}

	// Parse JSON body into a struct
	var user credentials
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	username := user.Username
	password := user.Password

	hashedPassword, err := bcrypt.GenerateFromPassword([]byte(password), bcrypt.DefaultCost)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to hash password"})
		return
	}

	if username == "" && password == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "No information to update"})
		return
	}

	request := ""
	if username == "" {
		request = "UPDATE USERS SET password=$1 WHERE id=$2;"
		_, err = utils.Db.Exec(request, hashedPassword, userID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	} else {
		if password == "" {
			request = "UPDATE USERS SET name=$1 WHERE id=$2;"
			_, err = utils.Db.Exec(request, username, userID)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
		} else {
			request = "UPDATE USERS SET name=$1, password=$2 WHERE id=$3;"
			_, err = utils.Db.Exec(request, username, hashedPassword, userID)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "User updated successfully"})
}

func UserDeleter(c *gin.Context) {
	// Ensure AuthMiddleware has set the user_id in the context
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "User ID not found"})
		return
	}

	_, err := utils.Db.Exec("DELETE FROM USERS WHERE id=$1;", userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "User deleted successfully"})
}

func UserSearcher(c *gin.Context) {
	// UserSearcher does not require userID as per the logic, so no change needed here
	searchName := c.Query("search")

	if searchName == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Search query is required"})
		return
	}

	var users []models.User = []models.User{}
	rows, err := utils.Db.Query("SELECT id, name FROM USERS WHERE name LIKE $1;", "%"+searchName+"%")
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	for rows.Next() {
		var u models.User
		if err := rows.Scan(&u.ID, &u.Username); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		users = append(users, u)
	}
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"users": users})
}

func UserAuthenticator(c *gin.Context) {
	// Log the request method and URL path
	log.Printf("Request Method: %s, URL Path: %s", c.Request.Method, c.Request.URL.Path)
	// Assume username and password are sent as JSON
	var user credentials
	if err := c.ShouldBindJSON(&user); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	// Validate user credentials against the database
	var dbUser models.User
	row := utils.Db.QueryRow("SELECT id, name, password FROM USERS WHERE name = $1;", user.Username)
	err := row.Scan(&dbUser.ID, &dbUser.Username, &dbUser.Password)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	} else if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if err := bcrypt.CompareHashAndPassword([]byte(dbUser.Password), []byte(user.Password)); err != nil {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid username or password"})
		return
	}

	// Create a JWT token for the user
	token, err := utils.CreateToken(dbUser.ID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "Failed to create token"})
		return
	}

	c.SetCookie("token", token, 3600, "/", "localhost", false, true)
	c.JSON(http.StatusOK, gin.H{"message": "Authentication successful", "token": token})
}

type credentials struct {
	Username string `json:"name"`
	Password string `json:"password"`
}
