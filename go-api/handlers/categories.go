package handlers

import (
	"database/sql"
	"go-api/models"
	"go-api/utils"
	"net/http"
	"strconv"

	"github.com/gin-gonic/gin"
	"github.com/jmoiron/sqlx"
)

func CategoryCreator(c *gin.Context) {
	var category models.Category
	if err := c.ShouldBindJSON(&category); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	// Get authenticated user ID
	userID, ok := c.Get("user_id")
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User authentication required"})
		return
	}

	authUserID, ok := userID.(int)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID"})
		return
	}

	// Insert new category and get its ID
	var categoryID int64
	err := utils.Db.QueryRow(`
        INSERT INTO CATEGORIES (name, color) VALUES ($1, $2) RETURNING id;
    `, category.Name, category.Color).Scan(&categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	// Insert into ACCESSES table
	_, err = utils.Db.Exec(`
        INSERT INTO ACCESSES (category_id, user_id, role) VALUES ($1, $2, 4);
    `, categoryID, authUserID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"message": "Category created successfully", "category_id": categoryID})
}

func CategoryReader(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User authentication required"})
		return
	}

	authUserID, ok := userID.(int)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID"})
		return
	}

	rows, err := utils.Db.Query(`
        SELECT C.id, C.name, C.color
        FROM CATEGORIES C
        JOIN ACCESSES A ON C.id = A.category_id
        WHERE A.user_id = $1;
    `, authUserID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	var categories []models.Category = []models.Category{}
	for rows.Next() {
		var category models.Category
		if err := rows.Scan(&category.ID, &category.Name, &category.Color); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		categories = append(categories, category)
	}

	if err = rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"categories": categories})
}

func CategoryUpdater(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User authentication required"})
		return
	}

	authUserID, ok := userID.(int)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID"})
		return
	}

	categoryID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID"})
		return
	}

	role, err := utils.GetUserRoleForCategory(authUserID, categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if role < 3 {
		c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions to update the category"})
		return
	}

	var updateData map[string]interface{}
	if err := c.ShouldBindJSON(&updateData); err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid request payload"})
		return
	}

	query, args, err := sqlx.In("UPDATE categories SET name = $1, color = $2 WHERE id = $3;", updateData["name"], updateData["color"], categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	result, err := utils.Db.Exec(query, args...)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	rowsAffected, _ := result.RowsAffected()
	if rowsAffected == 0 {
		c.JSON(http.StatusNotFound, gin.H{"error": "Category not found"})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Category updated successfully"})
}

func CategoryDeleter(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User authentication required"})
		return
	}

	authUserID, ok := userID.(int)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID"})
		return
	}

	categoryID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID"})
		return
	}

	role, err := utils.GetUserRoleForCategory(authUserID, categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if role != 4 {
		c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions to delete the category"})
		return
	}

	_, err = utils.Db.Exec("DELETE FROM CATEGORIES WHERE id=$1;", categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Category deleted successfully"})
}

func CategoryGetterByID(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User authentication required"})
		return
	}

	authUserID, ok := userID.(int)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID"})
		return
	}

	categoryID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID"})
		return
	}

	role, err := utils.GetUserRoleForCategory(authUserID, categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if role < 0 {
		c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions to access the category"})
		return
	}

	var category models.Category
	err = utils.Db.Get(&category, "SELECT id, name, color FROM CATEGORIES WHERE id=$1;", categoryID)
	if err != nil {
		if err == sql.ErrNoRows {
			c.JSON(http.StatusNotFound, gin.H{"error": "Category not found"})
			return
		}
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"category": category})
}

func GrantAccess(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "User authentication required"})
		return
	}

	authUserID, ok := userID.(int)
	if !ok {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Invalid user ID"})
		return
	}

	categoryID, err := strconv.Atoi(c.Param("id"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID"})
		return
	}

	role, err := strconv.Atoi(c.Query("level"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid role level"})
		return
	}

	targetID, err := strconv.Atoi(c.Query("user"))
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid user ID"})
		return
	}

	if targetID == authUserID {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "You cannot grant permissions to yourself"})
	}

	userRole, err := utils.GetUserRoleForCategory(authUserID, categoryID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	targetRole, err := utils.GetUserRoleForCategory(targetID, categoryID)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": err.Error()})
		return
	}

	if userRole > targetRole && userRole > 2 && userRole > role {
		_, err = utils.Db.Exec("DELETE FROM accesses WHERE user_id = $1 AND category_id = $2;", targetID, categoryID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		if role != -1 {
			_, err = utils.Db.Exec("INSERT INTO accesses (user_id, category_id, role) VALUES ($1, $2, $3);", targetID, categoryID, role)
			if err != nil {
				c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
				return
			}
		}

		c.JSON(http.StatusAccepted, gin.H{"message": "permissions granted successfully"})
	} else {
		c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions to perform the action"})
		return
	}
}
