# ResearchGraph 需求文档 v1.0

## 1. 项目名称

**ResearchGraph：融合 Zotero 式文献管理、Obsidian 式双链笔记与 AI 知识图谱分析的本地科研协作系统**

## 2. 项目背景

科研小组在进行文献调研时通常会遇到以下问题：

1. 论文数量多，难以统一管理；
2. PDF、BibTeX、阅读笔记分散在不同位置；
3. 组内成员不知道彼此阅读了哪些论文；
4. 论文之间的引用关系、方法关系、主题关系不够直观；
5. 写 Related Work 时，难以快速找到某个方向下的代表论文；
6. 传统文献管理工具偏重“条目管理”，知识网络和协作功能较弱。

本系统参考 Zotero 的本地文献管理思想。Zotero 官方文档中说明其本地数据目录包含数据库与附件文件，其中包括 `zotero.sqlite` 和 `storage` 等内容，这启发本项目采用“结构化元数据数据库 + 本地文件存储”的设计。([Zotero][1])

同时，系统参考 Obsidian 的双向链接思想，将论文、笔记、概念、标签、作者、项目组织为知识图谱，并通过 AI 分析模块自动推荐标签、相似论文和潜在关系边。

---

# 3. 项目目标

## 3.1 核心目标

实现一个本地科研论文管理与协作系统，支持：

1. Zotero-like 文献管理；
2. Obsidian-like Markdown 双链笔记；
3. AI 自动标签、相似论文推荐、关系补边；
4. 科研小组项目协作；
5. 知识图谱可视化；
6. 数据库课程要求中的表设计、约束、事务、视图、触发器、复杂查询、索引等内容。

## 3.2 项目边界

本项目不是完整复刻 Zotero 或 Obsidian，而是实现一个适合数据库大作业展示的最小可行系统。

优先保证：

```text
数据库设计完整
核心功能可演示
前后端可运行
SQL 查询丰富
AI 分析逻辑清晰
知识图谱展示效果好
```

暂不要求：

```text
真实多人在线同步
复杂权限系统
完整 PDF 标注器
大模型在线调用
跨设备云同步
生产级安全加密
```

---

# 4. 推荐技术栈

## 4.1 前端

```text
Vue3
Vite
Element Plus
Axios
Vue Router
Cytoscape.js
Markdown 编辑器：md-editor-v3 或 @kangc/v-md-editor
```

Cytoscape.js 是一个开源 JavaScript 图论和网络可视化库，适合用于本系统的知识图谱页面。([Cytoscape.js][2])

## 4.2 后端

```text
Python 3.10+
FastAPI
SQLAlchemy
Pydantic
Uvicorn
python-multipart
bibtexparser
scikit-learn
numpy
```

FastAPI 适合快速构建 API，并且内置基于 OpenAPI 的交互式接口文档页面，默认可通过 `/docs` 使用 Swagger UI 测试接口。([FastAPI][3])

## 4.3 数据库

```text
SQLite
```

扩展功能可以使用：

```text
SQLite FTS5 全文检索
```

SQLite FTS5 是 SQLite 的全文搜索虚拟表模块，适合对论文标题、摘要、笔记内容进行全文检索。([SQLite][4])

## 4.4 开发工具

```text
VS Code
DBeaver
DB Browser for SQLite
Apifox / Postman
draw.io / ProcessOn
Git + GitHub / Gitee
```

---

# 5. 系统角色

系统包含三类用户角色。

| 角色     | 权限                       |
| ------ | ------------------------ |
| Admin  | 管理项目、成员、论文、任务、关系图谱       |
| Member | 添加论文、写笔记、确认 AI 推荐、完成阅读任务 |
| Viewer | 查看论文、笔记、图谱和任务进度          |

本项目可以简化登录逻辑，使用本地账号密码登录即可，不需要实现真实邮箱验证。

---

# 6. 四大功能模块

系统拆分为四个模块，分别对应四位同学的工作。

---

## 模块 A：Zotero-like 文献管理模块

### 6.1 功能目标

实现论文元数据、作者、会议、标签、PDF 附件和 BibTeX 的管理。

### 6.2 主要功能

1. 新增论文；
2. 编辑论文；
3. 删除论文；
4. 查询论文列表；
5. 查看论文详情；
6. 管理作者；
7. 管理会议 / 期刊；
8. 管理标签；
9. 管理 Collection；
10. 上传 PDF 附件；
11. 导入 BibTeX；
12. 查看论文完整信息，包括作者、标签、会议、年份、摘要、附件路径。

### 6.3 页面需求

#### 论文列表页 `/papers`

功能：

```text
显示论文标题、作者、年份、会议、标签、阅读状态
支持按标题搜索
支持按标签筛选
支持按年份筛选
支持分页
支持新增、编辑、删除
```

#### 论文详情页 `/papers/:id`

功能：

```text
显示论文完整元数据
显示作者列表
显示标签列表
显示 BibTeX
显示 PDF 附件
显示相关笔记
显示相关论文关系
```

#### BibTeX 导入页 `/import/bibtex`

功能：

```text
上传 .bib 文件
解析 BibTeX
预览解析结果
确认导入
写入 papers、authors、paper_authors、venues、bibtex_entries 表
```

### 6.4 核心数据表

```text
papers
authors
paper_authors
venues
tags
paper_tags
collections
collection_papers
attachments
bibtex_entries
```

---

## 模块 B：Obsidian-like Markdown 笔记与双链模块

### 6.5 功能目标

实现论文阅读笔记、Markdown 编辑、双向链接、概念卡片和反向链接。

### 6.6 主要功能

1. 为论文创建阅读笔记；
2. 编辑 Markdown 笔记；
3. 预览 Markdown；
4. 支持 `[[概念名]]` 形式的双向链接；
5. 自动解析笔记中的双链；
6. 自动创建概念卡片；
7. 查询某个概念被哪些笔记引用；
8. 查询某篇笔记的反向链接；
9. 建立 note-note、note-concept、paper-note 关系。

### 6.7 页面需求

#### 笔记编辑页 `/notes/:id`

功能：

```text
左侧 Markdown 编辑
右侧 Markdown 预览
保存笔记
解析 [[双链]]
显示当前笔记关联的概念
```

#### 概念卡片页 `/concepts/:id`

功能：

```text
显示概念名称
显示概念描述
显示引用该概念的笔记列表
显示关联论文
```

#### 反向链接页 `/notes/:id/backlinks`

功能：

```text
显示哪些笔记链接到了当前笔记
显示哪些概念与当前笔记有关
```

### 6.8 双链解析规则

笔记内容示例：

```markdown
这篇论文使用了 [[Flow Matching]] 的思想，并且与 [[DMD2]] 有关。
```

后端需要解析出：

```text
Flow Matching
DMD2
```

处理逻辑：

```text
1. 使用正则表达式提取 [[...]] 中的内容；
2. 判断 concepts 表中是否已有该概念；
3. 没有则自动创建；
4. 在 note_concepts 表中建立 note_id 和 concept_id 的关系；
5. 返回解析结果给前端。
```

### 6.9 核心数据表

```text
notes
concepts
note_concepts
note_links
paper_notes
link_parse_logs
```

---

## 模块 C：AI 科研分析模块

### 6.10 功能目标

实现轻量级 AI 分析，包括自动标签推荐、相似论文推荐、知识图谱关系补边、Related Work 聚类。

### 6.11 AI 实现原则

本项目不训练大模型，优先使用可解释、易运行的轻量方法。

推荐基础实现：

```text
TF-IDF + Cosine Similarity
```

可选增强实现：

```text
sentence-transformers embedding + cosine similarity
```

大作业阶段优先实现 TF-IDF 版本。

### 6.12 AI 功能 1：自动标签推荐

输入：

```text
论文标题
论文摘要
论文关键词
```

输出：

```text
推荐标签列表
每个标签的置信度
推荐原因
```

示例：

```json
[
  {
    "tag_name": "Flow Matching",
    "confidence": 0.87,
    "reason": "title and abstract contain flow, matching, transport"
  },
  {
    "tag_name": "Diffusion Model",
    "confidence": 0.76,
    "reason": "abstract contains diffusion and generative model"
  }
]
```

用户可以接受或拒绝推荐标签。

接受后：

```text
写入 tags 表和 paper_tags 表
更新 ai_tag_suggestions.is_accepted = 1
```

### 6.13 AI 功能 2：相似论文推荐

输入：

```text
当前论文的标题 + 摘要 + 笔记
数据库中其他论文的标题 + 摘要 + 笔记
```

输出：

```text
Top-k 相似论文
相似度分数
推荐理由
```

推荐逻辑：

```text
1. 拼接论文 title + abstract；
2. 使用 TF-IDF 转向量；
3. 计算当前论文与其他论文的 cosine similarity；
4. 返回 Top-k；
5. 写入 paper_similarity 表。
```

### 6.14 AI 功能 3：知识图谱关系补边

系统根据以下信息推荐论文关系：

```text
论文语义相似度
标签重合度
共同作者
共同引用
笔记中出现的论文名或概念名
```

推荐关系类型：

```text
same_topic
method_related
possible_baseline
compares_with
extends
improves
uses_method_of
```

示例：

```json
{
  "source_paper": "AnyFlow",
  "target_paper": "MeanFlow",
  "relation_type": "method_related",
  "confidence": 0.82,
  "reason": "high semantic similarity and shared tags: Flow Matching, Distillation"
}
```

用户确认后写入正式的 `paper_relations` 表。

### 6.15 AI 功能 4：Related Work 聚类

输入：

```text
项目 ID
研究主题关键词
```

输出：

```text
研究主题分组
每组代表论文
每组关键词
每篇论文的相关性分数
```

示例：

```text
主题：Flow Matching Distillation

Cluster 1：Consistency-based Distillation
代表论文：Consistency Models, sCM, SANA-Sprint

Cluster 2：Adversarial Distillation
代表论文：DMD, DMD2, SiD

Cluster 3：Flow-based Distillation
代表论文：AnyFlow, MeanFlow, Shortcut Models
```

### 6.16 核心数据表

```text
ai_tag_suggestions
paper_similarity
ai_relation_suggestions
research_clusters
cluster_papers
```

---

## 模块 D：科研协作与知识图谱可视化模块

### 6.17 功能目标

实现项目空间、成员管理、阅读任务、评论讨论、活动日志和知识图谱展示。

### 6.18 主要功能

1. 用户登录；
2. 创建科研项目；
3. 添加项目成员；
4. 设置成员角色；
5. 分配论文阅读任务；
6. 更新任务状态；
7. 评论论文、笔记或任务；
8. 记录活动日志；
9. 生成知识图谱数据；
10. 前端可视化知识图谱；
11. 支持图谱筛选、搜索、点击节点查看详情。

### 6.19 页面需求

#### Dashboard `/dashboard`

显示：

```text
论文总数
笔记总数
项目总数
待完成任务数
最近新增论文
最近活动日志
高频标签
```

#### 项目页 `/projects/:id`

显示：

```text
项目名称
项目描述
成员列表
项目论文列表
阅读任务列表
项目知识图谱入口
```

#### 阅读任务页 `/tasks`

显示：

```text
任务名称
对应论文
负责人
截止时间
任务状态
完成按钮
评论入口
```

任务状态：

```text
todo
reading
done
reported
```

#### 知识图谱页 `/graph`

功能：

```text
显示 paper、author、tag、concept、note、project 节点
显示 authored_by、has_tag、links_to、same_topic 等边
支持节点类型筛选
支持边类型筛选
支持搜索节点
支持点击节点查看详情
支持缩放、拖拽、布局刷新
```

### 6.20 图谱节点类型

| 节点类型    | 示例                          |
| ------- | --------------------------- |
| paper   | AnyFlow                     |
| author  | Zhang San                   |
| venue   | CVPR                        |
| tag     | Flow Matching               |
| concept | Classifier-free Guidance    |
| note    | MeanFlow Objective 笔记       |
| project | Object Removal Distillation |

### 6.21 图谱边类型

| 边类型              | 含义     |
| ---------------- | ------ |
| authored_by      | 论文-作者  |
| published_in     | 论文-会议  |
| has_tag          | 论文-标签  |
| has_note         | 论文-笔记  |
| mentions_concept | 笔记-概念  |
| links_to         | 笔记-笔记  |
| cites            | 论文引用论文 |
| same_topic       | 同主题    |
| method_related   | 方法相关   |
| improves         | 改进     |
| compares_with    | 对比     |
| assigned_to      | 任务-用户  |

### 6.22 核心数据表

```text
users
projects
project_members
reading_tasks
task_assignments
comments
activity_logs
paper_relations
```

---

# 7. 数据库设计

## 7.1 用户与项目表

```sql
CREATE TABLE users (
    user_id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL UNIQUE,
    email TEXT UNIQUE,
    password_hash TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE projects (
    project_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_name TEXT NOT NULL,
    description TEXT,
    owner_id INTEGER NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (owner_id) REFERENCES users(user_id)
);

CREATE TABLE project_members (
    project_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK(role IN ('admin', 'member', 'viewer')),
    joined_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (project_id, user_id),
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

## 7.2 论文元数据表

```sql
CREATE TABLE venues (
    venue_id INTEGER PRIMARY KEY AUTOINCREMENT,
    venue_name TEXT NOT NULL,
    venue_type TEXT CHECK(venue_type IN ('conference', 'journal', 'workshop', 'preprint'))
);

CREATE TABLE papers (
    paper_id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    abstract TEXT,
    year INTEGER,
    venue_id INTEGER,
    paper_type TEXT DEFAULT 'article',
    doi TEXT,
    arxiv_id TEXT,
    url TEXT,
    reading_status TEXT DEFAULT 'unread'
        CHECK(reading_status IN ('unread', 'reading', 'finished', 'archived')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (venue_id) REFERENCES venues(venue_id)
);
```

## 7.3 作者关系表

```sql
CREATE TABLE authors (
    author_id INTEGER PRIMARY KEY AUTOINCREMENT,
    author_name TEXT NOT NULL,
    affiliation TEXT
);

CREATE TABLE paper_authors (
    paper_id INTEGER NOT NULL,
    author_id INTEGER NOT NULL,
    author_order INTEGER,
    is_corresponding BOOLEAN DEFAULT 0,
    PRIMARY KEY (paper_id, author_id),
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (author_id) REFERENCES authors(author_id)
);
```

## 7.4 标签与 Collection 表

```sql
CREATE TABLE tags (
    tag_id INTEGER PRIMARY KEY AUTOINCREMENT,
    tag_name TEXT NOT NULL UNIQUE,
    color TEXT
);

CREATE TABLE paper_tags (
    paper_id INTEGER NOT NULL,
    tag_id INTEGER NOT NULL,
    PRIMARY KEY (paper_id, tag_id),
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (tag_id) REFERENCES tags(tag_id)
);

CREATE TABLE collections (
    collection_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER,
    collection_name TEXT NOT NULL,
    parent_id INTEGER,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (parent_id) REFERENCES collections(collection_id)
);

CREATE TABLE collection_papers (
    collection_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    PRIMARY KEY (collection_id, paper_id),
    FOREIGN KEY (collection_id) REFERENCES collections(collection_id),
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);
```

## 7.5 附件与 BibTeX 表

```sql
CREATE TABLE attachments (
    attachment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    file_name TEXT NOT NULL,
    file_path TEXT NOT NULL,
    file_type TEXT,
    uploaded_by INTEGER,
    uploaded_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (uploaded_by) REFERENCES users(user_id)
);

CREATE TABLE bibtex_entries (
    bibtex_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    bibtex_key TEXT,
    raw_bibtex TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);
```

## 7.6 笔记与双链表

```sql
CREATE TABLE notes (
    note_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    content TEXT NOT NULL,
    note_type TEXT CHECK(note_type IN ('summary', 'method', 'experiment', 'limitation', 'idea', 'other')),
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE concepts (
    concept_id INTEGER PRIMARY KEY AUTOINCREMENT,
    concept_name TEXT NOT NULL UNIQUE,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE note_concepts (
    note_id INTEGER NOT NULL,
    concept_id INTEGER NOT NULL,
    confidence REAL DEFAULT 1.0,
    source TEXT DEFAULT 'manual',
    PRIMARY KEY (note_id, concept_id),
    FOREIGN KEY (note_id) REFERENCES notes(note_id),
    FOREIGN KEY (concept_id) REFERENCES concepts(concept_id)
);

CREATE TABLE note_links (
    source_note_id INTEGER NOT NULL,
    target_note_id INTEGER NOT NULL,
    link_type TEXT DEFAULT 'manual',
    confidence REAL DEFAULT 1.0,
    PRIMARY KEY (source_note_id, target_note_id),
    FOREIGN KEY (source_note_id) REFERENCES notes(note_id),
    FOREIGN KEY (target_note_id) REFERENCES notes(note_id)
);
```

## 7.7 论文关系与 AI 推荐表

```sql
CREATE TABLE paper_relations (
    relation_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_paper_id INTEGER NOT NULL,
    target_paper_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL
        CHECK(relation_type IN (
            'cites', 'same_topic', 'method_related', 'extends',
            'improves', 'compares_with', 'contradicts',
            'baseline_of', 'uses_method_of'
        )),
    weight REAL DEFAULT 1.0,
    description TEXT,
    generated_by TEXT DEFAULT 'user',
    confidence REAL DEFAULT 1.0,
    is_confirmed BOOLEAN DEFAULT 1,
    created_by INTEGER,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (target_paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (created_by) REFERENCES users(user_id)
);

CREATE TABLE ai_tag_suggestions (
    suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    paper_id INTEGER NOT NULL,
    tag_name TEXT NOT NULL,
    confidence REAL,
    reason TEXT,
    model_name TEXT DEFAULT 'tfidf',
    is_accepted BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id)
);

CREATE TABLE paper_similarity (
    source_paper_id INTEGER NOT NULL,
    target_paper_id INTEGER NOT NULL,
    similarity_score REAL NOT NULL,
    method TEXT DEFAULT 'tfidf_cosine',
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    PRIMARY KEY (source_paper_id, target_paper_id),
    FOREIGN KEY (source_paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (target_paper_id) REFERENCES papers(paper_id)
);

CREATE TABLE ai_relation_suggestions (
    suggestion_id INTEGER PRIMARY KEY AUTOINCREMENT,
    source_paper_id INTEGER NOT NULL,
    target_paper_id INTEGER NOT NULL,
    relation_type TEXT NOT NULL,
    confidence REAL,
    reason TEXT,
    is_accepted BOOLEAN DEFAULT 0,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (source_paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (target_paper_id) REFERENCES papers(paper_id)
);
```

## 7.8 阅读任务与评论表

```sql
CREATE TABLE reading_tasks (
    task_id INTEGER PRIMARY KEY AUTOINCREMENT,
    project_id INTEGER NOT NULL,
    paper_id INTEGER NOT NULL,
    assigned_by INTEGER NOT NULL,
    title TEXT NOT NULL,
    task_description TEXT,
    deadline DATE,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (project_id) REFERENCES projects(project_id),
    FOREIGN KEY (paper_id) REFERENCES papers(paper_id),
    FOREIGN KEY (assigned_by) REFERENCES users(user_id)
);

CREATE TABLE task_assignments (
    task_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    status TEXT DEFAULT 'todo'
        CHECK(status IN ('todo', 'reading', 'done', 'reported')),
    finished_at DATETIME,
    PRIMARY KEY (task_id, user_id),
    FOREIGN KEY (task_id) REFERENCES reading_tasks(task_id),
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE comments (
    comment_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    target_type TEXT NOT NULL CHECK(target_type IN ('paper', 'note', 'task')),
    target_id INTEGER NOT NULL,
    content TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);

CREATE TABLE activity_logs (
    log_id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    action_type TEXT NOT NULL,
    target_type TEXT,
    target_id INTEGER,
    description TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(user_id)
);
```

---

# 8. 视图、索引、触发器与事务要求

## 8.1 必须实现的视图

### 论文详情视图

```sql
CREATE VIEW paper_detail_view AS
SELECT 
    p.paper_id,
    p.title,
    p.year,
    p.abstract,
    v.venue_name,
    GROUP_CONCAT(DISTINCT a.author_name) AS authors,
    GROUP_CONCAT(DISTINCT t.tag_name) AS tags
FROM papers p
LEFT JOIN venues v ON p.venue_id = v.venue_id
LEFT JOIN paper_authors pa ON p.paper_id = pa.paper_id
LEFT JOIN authors a ON pa.author_id = a.author_id
LEFT JOIN paper_tags pt ON p.paper_id = pt.paper_id
LEFT JOIN tags t ON pt.tag_id = t.tag_id
GROUP BY p.paper_id;
```

### 项目任务进度视图

```sql
CREATE VIEW project_task_progress_view AS
SELECT 
    p.project_id,
    p.project_name,
    u.username,
    COUNT(ta.task_id) AS total_tasks,
    SUM(CASE WHEN ta.status IN ('done', 'reported') THEN 1 ELSE 0 END) AS finished_tasks
FROM projects p
JOIN reading_tasks rt ON p.project_id = rt.project_id
JOIN task_assignments ta ON rt.task_id = ta.task_id
JOIN users u ON ta.user_id = u.user_id
GROUP BY p.project_id, u.user_id;
```

## 8.2 必须实现的索引

```sql
CREATE INDEX idx_papers_title ON papers(title);
CREATE INDEX idx_papers_year ON papers(year);
CREATE INDEX idx_paper_tags_tag_id ON paper_tags(tag_id);
CREATE INDEX idx_paper_authors_author_id ON paper_authors(author_id);
CREATE INDEX idx_relations_source ON paper_relations(source_paper_id);
CREATE INDEX idx_relations_target ON paper_relations(target_paper_id);
CREATE INDEX idx_notes_paper_id ON notes(paper_id);
```

## 8.3 必须实现的触发器

### 自动更新论文修改时间

```sql
CREATE TRIGGER trg_update_paper_timestamp
AFTER UPDATE ON papers
FOR EACH ROW
BEGIN
    UPDATE papers
    SET updated_at = CURRENT_TIMESTAMP
    WHERE paper_id = OLD.paper_id;
END;
```

### 任务完成后写入活动日志

```sql
CREATE TRIGGER trg_task_done_log
AFTER UPDATE ON task_assignments
FOR EACH ROW
WHEN NEW.status = 'done'
BEGIN
    INSERT INTO activity_logs(user_id, action_type, target_type, target_id, description)
    VALUES(
        NEW.user_id,
        'TASK_DONE',
        'task',
        NEW.task_id,
        'User completed a reading task'
    );
END;
```

## 8.4 必须展示的事务

BibTeX 导入时需要使用事务：

```text
1. 插入 papers
2. 插入 venues
3. 插入 authors
4. 插入 paper_authors
5. 插入 bibtex_entries
6. 插入 activity_logs
```

要求：

```text
任一步失败，全部回滚
全部成功，统一提交
```

---

# 9. 后端 API 需求

## 9.1 文献管理 API

```text
GET    /api/papers
POST   /api/papers
GET    /api/papers/{paper_id}
PUT    /api/papers/{paper_id}
DELETE /api/papers/{paper_id}

GET    /api/authors
POST   /api/authors
GET    /api/tags
POST   /api/tags
POST   /api/papers/{paper_id}/tags
DELETE /api/papers/{paper_id}/tags/{tag_id}

POST   /api/import/bibtex
POST   /api/papers/{paper_id}/attachments
GET    /api/papers/{paper_id}/attachments
```

## 9.2 笔记 API

```text
GET    /api/notes
POST   /api/notes
GET    /api/notes/{note_id}
PUT    /api/notes/{note_id}
DELETE /api/notes/{note_id}

POST   /api/notes/{note_id}/parse-links
GET    /api/notes/{note_id}/backlinks
GET    /api/papers/{paper_id}/notes
GET    /api/concepts
GET    /api/concepts/{concept_id}
GET    /api/concepts/{concept_id}/notes
```

## 9.3 AI API

```text
POST /api/ai/tag-suggestions/{paper_id}
GET  /api/ai/tag-suggestions/{paper_id}
POST /api/ai/tag-suggestions/{suggestion_id}/accept

POST /api/ai/similarity/{paper_id}
GET  /api/ai/similarity/{paper_id}

POST /api/ai/relation-suggestions/{paper_id}
GET  /api/ai/relation-suggestions/{paper_id}
POST /api/ai/relation-suggestions/{suggestion_id}/accept

POST /api/ai/clusters
GET  /api/ai/clusters/{project_id}
```

## 9.4 项目协作 API

```text
POST /api/login

GET    /api/projects
POST   /api/projects
GET    /api/projects/{project_id}
PUT    /api/projects/{project_id}
DELETE /api/projects/{project_id}

GET  /api/projects/{project_id}/members
POST /api/projects/{project_id}/members

GET    /api/tasks
POST   /api/tasks
GET    /api/tasks/{task_id}
PUT    /api/tasks/{task_id}
DELETE /api/tasks/{task_id}
PUT    /api/tasks/{task_id}/status

POST /api/comments
GET  /api/comments
```

## 9.5 图谱 API

```text
GET /api/graph
GET /api/graph/project/{project_id}
GET /api/graph/paper/{paper_id}
GET /api/graph/concept/{concept_id}
```

图谱 API 返回格式：

```json
{
  "nodes": [
    {
      "id": "paper_1",
      "label": "AnyFlow",
      "type": "paper",
      "data": {
        "year": 2025,
        "venue": "arXiv"
      }
    },
    {
      "id": "tag_1",
      "label": "Flow Matching",
      "type": "tag"
    }
  ],
  "edges": [
    {
      "id": "edge_1",
      "source": "paper_1",
      "target": "tag_1",
      "type": "has_tag",
      "weight": 1.0
    }
  ]
}
```

---

# 10. 前端页面结构

```text
/
├── /login
├── /dashboard
├── /papers
├── /papers/:id
├── /import/bibtex
├── /notes
├── /notes/:id
├── /concepts
├── /concepts/:id
├── /ai
├── /projects
├── /projects/:id
├── /tasks
└── /graph
```

## 10.1 页面优先级

必须完成：

```text
/login
/dashboard
/papers
/papers/:id
/notes/:id
/ai
/tasks
/graph
```

可以后续完善：

```text
/concepts
/projects/:id
/import/bibtex
```

---

# 11. 系统演示流程

最终答辩建议使用下面的完整流程：

```text
1. 用户登录系统
2. 创建科研项目
3. 导入一篇 BibTeX 论文
4. 上传 PDF 附件
5. 查看论文详情
6. 为论文添加 Markdown 阅读笔记
7. 在笔记中输入 [[Flow Matching]] 和 [[DMD2]]
8. 系统解析双链并生成概念节点
9. 运行 AI 标签推荐
10. 接受 AI 推荐标签
11. 运行相似论文推荐
12. 接受 AI 推荐关系边
13. 给成员分配阅读任务
14. 成员更新任务状态
15. 打开知识图谱页面
16. 展示论文、作者、标签、笔记、概念、关系边
```

---

# 12. 四人分工

| 成员 | 模块                 | 主要产出                       |
| -- | ------------------ | -------------------------- |
| A  | Zotero-like 文献管理   | 论文、作者、标签、BibTeX、附件、论文详情页   |
| B  | Obsidian-like 笔记双链 | Markdown 编辑、双链解析、概念卡片、反向链接 |
| C  | AI 科研分析            | 自动标签、相似论文推荐、AI 补边、主题聚类     |
| D  | 协作与知识图谱            | 用户项目、阅读任务、评论、知识图谱可视化、系统集成  |

每位成员都需要提交：

```text
1. 负责的数据表
2. 负责的后端接口
3. 负责的前端页面
4. 负责的复杂 SQL
5. 功能测试截图
6. 报告对应章节
7. PPT 展示页
```

---

# 13. 项目目录结构

```text
research-graph/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models/
│   │   ├── paper.py
│   │   ├── note.py
│   │   ├── ai.py
│   │   └── project.py
│   ├── schemas/
│   │   ├── paper.py
│   │   ├── note.py
│   │   ├── ai.py
│   │   └── project.py
│   ├── routers/
│   │   ├── papers.py
│   │   ├── notes.py
│   │   ├── ai.py
│   │   ├── graph.py
│   │   └── projects.py
│   ├── services/
│   │   ├── bibtex_service.py
│   │   ├── note_parser.py
│   │   ├── ai_service.py
│   │   └── graph_service.py
│   ├── storage/
│   │   ├── pdf/
│   │   └── bibtex/
│   ├── scripts/
│   │   ├── init_db.sql
│   │   └── seed_data.sql
│   ├── requirements.txt
│   └── research_graph.db
│
├── frontend/
│   ├── src/
│   │   ├── views/
│   │   │   ├── Login.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── PaperList.vue
│   │   │   ├── PaperDetail.vue
│   │   │   ├── NoteEditor.vue
│   │   │   ├── AIAnalysis.vue
│   │   │   ├── GraphView.vue
│   │   │   ├── ProjectDashboard.vue
│   │   │   └── TaskList.vue
│   │   ├── components/
│   │   │   ├── PaperForm.vue
│   │   │   ├── TagSelector.vue
│   │   │   ├── GraphPanel.vue
│   │   │   └── MarkdownEditor.vue
│   │   ├── api/
│   │   │   ├── papers.js
│   │   │   ├── notes.js
│   │   │   ├── ai.js
│   │   │   └── graph.js
│   │   ├── router/
│   │   └── main.js
│   └── package.json
│
├── docs/
│   ├── requirements.md
│   ├── er_diagram.drawio
│   ├── api_design.md
│   ├── sql_queries.md
│   └── report_outline.md
│
└── README.md
```

---

# 14. AI 编程助手开发提示词

下面这些可以直接给 Codex / Claude Code 使用。

## 14.1 总体开发提示词

```text
请根据以下需求实现一个名为 ResearchGraph 的本地科研论文管理与知识图谱协作系统。

技术栈：
- 前端：Vue3 + Vite + Element Plus + Axios + Cytoscape.js
- 后端：FastAPI + SQLAlchemy + SQLite
- AI：scikit-learn 实现 TF-IDF + cosine similarity
- 文件存储：本地 storage/pdf 和 storage/bibtex

系统包含四个模块：
1. Zotero-like 文献管理：论文、作者、会议、标签、BibTeX、PDF 附件；
2. Obsidian-like 笔记双链：Markdown 笔记、[[双链]] 解析、概念卡片、反向链接；
3. AI 科研分析：自动标签推荐、相似论文推荐、AI 关系补边；
4. 科研协作与知识图谱：项目、成员、阅读任务、评论、Cytoscape.js 图谱可视化。

请先生成完整的项目目录结构，然后实现后端数据库模型、API 路由、前端页面和基础联调。
要求代码清晰、可运行、模块化，不要一次性写成单个巨大文件。
```

## 14.2 后端开发提示词

```text
请为 ResearchGraph 项目实现 FastAPI 后端。

要求：
1. 使用 SQLAlchemy 定义数据库模型；
2. 使用 SQLite 作为数据库；
3. 按 models、schemas、routers、services 分层；
4. 实现 papers、notes、ai、projects、graph 五组路由；
5. 支持 CORS，允许 Vue 前端访问；
6. 提供 init_db 初始化逻辑；
7. 提供 seed_data 测试数据；
8. 文件上传保存到 storage/pdf 或 storage/bibtex；
9. BibTeX 使用 bibtexparser 解析；
10. AI 模块使用 scikit-learn 的 TfidfVectorizer 和 cosine_similarity；
11. 图谱接口返回 nodes 和 edges JSON；
12. 代码应包含必要的错误处理。
```

## 14.3 前端开发提示词

```text
请为 ResearchGraph 项目实现 Vue3 + Vite 前端。

要求：
1. 使用 Element Plus 搭建管理系统界面；
2. 使用 Axios 调用 FastAPI 后端；
3. 使用 Vue Router 管理页面；
4. 实现页面：
   - Login.vue
   - Dashboard.vue
   - PaperList.vue
   - PaperDetail.vue
   - NoteEditor.vue
   - AIAnalysis.vue
   - TaskList.vue
   - GraphView.vue
5. PaperList 支持搜索、筛选、分页；
6. PaperDetail 显示论文元数据、作者、标签、笔记、附件；
7. NoteEditor 支持 Markdown 编辑和保存；
8. AIAnalysis 显示 AI 推荐标签、相似论文、推荐关系，并支持确认；
9. GraphView 使用 Cytoscape.js 渲染知识图谱；
10. 页面风格简洁，适合课程项目展示。
```

## 14.4 AI 模块开发提示词

```text
请实现 ResearchGraph 的 AI 分析模块。

功能：
1. 自动标签推荐：
   - 输入 paper_id；
   - 读取论文 title 和 abstract；
   - 使用 TF-IDF 提取关键词；
   - 与已有 tags 匹配；
   - 写入 ai_tag_suggestions 表。

2. 相似论文推荐：
   - 输入 paper_id；
   - 读取所有论文的 title + abstract；
   - 使用 TfidfVectorizer 生成向量；
   - 使用 cosine_similarity 计算当前论文与其他论文的相似度；
   - 返回 Top-k；
   - 写入 paper_similarity 表。

3. 关系补边推荐：
   - 根据相似度分数和标签重合度推荐 relation_type；
   - 关系类型包括 same_topic、method_related、possible_baseline、compares_with；
   - 写入 ai_relation_suggestions 表；
   - 用户接受后写入 paper_relations 表。

要求：
- 不调用外部大模型；
- 保持算法可解释；
- 返回推荐原因 reason；
- 提供对应 API。
```

## 14.5 知识图谱模块开发提示词

```text
请实现 ResearchGraph 的知识图谱模块。

后端要求：
1. 提供 GET /api/graph 接口；
2. 从 papers、authors、tags、notes、concepts、paper_relations 等表中生成图谱；
3. 返回格式为：
{
  "nodes": [
    {"id": "paper_1", "label": "...", "type": "paper"}
  ],
  "edges": [
    {"id": "edge_1", "source": "paper_1", "target": "tag_1", "type": "has_tag"}
  ]
}
4. 支持按 project_id、paper_id、node_type、edge_type 筛选。

前端要求：
1. 使用 Cytoscape.js 渲染图谱；
2. 不同节点类型使用不同形状或颜色；
3. 支持拖拽、缩放、点击节点查看详情；
4. 支持按节点类型和边类型筛选；
5. 支持搜索节点并高亮邻居。
```

---

# 15. 验收标准

## 15.1 基础验收

系统需要能够完成：

```text
1. 成功启动后端 FastAPI；
2. 成功启动前端 Vue；
3. 前端能够访问后端接口；
4. 数据库能够正确创建表；
5. 能够添加、编辑、删除、查询论文；
6. 能够导入 BibTeX；
7. 能够上传 PDF 附件；
8. 能够创建 Markdown 笔记；
9. 能够解析 [[双链]]；
10. 能够生成 AI 推荐标签；
11. 能够推荐相似论文；
12. 能够确认 AI 推荐关系；
13. 能够创建阅读任务；
14. 能够展示知识图谱。
```

## 15.2 数据库验收

必须包含：

```text
不少于 15 张数据表
至少 3 个多对多关系
至少 2 个自关联结构
至少 2 个视图
至少 2 个触发器
至少 6 条复杂 SQL 查询
至少 5 个索引
至少 1 个事务场景
```

## 15.3 展示验收

答辩时必须展示：

```text
1. ER 图
2. 系统功能模块图
3. 数据库表结构
4. 核心 SQL 查询结果
5. BibTeX 导入流程
6. Markdown 双链解析流程
7. AI 推荐标签流程
8. 相似论文推荐流程
9. 阅读任务协作流程
10. 知识图谱可视化效果
```

---

# 16. 推荐开发顺序

```text
第 1 步：搭建 FastAPI + SQLite + Vue3 基础框架
第 2 步：完成 papers、authors、tags 基础 CRUD
第 3 步：完成 BibTeX 导入和 PDF 上传
第 4 步：完成 notes、concepts、note_links
第 5 步：完成 AI 标签推荐和相似论文推荐
第 6 步：完成 paper_relations 和 AI 补边确认
第 7 步：完成 projects、tasks、comments
第 8 步：完成 graph API
第 9 步：完成 Cytoscape.js 前端图谱
第 10 步：准备测试数据、报告截图和 PPT 演示
```

---

# 17. 最小可行版本范围

时间不足时，优先实现以下内容：

```text
1. 论文 CRUD
2. 作者与标签管理
3. BibTeX 导入
4. Markdown 笔记
5. [[双链]] 解析
6. AI 标签推荐
7. 相似论文推荐
8. 知识图谱展示
```

可以简化：

```text
用户权限
评论系统
任务复杂状态流转
Related Work 聚类
PDF 在线预览
```

---

# 18. 报告结构建议

```text
1. 绪论
   1.1 选题背景
   1.2 系统目标
   1.3 创新点

2. 需求分析
   2.1 用户角色分析
   2.2 文献管理需求
   2.3 双链笔记需求
   2.4 AI 分析需求
   2.5 科研协作需求

3. 数据库设计
   3.1 概念结构设计 ER 图
   3.2 逻辑结构设计
   3.3 表结构设计
   3.4 主键、外键与约束
   3.5 视图、索引、触发器设计

4. 系统实现
   4.1 系统架构
   4.2 文献管理模块
   4.3 双链笔记模块
   4.4 AI 分析模块
   4.5 协作与知识图谱模块

5. SQL 查询与数据库特性
   5.1 多表连接查询
   5.2 聚合统计查询
   5.3 自关联查询
   5.4 事务实现
   5.5 触发器实现
   5.6 索引优化

6. 系统测试与展示
   6.1 测试数据
   6.2 功能测试
   6.3 查询结果截图
   6.4 系统界面截图

7. 小组分工

8. 总结与展望
```


