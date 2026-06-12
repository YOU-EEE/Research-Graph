"""AIProvider 抽象接口 + 工厂。

上层 service 只依赖本接口，不关心 local / cloud，从而通过配置一键切换。
"""
from __future__ import annotations

import abc
from dataclasses import dataclass, field


@dataclass
class PaperInput:
    """喂给 AI 的论文最小信息。"""
    id: int
    title: str
    abstract: str = ""
    year: int | None = None
    venue: str = ""
    notes: str = ""

    @property
    def text(self) -> str:
        """用于嵌入 / 相似度的拼接文本。"""
        return f"{self.title}. {self.abstract} {self.notes}".strip()


@dataclass
class TagSuggestion:
    tag_name: str
    score: float
    reason: str = ""


@dataclass
class RelationSuggestion:
    dst_paper_id: int
    relation_type: str            # same_topic | method_related | possible_baseline | improves | compares_with
    score: float
    reason: str = ""


@dataclass
class ClusterSuggestion:
    label: str
    description: str
    paper_ids: list[int] = field(default_factory=list)
    membership: dict[int, float] = field(default_factory=dict)  # paper_id -> 接近度 0~1


VALID_RELATIONS = (
    "same_topic", "method_related", "possible_baseline", "improves", "compares_with",
)


class AIProvider(abc.ABC):
    """所有 AI 实现遵循的统一接口。"""

    #: 写入 AI 表的 model 字段（来源标识）
    model_name: str = "unknown"
    #: 'local' | 'cloud'
    mode: str = "local"
    #: 关系/候选的相似度阈值（service 按嵌入方式动态设置）
    similarity_threshold: float = 0.45

    @abc.abstractmethod
    def embed(self, texts: list[str]) -> list[list[float]]:
        """返回每段文本的向量（已可直接做余弦相似度）。"""

    @abc.abstractmethod
    def suggest_tags(self, paper: PaperInput, max_tags: int) -> list[TagSuggestion]:
        """根据标题 + 摘要推荐标签。"""

    @abc.abstractmethod
    def suggest_relations(
        self, paper: PaperInput, candidates: list[PaperInput], similarities: dict[int, float],
    ) -> list[RelationSuggestion]:
        """为 paper 推荐与 candidates 的关系边。similarities: candidate_id -> 相似度。"""

    @abc.abstractmethod
    def name_cluster(self, papers: list[PaperInput]) -> tuple[str, str]:
        """给一组论文起一个研究主题名 (label, description)。"""


def get_provider(mode: str) -> AIProvider:
    """工厂：按模式返回对应实现。延迟导入，避免无谓依赖加载。"""
    mode = mode.lower()
    if mode == "local":
        from .local_provider import LocalProvider

        return LocalProvider()
    if mode == "cloud":
        from .cloud_provider import CloudProvider

        return CloudProvider()
    raise ValueError(f"未知模式 {mode!r}，应为 'local' 或 'cloud'")
