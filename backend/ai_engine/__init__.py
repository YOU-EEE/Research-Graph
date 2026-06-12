"""AI 分析引擎（成员 C）——与具体数据库解耦的「大脑」。

只负责：嵌入 / 标签 / 关系 / 聚类命名，输入是 PaperInput，输出是建议对象。
持久化（读写 SQLAlchemy 表）由 backend/services/ai_service.py 负责。

通过 AI_MODE=local|cloud 一键切换离线模型 / 云端 OpenAI 格式 API。
"""
from .provider import (
    AIProvider,
    ClusterSuggestion,
    PaperInput,
    RelationSuggestion,
    TagSuggestion,
    VALID_RELATIONS,
    get_provider,
)

__all__ = [
    "AIProvider",
    "ClusterSuggestion",
    "PaperInput",
    "RelationSuggestion",
    "TagSuggestion",
    "VALID_RELATIONS",
    "get_provider",
]
