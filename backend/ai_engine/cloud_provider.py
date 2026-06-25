"""云端实现，统一走 OpenAI API 格式。

- 通过 `openai` SDK + 可配置 base_url，兼容 OpenAI / DeepSeek / Ollama / vLLM 等端点。
- 标签 / 关系 / 聚类命名：Chat Completions（要求严格 JSON 输出）。
- 嵌入：/v1/embeddings 接口。

若某端点不提供 embeddings，可在 .env 设 ALLOW_TFIDF_FALLBACK 并改用 local 嵌入；
本实现专注云端，嵌入失败会抛出清晰错误。
"""
from __future__ import annotations

import json
import math
import re

from . import config
from .provider import (
    VALID_RELATIONS,
    AIProvider,
    PaperInput,
    RelationSuggestion,
    TagSuggestion,
)


def _norm(vec: list[float]) -> list[float]:
    n = math.sqrt(sum(x * x for x in vec)) or 1.0
    return [x / n for x in vec]


def _extract_json(text: str):
    """从模型回复中提取首个 JSON 对象 / 数组。"""
    text = text.strip()
    # 去掉可能的 ```json 围栏
    text = re.sub(r"^```(?:json)?|```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    match = re.search(r"(\[.*\]|\{.*\})", text, flags=re.DOTALL)
    if match:
        return json.loads(match.group(1))
    raise ValueError(f"无法从模型输出解析 JSON：{text[:200]!r}")


class CloudProvider(AIProvider):
    def __init__(self) -> None:
        self.mode = "cloud"
        self.model_name = f"cloud:{config.CHAT_MODEL}"
        if not config.OPENAI_API_KEY:
            raise RuntimeError(
                "云端模式需要 OPENAI_API_KEY（可在 .env 配置），"
                "或改用 local 模式跑离线分析。"
            )
        from openai import OpenAI

        self._client = OpenAI(
            api_key=config.OPENAI_API_KEY,
            base_url=config.OPENAI_BASE_URL,
        )

    def _chat_json(self, system: str, user: str):
        resp = self._client.chat.completions.create(
            model=config.CHAT_MODEL,
            messages=[
                {"role": "system", "content": system},
                {"role": "user", "content": user},
            ],
            temperature=0.2,
        )
        return _extract_json(resp.choices[0].message.content or "")

    # ---------------- 嵌入 ----------------
    def embed(self, texts: list[str]) -> list[list[float]]:
        # 部分端点限制单批条数（如 DashScope ≤ 10），按 EMBED_BATCH_SIZE 分批后再拼接
        batch_size = max(1, config.EMBED_BATCH_SIZE)
        out: list[list[float]] = []
        for start in range(0, len(texts), batch_size):
            chunk = texts[start:start + batch_size]
            resp = self._client.embeddings.create(
                model=config.EMBED_MODEL, input=chunk
            )
            # 按 index 排序，确保返回顺序与输入一致
            ordered = sorted(resp.data, key=lambda d: d.index)
            out.extend(_norm(list(d.embedding)) for d in ordered)
        return out

    # ---------------- 标签 ----------------
    def suggest_tags(self, paper: PaperInput, max_tags: int) -> list[TagSuggestion]:
        system = (
            "你是论文主题标注助手。根据标题和摘要给出简洁的英文小写连字符标签"
            "（如 graph-neural-network）。只输出 JSON 数组，元素为 "
            '{"tag": string, "score": number(0~1), "reason": string(中文简述)}。'
        )
        user = (
            f"最多 {max_tags} 个标签。\n标题：{paper.title}\n摘要：{paper.abstract}"
        )
        data = self._chat_json(system, user)
        out = []
        for item in data[:max_tags]:
            tag = str(item.get("tag", "")).strip().lower()
            if tag:
                out.append(TagSuggestion(
                    tag_name=tag,
                    score=float(item.get("score", 0.7)),
                    reason=str(item.get("reason", "")),
                ))
        return out

    # ---------------- 关系 ----------------
    def suggest_relations(
        self, paper: PaperInput, candidates: list[PaperInput], similarities: dict[int, float],
    ) -> list[RelationSuggestion]:
        cand_lines = [
            {
                "id": c.id,
                "title": c.title,
                "year": c.year,
                "abstract": c.abstract[:300],
                "similarity": round(similarities.get(c.id, 0.0), 3),
            }
            for c in candidates
        ]
        system = (
            "你是科研关系分析助手。判断「源论文」与每个「候选论文」之间的关系，"
            f"类型必须取自：{list(VALID_RELATIONS)}。"
            "只为确有关系的候选输出。只输出 JSON 数组，元素为 "
            '{"dst_paper_id": int, "relation_type": string, '
            '"score": number(0~1), "reason": string(中文简述)}。'
        )
        user = json.dumps(
            {
                "source": {"title": paper.title, "year": paper.year,
                           "abstract": paper.abstract[:500]},
                "candidates": cand_lines,
            },
            ensure_ascii=False,
        )
        data = self._chat_json(system, user)
        out = []
        for item in data:
            rel = str(item.get("relation_type", "")).strip()
            if rel not in VALID_RELATIONS:
                continue
            try:
                dst = int(item["dst_paper_id"])
            except (KeyError, ValueError, TypeError):
                continue
            out.append(RelationSuggestion(
                dst_paper_id=dst,
                relation_type=rel,
                score=float(item.get("score", 0.7)),
                reason=str(item.get("reason", "")),
            ))
        return out

    # ---------------- 聚类命名 ----------------
    def name_cluster(self, papers: list[PaperInput]) -> tuple[str, str]:
        titles = [p.title for p in papers]
        system = (
            "你是科研主题归纳助手。给定一组论文标题，归纳它们的共同研究主题。"
            '只输出 JSON 对象 {"label": string(简短主题名), "description": string(中文一句话)}。'
        )
        user = "论文标题：\n" + "\n".join(f"- {t}" for t in titles)
        data = self._chat_json(system, user)
        return (
            str(data.get("label", "未命名主题")),
            str(data.get("description", f"包含 {len(papers)} 篇论文。")),
        )
