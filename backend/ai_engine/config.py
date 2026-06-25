"""AI 引擎配置：从环境变量 / .env 读取，决定模式与模型参数。

关键开关：
    AI_MODE = local | cloud      # 一键切换本地离线模型 / 云端 OpenAI 格式 API

本地模式：
    LOCAL_EMBED_MODEL            # sentence-transformers 模型名
    ALLOW_TFIDF_FALLBACK         # 无法加载嵌入模型时是否降级为纯 TF-IDF（离线）

云端模式（OpenAI API 格式，兼容 OpenAI / DeepSeek / Ollama / vLLM 等）：
    OPENAI_API_KEY / OPENAI_BASE_URL / CHAT_MODEL / EMBED_MODEL
"""
from __future__ import annotations

import os

# 抑制 Windows + MKL 下 KMeans 的内存泄漏警告（须在 numpy/sklearn 计算前设置）
os.environ.setdefault("OMP_NUM_THREADS", "1")

try:
    from dotenv import load_dotenv

    load_dotenv()
except Exception:  # python-dotenv 未安装时不致命
    pass


def _get(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def _get_bool(name: str, default: bool) -> bool:
    val = os.environ.get(name)
    if val is None:
        return default
    return val.strip().lower() in ("1", "true", "yes", "on")


# ---- 模式 ----
AI_MODE = _get("AI_MODE", "local").lower()  # local | cloud

# ---- 本地模式 ----
LOCAL_EMBED_MODEL = _get("LOCAL_EMBED_MODEL", "all-MiniLM-L6-v2")
ALLOW_TFIDF_FALLBACK = _get_bool("ALLOW_TFIDF_FALLBACK", True)

# ---- 云端模式（OpenAI 格式）----
OPENAI_API_KEY = _get("OPENAI_API_KEY")
OPENAI_BASE_URL = _get("OPENAI_BASE_URL", "https://api.openai.com/v1")
CHAT_MODEL = _get("CHAT_MODEL", "gpt-4o-mini")
EMBED_MODEL = _get("EMBED_MODEL", "text-embedding-3-small")
# 部分云端 embedding 端点（如阿里云 DashScope）限制单次请求条数，需分批调用
EMBED_BATCH_SIZE = int(_get("EMBED_BATCH_SIZE", "10"))

# ---- 分析参数 ----
# 嵌入模型（sentence-transformers / OpenAI）语义相似度阈值
SIMILARITY_THRESHOLD = float(_get("SIMILARITY_THRESHOLD", "0.45"))
# TF-IDF 降级模式下相似度整体偏低，使用更低阈值
TFIDF_SIMILARITY_THRESHOLD = float(_get("TFIDF_SIMILARITY_THRESHOLD", "0.18"))
TOP_K_SIMILAR = int(_get("TOP_K_SIMILAR", "5"))
NUM_CLUSTERS = int(_get("NUM_CLUSTERS", "3"))
MAX_TAGS_PER_PAPER = int(_get("MAX_TAGS_PER_PAPER", "5"))


def resolve_mode(req_mode: str | None = None) -> str:
    """显式传入的 mode 优先于环境变量 AI_MODE。"""
    mode = (req_mode or AI_MODE or "local").lower()
    if mode not in ("local", "cloud"):
        raise ValueError(f"未知 AI_MODE: {mode!r}，应为 'local' 或 'cloud'")
    return mode
