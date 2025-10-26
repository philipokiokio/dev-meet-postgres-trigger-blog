<?php
$pdo = new PDO("pgsql:host=localhost;port=5432;dbname=mydb", "user", "pass");
$pdo->beginTransaction();

try {
    $stmts = [
        "CREATE EXTENSION IF NOT EXISTS pgcrypto;",
        "CREATE OR REPLACE FUNCTION trgfunc_article_analytics_record() RETURNS TRIGGER AS \$\$ BEGIN
            INSERT INTO article_analytics (id, article_id, likes, comments, date_created_utc, date_updated_utc)
            VALUES (gen_random_uuid(), NEW.id, 0, 0, now(), now()); RETURN NEW; END; \$\$ LANGUAGE plpgsql;",
        "CREATE TRIGGER trg_article_analytics_record AFTER INSERT ON articles FOR EACH ROW
            EXECUTE FUNCTION trgfunc_article_analytics_record();",
        "CREATE OR REPLACE FUNCTION trgfunc_delete_article_analytics_record() RETURNS TRIGGER AS \$\$ BEGIN
            DELETE FROM article_analytics WHERE article_id = OLD.id; RETURN OLD; END; \$\$ LANGUAGE plpgsql;",
        "CREATE TRIGGER trg_delete_article_analytics_record AFTER DELETE ON articles FOR EACH ROW
            EXECUTE FUNCTION trgfunc_delete_article_analytics_record();",
        // ... repeat likes/comments increment/decrement functions & triggers
    ];

    foreach ($stmts as $stmt) {
        $pdo->exec($stmt);
    }

    $pdo->commit();
    echo "Triggers created successfully\n";
} catch (PDOException $e) {
    $pdo->rollBack();
    echo "Error: " . $e->getMessage() . "\n";
}