from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import papers
from database import Base, engine, init_sqlite_schema

Base.metadata.create_all(bind=engine)
init_sqlite_schema()

app = FastAPI(title="ResearchGraph API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(papers.router, prefix="/api/papers", tags=["papers"])
app.include_router(papers.authors_router, prefix="/api/authors", tags=["authors"])
app.include_router(papers.tags_router, prefix="/api/tags", tags=["tags"])
app.include_router(papers.venues_router, prefix="/api/venues", tags=["venues"])
app.include_router(
    papers.collections_router, prefix="/api/collections", tags=["collections"]
)
app.include_router(papers.import_router, prefix="/api/import", tags=["import"])
# app.include_router(notes.router, prefix="/api/notes", tags=["notes"])
# app.include_router(ai.router, prefix="/api/ai", tags=["ai"])
# app.include_router(graph.router, prefix="/api/graph", tags=["graph"])
# app.include_router(tasks.router, prefix="/api/tasks", tags=["tasks"])


@app.get("/")
def root():
    return {"message": "ResearchGraph backend is running"}
