from datetime import datetime
from uuid import uuid4

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class AbstractBase(DeclarativeBase):
    __abstract__ = True
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    date_created_utc = Column(DateTime(), default=datetime.utcnow)
    date_updated_utc = Column(DateTime(), onupdate=datetime.utcnow)

    def as_dict(self):
        return {field.name: getattr(self, field.name) for field in self.__table__.c}


class Article(AbstractBase):

    __tablename__ = "articles"
    title = Column(String, nullable=False)
    body = Column(String, nullable=False)
    status = Column(String, nullable=True)
    author_id = Column(UUID(as_uuid=True))
    manual_likes = Column(Integer, nullable=False, server_default="0")
    manual_comments = Column(Integer, nullable=False, server_default="0")
    # One-to-many relationships
    comments = relationship(
        "ArticleComment",
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    likes = relationship(
        "ArticleLike",
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )
    analytics = relationship(
        "ArticleAnalytics",
        uselist=False,
        back_populates="article",
        cascade="all, delete-orphan",
        passive_deletes=True,
    )


class ArticleComment(AbstractBase):

    __tablename__ = "article_comments"
    text = Column(String, nullable=False)
    article_id = Column(UUID, ForeignKey("articles.id", ondelete="CASCADE"))
    author_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    article = relationship("Article", back_populates="comments")


class ArticleLike(AbstractBase):

    __tablename__ = "article_likes"
    author_id = Column(UUID(as_uuid=True), primary_key=True, default=uuid4)
    article_id = Column(UUID, ForeignKey("articles.id", ondelete="CASCADE"))
    article = relationship("Article", back_populates="likes")


class ArticleAnalytics(AbstractBase):
    __tablename__ = "article_analytics"

    likes = Column(Integer, nullable=False, server_default="0")
    comments = Column(Integer, nullable=False, server_default="0")
    article_id = Column(UUID, ForeignKey("articles.id", ondelete="CASCADE"))
    article = relationship("Article", back_populates="analytics")
