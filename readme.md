



# Running PostgreSQL Trigger Scripts in Node.js

## 1️⃣ How it runs

You can create a script, e.g., `create_triggers.js`:

project/
├─ migrations/
│ └─ create_triggers.js
├─ src/
│ └─ ...
├─ package.json

arduino


Then you run it manually in the terminal:

```
node migrations/create_triggers.js```
This will connect to your database, execute the SQL statements to create triggers/functions, and exit.

2️⃣ Alternatives in Node.js projects
Migration frameworks
If you use a framework like Knex.js or TypeORM, you can integrate the trigger creation into a migration:



npx knex migrate:latest
Or use TypeORM migrations. Inside the migration file, you can execute raw SQL exactly like the script shown earlier.

Startup scripts (less common)
You could run a trigger creation script at application startup, but it’s not recommended — triggers should only be created once. Running on every startup can lead to already exists errors or race conditions in production.

✅ Best practice
Keep it as a migration or manual script.

Run it in the terminal before your app starts using the database.

Use transactions in the script to ensure safety.

Once the triggers are installed, all inserts/updates/deletes from your Node.js app automatically invoke them — no extra code is needed.


# Running PostgreSQL Trigger in Go


Here’s a clear breakdown of how to run the Go and PHP trigger scripts you have for PostgreSQL. Both are one-off migration scripts that connect to your database and execute raw SQL.

Go

Create a Go file, e.g., create_triggers.go:
```
package main

import (
    "database/sql"
    "fmt"
    _ "github.com/lib/pq"
)

func main() {
    dsn := "postgres://username:password@localhost:5432/dbname?sslmode=disable"
    db, err := sql.Open("postgres", dsn)
    if err != nil {
        panic(err)
    }
    defer db.Close()

    tx, err := db.Begin()
    if err != nil {
        panic(err)
    }

    _, err = tx.Exec(`
        CREATE OR REPLACE FUNCTION trgfunc_article_analytics_record()
        RETURNS TRIGGER AS $$
        BEGIN
            INSERT INTO article_analytics (id, article_id, likes, comments, date_created_utc, date_updated_utc)
            VALUES (gen_random_uuid(), NEW.id, 0, 0, now(), now());
            RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
    `)
    if err != nil {
        tx.Rollback()
        panic(err)
    }

    _, err = tx.Exec(`
        CREATE TRIGGER trg_article_analytics_record
        AFTER INSERT ON articles
        FOR EACH ROW
        EXECUTE FUNCTION trgfunc_article_analytics_record();
    `)
    if err != nil {
        tx.Rollback()
        panic(err)
    }

    tx.Commit()
    fmt.Println("Triggers created successfully!")
}

```


Run it in the terminal:

```go run create_triggers.go```


The script connects to your database, executes the SQL, and exits. You only run it once (like a migration).


# Running PostgreSQL Trigger in Go

PHP

Create a PHP file, e.g., create_triggers.php:
```
<?php
$dsn = "pgsql:host=localhost;port=5432;dbname=your_db;user=your_user;password=your_password";

try {
    $pdo = new PDO($dsn);

    $pdo->beginTransaction();

    $pdo->exec("
        CREATE OR REPLACE FUNCTION trgfunc_article_analytics_record()
        RETURNS TRIGGER AS \$\$
        BEGIN
            INSERT INTO article_analytics (id, article_id, likes, comments, date_created_utc, date_updated_utc)
            VALUES (gen_random_uuid(), NEW.id, 0, 0, now(), now());
            RETURN NEW;
        END;
        \$\$ LANGUAGE plpgsql;
    ");

    $pdo->exec("
        CREATE TRIGGER trg_article_analytics_record
        AFTER INSERT ON articles
        FOR EACH ROW
        EXECUTE FUNCTION trgfunc_article_analytics_record();
    ");

    $pdo->commit();
    echo "Triggers created successfully!\n";

} catch (PDOException $e) {
    $pdo->rollBack();
    echo "Error: " . $e->getMessage() . "\n";
}
```

Run it in the terminal:

``php create_triggers.php```


Just like Go, this runs the SQL and exits. It’s a one-off operation.