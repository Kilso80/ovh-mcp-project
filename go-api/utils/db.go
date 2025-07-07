package utils

import (
	"database/sql"
	"github.com/jmoiron/sqlx"

	_ "github.com/lib/pq"
)

type DB interface {
	Query(string, ...interface{}) (*sql.Rows, error)
	QueryRow(string, ...interface{}) *sql.Row
	Exec(string, ...interface{}) (sql.Result, error)
}

var Db *sqlx.DB

func InitDB(dataSourceName string) (*sqlx.DB, error) {
	conn, err := sqlx.Open("postgres", dataSourceName)
	if err != nil {
		return nil, err
	}

	if err := conn.Ping(); err != nil {
		conn.Close()
		return nil, err
	}

	createTableSQL := `
	CREATE TABLE IF NOT EXISTS TASKS (
	    id SERIAL PRIMARY KEY,
	    name VARCHAR(30),
	    parent INT,
	    status INT REFERENCES STATUS(id),
	    category INT REFERENCES CATEGORIES(id),
	    creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	    edited TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	    priorityOrder INT,
	    FOREIGN KEY (parent) REFERENCES TASKS(id)
	);

	CREATE TABLE IF NOT EXISTS CATEGORIES (
        id SERIAL PRIMARY KEY,
        name VARCHAR(64) NOT NULL,
        color INT NOT NULL
    );

    CREATE TABLE IF NOT EXISTS ACCESSES (
        category_id INT REFERENCES CATEGORIES(id),
        user_id INT REFERENCES USERS(id),
        role INT NOT NULL,
        PRIMARY KEY (category_id, user_id)
    );
	`

	_, err = conn.Exec(createTableSQL)
	if err != nil {
		return nil, err
	}

	return conn, nil
}

func CleanupTokens() {
	Db.Exec("DELETE FROM TOKENS WHERE expiration < CURRENT_TIMESTAMP;")
}

func GetUserRoleForCategory(userID, categoryID int) (int, error) {
	var role int
	err := Db.QueryRow("SELECT role FROM ACCESSES WHERE user_id=$1 AND category_id=$2;", userID, categoryID).Scan(&role)
	if err != nil {
		if err == sql.ErrNoRows {
			return -1, nil // User has no access to the category
		}
		return -1, err
	}
	return role, nil
}
