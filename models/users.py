from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, Integer, String
from sqlalchemy.orm import relationship

from database import Base


class User(Base):
    __tablename__ = "users"

    # todo
    id = Column(Integer, primary_key=True, index=True)
    uid = Column(String, unique=True, index=True)
    created_at = Column(DateTime, default=datetime.now)
    last_signed_in = Column(DateTime, default=datetime.now)
    email = Column(String, unique=True)
    is_male = Column(Boolean)
    first_name = Column(String(32))
    last_name = Column(String(32))
    country = Column(String(64))
    is_disabled = Column(Boolean, default=False)

    liked_research = relationship("Research", secondary="likes", back_populates="liked_users")
    saved_research = relationship("Research", secondary="user_research", back_populates="saved_users")
    liked_article = relationship("Article", secondary="article_like", back_populates="liked_users")
    saved_article = relationship("Article", secondary="user_article", back_populates="saved_users")
    followed_diseases = relationship("Disease", secondary="user_disease", back_populates="followers")

    def __repr__(self):
        return f"User(id={self.id}, uid={self.uid}, first_name={self.first_name}, last_name={self.last_name})"
