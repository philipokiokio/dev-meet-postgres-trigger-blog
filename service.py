from uuid import UUID

from fastapi import HTTPException
from sqlalchemy.orm import Session

from models import Article, ArticleAnalytics, ArticleComment, ArticleLike
from schemas import (
    ArticleCommentBase,
    ArticleCommentRead,
    ArticleCreate,
    ArticleLikeBase,
    ArticleLikeRead,
    ArticleRead,
)


def create_article(session: Session, article: ArticleCreate, author_id: UUID):

    article_in = Article(**article.model_dump(), author_id=author_id)

    session.add(article_in)
    session.commit()
    session.refresh(article_in)

    return ArticleRead(**article_in.as_dict(), analytics=article_in.analytics)


def get_article(session: Session, article_id: UUID):

    article = session.query(Article).filter(Article.id == article_id).first()

    if article is None:
        raise HTTPException(status_code=404, detail="article not found")

    return ArticleRead(
        **article.as_dict(),
        analytics=article.analytics,
        likes=article.likes,
        comments=article.comments
    )


def create_article_comment(
    session: Session, article_comment_in: ArticleCommentBase, article_id: UUID
):

    article_comment = ArticleComment(
        **article_comment_in.model_dump(), article_id=article_id
    )

    session.add(article_comment)
    session.commit()

    add_manual_comment_count(session=session, article_comment=article_comment)

    return ArticleCommentRead(**article_comment.as_dict())


def like_article(session: Session, article_id: UUID, article_like: ArticleLikeBase):

    article__like = ArticleLike(**article_like.model_dump(), article_id=article_id)

    session.add(article__like)
    session.commit()
    add_manual_like_count(session=session, article_like=article__like)

    return ArticleLikeRead(**article__like.as_dict())


def add_manual_comment_count(
    session: Session, article_comment: ArticleComment, error: bool = False
):

    if error is False:
        article_comment.article.manual_comments += 1

    # HYPOTHETICAL EXCEPTION
    else:
        article_comment.article.manual_comments += "e1"
    session.commit()


def add_manual_like_count(
    session: Session, article_like: ArticleLike, error: bool = False
):
    if error is False:

        article_like.article.manual_likes += 1
    else:
        # HYPOTHETICAL EXCEPTION
        article_like.article.manual_likes += "e1"
    session.commit()
