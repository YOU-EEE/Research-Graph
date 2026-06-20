from pathlib import Path
from typing import Optional
from uuid import uuid4

import bibtexparser
from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import (
    Attachment,
    Author,
    BibtexEntry,
    Collection,
    Paper,
    Tag,
    Venue,
)
from schemas import (
    AttachmentOut,
    AuthorCreate,
    AuthorOut,
    BibtexEntryOut,
    BibtexImportResult,
    BibtexImportText,
    CollectionCreate,
    CollectionOut,
    PaperCreate,
    PaperDetailOut,
    PaperOut,
    PaperUpdate,
    TagCreate,
    TagOut,
    VenueCreate,
    VenueOut,
)

router = APIRouter()
authors_router = APIRouter()
tags_router = APIRouter()
venues_router = APIRouter()
collections_router = APIRouter()
import_router = APIRouter()

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_STORAGE_DIR = BASE_DIR / "storage" / "pdf"
BIBTEX_STORAGE_DIR = BASE_DIR / "storage" / "bibtex"
STORAGE_DIR = BASE_DIR / "storage"
ALLOWED_READING_STATUS = {"unread", "reading", "finished", "archived"}


def _normalize_name(name: str) -> str:
    return " ".join(name.strip().split())


def _dedupe_names(names: list[str]) -> list[str]:
    seen = set()
    result = []
    for name in names:
        normalized = _normalize_name(name)
        key = normalized.casefold()
        if normalized and key not in seen:
            seen.add(key)
            result.append(normalized)
    return result


def _validate_reading_status(status: Optional[str]) -> None:
    if status and status not in ALLOWED_READING_STATUS:
        raise HTTPException(
            status_code=400,
            detail=f"reading_status must be one of {sorted(ALLOWED_READING_STATUS)}",
        )


def _get_or_create_author(db: Session, name: str) -> Author:
    author_name = _normalize_name(name)
    if not author_name:
        raise HTTPException(status_code=400, detail="author name cannot be empty")

    author = db.query(Author).filter(Author.author_name == author_name).first()
    if not author:
        author = Author(author_name=author_name)
        db.add(author)
    return author


def _get_or_create_tag(db: Session, name: str, color: Optional[str] = None) -> Tag:
    tag_name = _normalize_name(name)
    if not tag_name:
        raise HTTPException(status_code=400, detail="tag name cannot be empty")

    tag = db.query(Tag).filter(Tag.tag_name == tag_name).first()
    if not tag:
        tag = Tag(tag_name=tag_name, color=color)
        db.add(tag)
    elif color and not tag.color:
        tag.color = color
    return tag


def _get_or_create_venue(
    db: Session, name: Optional[str], venue_type: Optional[str] = None
) -> Optional[Venue]:
    if not name:
        return None

    venue_name = _normalize_name(name)
    if not venue_name:
        return None

    venue = db.query(Venue).filter(Venue.venue_name == venue_name).first()
    if not venue:
        venue = Venue(
            venue_name=venue_name,
            venue_type=venue_type or "conference",
        )
        db.add(venue)
    return venue


def _paper_query(db: Session):
    return db.query(Paper).options(
        joinedload(Paper.authors),
        joinedload(Paper.tags),
        joinedload(Paper.venue_ref),
        joinedload(Paper.attachments),
        joinedload(Paper.bibtex_entries),
        joinedload(Paper.collections),
    )


def _apply_paper_relations(db: Session, paper: Paper, data: PaperCreate | PaperUpdate):
    venue_name = getattr(data, "venue_name", None)
    venue_type = getattr(data, "venue_type", None)
    if getattr(data, "venue_id", None):
        venue = db.query(Venue).filter(Venue.venue_id == data.venue_id).first()
        if not venue:
            raise HTTPException(status_code=404, detail="Venue not found")
        paper.venue_ref = venue
        paper.venue = venue.venue_name
    elif venue_name:
        venue = _get_or_create_venue(db, venue_name, venue_type)
        paper.venue_ref = venue
        paper.venue = venue.venue_name if venue else paper.venue
    elif getattr(data, "venue", None):
        venue = _get_or_create_venue(db, data.venue, venue_type)
        paper.venue_ref = venue

    if getattr(data, "author_names", None) is not None:
        paper.authors = [
            _get_or_create_author(db, name) for name in _dedupe_names(data.author_names)
        ]

    if getattr(data, "tag_names", None) is not None:
        paper.tags = [
            _get_or_create_tag(db, name) for name in _dedupe_names(data.tag_names)
        ]


def _bibtex_authors(entry: dict) -> list[str]:
    author_text = entry.get("author") or ""
    return [_normalize_name(name) for name in author_text.split(" and ") if name.strip()]


def _bibtex_raw(entry: dict) -> str:
    bib_database = bibtexparser.bibdatabase.BibDatabase()
    bib_database.entries = [entry]
    return bibtexparser.dumps(bib_database).strip()


def _import_bibtex_entries(db: Session, raw_bibtex: str) -> list[Paper]:
    bib_database = bibtexparser.loads(raw_bibtex)
    imported_papers: list[Paper] = []

    for entry in bib_database.entries:
        venue_name = (
            entry.get("booktitle")
            or entry.get("journal")
            or entry.get("publisher")
            or entry.get("archiveprefix")
        )
        venue = _get_or_create_venue(
            db,
            venue_name,
            "conference" if entry.get("booktitle") else "journal",
        )
        year_value = entry.get("year")
        year = int(year_value) if year_value and year_value.isdigit() else None

        paper = Paper(
            title=entry.get("title") or entry.get("ID") or "Untitled BibTeX Entry",
            abstract=entry.get("abstract"),
            year=year,
            venue=venue.venue_name if venue else venue_name,
            venue_ref=venue,
            paper_type=entry.get("ENTRYTYPE") or "article",
            doi=entry.get("doi"),
            arxiv_id=entry.get("eprint"),
            url=entry.get("url"),
            reading_status="unread",
        )
        paper.authors = [
            _get_or_create_author(db, name)
            for name in _dedupe_names(_bibtex_authors(entry))
        ]
        paper.tags = [
            _get_or_create_tag(db, keyword)
            for keyword in _dedupe_names((entry.get("keywords") or "").split(","))
        ]

        db.add(paper)
        db.flush()
        db.add(
            BibtexEntry(
                paper_id=paper.paper_id,
                bibtex_key=entry.get("ID"),
                raw_bibtex=_bibtex_raw(entry),
            )
        )
        imported_papers.append(paper)

    return imported_papers


def _resolve_attachment_path(attachment: Attachment) -> Path:
    file_path = Path(attachment.file_path)
    if not file_path.is_absolute():
        file_path = BASE_DIR / file_path

    resolved_path = file_path.resolve()
    storage_root = STORAGE_DIR.resolve()
    if not resolved_path.is_file() or not resolved_path.is_relative_to(storage_root):
        raise HTTPException(status_code=404, detail="Attachment file not found")
    return resolved_path


def _attachment_storage_path(attachment: Attachment) -> Optional[Path]:
    file_path = Path(attachment.file_path)
    if not file_path.is_absolute():
        file_path = BASE_DIR / file_path

    resolved_path = file_path.resolve()
    if not resolved_path.is_relative_to(STORAGE_DIR.resolve()):
        return None
    return resolved_path


def _delete_attachment_files(attachments: list[Attachment]) -> None:
    for attachment in attachments:
        file_path = _attachment_storage_path(attachment)
        if not file_path:
            continue
        try:
            file_path.unlink(missing_ok=True)
        except OSError:
            continue


@router.get("/", response_model=list[PaperDetailOut])
def list_papers(
    keyword: Optional[str] = None,
    tag_id: Optional[int] = None,
    tag: Optional[str] = None,
    year: Optional[int] = None,
    venue_id: Optional[int] = None,
    reading_status: Optional[str] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    _validate_reading_status(reading_status)
    query = _paper_query(db)

    if keyword:
        query = query.filter(Paper.title.contains(keyword))
    if tag_id:
        query = query.join(Paper.tags).filter(Tag.tag_id == tag_id)
    if tag:
        query = query.join(Paper.tags).filter(Tag.tag_name == tag)
    if year:
        query = query.filter(Paper.year == year)
    if venue_id:
        query = query.filter(Paper.venue_id == venue_id)
    if reading_status:
        query = query.filter(Paper.reading_status == reading_status)

    return (
        query.order_by(Paper.paper_id.desc())
        .offset(skip)
        .limit(limit)
        .all()
    )


@router.post("/", response_model=PaperDetailOut)
def create_paper(data: PaperCreate, db: Session = Depends(get_db)):
    _validate_reading_status(data.reading_status)
    paper = Paper(
        title=data.title,
        abstract=data.abstract,
        year=data.year,
        venue=data.venue,
        paper_type=data.paper_type,
        doi=data.doi,
        arxiv_id=data.arxiv_id,
        url=data.url,
        reading_status=data.reading_status,
    )
    _apply_paper_relations(db, paper, data)

    db.add(paper)
    db.commit()
    return _paper_query(db).filter(Paper.paper_id == paper.paper_id).one()


@router.get("/{paper_id}", response_model=PaperDetailOut)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = _paper_query(db).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


@router.put("/{paper_id}", response_model=PaperDetailOut)
def update_paper(paper_id: int, data: PaperUpdate, db: Session = Depends(get_db)):
    _validate_reading_status(data.reading_status)
    paper = _paper_query(db).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    scalar_fields = {
        "title",
        "abstract",
        "year",
        "venue_id",
        "venue",
        "paper_type",
        "doi",
        "arxiv_id",
        "url",
        "reading_status",
    }
    for key, value in data.model_dump(exclude_unset=True).items():
        if key in scalar_fields:
            setattr(paper, key, value)

    _apply_paper_relations(db, paper, data)
    db.commit()
    return _paper_query(db).filter(Paper.paper_id == paper.paper_id).one()


@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = (
        db.query(Paper)
        .options(joinedload(Paper.attachments))
        .filter(Paper.paper_id == paper_id)
        .first()
    )
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    attachments = list(paper.attachments)
    db.delete(paper)
    db.commit()
    _delete_attachment_files(attachments)
    return {"message": "Paper deleted"}


@authors_router.get("/", response_model=list[AuthorOut])
def list_authors(db: Session = Depends(get_db)):
    return db.query(Author).order_by(Author.author_name).all()


@authors_router.post("/", response_model=AuthorOut)
def create_author(data: AuthorCreate, db: Session = Depends(get_db)):
    author_name = _normalize_name(data.author_name)
    if not author_name:
        raise HTTPException(status_code=400, detail="author name cannot be empty")

    existing = db.query(Author).filter(Author.author_name == author_name).first()
    if existing:
        return existing

    author = Author(author_name=author_name, affiliation=data.affiliation)
    db.add(author)
    db.commit()
    db.refresh(author)
    return author


@tags_router.get("/", response_model=list[TagOut])
def list_tags(db: Session = Depends(get_db)):
    return db.query(Tag).order_by(Tag.tag_name).all()


@tags_router.post("/", response_model=TagOut)
def create_tag(data: TagCreate, db: Session = Depends(get_db)):
    tag = _get_or_create_tag(db, data.tag_name, data.color)
    db.commit()
    db.refresh(tag)
    return tag


@tags_router.delete("/{tag_id}")
def delete_tag(tag_id: int, db: Session = Depends(get_db)):
    tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    tag.papers.clear()
    db.delete(tag)
    db.commit()
    return {"message": "Tag deleted"}


@router.post("/{paper_id}/tags", response_model=PaperDetailOut)
def add_paper_tag(paper_id: int, data: TagCreate, db: Session = Depends(get_db)):
    paper = _paper_query(db).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    tag = _get_or_create_tag(db, data.tag_name, data.color)
    if tag not in paper.tags:
        paper.tags.append(tag)
    db.commit()
    return _paper_query(db).filter(Paper.paper_id == paper_id).one()


@router.delete("/{paper_id}/tags/{tag_id}", response_model=PaperDetailOut)
def remove_paper_tag(paper_id: int, tag_id: int, db: Session = Depends(get_db)):
    paper = _paper_query(db).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    tag = db.query(Tag).filter(Tag.tag_id == tag_id).first()
    if not tag:
        raise HTTPException(status_code=404, detail="Tag not found")

    if tag in paper.tags:
        paper.tags.remove(tag)
    db.commit()
    return _paper_query(db).filter(Paper.paper_id == paper_id).one()


@venues_router.get("/", response_model=list[VenueOut])
def list_venues(db: Session = Depends(get_db)):
    return db.query(Venue).order_by(Venue.venue_name).all()


@venues_router.post("/", response_model=VenueOut)
def create_venue(data: VenueCreate, db: Session = Depends(get_db)):
    venue = _get_or_create_venue(db, data.venue_name, data.venue_type)
    db.commit()
    db.refresh(venue)
    return venue


@venues_router.delete("/{venue_id}")
def delete_venue(venue_id: int, db: Session = Depends(get_db)):
    venue = db.query(Venue).filter(Venue.venue_id == venue_id).first()
    if not venue:
        raise HTTPException(status_code=404, detail="Venue not found")

    for paper in venue.papers:
        if paper.venue == venue.venue_name:
            paper.venue = None
        paper.venue_ref = None

    db.delete(venue)
    db.commit()
    return {"message": "Venue deleted"}


@collections_router.get("/", response_model=list[CollectionOut])
def list_collections(db: Session = Depends(get_db)):
    collections = db.query(Collection).order_by(Collection.collection_name).all()
    result = []
    for collection in collections:
        data = CollectionOut.model_validate(collection)
        data.paper_count = len(collection.papers)
        result.append(data)
    return result


@collections_router.post("/", response_model=CollectionOut)
def create_collection(data: CollectionCreate, db: Session = Depends(get_db)):
    if data.parent_id:
        parent = (
            db.query(Collection)
            .filter(Collection.collection_id == data.parent_id)
            .first()
        )
        if not parent:
            raise HTTPException(status_code=404, detail="Parent collection not found")

    collection = Collection(**data.model_dump())
    db.add(collection)
    db.commit()
    db.refresh(collection)
    return collection


@collections_router.delete("/{collection_id}")
def delete_collection(collection_id: int, db: Session = Depends(get_db)):
    collection = (
        db.query(Collection).filter(Collection.collection_id == collection_id).first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    children = (
        db.query(Collection)
        .filter(Collection.parent_id == collection.collection_id)
        .count()
    )
    if children:
        raise HTTPException(
            status_code=400,
            detail="Collection has child collections. Delete children first.",
        )

    collection.papers.clear()
    db.delete(collection)
    db.commit()
    return {"message": "Collection deleted"}


@collections_router.get("/{collection_id}/papers", response_model=list[PaperDetailOut])
def list_collection_papers(collection_id: int, db: Session = Depends(get_db)):
    collection = (
        db.query(Collection).filter(Collection.collection_id == collection_id).first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    return (
        _paper_query(db)
        .join(Paper.collections)
        .filter(Collection.collection_id == collection_id)
        .order_by(Paper.paper_id.desc())
        .all()
    )


@collections_router.post("/{collection_id}/papers/{paper_id}", response_model=CollectionOut)
def add_paper_to_collection(
    collection_id: int, paper_id: int, db: Session = Depends(get_db)
):
    collection = (
        db.query(Collection).filter(Collection.collection_id == collection_id).first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if paper not in collection.papers:
        collection.papers.append(paper)
    db.commit()
    db.refresh(collection)
    return collection


@collections_router.delete("/{collection_id}/papers/{paper_id}", response_model=CollectionOut)
def remove_paper_from_collection(
    collection_id: int, paper_id: int, db: Session = Depends(get_db)
):
    collection = (
        db.query(Collection).filter(Collection.collection_id == collection_id).first()
    )
    if not collection:
        raise HTTPException(status_code=404, detail="Collection not found")

    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    if paper in collection.papers:
        collection.papers.remove(paper)
    db.commit()
    db.refresh(collection)
    return collection


@router.post("/{paper_id}/attachments", response_model=AttachmentOut)
def upload_attachment(
    paper_id: int,
    file: UploadFile = File(...),
    db: Session = Depends(get_db),
):
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    PDF_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    suffix = Path(file.filename or "").suffix
    stored_name = f"{paper_id}_{uuid4().hex}{suffix}"
    file_path = PDF_STORAGE_DIR / stored_name

    with file_path.open("wb") as out_file:
        out_file.write(file.file.read())

    attachment = Attachment(
        paper_id=paper_id,
        file_name=file.filename or stored_name,
        file_path=str(file_path.relative_to(BASE_DIR)),
        file_type=file.content_type,
    )
    db.add(attachment)
    db.commit()
    db.refresh(attachment)
    return attachment


@router.get("/{paper_id}/attachments", response_model=list[AttachmentOut])
def list_attachments(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return (
        db.query(Attachment)
        .filter(Attachment.paper_id == paper_id)
        .order_by(Attachment.attachment_id.desc())
        .all()
    )


@router.get("/{paper_id}/attachments/{attachment_id}/preview")
def preview_attachment(
    paper_id: int,
    attachment_id: int,
    db: Session = Depends(get_db),
):
    attachment = (
        db.query(Attachment)
        .filter(
            Attachment.paper_id == paper_id,
            Attachment.attachment_id == attachment_id,
        )
        .first()
    )
    if not attachment:
        raise HTTPException(status_code=404, detail="Attachment not found")

    file_path = _resolve_attachment_path(attachment)
    media_type = attachment.file_type or "application/octet-stream"
    if file_path.suffix.lower() == ".pdf":
        media_type = "application/pdf"

    return FileResponse(
        path=file_path,
        media_type=media_type,
        filename=attachment.file_name,
        headers={"Content-Disposition": f'inline; filename="{attachment.file_name}"'},
    )


@router.get("/{paper_id}/bibtex", response_model=list[BibtexEntryOut])
def list_bibtex_entries(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return (
        db.query(BibtexEntry)
        .filter(BibtexEntry.paper_id == paper_id)
        .order_by(BibtexEntry.bibtex_id.desc())
        .all()
    )


@import_router.post("/bibtex", response_model=BibtexImportResult)
def import_bibtex_text(data: BibtexImportText, db: Session = Depends(get_db)):
    try:
        imported = _import_bibtex_entries(db, data.raw_bibtex)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid BibTeX: {exc}") from exc

    return BibtexImportResult(
        imported_count=len(imported),
        paper_ids=[paper.paper_id for paper in imported],
    )


@import_router.post("/bibtex/file", response_model=BibtexImportResult)
def import_bibtex_file(file: UploadFile = File(...), db: Session = Depends(get_db)):
    content = file.file.read().decode("utf-8")
    BIBTEX_STORAGE_DIR.mkdir(parents=True, exist_ok=True)
    stored_name = f"{uuid4().hex}_{file.filename or 'import.bib'}"
    stored_path = BIBTEX_STORAGE_DIR / stored_name
    stored_path.write_text(content, encoding="utf-8")

    try:
        imported = _import_bibtex_entries(db, content)
        db.commit()
    except Exception as exc:
        db.rollback()
        raise HTTPException(status_code=400, detail=f"Invalid BibTeX: {exc}") from exc

    return BibtexImportResult(
        imported_count=len(imported),
        paper_ids=[paper.paper_id for paper in imported],
    )
