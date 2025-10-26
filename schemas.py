from datetime import datetime
from enum import Enum
from typing import Optional
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class ArticleStatus(Enum):
    publish = "Publish"
    draft = "Draft"


class AbstractModel(BaseModel):
    model_config = ConfigDict(use_enum_values=True, from_attributes=True)


class ArticleBase(AbstractModel):

    title: str
    body: str
    status: ArticleStatus


class ArticleCreate(ArticleBase):
    status: ArticleStatus


class ArticleAnalytics(AbstractModel):
    likes: int
    comments: int


class ArticleAnalyticsRead(ArticleAnalytics):
    likes: int = 0
    comments: int = 0


class ArticleCommentBase(AbstractModel):
    text: str
    author_id: UUID


class ArticleCommentRead(ArticleCommentBase):

    id: UUID
    article_id: UUID


class ArticleLikeBase(AbstractModel):
    author_id: UUID


class ArticleLikeRead(ArticleLikeBase):
    article_id: UUID
    id: UUID


class ArticleNoTRead(ArticleCreate):
    analytics: ArticleAnalytics
    comments: list[ArticleCommentRead] = []
    likes: list[ArticleLikeRead] = []


class ArticleRead(ArticleCreate):
    id: UUID
    manual_likes: int = 0
    manual_comments: int = 0
    analytics: Optional[ArticleAnalyticsRead] = None
    comments: list[ArticleCommentRead] = []
    likes: list[ArticleLikeRead] = []
    date_created_utc: datetime
    author_id: UUID
