from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

trgfunc_article_analytics_record = PGFunction(
    schema="public",
    signature="trgfunc_article_analytics_record()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN 
        INSERT INTO article_analytics (id, article_id, likes, comments,date_created_utc, date_updated_utc)
        VALUES (gen_random_uuid(),NEW.id, 0,0, now(), now());
        RETURN NEW;
    END;
    $$ LANGUAGE plpgsql;
""",
)
trg_article_analytics_record = PGTrigger(
    schema="public",
    signature="trg_article_analytics_record",
    on_entity="public.articles",
    is_constraint=False,
    definition="""AFTER INSERT ON articles
        FOR EACH ROW
        EXECUTE FUNCTION trgfunc_article_analytics_record()""",
)


# Function: delete analytics record after article delete
trgfunc_delete_article_analytics_record = PGFunction(
    schema="public",
    signature="trgfunc_delete_article_analytics_record()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN
        DELETE FROM article_analytics
        WHERE article_id = OLD.id;
        RETURN OLD;
    END;
    $$ LANGUAGE plpgsql;
""",
)

trg_delete_article_analytics_record = PGTrigger(
    schema="public",
    signature="trg_delete_article_analytics_record",
    on_entity="public.articles",
    is_constraint=False,
    definition="""AFTER DELETE ON articles
        FOR EACH ROW
        EXECUTE FUNCTION trgfunc_delete_article_analytics_record()""",
)
