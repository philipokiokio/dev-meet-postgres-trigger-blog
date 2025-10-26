package main

import (
    "database/sql"
    _ "github.com/lib/pq"
    "log"
)

func main() {
    db, _ := sql.Open("postgres", "postgres://user:pass@localhost:5432/mydb?sslmode=disable")
    defer db.Close()

    stmts := []string{
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
        `CREATE OR REPLACE FUNCTION trgfunc_article_analytics_record() RETURNS TRIGGER AS $$
            BEGIN
              INSERT INTO article_analytics (id, article_id, likes, comments, date_created_utc, date_updated_utc)
              VALUES (gen_random_uuid(), NEW.id, 0, 0, now(), now());
              RETURN NEW;
            END; $$ LANGUAGE plpgsql;`,
        `CREATE TRIGGER trg_article_analytics_record AFTER INSERT ON articles FOR EACH ROW
            EXECUTE FUNCTION trgfunc_article_analytics_record();`,
        `CREATE OR REPLACE FUNCTION trgfunc_delete_article_analytics_record() RETURNS TRIGGER AS $$
            BEGIN DELETE FROM article_analytics WHERE article_id = OLD.id; RETURN OLD; END; $$ LANGUAGE plpgsql;`,
        `CREATE TRIGGER trg_delete_article_analytics_record AFTER DELETE ON articles FOR EACH ROW
            EXECUTE FUNCTION trgfunc_delete_article_analytics_record();`,
        // ... repeat likes/comments increment/decrement functions & triggers
    }

    tx, _ := db.Begin()
    for _, stmt := range stmts {
        if _, err := tx.Exec(stmt); err != nil {
            tx.Rollback()
            log.Fatal(err)
        }
    }
    tx.Commit()
    log.Println("Triggers created successfully")
}
