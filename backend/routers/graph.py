"""模块 D：知识图谱路由"""
from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session, joinedload

from database import get_db
from models import (
    Paper,
    Author,
    Venue,
    Tag,
    Note,
    Concept,
    Project,
    PaperRelation,
    NoteConcept,
    note_links,
    paper_authors,
    paper_tags,
    ReadingTask,
    TaskAssignment,
    User,
)
from routers.auth import get_current_user
from schemas import GraphData, GraphNode, GraphEdge

router = APIRouter()


@router.get("/graph", response_model=GraphData)
def get_graph(
    project_id: Optional[int] = None,
    paper_id: Optional[int] = None,
    concept_id: Optional[int] = None,
    node_type: Optional[str] = None,
    edge_type: Optional[str] = None,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """
    获取知识图谱数据。

    参数:
    - project_id: 按项目筛选
    - paper_id: 聚焦某篇论文
    - concept_id: 聚焦某个概念
    - node_type: 筛选节点类型 (paper/author/venue/tag/concept/note/project)
    - edge_type: 筛选边类型
    """
    nodes: list[GraphNode] = []
    edges: list[GraphEdge] = []
    included_paper_ids: set[int] = set()
    included_author_ids: set[int] = set()
    included_tag_ids: set[int] = set()
    included_concept_ids: set[int] = set()
    included_note_ids: set[int] = set()
    included_venue_ids: set[int] = set()
    included_user_ids: set[int] = set()

    # --- 确定论文范围 ---
    paper_query = db.query(Paper)
    if paper_id:
        paper_query = paper_query.filter(Paper.paper_id == paper_id)
    papers = paper_query.all()

    for p in papers:
        included_paper_ids.add(p.paper_id)

    # 如果指定了 project_id，加入项目相关的论文
    if project_id:
        project = db.query(Project).filter(Project.project_id == project_id).first()
        if project:
            if not node_type or node_type == "project":
                nodes.append(
                    GraphNode(
                        id=f"project_{project.project_id}",
                        label=project.project_name,
                        type="project",
                        data={
                            "description": project.description,
                            "owner_id": project.owner_id,
                        },
                    )
                )
            # 项目论文（通过阅读任务关联）
            tasks = (
                db.query(ReadingTask)
                .filter(ReadingTask.project_id == project_id)
                .all()
            )
            for t in tasks:
                included_paper_ids.add(t.paper_id)
                # 任务-用户边
                for a in t.assignments:
                    included_user_ids.add(a.user_id)
                    if not edge_type or edge_type == "assigned_to":
                        edges.append(
                            GraphEdge(
                                id=f"assigned_to_{t.task_id}_{a.user_id}",
                                source=f"task_{t.task_id}",
                                target=f"user_{a.user_id}",
                                type="assigned_to",
                            )
                        )

    # --- 收集作者、标签、会议 ---
    for p_id in included_paper_ids:
        paper = db.query(Paper).filter(Paper.paper_id == p_id).first()
        if not paper:
            continue
        if not node_type or node_type == "paper":
            nodes.append(
                GraphNode(
                    id=f"paper_{paper.paper_id}",
                    label=paper.title,
                    type="paper",
                    data={
                        "year": paper.year,
                        "venue": paper.venue,
                        "reading_status": paper.reading_status,
                    },
                )
            )
        # 会议节点
        if paper.venue_ref:
            v = paper.venue_ref
            if v.venue_id not in included_venue_ids:
                included_venue_ids.add(v.venue_id)
                if not node_type or node_type == "venue":
                    nodes.append(
                        GraphNode(
                            id=f"venue_{v.venue_id}",
                            label=v.venue_name,
                            type="venue",
                            data={"venue_type": v.venue_type},
                        )
                    )
            if not edge_type or edge_type == "published_in":
                edges.append(
                    GraphEdge(
                        id=f"published_in_{paper.paper_id}_{v.venue_id}",
                        source=f"paper_{paper.paper_id}",
                        target=f"venue_{v.venue_id}",
                        type="published_in",
                    )
                )

        # 作者节点
        for author in paper.authors:
            if author.author_id not in included_author_ids:
                included_author_ids.add(author.author_id)
                if not node_type or node_type == "author":
                    nodes.append(
                        GraphNode(
                            id=f"author_{author.author_id}",
                            label=author.author_name,
                            type="author",
                            data={"affiliation": author.affiliation},
                        )
                    )
            if not edge_type or edge_type == "authored_by":
                edges.append(
                    GraphEdge(
                        id=f"authored_by_{paper.paper_id}_{author.author_id}",
                        source=f"paper_{paper.paper_id}",
                        target=f"author_{author.author_id}",
                        type="authored_by",
                    )
                )

        # 标签节点
        for tag in paper.tags:
            if tag.tag_id not in included_tag_ids:
                included_tag_ids.add(tag.tag_id)
                if not node_type or node_type == "tag":
                    nodes.append(
                        GraphNode(
                            id=f"tag_{tag.tag_id}",
                            label=tag.tag_name,
                            type="tag",
                            data={"color": tag.color},
                        )
                    )
            if not edge_type or edge_type == "has_tag":
                edges.append(
                    GraphEdge(
                        id=f"has_tag_{paper.paper_id}_{tag.tag_id}",
                        source=f"paper_{paper.paper_id}",
                        target=f"tag_{tag.tag_id}",
                        type="has_tag",
                    )
                )

        # 笔记节点
        for note in paper.notes:
            if note.note_id not in included_note_ids:
                included_note_ids.add(note.note_id)
                if not node_type or node_type == "note":
                    nodes.append(
                        GraphNode(
                            id=f"note_{note.note_id}",
                            label=note.title,
                            type="note",
                            data={"note_type": note.note_type},
                        )
                    )
            if not edge_type or edge_type == "has_note":
                edges.append(
                    GraphEdge(
                        id=f"has_note_{paper.paper_id}_{note.note_id}",
                        source=f"paper_{paper.paper_id}",
                        target=f"note_{note.note_id}",
                        type="has_note",
                    )
                )

        # 概念 (通过笔记)
        for note in paper.notes:
            note_concepts = (
                db.query(NoteConcept)
                .filter(NoteConcept.note_id == note.note_id)
                .all()
            )
            for nc in note_concepts:
                concept = (
                    db.query(Concept)
                    .filter(Concept.concept_id == nc.concept_id)
                    .first()
                )
                if concept and concept.concept_id not in included_concept_ids:
                    included_concept_ids.add(concept.concept_id)
                    if not node_type or node_type == "concept":
                        nodes.append(
                            GraphNode(
                                id=f"concept_{concept.concept_id}",
                                label=concept.concept_name,
                                type="concept",
                                data={"description": concept.description},
                            )
                        )
                if concept and (not edge_type or edge_type == "mentions_concept"):
                    edges.append(
                        GraphEdge(
                            id=f"mentions_concept_{note.note_id}_{nc.concept_id}",
                            source=f"note_{note.note_id}",
                            target=f"concept_{nc.concept_id}",
                            type="mentions_concept",
                            weight=nc.confidence,
                        )
                    )

    # --- 论文关系边 ---
    paper_ids_list = list(included_paper_ids)
    if paper_ids_list:
        relations = (
            db.query(PaperRelation)
            .filter(
                (PaperRelation.source_paper_id.in_(paper_ids_list))
                | (PaperRelation.target_paper_id.in_(paper_ids_list))
            )
            .all()
        )
        for rel in relations:
            if not edge_type or edge_type == rel.relation_type:
                edges.append(
                    GraphEdge(
                        id=f"{rel.relation_type}_{rel.source_paper_id}_{rel.target_paper_id}",
                        source=f"paper_{rel.source_paper_id}",
                        target=f"paper_{rel.target_paper_id}",
                        type=rel.relation_type,
                        weight=rel.weight,
                    )
                )
            # 确保相关论文节点也被包含
            if rel.source_paper_id not in included_paper_ids:
                src_paper = db.query(Paper).filter(Paper.paper_id == rel.source_paper_id).first()
                if src_paper:
                    included_paper_ids.add(rel.source_paper_id)
                    if not node_type or node_type == "paper":
                        nodes.append(
                            GraphNode(
                                id=f"paper_{src_paper.paper_id}",
                                label=src_paper.title,
                                type="paper",
                                data={"year": src_paper.year},
                            )
                        )
            if rel.target_paper_id not in included_paper_ids:
                tgt_paper = db.query(Paper).filter(Paper.paper_id == rel.target_paper_id).first()
                if tgt_paper:
                    included_paper_ids.add(rel.target_paper_id)
                    if not node_type or node_type == "paper":
                        nodes.append(
                            GraphNode(
                                id=f"paper_{tgt_paper.paper_id}",
                                label=tgt_paper.title,
                                type="paper",
                                data={"year": tgt_paper.year},
                            )
                        )

    # --- 笔记间链接 ---
    note_ids_list = list(included_note_ids)
    if note_ids_list:
        note_link_rows = (
            db.query(note_links)
            .filter(
                note_links.c.source_note_id.in_(note_ids_list)
                | note_links.c.target_note_id.in_(note_ids_list)
            )
            .all()
        )
        for nl in note_link_rows:
            if not edge_type or edge_type == "links_to":
                edges.append(
                    GraphEdge(
                        id=f"links_to_{nl.source_note_id}_{nl.target_note_id}",
                        source=f"note_{nl.source_note_id}",
                        target=f"note_{nl.target_note_id}",
                        type="links_to",
                        weight=nl.confidence,
                    )
                )

    # --- 用户节点 ---
    for uid in included_user_ids:
        user = db.query(User).filter(User.user_id == uid).first()
        if user and (not node_type or node_type == "project"):
            # 将用户节点的 type 设为 "user"，但能出现在图谱中
            existing = any(n.id == f"user_{uid}" for n in nodes)
            if not existing:
                nodes.append(
                    GraphNode(
                        id=f"user_{user.user_id}",
                        label=user.username,
                        type="user",
                    )
                )

    # --- 按 node_type 过滤 ---
    if node_type:
        nodes = [n for n in nodes if n.type == node_type]

    # --- 按 edge_type 过滤 ---
    if edge_type:
        edges = [e for e in edges if e.type == edge_type]

    return GraphData(nodes=nodes, edges=edges)


@router.get("/graph/project/{project_id}", response_model=GraphData)
def get_project_graph(
    project_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取项目的知识图谱。"""
    return get_graph(project_id=project_id, db=db, _user=_user)


@router.get("/graph/paper/{paper_id}", response_model=GraphData)
def get_paper_graph(
    paper_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取论文相关的知识图谱。"""
    return get_graph(paper_id=paper_id, db=db, _user=_user)


@router.get("/graph/concept/{concept_id}", response_model=GraphData)
def get_concept_graph(
    concept_id: int,
    db: Session = Depends(get_db),
    _user: User = Depends(get_current_user),
):
    """获取概念相关的知识图谱。"""
    return get_graph(concept_id=concept_id, db=db, _user=_user)
