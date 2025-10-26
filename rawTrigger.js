import pkg from 'pg';
const { Pool } = pkg;

const pool = new Pool({ connectionString: process.env.DATABASE_URL });

async function createTriggers() {
  const client = await pool.connect();
  try {
    await client.query('BEGIN');
    await client.query("CREATE EXTENSION IF NOT EXISTS pgcrypto;");

    const sqlStatements = [
      // Article insert/delete triggers
      `CREATE OR REPLACE FUNCTION trgfunc_article_analytics_record() RETURNS TRIGGER AS $$
        BEGIN
          INSERT INTO article_analytics (id, article_id, likes, comments, date_created_utc, date_updated_utc)
          VALUES (gen_random_uuid(), NEW.id, 0, 0, now(), now());
          RETURN NEW;
        END; $$ LANGUAGE plpgsql;`,
      `CREATE TRIGGER trg_article_analytics_record AFTER INSERT ON articles
        FOR EACH ROW EXECUTE FUNCTION trgfunc_article_analytics_record();`,
      `CREATE OR REPLACE FUNCTION trgfunc_delete_article_analytics_record() RETURNS TRIGGER AS $$
        BEGIN
          DELETE FROM article_analytics WHERE article_id = OLD.id;
          RETURN OLD;
        END; $$ LANGUAGE plpgsql;`,
      `CREATE TRIGGER trg_delete_article_analytics_record AFTER DELETE ON articles
        FOR EACH ROW EXECUTE FUNCTION trgfunc_delete_article_analytics_record();`,
      
      // Likes increment/decrement
      `CREATE OR REPLACE FUNCTION trgfunc_increment_article_like_count() RETURNS TRIGGER AS $$
        BEGIN
          UPDATE article_analytics SET likes = likes + 1, date_updated_utc = now() WHERE article_id = NEW.article_id;
          RETURN NEW;
        END; $$ LANGUAGE plpgsql;`,
      `CREATE TRIGGER trg_increment_article_like_count AFTER INSERT ON article_likes
        FOR EACH ROW EXECUTE FUNCTION trgfunc_increment_article_like_count();`,
      `CREATE OR REPLACE FUNCTION trgfunc_decrement_article_like_count() RETURNS TRIGGER AS $$
        BEGIN
          UPDATE article_analytics SET likes = likes - 1, date_updated_utc = now() WHERE article_id = OLD.article_id;
          RETURN OLD;
        END; $$ LANGUAGE plpgsql;`,
      `CREATE TRIGGER trg_decrement_article_like_count AFTER DELETE ON article_likes
        FOR EACH ROW EXECUTE FUNCTION trgfunc_decrement_article_like_count();`,

      // Comments increment/decrement
      `CREATE OR REPLACE FUNCTION trgfunc_increment_article_comment_count() RETURNS TRIGGER AS $$
        BEGIN
          UPDATE article_analytics SET comments = comments + 1, date_updated_utc = now() WHERE article_id = NEW.article_id;
          RETURN NEW;
        END; $$ LANGUAGE plpgsql;`,
      `CREATE TRIGGER trg_increment_article_comment_count AFTER INSERT ON article_comments
        FOR EACH ROW EXECUTE FUNCTION trgfunc_increment_article_comment_count();`,
      `CREATE OR REPLACE FUNCTION trgfunc_decrement_article_comment_count() RETURNS TRIGGER AS $$
        BEGIN
          UPDATE article_analytics SET comments = comments - 1, date_updated_utc = now() WHERE article_id = OLD.article_id;
          RETURN OLD;
        END; $$ LANGUAGE plpgsql;`,
      `CREATE TRIGGER trg_decrement_article_comment_count AFTER DELETE ON article_comments
        FOR EACH ROW EXECUTE FUNCTION trgfunc_decrement_article_comment_count();`,
    ];

    for (const stmt of sqlStatements) {
      await client.query(stmt);
    }

    await client.query('COMMIT');
    console.log('All triggers created!');
  } catch (err) {
    await client.query('ROLLBACK');
    console.error('Error creating triggers', err);
  } finally {
    client.release();
  }
}

createTriggers();