package models

import (
	"time"
)

type Task struct {
	ID            int       `json:"id"`
	Name          string    `json:"name"`
	Parent        int       `json:"parent"`
	Status        int       `json:"status_id"`
	Category      int       `json:"category_id"`
	Creation      time.Time `json:"creation"`
	Edited        time.Time `json:"edited"`
	PriorityOrder int       `json:"order_id"`
}

type Status struct {
	ID          int    `json:"id"`
	Name        string `json:"name"`
	Description string `json:"description"`
}

type Category struct {
	ID    int    `json:"id"`
	Name  string `json:"name"`
	Color string `json:"color"`
}

type User struct {
	ID       int    `json:"id"`
	Username string `json:"username"`
	Password string `json:"-"`
}

type Token struct {
	ID         int       `json:"id"`
	UserID     int       `json:"-"`
	Token      string    `json:"token"`
	Expiration time.Time `json:"expiration"`
}
