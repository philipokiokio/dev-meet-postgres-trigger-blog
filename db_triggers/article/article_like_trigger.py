from alembic_utils.pg_function import PGFunction
from alembic_utils.pg_trigger import PGTrigger

trgfunc_increment_article_like_count = PGFunction(
    schema="public",
    signature="trgfunc_increment_article_like_count()",
    definition="""
    RETURNS TRIGGER AS $$
    BEGIN 
        UPDATE article_analytics
    SET likes = likes + 1,
        date_updated_utc = now()
    WHERE article_id = NEW.article_id;
    RETURN NEW;


    END;
    $$ LANGUAGE plpgsql;
""",
)
trg_increment_article_like_count = PGTrigger(
    schema="public",
    signature="trg_increment_article_like_count",
    on_entity="public.article_likes",
    is_constraint=False,
    definition="""AFTER INSERT ON article_likes
        FOR EACH ROW
        EXECUTE FUNCTION trgfunc_increment_article_like_count()""",
)


trgfunc_decrement_article_like_count = PGFunction(
    schema="public",
    signature="trgfunc_decrement_article_like_count()",
    definition="""
RETURNS TRIGGER AS $$
BEGIN
    UPDATE article_analytics
    SET likes = likes - 1,
        date_updated_utc = now()
    WHERE article_id = OLD.article_id;
    RETURN OLD;
END;
$$ LANGUAGE plpgsql;
""",
)

trg_decrement_article_like_count = PGTrigger(
    schema="public",
    signature="trg_decrement_article_like_count",
    on_entity="public.article_likes",
    is_constraint=False,
    definition="""AFTER DELETE ON article_likes
        FOR EACH ROW
        EXECUTE FUNCTION trgfunc_decrement_article_like_count()""",
)
