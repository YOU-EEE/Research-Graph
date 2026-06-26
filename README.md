# ResearchGraph

ResearchGraph 是一个面向科研阅读、文献管理和团队协作的知识图谱系统。项目将论文元数据、阅读笔记、概念卡片、AI 分析结果、项目协作和阅读任务统一管理，并通过知识图谱进行可视化呈现。

本项目适合用于课程项目演示、科研文献管理原型、Related Work 整理和团队阅读协作场景。

## 主要功能

- **用户与工作台**
  - 用户注册、登录
  - Dashboard 展示论文数、笔记数、项目数、待完成任务、最近论文、活动日志和高频标签

- **论文管理**
  - 论文结构化录入：标题、摘要、年份、状态、类型、作者、标签、会议/期刊、URL、DOI、arXiv ID
  - 论文搜索与筛选
  - 标签、会议/期刊、文献目录管理
  - 论文详情页、附件上传、BibTeX 原文保存

- **BibTeX 导入**
  - 支持粘贴 BibTeX 文本
  - 支持上传 `.bib` 文件
  - 自动解析论文、作者、来源、标签和原始 BibTeX 条目

- **阅读笔记与概念卡片**
  - Markdown 阅读笔记
  - 笔记关联论文
  - 使用 `[[Concept Name]]` 语法解析概念
  - 概念列表、概念详情、关联笔记、反向链接和相关笔记

- **AI 科研分析**
  - 自动标签推荐
  - 相似论文推荐
  - 知识图谱关系补边
  - Related Work 主题聚类
  - 支持本地模式和 OpenAI-compatible 云端模式

- **科研项目与协作**
  - 创建科研项目
  - 项目成员与角色管理
  - 创建阅读任务、分配负责人、跟踪任务状态
  - 任务评论和活动日志

- **知识图谱可视化**
  - 使用 Cytoscape 展示论文、作者、会议、标签、笔记、概念、项目、用户和 AI 聚类主题
  - 支持节点搜索、节点类型筛选、边类型筛选、布局切换和节点高亮
  - 支持项目视角图谱

## 技术架构

```text
Research-Graph
├── backend/                 FastAPI 后端
│   ├── main.py              API 入口，注册所有路由
│   ├── database.py          SQLite / SQLAlchemy 初始化
│   ├── models.py            数据库 ORM 模型
│   ├── schemas.py           Pydantic 数据模型
│   ├── routers/             业务 API 路由
│   │   ├── auth.py          用户注册、登录
│   │   ├── papers.py        论文、作者、标签、会议、目录、BibTeX
│   │   ├── notes.py         阅读笔记、概念卡片
│   │   ├── ai.py            AI 分析接口
│   │   ├── projects.py      项目、成员、任务、评论
│   │   └── graph.py         知识图谱数据接口
│   ├── services/            业务服务层
│   ├── ai_engine/           本地 / 云端 AI Provider
│   ├── seed_papers.py       演示数据种子脚本
│   └── generate_ai_data.py  预生成 AI 相似度、关系和聚类
│
├── frontend/                Vue 3 前端
│   ├── src/
│   │   ├── views/           页面组件
│   │   ├── components/      通用组件
│   │   ├── api/             Axios API 封装
│   │   ├── router/          Vue Router 路由
│   │   └── style.css        全局样式
│   ├── package.json
│   └── vite.config.js
│
├── demo/                    演示截图
├── docs/                    项目说明、演示文档和报告源码
│   ├── DEMO_GUIDE.md        功能介绍文档
│   ├── ResearchGraph_Demo.md Marp 横版演示 slides
│   └── REPORT.md            报告 Markdown 源文档
├── Demo.pptx                演示 PPT
├── REPORT.pdf               项目报告
├── requirements.txt         Python 依赖
└── README.md
```

### 后端

- Web 框架：FastAPI
- ORM：SQLAlchemy
- 数据库：SQLite
- API 文档：FastAPI 自动生成 Swagger UI
- AI 分析：本地 `sentence-transformers` / TF-IDF fallback，或 OpenAI-compatible API

后端启动时会自动创建数据库表，并执行 SQLite 补充初始化，包括索引、触发器和视图。

默认数据库文件：

```text
backend/research_graph.db
```

### 前端

- 框架：Vue 3
- 构建工具：Vite
- UI 组件：Element Plus
- HTTP：Axios
- Markdown 编辑：md-editor-v3
- 图谱可视化：Cytoscape
- 路由：Vue Router

前端默认请求：

```text
http://127.0.0.1:8000/api
```

可通过 `VITE_API_BASE_URL` 修改 API 地址。

## 环境要求

建议环境：

- Python 3.10+
- Node.js 18+
- npm 9+
- Windows / macOS / Linux 均可运行

本项目默认使用 SQLite，不需要额外安装数据库服务。

## 后端运行指南

在项目根目录执行：

```bash
cd backend
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
```

macOS / Linux：

```bash
source .venv/bin/activate
```

安装依赖：

```bash
python -m pip install --upgrade pip
python -m pip install -r ../requirements.txt
```

启动后端：

```bash
uvicorn main:app --reload
```

默认地址：

```text
http://127.0.0.1:8000
```

API 文档：

```text
http://127.0.0.1:8000/docs
```

健康检查：

```text
http://127.0.0.1:8000/
```

返回示例：

```json
{"message": "ResearchGraph backend is running"}
```

## 前端运行指南

打开另一个终端，在项目根目录执行：

```bash
cd frontend
npm install
npm run dev
```

前端默认地址通常为：

```text
http://localhost:5173
```

如果端口被占用，以 Vite 终端输出的新地址为准。

### 前端 API 地址配置

如需修改后端地址，可在 `frontend/.env` 中配置：

```env
VITE_API_BASE_URL=http://127.0.0.1:8000/api
```

修改后需要重启前端开发服务器。

## 首次使用

1. 启动后端。
2. 启动前端。
3. 打开前端页面。
4. 在登录页切换到注册，创建一个用户。
5. 登录后进入 Dashboard。

前端会把用户信息保存到浏览器 `localStorage`，并在请求中自动携带 `x-user-id` 请求头。未登录访问业务页面会自动跳转到登录页。

## 准备演示数据

如果数据库为空，论文列表、AI 分析和知识图谱页面会比较空。推荐导入演示数据。

### 方式一：前端导入 BibTeX

进入：

```text
BibTeX 导入
```

页面自带示例 BibTeX，可直接点击导入。该方式适合快速验证 BibTeX 解析和论文入库。

### 方式二：运行种子脚本

在后端目录执行：

```bash
cd backend
python seed_papers.py
```

该脚本会创建一批演示论文、作者、标签、会议、论文关系、阅读笔记和概念，用于展示论文管理、笔记、概念卡片和知识图谱。

如需预生成 AI 相似度、关系建议和主题聚类，可继续执行：

```bash
python generate_ai_data.py
```

## AI 配置

AI 模块支持两种模式：

```text
local：本地模式
cloud：云端 OpenAI-compatible API 模式
```

### 本地模式

默认模式为 `local`。

本地模式会优先尝试使用 `sentence-transformers` 模型：

```env
AI_MODE=local
LOCAL_EMBED_MODEL=all-MiniLM-L6-v2
ALLOW_TFIDF_FALLBACK=true
```

如果本地模型不可用，并且 `ALLOW_TFIDF_FALLBACK=true`，系统会降级为 TF-IDF，不依赖云端 API。

### 云端模式

云端模式使用 OpenAI-compatible 接口，可兼容 OpenAI、DeepSeek、Ollama、vLLM 等提供相似 API 格式的服务。

可在 `backend/.env` 中配置：

```env
AI_MODE=cloud
OPENAI_API_KEY=your_api_key
OPENAI_BASE_URL=https://api.openai.com/v1
CHAT_MODEL=gpt-4o-mini
EMBED_MODEL=text-embedding-3-small
EMBED_BATCH_SIZE=10
```

常用分析参数：

```env
SIMILARITY_THRESHOLD=0.45
TFIDF_SIMILARITY_THRESHOLD=0.18
TOP_K_SIMILAR=5
NUM_CLUSTERS=3
MAX_TAGS_PER_PAPER=5
```

修改 `.env` 后需要重启后端。

## 常用页面

```text
/login             登录 / 注册
/dashboard         Dashboard
/papers            论文管理
/papers/:id        论文详情
/import/bibtex     BibTeX 导入
/notes             阅读笔记
/notes/:id         笔记编辑器
/concepts          概念卡片
/concepts/:id      概念详情
/ai                AI 分析
/projects          科研项目
/projects/:id      项目详情
/tasks             阅读任务
/graph             知识图谱
```

## 关键 API 模块

后端 API 统一以 `/api` 为前缀：

```text
/api/papers        论文管理
/api/authors       作者
/api/tags          标签
/api/venues        会议 / 期刊
/api/collections   文献目录
/api/import        BibTeX 导入
/api/notes         阅读笔记
/api/concepts      概念卡片
/api/ai            AI 分析
/api/auth          用户注册 / 登录
/api/projects      项目与协作
/api/tasks         阅读任务
/api/graph         知识图谱
```

详细接口以 FastAPI 文档为准：

```text
http://127.0.0.1:8000/docs
```

## 构建前端

在 `frontend` 目录执行：

```bash
npm run build
```

构建产物会生成到：

```text
frontend/dist
```

本地预览构建结果：

```bash
npm run preview
```

## 演示文档

项目包含两份演示材料：

- `docs/DEMO_GUIDE.md`：介绍性的功能演示文档
- `docs/ResearchGraph_Demo.md`：Marp 横版 Markdown slides，适合导出 PPT/PDF
- `Demo.pptx`：已导出的演示 PPT

如果安装了 Marp CLI，可导出 slides：

```bash
marp docs/ResearchGraph_Demo.md --pptx
marp docs/ResearchGraph_Demo.md --pdf
```

也可以使用 VS Code 的 Marp 扩展进行预览和导出。

## 常见问题

### 1. 前端请求后端失败

确认后端已启动，并且前端 API 地址正确：

```text
http://127.0.0.1:8000/api
```

如后端端口改变，请设置 `frontend/.env` 中的 `VITE_API_BASE_URL`。

### 2. 数据库为空

先注册用户，再运行：

```bash
cd backend
python seed_papers.py
```

然后刷新前端页面。

### 3. AI 分析提示论文数量不足

相似论文推荐和聚类至少需要 2 篇论文。请先导入 BibTeX 或运行种子脚本。

### 4. 本地 AI 模型加载失败

如果无法下载或加载 `sentence-transformers` 模型，可以保持：

```env
ALLOW_TFIDF_FALLBACK=true
```

系统会自动使用 TF-IDF 降级模式。

### 5. SQLite 出现锁等待

项目已启用 WAL 和 `busy_timeout`，一般开发演示场景可正常使用。如果仍出现锁等待，确认没有多个后端进程同时写入同一个数据库文件。

## 项目状态

当前版本是课程项目原型，重点覆盖科研文献管理、阅读笔记、AI 辅助分析、协作任务和知识图谱可视化的完整功能闭环。后续可继续扩展权限系统、PDF 在线阅读、引用网络导入、多人实时协作和更完整的 AI 工作流。
