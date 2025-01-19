import json
from datetime import datetime
from typing import TYPE_CHECKING

from sqlalchemy import Column, Integer, String, ForeignKey, Text, DateTime, Table
from flask import current_app, g
from flask_appbuilder import Model
from flask_appbuilder.security.sqla.models import User
from sqlalchemy.orm import Mapped, relationship

metadata = Model.metadata


class Category(Model):
    __tablename__ = "category"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    cover = Column(String, default="/static/i/noimage.jpg")

class Author(Model):
    __tablename__ = "author"
    
    id = Column(Integer, primary_key=True)
    first_name = Column(String, nullable=False)
    last_name = Column(String, nullable=True)
    cover = Column(String, default="/static/i/noimage.jpg")

    @property
    def name(self) -> str:
        return f"{self.first_name} {self.last_name}"

CategoryBookTables = Table(
    "category_book_tables",
    metadata,
    Column("id", Integer, primary_key=True),
    Column("book_id", Integer, ForeignKey("book.id")),
    Column("category_id", Integer, ForeignKey("category.id")),
)

class Book(Model):
    __tablename__ = "book"
    
    id = Column(Integer, primary_key=True)
    name = Column(String, nullable=False, unique=True)
    description = Column(String, nullable=True)
    cover = Column(String, default="/static/i/noimage.jpg")
    
    author_id = Column(Integer, ForeignKey("author.id"))

    author = relationship(Author, backref="book", foreign_keys=[author_id])
    categories = relationship(
        Category,
        secondary=CategoryBookTables,
        backref="row_level_security_filters",
    )

    @property
    def author_name(self) -> str:
        return self.author.name

class Page(Model):
    __tablename__ = "page"
    
    id = Column(Integer, primary_key=True)
    position = Column(Integer, nullable=False)
    cover = Column(String, default="/static/i/noimage.jpg")
    
    book_id = Column(Integer, ForeignKey("book.id"))
    book = relationship(Book, backref="page", foreign_keys=[book_id])
