package middleware

import (
	"go-api/utils"

	"github.com/gin-gonic/gin"
)

func AuthMiddleware() gin.HandlerFunc {
	return func(c *gin.Context) {
		utils.CleanupTokens()
		userID := utils.GetUserIDFromToken(c)
		c.Set("user_id", -1)
		if userID == 0 {
			c.Abort()
		} else {
			c.Set("user_id", userID)
			c.Next()
		}
	}
}
