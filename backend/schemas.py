from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List


class PaperBase(BaseModel):
    title: str
    abstract: Optional[str] = None
    year: Optional[int] = None
    venue_id: Optional[int] = None
    venue: Optional[str] = None
    paper_type: Optional[str] = "article"
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    reading_status: Optional[str] = "unread"


class PaperCreate(PaperBase):
    author_names: List[str] = Field(default_factory=list)
    tag_names: List[str] = Field(default_factory=list)
    venue_name: Optional[str] = None
    venue_type: Optional[str] = "conference"


class PaperUpdate(BaseModel):
    title: Optional[str] = None
    abstract: Optional[str] = None
    year: Optional[int] = None
    venue_id: Optional[int] = None
    venue: Optional[str] = None
    venue_name: Optional[str] = None
    venue_type: Optional[str] = None
    paper_type: Optional[str] = None
    doi: Optional[str] = None
    arxiv_id: Optional[str] = None
    url: Optional[str] = None
    reading_status: Optional[str] = None
    author_names: Optional[List[str]] = None
    tag_names: Optional[List[str]] = None


class PaperOut(PaperBase):
    model_config = ConfigDict(from_attributes=True)

    paper_id: int


class AuthorBase(BaseModel):
    author_name: str
    affiliation: Optional[str] = None


class AuthorCreate(AuthorBase):
    pass


class AuthorOut(AuthorBase):
    model_config = ConfigDict(from_attributes=True)

    author_id: int


class TagBase(BaseModel):
    tag_name: str
    color: Optional[str] = None


class TagCreate(TagBase):
    pass


class TagOut(TagBase):
    model_config = ConfigDict(from_attributes=True)

    tag_id: int


class VenueBase(BaseModel):
    venue_name: str
    venue_type: Optional[str] = "conference"


class VenueCreate(VenueBase):
    pass


class VenueOut(VenueBase):
    model_config = ConfigDict(from_attributes=True)

    venue_id: int


class AttachmentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    attachment_id: int
    paper_id: int
    file_name: str
    file_path: str
    file_type: Optional[str] = None
    uploaded_by: Optional[int] = None


class BibtexEntryOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    bibtex_id: int
    paper_id: int
    bibtex_key: Optional[str] = None
    raw_bibtex: str


class CollectionBase(BaseModel):
    collection_name: str
    project_id: Optional[int] = None
    parent_id: Optional[int] = None


class CollectionCreate(CollectionBase):
    pass


class CollectionOut(CollectionBase):
    model_config = ConfigDict(from_attributes=True)

    collection_id: int
    paper_count: Optional[int] = None


class PaperDetailOut(PaperOut):
    authors: List[AuthorOut] = Field(default_factory=list)
    tags: List[TagOut] = Field(default_factory=list)
    venue_ref: Optional[VenueOut] = None
    attachments: List[AttachmentOut] = Field(default_factory=list)
    bibtex_entries: List[BibtexEntryOut] = Field(default_factory=list)
    collections: List[CollectionOut] = Field(default_factory=list)


class BibtexImportText(BaseModel):
    raw_bibtex: str


class BibtexImportResult(BaseModel):
    imported_count: int
    paper_ids: List[int]


class NoteCreate(BaseModel):
    paper_id: Optional[int] = None
    title: str
    content: str
    note_type: Optional[str] = "summary"


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    note_id: int
    paper_id: Optional[int]
    title: str
    content: str
    note_type: Optional[str]


class TagSuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggestion_id: int
    paper_id: int
    tag_name: str
    confidence: Optional[float]
    reason: Optional[str]
    is_accepted: bool
