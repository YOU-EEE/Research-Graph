import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, insert, select
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import Concept, Note, NoteConcept, Paper, note_links
from schemas import (
    ConceptCreate,
    ConceptOut,
    ConceptUpdate,
    NoteBacklinksOut,
    NoteCreate,
    NoteLinkOut,
    NoteOut,
    NoteParseResult,
    NoteUpdate,
)

router = APIRouter()
concepts_router = APIRouter()

LINK_PATTERN = re.compile(r"\[\[([^\[\]\n]+)\]\]")


def _normalize_name(value: str) -> str:
    return " ".join(value.strip().split())


def _extract_link_names(content: str) -> list[str]:
    names = []
    seen = set()
    for raw in LINK_PATTERN.findall(content or ""):
        # Obsidian-style aliases: [[Target|Alias]] should point to Target.
        name = _normalize_name(raw.split("|", 1)[0])
        key = name.casefold()
        if name and key not in seen:
            seen.add(key)
            names.append(name)
    return names


def _note_out(note: Note) -> NoteOut:
    return NoteOut(
        note_id=note.note_id,
        paper_id=note.paper_id,
        title=note.title,
        content=note.content,
        note_type=note.note_type,
        created_at=str(note.created_at) if note.created_at else None,
        updated_at=str(note.updated_at) if note.updated_at else None,
        paper_title=note.paper.title if note.paper else None,
    )


def _note_link_out(note: Note) -> NoteLinkOut:
    return NoteLinkOut(
        note_id=note.note_id,
        title=note.title,
        paper_id=note.paper_id,
        paper_title=note.paper.title if note.paper else None,
    )


def _concept_out(db: Session, concept: Concept) -> ConceptOut:
    note_count = (
        db.query(func.count(NoteConcept.note_id))
        .filter(NoteConcept.concept_id == concept.concept_id)
        .scalar()
    )
    return ConceptOut(
        concept_id=concept.concept_id,
        concept_name=concept.concept_name,
        description=concept.description,
        created_at=str(concept.created_at) if concept.created_at else None,
        note_count=note_count or 0,
    )


def _require_note(db: Session, note_id: int) -> Note:
    note = (
        db.query(Note)
        .options(joinedload(Note.paper))
        .filter(Note.note_id == note_id)
        .first()
    )
    if not note:
        raise HTTPException(status_code=404, detail="Note not found")
    return note


def _require_paper(db: Session, paper_id: int) -> Paper:
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


def _get_or_create_concept(db: Session, name: str) -> Concept:
    concept = (
        db.query(Concept)
        .filter(func.lower(Concept.concept_name) == name.casefold())
        .first()
    )
    if concept:
        return concept
    concept = Concept(concept_name=name)
    db.add(concept)
    db.flush()
    return concept


def _sync_note_links(db: Session, note: Note) -> tuple[list[Concept], list[Note]]:
    link_names = _extract_link_names(note.content)

    db.query(NoteConcept).filter(NoteConcept.note_id == note.note_id).delete(
        synchronize_session=False
    )
    db.execute(
        note_links.delete().where(note_links.c.source_note_id == note.note_id)
    )

    concepts = []
    linked_notes = []
    for name in link_names:
        concept = _get_or_create_concept(db, name)
        db.add(
            NoteConcept(
                note_id=note.note_id,
                concept_id=concept.concept_id,
                confidence=1.0,
                source="wikilink",
            )
        )
        concepts.append(concept)

        target_note = (
            db.query(Note)
            .filter(
                Note.note_id != note.note_id,
                func.lower(Note.title) == name.casefold(),
            )
            .first()
        )
        if target_note:
            db.execute(
                insert(note_links).values(
                    source_note_id=note.note_id,
                    target_note_id=target_note.note_id,
                    link_type="wikilink",
                    confidence=1.0,
                )
            )
            linked_notes.append(target_note)

    return concepts, linked_notes


@router.get("/", response_model=list[NoteOut])
def list_notes(
    paper_id: Optional[int] = None,
    keyword: Optional[str] = None,
    concept_id: Optional[int] = None,
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=50, ge=1, le=200),
    db: Session = Depends(get_db),
):
    query = db.query(Note).options(joinedload(Note.paper))
    if paper_id:
        query = query.filter(Note.paper_id == paper_id)
    if keyword:
        like = f"%{keyword}%"
        query = query.filter((Note.title.like(like)) | (Note.content.like(like)))
    if concept_id:
        query = query.join(NoteConcept).filter(NoteConcept.concept_id == concept_id)
    notes = query.order_by(Note.updated_at.desc()).offset(skip).limit(limit).all()
    return [_note_out(note) for note in notes]


@router.post("/", response_model=NoteOut)
def create_note(data: NoteCreate, db: Session = Depends(get_db)):
    if data.paper_id is not None:
        _require_paper(db, data.paper_id)
    note = Note(
        paper_id=data.paper_id,
        title=data.title,
        content=data.content,
        note_type=data.note_type or "summary",
    )
    db.add(note)
    db.flush()
    _sync_note_links(db, note)
    db.commit()
    return _note_out(_require_note(db, note.note_id))


@router.get("/{note_id}", response_model=NoteOut)
def get_note(note_id: int, db: Session = Depends(get_db)):
    return _note_out(_require_note(db, note_id))


@router.put("/{note_id}", response_model=NoteOut)
def update_note(note_id: int, data: NoteUpdate, db: Session = Depends(get_db)):
    note = _require_note(db, note_id)
    update_data = data.model_dump(exclude_unset=True)
    if "paper_id" in update_data and update_data["paper_id"] is not None:
        _require_paper(db, update_data["paper_id"])
    for key, value in update_data.items():
        setattr(note, key, value)
    db.flush()
    _sync_note_links(db, note)
    db.commit()
    return _note_out(_require_note(db, note_id))


@router.delete("/{note_id}")
def delete_note(note_id: int, db: Session = Depends(get_db)):
    note = _require_note(db, note_id)
    db.query(NoteConcept).filter(NoteConcept.note_id == note_id).delete(
        synchronize_session=False
    )
    db.execute(
        note_links.delete().where(
            (note_links.c.source_note_id == note_id)
            | (note_links.c.target_note_id == note_id)
        )
    )
    db.delete(note)
    db.commit()
    return {"message": "Note deleted"}


@router.post("/{note_id}/parse-links", response_model=NoteParseResult)
def parse_note_links(note_id: int, db: Session = Depends(get_db)):
    note = _require_note(db, note_id)
    concepts, linked_notes = _sync_note_links(db, note)
    db.commit()
    return NoteParseResult(
        note_id=note_id,
        concepts=[_concept_out(db, concept) for concept in concepts],
        linked_notes=[_note_link_out(linked) for linked in linked_notes],
    )


@router.get("/{note_id}/backlinks", response_model=NoteBacklinksOut)
def get_note_backlinks(note_id: int, db: Session = Depends(get_db)):
    note = _require_note(db, note_id)

    inbound_ids = [
        row[0]
        for row in db.execute(
            select(note_links.c.source_note_id).where(
                note_links.c.target_note_id == note_id
            )
        ).all()
    ]
    inbound_notes = (
        db.query(Note)
        .options(joinedload(Note.paper))
        .filter(Note.note_id.in_(inbound_ids))
        .all()
        if inbound_ids
        else []
    )

    concept_ids = [
        row[0]
        for row in db.query(NoteConcept.concept_id)
        .filter(NoteConcept.note_id == note.note_id)
        .all()
    ]
    shared_notes = (
        db.query(Note)
        .options(joinedload(Note.paper))
        .join(NoteConcept)
        .filter(Note.note_id != note_id, NoteConcept.concept_id.in_(concept_ids))
        .distinct()
        .all()
        if concept_ids
        else []
    )

    return NoteBacklinksOut(
        note_id=note_id,
        inbound_notes=[_note_link_out(item) for item in inbound_notes],
        shared_concept_notes=[_note_link_out(item) for item in shared_notes],
    )


@router.get("/paper/{paper_id}", response_model=list[NoteOut])
def list_paper_notes(paper_id: int, db: Session = Depends(get_db)):
    _require_paper(db, paper_id)
    notes = (
        db.query(Note)
        .options(joinedload(Note.paper))
        .filter(Note.paper_id == paper_id)
        .order_by(Note.updated_at.desc())
        .all()
    )
    return [_note_out(note) for note in notes]


@concepts_router.get("/", response_model=list[ConceptOut])
def list_concepts(
    keyword: Optional[str] = None,
    db: Session = Depends(get_db),
):
    query = db.query(Concept)
    if keyword:
        query = query.filter(Concept.concept_name.like(f"%{keyword}%"))
    concepts = query.order_by(Concept.concept_name).all()
    return [_concept_out(db, concept) for concept in concepts]


@concepts_router.post("/", response_model=ConceptOut)
def create_concept(data: ConceptCreate, db: Session = Depends(get_db)):
    name = _normalize_name(data.concept_name)
    if not name:
        raise HTTPException(status_code=400, detail="concept_name cannot be empty")
    existing = (
        db.query(Concept)
        .filter(func.lower(Concept.concept_name) == name.casefold())
        .first()
    )
    if existing:
        return _concept_out(db, existing)
    concept = Concept(concept_name=name, description=data.description)
    db.add(concept)
    db.commit()
    db.refresh(concept)
    return _concept_out(db, concept)


@concepts_router.get("/{concept_id}", response_model=ConceptOut)
def get_concept(concept_id: int, db: Session = Depends(get_db)):
    concept = db.query(Concept).filter(Concept.concept_id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    return _concept_out(db, concept)


@concepts_router.put("/{concept_id}", response_model=ConceptOut)
def update_concept(
    concept_id: int, data: ConceptUpdate, db: Session = Depends(get_db)
):
    concept = db.query(Concept).filter(Concept.concept_id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    update_data = data.model_dump(exclude_unset=True)
    if "concept_name" in update_data:
        update_data["concept_name"] = _normalize_name(update_data["concept_name"])
    for key, value in update_data.items():
        setattr(concept, key, value)
    db.commit()
    db.refresh(concept)
    return _concept_out(db, concept)


@concepts_router.get("/{concept_id}/notes", response_model=list[NoteOut])
def list_concept_notes(concept_id: int, db: Session = Depends(get_db)):
    concept = db.query(Concept).filter(Concept.concept_id == concept_id).first()
    if not concept:
        raise HTTPException(status_code=404, detail="Concept not found")
    notes = (
        db.query(Note)
        .options(joinedload(Note.paper))
        .join(NoteConcept)
        .filter(NoteConcept.concept_id == concept_id)
        .order_by(Note.updated_at.desc())
        .all()
    )
    return [_note_out(note) for note in notes]
