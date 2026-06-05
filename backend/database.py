from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./research_graph.db"

engine = create_engine(
    DATABASE_URL,
    connect_args={"check_same_thread": False}
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine
)

Base = declarative_base()


def init_sqlite_schema():
    """Create small SQLite-only additions that SQLAlchemy create_all cannot migrate."""
    if not DATABASE_URL.startswith("sqlite:///"):
        return

    with engine.begin() as connection:
        paper_columns = {
            row[1] for row in connection.exec_driver_sql("PRAGMA table_info(papers)")
        }
        if "venue_id" not in paper_columns:
            connection.exec_driver_sql("ALTER TABLE papers ADD COLUMN venue_id INTEGER")
        if "paper_type" not in paper_columns:
            connection.exec_driver_sql(
                "ALTER TABLE papers ADD COLUMN paper_type VARCHAR DEFAULT 'article'"
            )

        paper_author_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(paper_authors)")
        }
        if "is_corresponding" not in paper_author_columns:
            connection.exec_driver_sql(
                "ALTER TABLE paper_authors ADD COLUMN is_corresponding BOOLEAN DEFAULT 0"
            )

        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_papers_title ON papers(title)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_papers_year ON papers(year)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_paper_tags_tag_id ON paper_tags(tag_id)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_paper_authors_author_id "
            "ON paper_authors(author_id)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_notes_paper_id ON notes(paper_id)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_attachments_paper_id "
            "ON attachments(paper_id)"
        )
        connection.exec_driver_sql(
            "CREATE INDEX IF NOT EXISTS idx_bibtex_entries_paper_id "
            "ON bibtex_entries(paper_id)"
        )
        connection.exec_driver_sql(
            """
            CREATE TRIGGER IF NOT EXISTS trg_update_paper_timestamp
            AFTER UPDATE ON papers
            FOR EACH ROW
            BEGIN
                UPDATE papers
                SET updated_at = CURRENT_TIMESTAMP
                WHERE paper_id = OLD.paper_id;
            END
            """
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
