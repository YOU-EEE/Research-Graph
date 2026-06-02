**圣经**：https://chatgpt.com/share/6a1e89d9-1cac-83a5-91fc-5a97770c95f7

GPT给出的建议文件树：
```
research-graph/
├── backend/
│   ├── main.py
│   ├── database.py
│   ├── models.py
│   ├── schemas.py
│   ├── routers/
│   │   ├── papers.py
│   │   ├── notes.py
│   │   ├── ai.py
│   │   ├── graph.py
│   │   └── tasks.py
│   ├── services/
│   │   ├── note_parser.py
│   │   ├── ai_service.py
│   │   └── graph_service.py
│   ├── scripts/
│   │   ├── init_db.sql
│   │   └── seed_data.sql
│   ├── storage/
│   │   ├── pdf/
│   │   └── bibtex/
│   └── requirements.txt
│
├── frontend/
│   ├── src/
│   │   ├── api/
│   │   │   ├── papers.js
│   │   │   ├── notes.js
│   │   │   ├── ai.js
│   │   │   └── graph.js
│   │   ├── views/
│   │   │   ├── Dashboard.vue
│   │   │   ├── PaperList.vue
│   │   │   ├── PaperDetail.vue
│   │   │   ├── NoteEditor.vue
│   │   │   ├── AIAnalysis.vue
│   │   │   ├── GraphView.vue
│   │   │   └── TaskList.vue
│   │   ├── router/
│   │   │   └── index.js
│   │   ├── App.vue
│   │   └── main.js
│   └── package.json
│
├── docs/
│   ├── requirement.md
│   ├── er_diagram.drawio
│   ├── api_design.md
│   └── sql_queries.md
│
└── README.md
```

目前只完成了一个最初步的可以添加/删除/更改paper id的后端api，测试：
``` bash
cd backend
uvicorn main:app --reload 
```
