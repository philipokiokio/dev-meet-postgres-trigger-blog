import random
import string
from uuid import uuid4

import pytest

from models import Article, ArticleComment, ArticleLike
from schemas import ArticleCommentBase, ArticleCreate, ArticleLikeBase, ArticleStatus
from service import (
    add_manual_comment_count,
    add_manual_like_count,
    create_article,
    create_article_comment,
    like_article,
)


def random_string(length=12):
    letters = string.ascii_letters + string.digits
    return "".join(random.choice(letters) for _ in range(length))


def test_article_trigger_flow(session):
    author_id = uuid4()
    commentor_id = uuid4()
    liker_id = uuid4()

    article = ArticleCreate(title="Hello", body="World", status=ArticleStatus.publish)
    result = create_article(session=session, article=article, author_id=author_id)

    assert result.analytics.likes == 0
    assert result.analytics.comments == 0
    assert result.manual_comments == 0
    assert result.manual_likes == 0

    raw_orm_article = session.query(Article).filter(Article.id == result.id).first()

    assert raw_orm_article is not None
    # This tests the first trigger when an article is created
    assert raw_orm_article.analytics is not None

    for i in range(0, 5):

        create_article_comment(
            session=session,
            article_id=raw_orm_article.id,
            article_comment_in=ArticleCommentBase(
                text=random_string(49), author_id=commentor_id
            ),
        )

    assert raw_orm_article.manual_comments == 5

    for i in range(0, 5):

        like_article(
            session=session,
            article_id=raw_orm_article.id,
            article_like=ArticleLikeBase(author_id=liker_id),
        )

    assert raw_orm_article.manual_likes == 5
    session.refresh(raw_orm_article)

    assert raw_orm_article.analytics.likes == 5
    assert raw_orm_article.analytics.comments == 5

    # DRILLING DOWN TO EXCEPTIONS AND EDGE CASES
    raw_orm_article_like = ArticleLike(
        author_id=liker_id, article_id=raw_orm_article.id
    )
    session.add(raw_orm_article_like)
    session.commit()
    with pytest.raises(Exception):

        add_manual_like_count(
            session=session, article_like=raw_orm_article_like, error=True
        )

    session.refresh(raw_orm_article)
    assert raw_orm_article.manual_likes != 6
    assert raw_orm_article.analytics.likes == 6

    raw_orm_article_comment = ArticleComment(
        author_id=commentor_id,
        article_id=raw_orm_article.id,
        text=random_string(length=24),
    )
    session.add(raw_orm_article_comment)
    session.commit()

    with pytest.raises(Exception):

        add_manual_comment_count(
            session=session, article_comment=raw_orm_article_comment, error=True
        )
    session.refresh(raw_orm_article)
    assert raw_orm_article.manual_comments != 6
    assert raw_orm_article.analytics.comments == 6

    session.delete(raw_orm_article_comment)
    session.commit()
    session.refresh(raw_orm_article)
    assert raw_orm_article.manual_comments != 4
    assert raw_orm_article.analytics.comments == 5

    session.delete(raw_orm_article_like)
    session.commit()
    session.refresh(raw_orm_article)
    assert raw_orm_article.manual_likes != 4
    assert raw_orm_article.analytics.likes == 5
    ...
