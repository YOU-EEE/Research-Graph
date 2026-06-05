from sqlalchemy import (
    Column, Integer, String, Text, DateTime, ForeignKey,
    Table, Float, Boolean
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from database import Base


paper_authors = Table(
    "paper_authors",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.paper_id"), primary_key=True),
    Column("author_id", Integer, ForeignKey("authors.author_id"), primary_key=True),
    Column("author_order", Integer, default=0),
    Column("is_corresponding", Boolean, default=False),
)


paper_tags = Table(
    "paper_tags",
    Base.metadata,
    Column("paper_id", Integer, ForeignKey("papers.paper_id"), primary_key=True),
    Column("tag_id", Integer, ForeignKey("tags.tag_id"), primary_key=True)
)


class Paper(Base):
    __tablename__ = "papers"

    paper_id = Column(Integer, primary_key=True, index=True)
    title = Column(String, nullable=False, index=True)
    abstract = Column(Text)
    year = Column(Integer, index=True)
    venue_id = Column(Integer, ForeignKey("venues.venue_id"))
    venue = Column(String)
    paper_type = Column(String, default="article")
    doi = Column(String)
    arxiv_id = Column(String)
    url = Column(String)
    reading_status = Column(String, default="unread")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    authors = relationship("Author", secondary=paper_authors, back_populates="papers")
    tags = relationship("Tag", secondary=paper_tags, back_populates="papers")
    notes = relationship("Note", back_populates="paper")
    venue_ref = relationship("Venue", back_populates="papers")
    attachments = relationship(
        "Attachment", back_populates="paper", cascade="all, delete-orphan"
    )
    bibtex_entries = relationship(
        "BibtexEntry", back_populates="paper", cascade="all, delete-orphan"
    )
    collections = relationship(
        "Collection", secondary="collection_papers", back_populates="papers"
    )


class Venue(Base):
    __tablename__ = "venues"

    venue_id = Column(Integer, primary_key=True, index=True)
    venue_name = Column(String, nullable=False, unique=True)
    venue_type = Column(String, default="conference")

    papers = relationship("Paper", back_populates="venue_ref")


class Author(Base):
    __tablename__ = "authors"

    author_id = Column(Integer, primary_key=True, index=True)
    author_name = Column(String, nullable=False, unique=True)
    affiliation = Column(String)

    papers = relationship("Paper", secondary=paper_authors, back_populates="authors")


class Tag(Base):
    __tablename__ = "tags"

    tag_id = Column(Integer, primary_key=True, index=True)
    tag_name = Column(String, nullable=False, unique=True)
    color = Column(String)

    papers = relationship("Paper", secondary=paper_tags, back_populates="tags")


collection_papers = Table(
    "collection_papers",
    Base.metadata,
    Column(
        "collection_id",
        Integer,
        ForeignKey("collections.collection_id"),
        primary_key=True,
    ),
    Column("paper_id", Integer, ForeignKey("papers.paper_id"), primary_key=True),
)


class Collection(Base):
    __tablename__ = "collections"

    collection_id = Column(Integer, primary_key=True, index=True)
    project_id = Column(Integer, nullable=True)
    collection_name = Column(String, nullable=False)
    parent_id = Column(Integer, ForeignKey("collections.collection_id"))

    parent = relationship("Collection", remote_side=[collection_id])
    papers = relationship(
        "Paper", secondary=collection_papers, back_populates="collections"
    )


class Attachment(Base):
    __tablename__ = "attachments"

    attachment_id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.paper_id"), nullable=False)
    file_name = Column(String, nullable=False)
    file_path = Column(String, nullable=False)
    file_type = Column(String)
    uploaded_by = Column(Integer, nullable=True)
    uploaded_at = Column(DateTime, server_default=func.now())

    paper = relationship("Paper", back_populates="attachments")


class BibtexEntry(Base):
    __tablename__ = "bibtex_entries"

    bibtex_id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.paper_id"), nullable=False)
    bibtex_key = Column(String)
    raw_bibtex = Column(Text, nullable=False)
    created_at = Column(DateTime, server_default=func.now())

    paper = relationship("Paper", back_populates="bibtex_entries")


class Note(Base):
    __tablename__ = "notes"

    note_id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.paper_id"))
    user_id = Column(Integer, default=1)
    title = Column(String, nullable=False)
    content = Column(Text, nullable=False)
    note_type = Column(String, default="summary")
    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

    paper = relationship("Paper", back_populates="notes")


class Concept(Base):
    __tablename__ = "concepts"

    concept_id = Column(Integer, primary_key=True, index=True)
    concept_name = Column(String, nullable=False, unique=True)
    description = Column(Text)
    created_at = Column(DateTime, server_default=func.now())


class NoteConcept(Base):
    __tablename__ = "note_concepts"

    note_id = Column(Integer, ForeignKey("notes.note_id"), primary_key=True)
    concept_id = Column(Integer, ForeignKey("concepts.concept_id"), primary_key=True)
    confidence = Column(Float, default=1.0)
    source = Column(String, default="manual")


class PaperRelation(Base):
    __tablename__ = "paper_relations"

    relation_id = Column(Integer, primary_key=True, index=True)
    source_paper_id = Column(Integer, ForeignKey("papers.paper_id"))
    target_paper_id = Column(Integer, ForeignKey("papers.paper_id"))
    relation_type = Column(String, nullable=False)
    weight = Column(Float, default=1.0)
    description = Column(Text)
    generated_by = Column(String, default="user")
    confidence = Column(Float, default=1.0)
    is_confirmed = Column(Boolean, default=True)
    created_at = Column(DateTime, server_default=func.now())


class AITagSuggestion(Base):
    __tablename__ = "ai_tag_suggestions"

    suggestion_id = Column(Integer, primary_key=True, index=True)
    paper_id = Column(Integer, ForeignKey("papers.paper_id"))
    tag_name = Column(String, nullable=False)
    confidence = Column(Float)
    reason = Column(Text)
    model_name = Column(String, default="tfidf")
    is_accepted = Column(Boolean, default=False)
    created_at = Column(DateTime, server_default=func.now())


class PaperSimilarity(Base):
    __tablename__ = "paper_similarity"

    source_paper_id = Column(Integer, ForeignKey("papers.paper_id"), primary_key=True)
    target_paper_id = Column(Integer, ForeignKey("papers.paper_id"), primary_key=True)
    similarity_score = Column(Float, nullable=False)
    method = Column(String, default="tfidf_cosine")
    created_at = Column(DateTime, server_default=func.now())
