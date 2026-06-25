"""AI 分析服务（成员 C）。

把 ai_engine 的「大脑」(local/cloud 双模式) 接到本项目的 SQLAlchemy 表上：
读论文 -> 调 provider -> 写 AI 建议表；用户确认 -> 写正式表（tags/paper_relations）。

字段映射（本项目 schema vs 引擎内部）：
    score        -> confidence
    src/dst      -> source_paper_id / target_paper_id
    model/mode   -> model_name（如 local:tfidf / cloud:gpt-4o-mini）
    status       -> is_accepted (bool)
"""
from __future__ import annotations

import hashlib
import struct

import numpy as np
from fastapi import HTTPException
from sqlalchemy.orm import Session, joinedload

from ai_engine import PaperInput, get_provider
from ai_engine import config as ai_config
from models import (
    AIRelationSuggestion,
    AITagSuggestion,
    ClusterPaper,
    Paper,
    PaperEmbedding,
    PaperRelation,
    PaperSimilarity,
    ResearchCluster,
    Tag,
)


# ----------------- 通用工具 -----------------
def _vector_to_blob(vec: list[float]) -> bytes:
    return struct.pack(f"<{len(vec)}f", *vec)


def _text_hash(text: str) -> str:
    return hashlib.sha1((text or "").encode("utf-8")).hexdigest()


def _make_provider(mode: str | None):
    """按 mode（或环境变量 AI_MODE）创建 provider；失败给出清晰 HTTP 错误。"""
    try:
        resolved = ai_config.resolve_mode(mode)
        return get_provider(resolved)
    except (RuntimeError, ValueError) as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


def _load_inputs(db: Session) -> list[PaperInput]:
    """读取全部论文（拼接其笔记内容）为 PaperInput 列表。"""
    papers = (
        db.query(Paper).options(joinedload(Paper.notes)).order_by(Paper.paper_id).all()
    )
    inputs = []
    for p in papers:
        notes_text = " ".join((n.content or "") for n in p.notes)
        inputs.append(
            PaperInput(
                id=p.paper_id,
                title=p.title or "",
                abstract=p.abstract or "",
                year=p.year,
                venue=p.venue or "",
                notes=notes_text,
            )
        )
    return inputs


def _corpus(db: Session, provider):
    """计算全库嵌入矩阵，写入 paper_embeddings 缓存，并按嵌入方式设定相似度阈值。

    返回 (inputs, matrix(n,dim), method)。TF-IDF 语料相关，必须一次性喂入全部论文。
    """
    inputs = _load_inputs(db)
    if len(inputs) < 2:
        raise HTTPException(status_code=400, detail="论文数不足（至少需要 2 篇）以计算相似度/聚类")

    is_tfidf = provider.model_name == "local:tfidf"
    method = "tfidf_cosine" if is_tfidf else "embedding_cosine"
    provider.similarity_threshold = (
        ai_config.TFIDF_SIMILARITY_THRESHOLD if is_tfidf else ai_config.SIMILARITY_THRESHOLD
    )
    model = provider.model_name
    hashes = [_text_hash(p.text) for p in inputs]

    if is_tfidf:
        # TF-IDF 是语料相关的，向量随整库变化，必须一次性整库重算（无法按篇缓存）
        vectors = provider.embed([p.text for p in inputs])
        arr = np.asarray(vectors, dtype=np.float32)
        dim = int(arr.shape[1])
        for i, p in enumerate(inputs):
            blob = _vector_to_blob(arr[i].tolist())
            row = db.get(PaperEmbedding, p.id)
            if row is None:
                db.add(PaperEmbedding(paper_id=p.id, vector=blob, dim=dim,
                                      model=model, text_hash=hashes[i]))
            else:
                row.vector, row.dim, row.model, row.text_hash = blob, dim, model, hashes[i]
        db.commit()
        return inputs, arr, method

    # 云端 / 句向量：每篇向量相互独立，可按篇缓存复用。
    # 仅对「无缓存 / 模型不同 / 文本已变」的论文重新 embedding。
    cached: dict[int, np.ndarray] = {}
    for p, h in zip(inputs, hashes):
        row = db.get(PaperEmbedding, p.id)
        if row is not None and row.model == model and row.text_hash == h:
            cached[p.id] = np.frombuffer(row.vector, dtype=np.float32)

    missing = [(i, p) for i, p in enumerate(inputs) if p.id not in cached]
    if missing:
        new_vectors = provider.embed([p.text for _, p in missing])
        for (i, p), vec in zip(missing, new_vectors):
            v = np.asarray(vec, dtype=np.float32)
            cached[p.id] = v
            blob = _vector_to_blob(v.tolist())
            row = db.get(PaperEmbedding, p.id)
            if row is None:
                db.add(PaperEmbedding(paper_id=p.id, vector=blob, dim=int(v.shape[0]),
                                      model=model, text_hash=hashes[i]))
            else:
                row.vector, row.dim, row.model, row.text_hash = (
                    blob, int(v.shape[0]), model, hashes[i]
                )
        db.commit()

    arr = np.asarray([cached[p.id] for p in inputs], dtype=np.float32)
    return inputs, arr, method


def _cosine_matrix(arr: np.ndarray) -> np.ndarray:
    norms = np.linalg.norm(arr, axis=1, keepdims=True)
    norms[norms == 0] = 1.0
    unit = arr / norms
    return unit @ unit.T


def _require_paper(db: Session, paper_id: int) -> Paper:
    paper = db.query(Paper).filter(Paper.paper_id == paper_id).first()
    if not paper:
        raise HTTPException(status_code=404, detail="Paper not found")
    return paper


# ================= 1. 自动标签 =================
def generate_tag_suggestions(db: Session, paper_id: int, mode: str | None):
    paper = _require_paper(db, paper_id)
    provider = _make_provider(mode)
    paper_input = PaperInput(
        id=paper.paper_id, title=paper.title or "", abstract=paper.abstract or "",
        year=paper.year, venue=paper.venue or "",
    )

    suggestions = provider.suggest_tags(paper_input, ai_config.MAX_TAGS_PER_PAPER)

    # 重新生成前清掉该论文尚未被接受的旧建议，避免重复堆积
    db.query(AITagSuggestion).filter(
        AITagSuggestion.paper_id == paper_id,
        AITagSuggestion.is_accepted.is_(False),
    ).delete(synchronize_session=False)

    # 已被接受的标签不再重复建议（保持幂等）
    accepted = {
        r.tag_name for r in db.query(AITagSuggestion).filter(
            AITagSuggestion.paper_id == paper_id,
            AITagSuggestion.is_accepted.is_(True),
        )
    }

    rows = []
    for s in suggestions:
        if s.tag_name in accepted:
            continue
        row = AITagSuggestion(
            paper_id=paper_id,
            tag_name=s.tag_name,
            confidence=s.score,
            reason=s.reason,
            model_name=provider.model_name,
            is_accepted=False,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return rows


def list_tag_suggestions(db: Session, paper_id: int):
    return (
        db.query(AITagSuggestion)
        .filter(AITagSuggestion.paper_id == paper_id)
        .order_by(AITagSuggestion.confidence.desc())
        .all()
    )


def accept_tag_suggestion(db: Session, suggestion_id: int):
    """确认标签建议 -> 写 tags + paper_tags（事务），标记 is_accepted。"""
    sug = db.get(AITagSuggestion, suggestion_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Tag suggestion not found")

    paper = _require_paper(db, sug.paper_id)
    try:
        tag = db.query(Tag).filter(Tag.tag_name == sug.tag_name).first()
        if not tag:
            tag = Tag(tag_name=sug.tag_name)
            db.add(tag)
            db.flush()
        if tag not in paper.tags:
            paper.tags.append(tag)
        sug.is_accepted = True
        db.commit()
    except Exception:
        db.rollback()
        raise
    return sug, tag.tag_id


# ================= 2. 相似论文 =================
def generate_similarity(db: Session, paper_id: int, mode: str | None, top_k: int | None):
    _require_paper(db, paper_id)
    provider = _make_provider(mode)
    inputs, arr, method = _corpus(db, provider)

    id_to_idx = {p.id: i for i, p in enumerate(inputs)}
    if paper_id not in id_to_idx:
        raise HTTPException(status_code=404, detail="Paper not in corpus")
    i = id_to_idx[paper_id]
    sim = _cosine_matrix(arr)[i]

    k = top_k or ai_config.TOP_K_SIMILAR
    order = np.argsort(-sim)
    pairs = []
    for j in order:
        if j == i:
            continue
        score = float(sim[j])
        if score <= 0.1:
            continue
        pairs.append((inputs[j].id, score))
        if len(pairs) >= k:
            break

    # 覆盖式：先删该源论文旧的相似行
    db.query(PaperSimilarity).filter(
        PaperSimilarity.source_paper_id == paper_id
    ).delete(synchronize_session=False)
    for target_id, score in pairs:
        db.add(PaperSimilarity(
            source_paper_id=paper_id, target_paper_id=target_id,
            similarity_score=round(score, 4), method=method,
        ))
    db.commit()
    return list_similarity(db, paper_id)


def list_similarity(db: Session, paper_id: int):
    rows = (
        db.query(PaperSimilarity, Paper.title, Paper.year)
        .join(Paper, Paper.paper_id == PaperSimilarity.target_paper_id)
        .filter(PaperSimilarity.source_paper_id == paper_id)
        .order_by(PaperSimilarity.similarity_score.desc())
        .all()
    )
    return [
        {
            "target_paper_id": s.target_paper_id,
            "title": title,
            "year": year,
            "similarity_score": s.similarity_score,
            "method": s.method,
        }
        for s, title, year in rows
    ]


# ================= 3. 关系补边 =================
def generate_relation_suggestions(db: Session, paper_id: int, mode: str | None):
    paper = _require_paper(db, paper_id)
    provider = _make_provider(mode)
    inputs, arr, method = _corpus(db, provider)
    print("+++++++ corpus complete ++++++++")
    id_to_idx = {p.id: i for i, p in enumerate(inputs)}
    i = id_to_idx[paper_id]
    sim_row = _cosine_matrix(arr)[i]

    # 取相似度高于阈值的 top-k 作为候选
    order = np.argsort(-sim_row)
    candidates, similarities = [], {}
    for j in order:
        if j == i:
            continue
        s = float(sim_row[j])
        if s < provider.similarity_threshold:
            continue
        candidates.append(inputs[j])
        similarities[inputs[j].id] = s
        if len(candidates) >= ai_config.TOP_K_SIMILAR:
            break

    src_input = inputs[i]
    print("+++++++ relations before ++++++++")
    rels = provider.suggest_relations(src_input, candidates, similarities) if candidates else []
    print("+++++++ relations complete ++++++++")
    # 覆盖式：删该源论文未被接受的旧关系建议
    db.query(AIRelationSuggestion).filter(
        AIRelationSuggestion.source_paper_id == paper_id,
        AIRelationSuggestion.is_accepted.is_(False),
    ).delete(synchronize_session=False)

    # 已被接受的 (目标, 关系类型) 不再重复建议（保持幂等）
    accepted = {
        (r.target_paper_id, r.relation_type)
        for r in db.query(AIRelationSuggestion).filter(
            AIRelationSuggestion.source_paper_id == paper_id,
            AIRelationSuggestion.is_accepted.is_(True),
        )
    }

    rows = []
    for r in rels:
        if r.dst_paper_id == paper_id:
            continue
        if (r.dst_paper_id, r.relation_type) in accepted:
            continue
        row = AIRelationSuggestion(
            source_paper_id=paper_id,
            target_paper_id=r.dst_paper_id,
            relation_type=r.relation_type,
            confidence=r.score,
            reason=r.reason,
            is_accepted=False,
        )
        db.add(row)
        rows.append(row)
    db.commit()
    for r in rows:
        db.refresh(r)
    return list_relation_suggestions(db, paper_id)


def list_relation_suggestions(db: Session, paper_id: int):
    rows = (
        db.query(AIRelationSuggestion, Paper.title)
        .join(Paper, Paper.paper_id == AIRelationSuggestion.target_paper_id)
        .filter(AIRelationSuggestion.source_paper_id == paper_id)
        .order_by(AIRelationSuggestion.confidence.desc())
        .all()
    )
    out = []
    for s, title in rows:
        out.append({
            "suggestion_id": s.suggestion_id,
            "source_paper_id": s.source_paper_id,
            "target_paper_id": s.target_paper_id,
            "relation_type": s.relation_type,
            "confidence": s.confidence,
            "reason": s.reason,
            "is_accepted": s.is_accepted,
            "target_title": title,
        })
    return out


def accept_relation_suggestion(db: Session, suggestion_id: int):
    """确认关系建议 -> 写 paper_relations（事务），标记 is_accepted。"""
    sug = db.get(AIRelationSuggestion, suggestion_id)
    if not sug:
        raise HTTPException(status_code=404, detail="Relation suggestion not found")
    try:
        relation = PaperRelation(
            source_paper_id=sug.source_paper_id,
            target_paper_id=sug.target_paper_id,
            relation_type=sug.relation_type,
            weight=sug.confidence or 1.0,
            description=sug.reason,
            generated_by="ai",
            confidence=sug.confidence or 1.0,
            is_confirmed=True,
        )
        db.add(relation)
        sug.is_accepted = True
        db.commit()
        db.refresh(relation)
    except Exception:
        db.rollback()
        raise
    return sug, relation.relation_id


# ================= 4. Related Work 聚类 =================
def generate_clusters(db: Session, project_id: int | None, num_clusters: int | None,
                      mode: str | None):
    from sklearn.cluster import KMeans

    provider = _make_provider(mode)
    inputs, arr, _ = _corpus(db, provider)

    k = min(num_clusters or ai_config.NUM_CLUSTERS, len(inputs))
    if k < 1:
        raise HTTPException(status_code=400, detail="论文数不足以聚类")

    km = KMeans(n_clusters=k, random_state=42, n_init=10)
    labels = km.fit_predict(arr)
    centers = km.cluster_centers_
    method = "kmeans" if provider.mode == "local" else "kmeans+llm"

    # 重跑前清空旧聚类（同一 project 维度；project_id=None 视为全库聚类）
    old = db.query(ResearchCluster).filter(ResearchCluster.project_id.is_(project_id)
                                           if project_id is None else
                                           ResearchCluster.project_id == project_id)
    for c in old.all():
        db.delete(c)
    db.flush()

    for c in range(k):
        idxs = [i for i, lab in enumerate(labels) if lab == c]
        if not idxs:
            continue
        members = [inputs[i] for i in idxs]
        label, desc = provider.name_cluster(members)
        cluster = ResearchCluster(
            project_id=project_id, label=label, description=desc,
            method=method, num_papers=len(idxs),
        )
        db.add(cluster)
        db.flush()
        center = centers[c]
        cnorm = float(np.linalg.norm(center)) or 1.0
        for i in idxs:
            v = arr[i]
            vnorm = float(np.linalg.norm(v)) or 1.0
            membership = float(np.dot(v, center) / (vnorm * cnorm))
            db.add(ClusterPaper(
                cluster_id=cluster.cluster_id, paper_id=inputs[i].id,
                membership_score=round(membership, 4),
            ))
    db.commit()
    return list_clusters(db, project_id)


def list_clusters(db: Session, project_id: int | None):
    query = db.query(ResearchCluster)
    if project_id is not None:
        query = query.filter(ResearchCluster.project_id == project_id)
    clusters = query.order_by(ResearchCluster.cluster_id).all()

    out = []
    for c in clusters:
        members = (
            db.query(ClusterPaper, Paper.title)
            .join(Paper, Paper.paper_id == ClusterPaper.paper_id)
            .filter(ClusterPaper.cluster_id == c.cluster_id)
            .order_by(ClusterPaper.membership_score.desc())
            .all()
        )
        out.append({
            "cluster_id": c.cluster_id,
            "label": c.label,
            "description": c.description,
            "method": c.method,
            "num_papers": c.num_papers,
            "papers": [
                {"paper_id": m.paper_id, "title": title,
                 "membership_score": m.membership_score}
                for m, title in members
            ],
        })
    return out
