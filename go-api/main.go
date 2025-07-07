package main

import (
	"log"

	"go-api/handlers"
	"go-api/middleware"
	"go-api/utils"

	"github.com/gin-contrib/cors"
	"github.com/gin-gonic/gin"
)

func setupRouter() *gin.Engine {
	corsConfig := cors.DefaultConfig()
	corsConfig.AllowOrigins = []string{"http://localhost:3000"}
	corsConfig.AddAllowHeaders("Content-Type", "Authorization")
	corsConfig.ExposeHeaders = []string{"Content-Length"}

	router := gin.Default()
	router.Use(cors.New(corsConfig))

	router.GET("/tasks", middleware.AuthMiddleware(), handlers.TasksGetter)
	router.POST("/tasks", middleware.AuthMiddleware(), handlers.TaskCreator)
	router.PUT("/tasks/:id", middleware.AuthMiddleware(), handlers.TaskUpdater)
	router.DELETE("/tasks/:id", middleware.AuthMiddleware(), handlers.TaskDeleter)

	router.POST("/users", handlers.UserCreator)
	router.PUT("/users", middleware.AuthMiddleware(), handlers.UserUpdater)
	router.POST("/users/auth", handlers.UserAuthenticator) // Changed from GET to POST, assuming it's for authentication
	router.DELETE("/users", middleware.AuthMiddleware(), handlers.UserDeleter)
	router.GET("/users", middleware.AuthMiddleware(), handlers.UserSearcher) // Fixed the route to /users

	router.POST("/categories", middleware.AuthMiddleware(), handlers.CategoryCreator)
	router.GET("/categories", middleware.AuthMiddleware(), handlers.CategoryReader)
	router.DELETE("/categories/:id", middleware.AuthMiddleware(), handlers.CategoryDeleter)
	router.PUT("/categories/:id", middleware.AuthMiddleware(), handlers.CategoryUpdater)
	router.GET("/categories/:id", middleware.AuthMiddleware(), handlers.CategoryGetterByID)
	router.PUT("/categories/:id/grant", middleware.AuthMiddleware(), handlers.GrantAccess)

	return router
}

func main() {
	var err error
	utils.Db, err = utils.InitDB("user=goapi password=tatatoto dbname=todolist sslmode=disable")
	if err != nil {
		log.Fatal("Failed to initialize database:", err)
	}
	defer utils.Db.Close()

	utils.CleanupTokens()

	r := setupRouter()
	r.Run(":8080")
}
