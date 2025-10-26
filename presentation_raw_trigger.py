"""create article analytics triggers

Revision ID: abc123def456
Revises:
Create Date: 2025-10-26 12:00:00.000000

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "abc123def456"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Enable pgcrypto for gen_random_uuid()
    op.execute("CREATE EXTENSION IF NOT EXISTS pgcrypto;")

    # --------------------------
    # Article analytics insert trigger
    # --------------------------
    op.execute(
        """
    CREATE OR REPLACE FUNCTION trgfunc_article_analytics_record()
    RETURNS TRIGGER AS $$
    BEGIN 
        INSERT INTO article_analytics (id, article_id, likes, comments, date_created_utc, date_updated_utc)
        VALUES (gen_random_uuid(), NEW.id, 0, 0, now(), now());
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trg_article_analytics_record
    AFTER INSERT ON articles
    FOR EACH ROW
    EXECUTE FUNCTION trgfunc_article_analytics_record();
    """
    )

    # --------------------------
    # Article analytics delete trigger
    # --------------------------
    op.execute(
        """
    CREATE OR REPLACE FUNCTION trgfunc_delete_article_analytics_record()
    RETURNS TRIGGER AS $$
    BEGIN
        DELETE FROM article_analytics
        WHERE article_id = OLD.id;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trg_delete_article_analytics_record
    AFTER DELETE ON articles
    FOR EACH ROW
    EXECUTE FUNCTION trgfunc_delete_article_analytics_record();
    """
    )

    # --------------------------
    # Increment article like count
    # --------------------------
    op.execute(
        """
    CREATE OR REPLACE FUNCTION trgfunc_increment_article_like_count()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE article_analytics
        SET likes = likes + 1,
            date_updated_utc = now()
        WHERE article_id = NEW.article_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trg_increment_article_like_count
    AFTER INSERT ON article_likes
    FOR EACH ROW
    EXECUTE FUNCTION trgfunc_increment_article_like_count();
    """
    )

    # --------------------------
    # Decrement article like count
    # --------------------------
    op.execute(
        """
    CREATE OR REPLACE FUNCTION trgfunc_decrement_article_like_count()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE article_analytics
        SET likes = likes - 1,
            date_updated_utc = now()
        WHERE article_id = OLD.article_id;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trg_decrement_article_like_count
    AFTER DELETE ON article_likes
    FOR EACH ROW
    EXECUTE FUNCTION trgfunc_decrement_article_like_count();
    """
    )

    # --------------------------
    # Increment article comment count
    # --------------------------
    op.execute(
        """
    CREATE OR REPLACE FUNCTION trgfunc_increment_article_comment_count()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE article_analytics
        SET comments = comments + 1,
            date_updated_utc = now()
        WHERE article_id = NEW.article_id;
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trg_increment_article_comment_count
    AFTER INSERT ON article_comments
    FOR EACH ROW
    EXECUTE FUNCTION trgfunc_increment_article_comment_count();
    """
    )

    # --------------------------
    # Decrement article comment count
    # --------------------------
    op.execute(
        """
    CREATE OR REPLACE FUNCTION trgfunc_decrement_article_comment_count()
    RETURNS TRIGGER AS $$
    BEGIN
        UPDATE article_analytics
        SET comments = comments - 1,
            date_updated_utc = now()
        WHERE article_id = OLD.article_id;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
    """
    )

    op.execute(
        """
    CREATE TRIGGER trg_decrement_article_comment_count
    AFTER DELETE ON article_comments
    FOR EACH ROW
    EXECUTE FUNCTION trgfunc_decrement_article_comment_count();
    """
    )


def downgrade():
    # Drop triggers first, then functions

    # Article triggers
    op.execute("DROP TRIGGER IF EXISTS trg_article_analytics_record ON articles;")
    op.execute(
        "DROP TRIGGER IF EXISTS trg_delete_article_analytics_record ON articles;"
    )
    op.execute("DROP FUNCTION IF EXISTS trgfunc_article_analytics_record();")
    op.execute("DROP FUNCTION IF EXISTS trgfunc_delete_article_analytics_record();")

    # Article likes triggers
    op.execute(
        "DROP TRIGGER IF EXISTS trg_increment_article_like_count ON article_likes;"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_decrement_article_like_count ON article_likes;"
    )
    op.execute("DROP FUNCTION IF EXISTS trgfunc_increment_article_like_count();")
    op.execute("DROP FUNCTION IF EXISTS trgfunc_decrement_article_like_count();")

    # Article comments triggers
    op.execute(
        "DROP TRIGGER IF EXISTS trg_increment_article_comment_count ON article_comments;"
    )
    op.execute(
        "DROP TRIGGER IF EXISTS trg_decrement_article_comment_count ON article_comments;"
    )
    op.execute("DROP FUNCTION IF EXISTS trgfunc_increment_article_comment_count();")
    op.execute("DROP FUNCTION IF EXISTS trgfunc_decrement_article_comment_count();")
