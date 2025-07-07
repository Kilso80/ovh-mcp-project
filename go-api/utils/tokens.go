package utils

import (
	"database/sql"
	"math/rand"
	"time"

	"github.com/gin-gonic/gin"
)

// Generate a random token for simplicity
func generateRandomToken(length int) string {
	rand.Seed(time.Now().UnixNano())
	const letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789"
	b := make([]byte, length)
	for i := range b {
		b[i] = letters[rand.Intn(len(letters))]
	}
	return string(b)
}

func CreateToken(userID int) (string, error) {
	token := generateRandomToken(32)
	query := "INSERT INTO TOKENS (token, user_id) VALUES ($1, $2);"
	_, err := Db.Exec(query, token, userID)
	if err != nil {
		return "", err
	}
	return token, nil
}

func GetUserIDFromToken(c *gin.Context) int {
	// Get token from the Authorization header
	authHeader := c.GetHeader("Authorization")
	if authHeader == "" {
		c.JSON(401, gin.H{"error": "Authentication required"})
		c.Abort()
		return 0
	}

	// Assuming the token is prefixed with "Bearer ", remove the prefix
	tokenString := authHeader[len("Bearer "):]

	var userID int
	query := "SELECT user_id FROM TOKENS WHERE token = $1 AND expiration > CURRENT_TIMESTAMP;"
	err := Db.QueryRow(query, tokenString).Scan(&userID)
	if err == sql.ErrNoRows {
		c.JSON(401, gin.H{"error": "Invalid token"})
		c.Abort()
		return 0
	} else if err != nil {
		c.JSON(500, gin.H{"error": "Internal server error"})
		c.Abort()
		return 0
	}

	return userID
}
