from sqlalchemy import create_engine, event
from sqlalchemy.orm import declarative_base, sessionmaker

DATABASE_URL = "sqlite:///./research_graph.db"

engine = create_engine(
    DATABASE_URL,
    # timeout：写锁被占用时最多排队等待 30s 再报 "database is locked"
    connect_args={"check_same_thread": False, "timeout": 30},
)


@event.listens_for(engine, "connect")
def _set_sqlite_pragma(dbapi_connection, connection_record):
    """每个新连接上启用 WAL，提升读写并发，减少 "database is locked"。"""
    cursor = dbapi_connection.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")     # 读写可并发
    cursor.execute("PRAGMA busy_timeout=30000")   # 忙等待 30s（与 timeout 一致）
    cursor.execute("PRAGMA synchronous=NORMAL")   # WAL 下兼顾安全与性能
    cursor.close()

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

        embedding_columns = {
            row[1]
            for row in connection.exec_driver_sql("PRAGMA table_info(paper_embeddings)")
        }
        if embedding_columns and "text_hash" not in embedding_columns:
            connection.exec_driver_sql(
                "ALTER TABLE paper_embeddings ADD COLUMN text_hash VARCHAR"
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

        # 触发器 2：任务被标记完成（done）后，自动写入活动日志
        connection.exec_driver_sql(
            """
            CREATE TRIGGER IF NOT EXISTS trg_task_done_log
            AFTER UPDATE ON task_assignments
            FOR EACH ROW
            WHEN NEW.status = 'done' AND OLD.status <> 'done'
            BEGIN
                INSERT INTO activity_logs(
                    user_id, action_type, target_type, target_id, description
                )
                VALUES (
                    NEW.user_id,
                    'TASK_DONE',
                    'task',
                    NEW.task_id,
                    'User completed a reading task'
                );
            END
            """
        )

        # 视图 1：论文详情视图（论文 + 会议 + 作者 + 标签 聚合为一行）
        connection.exec_driver_sql(
            """
            CREATE VIEW IF NOT EXISTS paper_detail_view AS
            SELECT
                p.paper_id,
                p.title,
                p.year,
                p.abstract,
                v.venue_name,
                GROUP_CONCAT(DISTINCT a.author_name) AS authors,
                GROUP_CONCAT(DISTINCT t.tag_name)    AS tags
            FROM papers p
            LEFT JOIN venues v        ON p.venue_id = v.venue_id
            LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
            LEFT JOIN authors a       ON pa.author_id = a.author_id
            LEFT JOIN paper_tags pt   ON p.paper_id = pt.paper_id
            LEFT JOIN tags t          ON pt.tag_id = t.tag_id
            GROUP BY p.paper_id
            """
        )

        # 视图 2：项目任务进度视图（按项目 + 成员统计完成情况）
        connection.exec_driver_sql(
            """
            CREATE VIEW IF NOT EXISTS project_task_progress_view AS
            SELECT
                p.project_id,
                p.project_name,
                u.username,
                COUNT(ta.task_id) AS total_tasks,
                SUM(CASE WHEN ta.status IN ('done', 'reported') THEN 1 ELSE 0 END)
                    AS finished_tasks
            FROM projects p
            JOIN reading_tasks rt    ON p.project_id = rt.project_id
            JOIN task_assignments ta ON rt.task_id = ta.task_id
            JOIN users u             ON ta.user_id = u.user_id
            GROUP BY p.project_id, u.user_id
            """
        )


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
