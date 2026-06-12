"""本地离线实现。

- 嵌入：优先 sentence-transformers；不可用时降级为 TF-IDF（纯离线，无需下载模型）。
- 标签：概念关键词词典扫描（确定性、可解释）。
- 关系：基于相似度 + 年份 + 方法关键词重叠 + 改进词的规则启发式。
- 聚类命名：聚合簇内论文的关键词，取最高频主题作为标签。
"""
from __future__ import annotations

import math

from . import config
from .provider import (
    AIProvider,
    PaperInput,
    RelationSuggestion,
    TagSuggestion,
)

# 概念关键词词典：tag -> 触发短语（小写匹配）
LEXICON: dict[str, list[str]] = {
    "transformer": ["transformer", "self-attention"],
    "attention": ["attention"],
    "pretraining": ["pre-training", "pretraining", "pre-trained", "masked language"],
    "language-model": ["language model", "bert", "gpt", "roberta", "electra"],
    "nlp": ["natural language", "language processing"],
    "cnn": ["convolutional", "convolution"],
    "image-recognition": ["image classification", "image recognition", "imagenet"],
    "residual-learning": ["residual"],
    "computer-vision": ["image", "vision"],
    "graph-neural-network": ["graph neural", "graph convolutional", "graph attention",
                             "gcn", "gnn"],
    "graph-learning": ["graph"],
    "node-classification": ["node classification", "semi-supervised", "node embeddings"],
    "representation-learning": ["representation learning", "representations", "embeddings"],
    "deep-learning": ["deep neural", "deep convolutional", "neural network"],
    "diffusion": ["diffusion", "denoising", "score-based"],
    "distillation": ["distillation", "distill", "teacher", "student model"],
    "flow-matching": ["flow matching", "flow-matching", "rectified flow", "optimal transport"],
    "generative-model": ["generative", "gan", "vae", "image generation"],
}

# 用于 method_related 判断的“方法类”标签子集
METHOD_TAGS = {
    "transformer", "attention", "cnn", "residual-learning",
    "graph-neural-network", "pretraining", "diffusion", "distillation", "flow-matching",
}

IMPROVE_WORDS = ("improve", "improves", "improving", "outperform", "outperforms",
                 "better", "state of the art", "state-of-the-art", "surpass")


def _norm(vec: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / n for x in vec]


class LocalProvider(AIProvider):
    def __init__(self) -> None:
        self.mode = "local"
        self._backend: str | None = None          # 'st' | 'tfidf'
        self._st_model = None
        self.model_name = f"local:{config.LOCAL_EMBED_MODEL}"

    # ---------------- 嵌入 ----------------
    def _ensure_embedder(self) -> None:
        if self._backend is not None:
            return
        try:
            from sentence_transformers import SentenceTransformer

            self._st_model = SentenceTransformer(config.LOCAL_EMBED_MODEL)
            self._backend = "st"
            self.model_name = f"local:{config.LOCAL_EMBED_MODEL}"
        except Exception as exc:  # 离线 / 未安装 / 无法下载
            if not config.ALLOW_TFIDF_FALLBACK:
                raise RuntimeError(
                    f"无法加载 sentence-transformers（{exc}），且已禁用 TF-IDF 降级。"
                ) from exc
            self._backend = "tfidf"
            self.model_name = "local:tfidf"

    def embed(self, texts: list[str]) -> list[list[float]]:
        self._ensure_embedder()
        if self._backend == "st":
            vecs = self._st_model.encode(texts, normalize_embeddings=True)
            return [list(map(float, v)) for v in vecs]
        # TF-IDF：在传入语料上拟合（service 一次性传入全部论文）
        from sklearn.feature_extraction.text import TfidfVectorizer

        vectorizer = TfidfVectorizer(stop_words="english", max_features=512)
        matrix = vectorizer.fit_transform(texts)
        return [_norm(row.toarray().ravel().tolist()) for row in matrix]

    # ---------------- 标签 ----------------
    def _tag_hits(self, text: str) -> dict[str, int]:
        low = text.lower()
        hits: dict[str, int] = {}
        for tag, phrases in LEXICON.items():
            count = sum(low.count(p) for p in phrases)
            if count:
                hits[tag] = count
        return hits

    def suggest_tags(self, paper: PaperInput, max_tags: int) -> list[TagSuggestion]:
        hits = self._tag_hits(paper.text)
        if not hits:
            return []
        ranked = sorted(hits.items(), key=lambda kv: kv[1], reverse=True)[:max_tags]
        out = []
        for tag, count in ranked:
            score = min(1.0, 0.5 + 0.15 * (count - 1))
            phrases = ", ".join(LEXICON[tag])
            reason = f"标题/摘要命中关键词「{phrases}」共 {count} 次"
            out.append(TagSuggestion(tag_name=tag, score=round(score, 3), reason=reason))
        return out

    # ---------------- 关系 ----------------
    def suggest_relations(
        self, paper: PaperInput, candidates: list[PaperInput], similarities: dict[int, float],
    ) -> list[RelationSuggestion]:
        threshold = self.similarity_threshold
        src_methods = set(self._tag_hits(paper.text)) & METHOD_TAGS
        src_text_low = paper.text.lower()
        out: list[RelationSuggestion] = []

        for cand in candidates:
            sim = similarities.get(cand.id, 0.0)
            if sim < threshold:
                continue
            cand_methods = set(self._tag_hits(cand.text)) & METHOD_TAGS
            shared = src_methods & cand_methods
            yr_s, yr_c = paper.year, cand.year
            rel_type = "same_topic"
            reason = f"嵌入相似度 {sim:.2f} ≥ 阈值 {threshold:.2f}"

            # 优先级：improves > possible_baseline > method_related > compares_with > same_topic
            if (yr_s and yr_c and yr_s > yr_c and sim >= threshold + 0.1
                    and any(w in src_text_low for w in IMPROVE_WORDS)):
                rel_type = "improves"
                reason = f"本文({yr_s})更新且含改进措辞，与较早工作({yr_c})高度相似({sim:.2f})"
            elif yr_s and yr_c and yr_c < yr_s and sim >= threshold + 0.05:
                rel_type = "possible_baseline"
                reason = f"目标工作({yr_c})更早且相似度高({sim:.2f})，可能作为基线"
            elif shared:
                rel_type = "method_related"
                reason = f"共享方法关键词 {sorted(shared)}，相似度 {sim:.2f}"
            elif yr_s and yr_c and abs(yr_s - yr_c) <= 1 and sim >= threshold:
                rel_type = "compares_with"
                reason = f"年份接近({yr_s} vs {yr_c})且相似({sim:.2f})，可能相互比较"

            out.append(RelationSuggestion(
                dst_paper_id=cand.id, relation_type=rel_type,
                score=round(float(sim), 3), reason=reason,
            ))
        return out

    # ---------------- 聚类命名 ----------------
    def name_cluster(self, papers: list[PaperInput]) -> tuple[str, str]:
        agg: dict[str, int] = {}
        for p in papers:
            for tag, count in self._tag_hits(p.text).items():
                agg[tag] = agg.get(tag, 0) + count
        if not agg:
            return ("未分类主题", f"包含 {len(papers)} 篇论文。")
        top = sorted(agg.items(), key=lambda kv: kv[1], reverse=True)[:2]
        label = " / ".join(t for t, _ in top)
        desc = f"包含 {len(papers)} 篇论文，主要关于 {', '.join(t for t, _ in top)}。"
        return (label, desc)
