package handlers

import (
	"database/sql"
	"fmt"
	"net/http"
	"strconv"

	"go-api/models"
	"go-api/utils"

	"github.com/gin-gonic/gin"
)

// TasksGetter retrieves all tasks.
func TasksGetter(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "User ID not found"})
		return
	}

	var tasks []models.Task = []models.Task{}
	rows, err := utils.Db.Query("SELECT t.id, t.name, t.parent, t.status_id, t.category_id, t.creation, t.edited, t.order_id FROM tasks AS t INNER JOIN accesses AS a ON a.category_id = t.category_id WHERE a.user_id = $1;", userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	defer rows.Close()

	for rows.Next() {
		var t models.Task
		var parent sql.NullInt64
		if err := rows.Scan(&t.ID, &t.Name, &parent, &t.Status, &t.Category, &t.Creation, &t.Edited, &t.PriorityOrder); err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
		if parent.Valid {
			t.Parent = int(parent.Int64)
		} else {
			t.Parent = -1 // Or any other default value that makes sense for your application
		}
		tasks = append(tasks, t)
	}
	if err := rows.Err(); err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}
	c.JSON(http.StatusOK, gin.H{"tasks": tasks})
}

func TaskCreator(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "User ID not found"})
		return
	}
	name := c.Query("name")
	parentIDStr := c.Query("parent")
	categoryIDStr := c.Query("category")
	priorityOrderStr := c.Query("priority_order")

	var parentID interface{}
	if parentIDStr == "" {
		parentID = nil
	} else {
		var err error
		parentID, err = strconv.Atoi(parentIDStr)
		if err != nil {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid parent ID format"})
			return
		}
	}
	categoryID, err := strconv.Atoi(categoryIDStr)
	if err != nil {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Invalid category ID format"})
		return
	}
	priorityOrder, err := strconv.Atoi(priorityOrderStr)
	if err != nil {
		priorityOrder = 0
	}

	if name == "" {
		c.JSON(http.StatusBadRequest, gin.H{"error": "Task name is required"})
		return
	}

	var role int
	err = utils.Db.QueryRow("SELECT role FROM accesses WHERE category_id = $1 AND user_id = $2", categoryID, userID).Scan(&role)
	if err == sql.ErrNoRows {
		c.JSON(http.StatusForbidden, gin.H{"error": "User does not have access to this category"})
		return
	} else if err != nil {
		fmt.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if role < 2 {
		c.JSON(http.StatusForbidden, gin.H{"error": "Insufficient permissions to create a task in this category"})
		return
	}

	if parentID != nil {
		var parentCategory int
		err = utils.Db.QueryRow("SELECT category FROM tasks WHERE id = $1", parentID).Scan(&parentCategory)
		if err == sql.ErrNoRows {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Parent task not found"})
			return
		} else if err != nil {
			fmt.Println(err)
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}

		if parentCategory != categoryID {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Parent task does not belong to the same category"})
			return
		}
	}

	var id int
	err = utils.Db.QueryRow("INSERT INTO TASKS(name, parent, status_id, category_id, order_id) VALUES($1, $2, $3, $4, $5) RETURNING id;", name, parentID, 1, categoryID, priorityOrder).Scan(&id)
	if err != nil {
		fmt.Println(err)
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusCreated, gin.H{"id": id})
}

func TaskUpdater(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "User ID not found"})
		return
	}
	taskIDStr := c.Param("id")
	taskID, _ := strconv.Atoi(taskIDStr)
	name := c.Query("name")
	parentIDStr := c.Query("parent")
	statusIDStr := c.Query("status")
	categoryIDStr := c.Query("category")
	priorityOrderStr := c.Query("priority_order")

	parentID, _ := strconv.Atoi(parentIDStr)
	statusID, _ := strconv.Atoi(statusIDStr)
	categoryID, _ := strconv.Atoi(categoryIDStr)
	priorityOrder, _ := strconv.Atoi(priorityOrderStr)

	// Fetch user role for the task's category
	role, err := utils.GetUserRoleForCategory(userID.(int), categoryID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	if role < 1 {
		c.JSON(http.StatusUnauthorized, gin.H{"error": "Unauthorized to update this task"})
		return
	}

	if role == 1 {
		// Only allow status update
		_, err = utils.Db.Exec("UPDATE TASKS SET status_id=$1, edited=CURRENT_TIMESTAMP WHERE id=$2;",
			statusID, taskID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	} else {
		// Allow full update
		if name == "" {
			c.JSON(http.StatusBadRequest, gin.H{"error": "Task name is required"})
			return
		}
		_, err = utils.Db.Exec("UPDATE TASKS SET name=$1, parent=$2, status_id=$3, category_id=$4, order_id=$5, edited=CURRENT_TIMESTAMP WHERE id=$6;",
			name, parentID, statusID, categoryID, priorityOrder, taskID)
		if err != nil {
			c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
			return
		}
	}

	c.JSON(http.StatusOK, gin.H{"message": "Task updated successfully"})
}

// TaskDeleter deletes a task.
func TaskDeleter(c *gin.Context) {
	userID, exists := c.Get("user_id")
	if !exists {
		c.JSON(http.StatusInternalServerError, gin.H{"error": "User ID not found"})
		return
	}

	taskIDStr := c.Param("id")
	taskID, _ := strconv.Atoi(taskIDStr)

	_, err := utils.Db.Exec("DELETE FROM tasks AS t WHERE id=$1 AND (SELECT COUNT(*) FROM accesses AS a WHERE t.category_id = a.category_id AND a.user_id = $2 AND a.role > 1) > 0;", taskID, userID)
	if err != nil {
		c.JSON(http.StatusInternalServerError, gin.H{"error": err.Error()})
		return
	}

	c.JSON(http.StatusOK, gin.H{"message": "Task deleted successfully"})
}
