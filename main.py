from enum import Enum
from uuid import UUID

from fastapi import FastAPI, status

import service as article_service
from db import DbSession
from db_triggers.router import discover_replaceable_entities
from schemas import (
    ArticleCommentBase,
    ArticleCommentRead,
    ArticleCreate,
    ArticleLikeBase,
    ArticleLikeRead,
    ArticleRead,
)


class User(Enum):
    RANDOM_USER = "db798861-102e-4118-9a3a-dfff89388ffc"
    RANDOM_USER_ONE = "8215de24-9aef-484a-befb-b5f7dbf89b8f"
    RANDOM_USER_TWO = "1e59bceb-c7f2-43ae-b75a-dd349946a194"


app = FastAPI()


@app.get("/", status_code=307)
def root():
    return {"message": "dev meets api blog"}


@app.post("/article", response_model=ArticleRead, status_code=status.HTTP_200_OK)
def create_article(db_session: DbSession, article: ArticleCreate, user: User):

    return article_service.create_article(
        session=db_session, article=article, author_id=UUID(user.value)
    )


@app.get(
    "/article/{article_id}", response_model=ArticleRead, status_code=status.HTTP_200_OK
)
def get_article(db_session: DbSession, article_id: UUID):

    return article_service.get_article(session=db_session, article_id=article_id)


@app.post(
    "/article/{article_id}/comment",
    response_model=ArticleCommentRead,
    status_code=status.HTTP_200_OK,
)
def create_comment(
    db_session: DbSession, article_id: UUID, article_comment_in: ArticleCommentBase
):
    get_article(db_session=db_session, article_id=article_id)

    return article_service.create_article_comment(
        session=db_session, article_comment_in=article_comment_in, article_id=article_id
    )


@app.post(
    "/article/{article_id}/like",
    response_model=ArticleLikeRead,
    status_code=status.HTTP_200_OK,
)
def create_like(
    db_session: DbSession, article_id: UUID, article_like_in: ArticleLikeBase
):
    get_article(db_session=db_session, article_id=article_id)
    return article_service.like_article(
        session=db_session, article_like_in=article_like_in, article_id=article_id
    )
