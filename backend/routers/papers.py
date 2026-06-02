from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database import get_db
from models import Paper, Author, Tag
from schemas import PaperCreate, PaperUpdate, PaperOut

router = APIRouter()


@router.get("/", response_model=list[PaperOut])
def list_papers(keyword: str | None = None, db: Session = Depends(get_db)):
    query = db.query(Paper)

    if keyword:
        query = query.filter(Paper.title.contains(keyword))

    return query.order_by(Paper.paper_id.desc()).all()


@router.post("/", response_model=PaperOut)
def create_paper(data: PaperCreate, db: Session = Depends(get_db)):
    paper = Paper(
        title=data.title,
        abstract=data.abstract,
        year=data.year,
        venue=data.venue,
        doi=data.doi,
        arxiv_id=data.arxiv_id,
        url=data.url,
        reading_status=data.reading_status,
    )

    for name in data.author_names:
        author = db.query(Author).filter(Author.author_name == name).first()
        if not author:
            author = Author(author_name=name)
        paper.authors.append(author)

    for name in data.tag_names:
        tag = db.query(Tag).filter(Tag.tag_name == name).first()
        if not tag:
            tag = Tag(tag_name=name)
        paper.tags.append(tag)

    db.add(paper)
    db.commit()
    db.refresh(paper)

    return paper


@router.get("/{paper_id}", response_model=PaperOut)
def get_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    return paper


@router.put("/{paper_id}", response_model=PaperOut)
def update_paper(paper_id: int, data: PaperUpdate, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    for key, value in data.model_dump(exclude_unset=True).items():
        setattr(paper, key, value)

    db.commit()
    db.refresh(paper)

    return paper


@router.delete("/{paper_id}")
def delete_paper(paper_id: int, db: Session = Depends(get_db)):
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()

    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")

    db.delete(paper)
    db.commit()

    return {"message": "Paper deleted"}