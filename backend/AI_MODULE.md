# AI 分析模块（成员 C）接入说明

本模块已接入 ResearchGraph 后端，复用同一个 FastAPI 应用与 `research_graph.db`，
对外暴露 `/api/ai/*` 接口（REQUIREMENTS §9.3）。支持 **本地离线 / 云端 OpenAI 格式 API** 两种模式，
通过 `?mode=local|cloud` 或环境变量 `AI_MODE` 一键切换。

## 新增文件（不改动他人业务逻辑）

```
backend/
  ai_engine/                 # 与 DB 解耦的「AI 大脑」（local/cloud 双模式）
    config.py                #   AI_MODE / 阈值 / 模型名等配置
    provider.py              #   AIProvider 抽象接口 + get_provider 工厂
    local_provider.py        #   离线：sentence-transformers→TF-IDF 降级 + 词典标签 + 规则关系 + 簇命名
    cloud_provider.py        #   云端：OpenAI 格式 Chat + /v1/embeddings
  services/ai_service.py     # 编排 + 持久化：读论文→调 provider→写本项目 schema
  routers/ai.py              # /api/ai/* 路由
  scripts/seed_ai_demo.py    # 演示论文（NLP/视觉/图 各 3 篇）
  requirements-ai.txt        # 额外依赖（python-dotenv、openai；可选 sentence-transformers）
```

对既有文件的最小改动：
- `models.py`：新增 `AIRelationSuggestion`、`ResearchCluster`、`ClusterPaper`、`PaperEmbedding`
  四个成员 C 的表（其余表沿用成员 A/B/D 定义）。
- `schemas.py`：新增 AI 相关响应模型。
- `main.py`：启用 `app.include_router(ai.router, prefix="/api/ai")`（原为注释占位）。

字段映射（本项目 schema ←→ AI 引擎内部）：`score→confidence`、
`src/dst→source/target_paper_id`、`model/mode→model_name`、`status→is_accepted`。

## 安装与运行

```bash
cd backend
pip install -r requirements.txt
pip install -r requirements-ai.txt        # AI 额外依赖
python scripts/seed_ai_demo.py            # 注入演示论文（可选）
uvicorn main:app --reload
```

打开 http://127.0.0.1:8000/docs 可直接测试 `ai` 分组接口。

## 接口一览（§9.3）

| 方法 | 路径 | 说明 |
|------|------|------|
| POST | `/api/ai/tag-suggestions/{paper_id}?mode=` | 生成标签建议 → `ai_tag_suggestions` |
| GET  | `/api/ai/tag-suggestions/{paper_id}` | 查看标签建议 |
| POST | `/api/ai/tag-suggestions/{suggestion_id}/accept` | 确认 → `tags` / `paper_tags`（事务） |
| POST | `/api/ai/similarity/{paper_id}?mode=&top_k=` | 计算相似论文 → `paper_similarity` |
| GET  | `/api/ai/similarity/{paper_id}` | 查看相似论文（含标题） |
| POST | `/api/ai/relation-suggestions/{paper_id}?mode=` | 生成关系建议 → `ai_relation_suggestions` |
| GET  | `/api/ai/relation-suggestions/{paper_id}` | 查看关系建议（含目标标题） |
| POST | `/api/ai/relation-suggestions/{suggestion_id}/accept` | 确认 → `paper_relations`（事务） |
| POST | `/api/ai/clusters`（body: `{project_id?, num_clusters?, mode?}`） | Related Work 聚类 → `research_clusters`/`cluster_papers` |
| GET  | `/api/ai/clusters/{project_id}` / `/api/ai/clusters` | 查看聚类 |

关系类型：`same_topic` / `method_related` / `possible_baseline` / `improves` / `compares_with`。

## 模式切换

- **local（默认，离线）**：装了 `sentence-transformers` 用语义向量，否则自动降级为 TF-IDF；
  标签走关键词词典，关系走规则启发式。无需联网、无需 Key。
- **cloud（OpenAI 格式）**：在 `backend/.env` 配置后用 `?mode=cloud`：
  ```
  AI_MODE=cloud
  OPENAI_API_KEY=sk-...
  OPENAI_BASE_URL=https://api.openai.com/v1   # 可指向 DeepSeek / Ollama / vLLM
  CHAT_MODEL=gpt-4o-mini
  EMBED_MODEL=text-embedding-3-small
  ```
  两种模式写入同一套表，`model_name` 字段区分来源，前端/SQL 无需改动。

## 前端对接（待成员 C/D 补 `AIAnalysis.vue`）

`frontend/src/api/` 下尚无 `ai.js`。建议新增，调用上表接口；
`AIAnalysis.vue` 展示标签/相似/关系建议并提供「接受」按钮（调用 `/accept`）。
当前后端接口已就绪，可先用 `/docs` 联调。
