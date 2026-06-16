from pydantic import BaseModel, ConfigDict, Field
from typing import Optional, List, Any


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


class NoteUpdate(BaseModel):
    paper_id: Optional[int] = None
    title: Optional[str] = None
    content: Optional[str] = None
    note_type: Optional[str] = None


class NoteOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    note_id: int
    paper_id: Optional[int]
    title: str
    content: str
    note_type: Optional[str]
    created_at: Any = None
    updated_at: Any = None
    paper_title: Optional[str] = None


class ConceptCreate(BaseModel):
    concept_name: str
    description: Optional[str] = None


class ConceptUpdate(BaseModel):
    concept_name: Optional[str] = None
    description: Optional[str] = None


class ConceptOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    concept_id: int
    concept_name: str
    description: Optional[str] = None
    created_at: Any = None
    note_count: int = 0


class NoteLinkOut(BaseModel):
    note_id: int
    title: str
    paper_id: Optional[int] = None
    paper_title: Optional[str] = None


class NoteParseResult(BaseModel):
    note_id: int
    concepts: List[ConceptOut] = Field(default_factory=list)
    linked_notes: List[NoteLinkOut] = Field(default_factory=list)


class NoteBacklinksOut(BaseModel):
    note_id: int
    inbound_notes: List[NoteLinkOut] = Field(default_factory=list)
    shared_concept_notes: List[NoteLinkOut] = Field(default_factory=list)


class TagSuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggestion_id: int
    paper_id: int
    tag_name: str
    confidence: Optional[float]
    reason: Optional[str]
    is_accepted: bool


# ---------- AI 分析模块（成员 C） ----------
class SimilarPaperOut(BaseModel):
    """相似论文一行（含目标论文标题，便于前端直接展示）。"""
    target_paper_id: int
    title: str
    year: Optional[int] = None
    similarity_score: float
    method: str


class RelationSuggestionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    suggestion_id: int
    source_paper_id: int
    target_paper_id: int
    relation_type: str
    confidence: Optional[float] = None
    reason: Optional[str] = None
    is_accepted: bool = False
    target_title: Optional[str] = None


class ClusterPaperOut(BaseModel):
    paper_id: int
    title: str
    membership_score: float


class ClusterOut(BaseModel):
    cluster_id: int
    label: str
    description: Optional[str] = None
    method: str
    num_papers: int
    papers: List[ClusterPaperOut] = Field(default_factory=list)


class ClusterRequest(BaseModel):
    """POST /api/ai/clusters 请求体。"""
    project_id: Optional[int] = None
    num_clusters: Optional[int] = None
    mode: Optional[str] = None      # local | cloud；缺省走环境变量 AI_MODE


class AcceptResult(BaseModel):
    message: str
    suggestion_id: int
    created_id: Optional[int] = None   # 新建的 tag_id / relation_id


# ============================================================
# 模块 D：科研协作与知识图谱可视化模块
# ============================================================

# ---------- 用户 ----------
class UserLogin(BaseModel):
    username: str
    password: str


class UserCreate(BaseModel):
    username: str
    password: str


class UserOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    user_id: int
    username: str
    created_at: Any = None


# ---------- 项目 ----------
class ProjectCreate(BaseModel):
    project_name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    project_name: Optional[str] = None
    description: Optional[str] = None


class ProjectOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    project_id: int
    project_name: str
    description: Optional[str] = None
    owner_id: int
    created_at: Any = None


class ProjectDetailOut(ProjectOut):
    member_count: int = 0
    paper_count: int = 0
    task_count: int = 0


# ---------- 项目成员 ----------
class MemberAdd(BaseModel):
    user_id: int
    role: str = "member"  # admin, member, viewer


class MemberUpdate(BaseModel):
    role: str


class MemberOut(BaseModel):
    user_id: int
    username: str = ""
    role: str
    joined_at: Any = None


# ---------- 阅读任务 ----------
class TaskCreate(BaseModel):
    project_id: int
    paper_id: int
    title: str
    task_description: Optional[str] = None
    deadline: Optional[str] = None  # YYYY-MM-DD
    assignee_ids: List[int] = Field(default_factory=list)


class TaskUpdate(BaseModel):
    title: Optional[str] = None
    task_description: Optional[str] = None
    deadline: Optional[str] = None
    assignee_ids: Optional[List[int]] = None


class TaskStatusUpdate(BaseModel):
    status: str  # todo, reading, done, reported


class TaskOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    task_id: int
    project_id: int
    paper_id: int
    assigned_by: int
    title: str
    task_description: Optional[str] = None
    deadline: Any = None
    created_at: Any = None


class TaskDetailOut(TaskOut):
    paper_title: str = ""
    assigner_name: str = ""
    assignees: List[MemberOut] = Field(default_factory=list)


# ---------- 评论 ----------
class CommentCreate(BaseModel):
    target_type: str  # paper, note, task
    target_id: int
    content: str


class CommentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    comment_id: int
    user_id: int
    username: str = ""
    target_type: str
    target_id: int
    content: str
    created_at: Any = None


# ---------- 活动日志 ----------
class ActivityLogOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    log_id: int
    user_id: Optional[int] = None
    username: str = ""
    action_type: str
    target_type: Optional[str] = None
    target_id: Optional[int] = None
    description: Optional[str] = None
    created_at: Any = None


# ---------- 知识图谱 ----------
class GraphNode(BaseModel):
    id: str
    label: str
    type: str  # paper, author, venue, tag, concept, note, project
    data: Optional[dict] = None


class GraphEdge(BaseModel):
    id: str
    source: str
    target: str
    type: str   # authored_by, published_in, has_tag, has_note, etc.
    weight: float = 1.0


class GraphData(BaseModel):
    nodes: List[GraphNode] = Field(default_factory=list)
    edges: List[GraphEdge] = Field(default_factory=list)


# ---------- Dashboard ----------
class DashboardStats(BaseModel):
    paper_count: int = 0
    note_count: int = 0
    project_count: int = 0
    pending_task_count: int = 0
    recent_papers: List[dict] = Field(default_factory=list)
    recent_activities: List[ActivityLogOut] = Field(default_factory=list)
    top_tags: List[dict] = Field(default_factory=list)
