"""AI 分析模块路由（成员 C）。

对应 REQUIREMENTS 9.3 的接口，本地/云端双模式通过 ?mode=local|cloud 切换
（缺省走环境变量 AI_MODE）。

    POST /api/ai/tag-suggestions/{paper_id}            生成标签建议
    GET  /api/ai/tag-suggestions/{paper_id}            查看标签建议
    POST /api/ai/tag-suggestions/{suggestion_id}/accept  确认 -> tags/paper_tags

    POST /api/ai/similarity/{paper_id}                 计算相似论文
    GET  /api/ai/similarity/{paper_id}                 查看相似论文

    POST /api/ai/relation-suggestions/{paper_id}       生成关系建议
    GET  /api/ai/relation-suggestions/{paper_id}       查看关系建议
    POST /api/ai/relation-suggestions/{suggestion_id}/accept  确认 -> paper_relations

    POST /api/ai/clusters                              生成 Related Work 聚类
    GET  /api/ai/clusters/{project_id}                 查看某项目聚类
    GET  /api/ai/clusters                              查看全库聚类
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from database import get_db
from schemas import (
    AcceptResult,
    ClusterOut,
    ClusterRequest,
    RelationSuggestionOut,
    SimilarPaperOut,
    TagSuggestionOut,
)
from services import ai_service

router = APIRouter()


# ---------------- 自动标签 ----------------
@router.post("/tag-suggestions/{paper_id}", response_model=list[TagSuggestionOut])
def create_tag_suggestions(
    paper_id: int,
    mode: Optional[str] = Query(default=None, description="local | cloud"),
    db: Session = Depends(get_db),
):
    return ai_service.generate_tag_suggestions(db, paper_id, mode)


@router.get("/tag-suggestions/{paper_id}", response_model=list[TagSuggestionOut])
def get_tag_suggestions(paper_id: int, db: Session = Depends(get_db)):
    return ai_service.list_tag_suggestions(db, paper_id)


@router.post("/tag-suggestions/{suggestion_id}/accept", response_model=AcceptResult)
def accept_tag_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    sug, tag_id = ai_service.accept_tag_suggestion(db, suggestion_id)
    return AcceptResult(
        message=f"标签 '{sug.tag_name}' 已写入 paper {sug.paper_id}",
        suggestion_id=suggestion_id, created_id=tag_id,
    )


# ---------------- 相似论文 ----------------
@router.post("/similarity/{paper_id}", response_model=list[SimilarPaperOut])
def create_similarity(
    paper_id: int,
    mode: Optional[str] = Query(default=None, description="local | cloud"),
    top_k: Optional[int] = Query(default=None, ge=1, le=50),
    db: Session = Depends(get_db),
):
    return ai_service.generate_similarity(db, paper_id, mode, top_k)


@router.get("/similarity/{paper_id}", response_model=list[SimilarPaperOut])
def get_similarity(paper_id: int, db: Session = Depends(get_db)):
    return ai_service.list_similarity(db, paper_id)


# ---------------- 关系补边 ----------------
@router.post("/relation-suggestions/{paper_id}", response_model=list[RelationSuggestionOut])
def create_relation_suggestions(
    paper_id: int,
    mode: Optional[str] = Query(default=None, description="local | cloud"),
    db: Session = Depends(get_db),
):
    return ai_service.generate_relation_suggestions(db, paper_id, mode)


@router.get("/relation-suggestions/{paper_id}", response_model=list[RelationSuggestionOut])
def get_relation_suggestions(paper_id: int, db: Session = Depends(get_db)):
    return ai_service.list_relation_suggestions(db, paper_id)


@router.post(
    "/relation-suggestions/{suggestion_id}/accept", response_model=AcceptResult
)
def accept_relation_suggestion(suggestion_id: int, db: Session = Depends(get_db)):
    sug, relation_id = ai_service.accept_relation_suggestion(db, suggestion_id)
    return AcceptResult(
        message=f"关系 {sug.relation_type} ({sug.source_paper_id}->{sug.target_paper_id}) "
                f"已写入 paper_relations",
        suggestion_id=suggestion_id, created_id=relation_id,
    )


# ---------------- Related Work 聚类 ----------------
@router.post("/clusters", response_model=list[ClusterOut])
def create_clusters(req: ClusterRequest, db: Session = Depends(get_db)):
    return ai_service.generate_clusters(db, req.project_id, req.num_clusters, req.mode)


@router.get("/clusters/{project_id}", response_model=list[ClusterOut])
def get_clusters(project_id: int, db: Session = Depends(get_db)):
    return ai_service.list_clusters(db, project_id)


@router.get("/clusters", response_model=list[ClusterOut])
def get_all_clusters(db: Session = Depends(get_db)):
    return ai_service.list_clusters(db, None)
