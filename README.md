# EduAgent - 多模态教育AI助手平台

<div align="center">

![EduAgent Logo](https://img.shields.io/badge/EduAgent-v1.0.0-brightgreen)
![Python](https://img.shields.io/badge/Python-3.9+-blue)
![Vue](https://img.shields.io/badge/Vue-3.4+-green)
![FastAPI](https://img.shields.io/badge/FastAPI-0.104+-teal)
![LightRAG](https://img.shields.io/badge/LightRAG-Enabled-orange)

**智能作业批改 | 知识图谱 | 多空间知识库 | AI问答**

[English](README_EN.md) | 简体中文

</div>

---

## 📚 目录

- [项目简介](#-项目简介)
- [核心功能](#-核心功能)
- [技术栈](#️-技术栈)
- [快速开始](#-快速开始)
- [详细安装步骤](#-详细安装步骤)
- [配置说明](#️-配置说明)
- [使用指南](#-使用指南)
- [API文档](#-api文档)
- [常见问题](#-常见问题)
- [项目结构](#-项目结构)
- [开发建议](#-开发建议)

---

## 🎯 项目简介

EduAgent是一个基于AI的多模态教育助手平台,集成了作业智能批改、知识图谱构建、多空间知识库管理等功能。通过LightRAG技术提供精准的知识检索和智能问答服务。

### 主要特性

- 🤖 **AI作业批改**: 支持图片上传,自动识别错误并提供详细分析
- 📊 **知识图谱**: 可视化知识点关系和学习路径
- 🗂️ **多空间知识库**: 独立的知识空间管理,支持课程分类
- 💡 **智能问答**: 基于LightRAG的混合检索模式(naive/local/global/hybrid)
- 📝 **文档处理**: 支持txt, md, pdf, docx等多种格式
- 🔐 **用户管理**: JWT认证,角色权限控制

---

## 🚀 核心功能

### 1. 作业批改系统
- 📸 上传作业照片(支持自动纠偏)
- 🔍 AI自动识别错题和知识点
- 📋 生成详细的错误分析报告
- 📈 追踪学习进度和薄弱环节

### 2. 知识库管理
- 📚 创建多个独立知识空间
- 📄 批量上传文档到指定空间
- 🔎 跨空间或指定空间检索
- 🗑️ 灵活的文档管理(增删改查)

### 3. 智能问答
- 💬 基于LightRAG的语义检索
- 🎯 四种检索模式可选
- 📌 引用来源追踪
- 🌐 支持多语言

---

## 🛠️ 技术栈

### 后端
- **框架**: FastAPI 0.104.1
- **数据库**: SQLite (异步 SQLAlchemy)
- **AI集成**: SiliconFlow API (Qwen系列模型)
- **知识检索**: LightRAG (知识图谱RAG)
- **嵌入模型**: Qwen3-Embedding-4B (2560维)
- **LLM模型**: Qwen3-Next-80B-A3B-Instruct (80B参数, 3B激活)
- **图像处理**: OpenCV, Pillow
- **认证**: JWT (python-jose)

### 前端
- **框架**: Vue 3.4 + TypeScript
- **UI库**: Naive UI 2.37
- **状态管理**: Pinia
- **路由**: Vue Router 4.2
- **HTTP客户端**: Axios
- **图标**: Lucide Vue Next
- **构建工具**: Vite 5.0

---

## ⚡ 快速开始

### 前置要求

- **Python**: 3.9 或更高版本
- **Node.js**: 16.x 或更高版本
- **npm**: 8.x 或更高版本
- **Git**: 用于克隆仓库

### 一键启动

```bash
# 克隆项目
git clone <repository-url>
cd EduAgent

# 启动后端(终端1)
cd backend
pip install -r requirements.txt
pip install lightrag-hku nest-asyncio PyMuPDF python-docx
python main.py

# 启动前端(终端2,新开一个终端)
cd frontend
npm install
npm run dev
```

访问 **http://localhost:3001** 开始使用!

---

## 📦 详细安装步骤

### 步骤 1: 后端安装

```bash
# 进入后端目录
cd backend

# 创建虚拟环境(推荐)
python -m venv venv

# 激活虚拟环境
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# 安装依赖
pip install -r requirements.txt

# 安装LightRAG(可选,用于知识库功能)
pip install lightrag-hku

# 安装nest-asyncio(修复异步事件循环问题)
pip install nest-asyncio

# 额外依赖(PDF/DOCX支持)
pip install PyMuPDF python-docx
```

### 步骤 2: 前端安装

```bash
# 进入前端目录
cd frontend

# 安装依赖
npm install

# 或使用yarn
yarn install

# 或使用pnpm
pnpm install
```

### 步骤 3: 配置环境变量

在`backend/`目录下创建`.env`文件:

```env
# API密钥(必需)
SILICONFLOW_API_KEY=your_siliconflow_api_key_here
# 可选: 如果使用其他AI功能
OPENROUTER_API_KEY=your_openrouter_api_key_here

# JWT密钥(建议修改)
SECRET_KEY=your_secret_key_here_change_in_production

# 数据库(默认SQLite)
DATABASE_URL=sqlite+aiosqlite:///./eduagent.db

# 上传目录
UPLOAD_DIR=./uploads

# CORS设置(可选)
BACKEND_CORS_ORIGINS=http://localhost:3001,http://127.0.0.1:3001
```

**重要**:
- `SILICONFLOW_API_KEY`: 用于知识库的嵌入和LLM功能 (必需)
  - 嵌入模型: `Qwen/Qwen3-Embedding-4B` (2560维向量)
  - LLM模型: `Qwen/Qwen3-Next-80B-A3B-Instruct` (80B参数, 3B激活)
- `SECRET_KEY`: 生产环境必须使用强随机密钥

### 步骤 4: 启动服务

#### 启动后端服务器

```bash
cd backend
python main.py
```

**预期输出**:
```
INFO:     Started server process [xxxxx]
INFO:     Waiting for application startup.
INFO:     Application startup complete.
INFO:     Uvicorn running on http://0.0.0.0:8000 (Press CTRL+C to quit)
```

后端API将运行在: **http://localhost:8000**
API文档: **http://localhost:8000/docs**

#### 启动前端开发服务器

```bash
cd frontend
npm run dev
```

**预期输出**:
```
VITE v5.x.x  ready in xxx ms

➜  Local:   http://localhost:3001/
➜  Network: use --host to expose
➜  press h to show help
```

前端应用将运行在: **http://localhost:3001**

---

## ⚙️ 配置说明

### 后端配置 (`backend/app/core/config.py`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `PROJECT_NAME` | 项目名称 | `"EduAgent"` |
| `VERSION` | 版本号 | `"1.0.0"` |
| `API_V1_STR` | API路径前缀 | `"/api/v1"` |
| `SECRET_KEY` | JWT密钥 | `"changethis"` ⚠️ |
| `ACCESS_TOKEN_EXPIRE_MINUTES` | Token过期时间(分钟) | `11520` (8天) |
| `DATABASE_URL` | 数据库连接 | `"sqlite+aiosqlite:///./eduagent.db"` |
| `OPENROUTER_API_KEY` | OpenRouter API密钥 | 需配置 |
| `DEFAULT_MODEL` | 默认AI模型 | `"x-ai/grok-4-fast:free"` |
| `UPLOAD_DIR` | 文件上传目录 | `"./uploads"` |
| `MAX_UPLOAD_SIZE` | 最大上传大小 | `10MB` |

### 前端配置 (`frontend/vite.config.ts`)

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `server.port` | 开发服务器端口 | `3001` |
| `server.host` | 绑定地址 | `"0.0.0.0"` |
| `proxy.'/api'` | API代理目标 | `"http://localhost:8000"` |

---

## 📖 使用指南

### 1. 用户注册与登录

1. 访问 http://localhost:3001
2. 点击"注册"创建新账户
3. 填写邮箱和密码完成注册
4. 使用账户登录系统

### 2. 上传作业进行批改

1. 进入"作业"页面
2. 点击"上传作业"
3. 选择作业图片(JPG/PNG格式)
4. (可选)输入课程名称
5. 提交后等待AI分析
6. 查看详细的批改报告

### 3. 管理知识库

#### 创建知识空间

1. 进入"知识库"页面
2. 点击"New Space"按钮
3. 输入空间名称(如"数学课程"、"物理实验")
4. 点击"Create Space"

#### 上传文档

1. 选择目标知识空间
2. 点击"Upload Document"
3. 选择文件(.txt/.md/.pdf/.docx)
4. (可选)填写标题和课程名称
5. 上传完成后文档会自动索引

#### 查询知识

1. 在搜索框输入问题
2. 选择检索模式:
   - **naive**: 简单匹配
   - **local**: 本地实体检索
   - **global**: 全局知识图谱
   - **hybrid**: 混合模式(推荐)
3. 查看答案和引用来源

### 4. 查看知识图谱

1. 进入"知识图谱"页面
2. 查看实体关系可视化
3. 探索知识点之间的连接

---

## 📡 API文档

### 认证相关

#### POST `/api/auth/register`
注册新用户

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123",
  "confirm_password": "password123",
  "full_name": "张三"
}
```

#### POST `/api/auth/test-login`
用户登录(开发用)

**请求体**:
```json
{
  "email": "user@example.com",
  "password": "password123"
}
```

**响应**:
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "user_id": 1,
  "email": "user@example.com",
  "role": "user",
  "name": "张三"
}
```

### 知识库相关

#### GET `/api/knowledge/spaces`
获取所有知识空间

**响应**:
```json
[
  {
    "space_name": "default",
    "lightrag_available": true,
    "total_documents": 5,
    "document_types": {
      "application/pdf": 3,
      "text/markdown": 2
    },
    "total_content_length": 125000
  }
]
```

#### POST `/api/knowledge/query?space_name=default`
查询知识库

**请求体**:
```json
{
  "question": "什么是二次函数?",
  "mode": "hybrid"
}
```

**响应**:
```json
{
  "question": "什么是二次函数?",
  "answer": "二次函数是形如 f(x) = ax² + bx + c (a≠0) 的函数...",
  "sources": ["数学教材.pdf", "代数基础.md"],
  "mode": "hybrid"
}
```

#### POST `/api/knowledge/upload-document?space_name=default`
上传文档到知识库

**请求**: multipart/form-data
- `file`: 文件
- `title`: 标题(可选)
- `course_name`: 课程名(可选)

**响应**:
```json
{
  "success": true,
  "message": "Document 'math_basics' added to knowledge space 'default' successfully",
  "filename": "math_basics.pdf",
  "doc_type": "application/pdf",
  "content_length": 45678,
  "lightrag_available": true
}
```

完整API文档访问: **http://localhost:8000/docs**

---

## ❓ 常见问题

### Q1: 后端启动报错 `ModuleNotFoundError: No module named 'lightrag'`

**解决方案**:
```bash
pip install lightrag-hku
```

### Q2: 前端报错 `Error: connect ECONNREFUSED 127.0.0.1:8000`

**原因**: 后端服务未启动

**解决方案**:
1. 确保后端服务在运行: `cd backend && python main.py`
2. 检查端口8000是否被占用

### Q3: CORS跨域错误

**解决方案**:
在`backend/app/core/config.py`中已添加3001端口,如仍有问题:
```python
BACKEND_CORS_ORIGINS: List[str] = [
    "http://localhost:3001",
    "http://127.0.0.1:3001",
]
```

### Q4: LightRAG查询失败 `RuntimeError: asyncio.run() cannot be called from a running event loop`

**解决方案**:
```bash
pip install nest-asyncio
```
已在最新版本中修复。

### Q5: 文档上传后无法查询或LightRAG初始化失败

**症状**:
- 控制台显示: `[RAG Init] ❌ LightRAG initialization failed`
- 或显示: `Invalid model_name: gpt-4o-mini`

**解决方案**:
1. **配置SiliconFlow API密钥** (必需):
```bash
# 在backend/.env文件中添加
SILICONFLOW_API_KEY=your_api_key_here
```

2. **安装必需依赖**:
```bash
pip install nest-asyncio httpx
```

3. **验证配置**:
```bash
cd backend
python test_siliconflow_integration.py
```

4. **检查模型配置**:
   - 嵌入模型: `Qwen/Qwen3-Embedding-4B` (2560维)
   - LLM模型: `Qwen/Qwen3-Next-80B-A3B-Instruct`
   - Tokenizer: 已修复为 `gpt-4` (兼容模式)

**成功日志示例**:
```
[RAG Init] Creating LightRAG instance with SiliconFlow embeddings...
[RAG Init] ✅ LightRAG instance created successfully for space 'default'
```

### Q6: 如何重置数据库?

```bash
cd backend
rm eduagent.db
python main.py  # 会自动创建新数据库
```

### Q7: PDF文档无法解析

**解决方案**:
```bash
pip install PyMuPDF  # 或 pip install fitz
```

### Q8: DOCX文档无法解析

**解决方案**:
```bash
pip install python-docx
```

### Q9: 知识空间切换后文档没有更新

**已修复**: 最新版本已支持空间切换时自动刷新文档列表。如果仍有问题,请刷新页面。

### Q10: Windows上运行报编码错误

**解决方案**:
```bash
# 设置环境变量
set PYTHONIOENCODING=utf-8
python main.py
```

---

## 📁 项目结构

```
EduAgent/
├── backend/                    # 后端代码
│   ├── main.py                # 入口文件
│   ├── requirements.txt       # Python依赖
│   ├── app/
│   │   ├── api/              # API路由
│   │   │   └── api_v1/
│   │   │       ├── api.py    # 路由聚合
│   │   │       └── endpoints/
│   │   │           ├── auth.py          # 认证端点
│   │   │           ├── assignments.py   # 作业端点
│   │   │           ├── knowledge.py     # 知识库端点
│   │   │           └── users.py         # 用户端点
│   │   ├── core/             # 核心配置
│   │   │   ├── config.py     # 配置管理
│   │   │   ├── security.py   # 安全工具
│   │   │   └── deps.py       # 依赖注入
│   │   ├── models/           # 数据库模型
│   │   │   ├── user.py
│   │   │   ├── assignment.py
│   │   │   └── course.py
│   │   ├── schemas/          # Pydantic模式
│   │   ├── services/         # 业务逻辑
│   │   │   ├── knowledge_base.py      # LightRAG集成
│   │   │   ├── assignment_workflow.py # 作业处理
│   │   │   └── doc_scanner.py         # 文档扫描
│   │   ├── agents/           # AI Agent
│   │   │   ├── multimodal_agent.py
│   │   │   └── course_analysis_agent.py
│   │   └── db/               # 数据库连接
│   ├── uploads/              # 文件上传目录
│   │   └── knowledge_spaces/ # 多空间知识库
│   │       ├── default/
│   │       └── [custom_spaces]/
│   └── eduagent.db           # SQLite数据库
│
├── frontend/                  # 前端代码
│   ├── package.json          # npm配置
│   ├── vite.config.ts        # Vite配置
│   ├── tsconfig.json         # TypeScript配置
│   ├── src/
│   │   ├── main.ts           # 入口文件
│   │   ├── App.vue           # 根组件
│   │   ├── router/           # 路由配置
│   │   │   └── index.ts
│   │   ├── stores/           # Pinia状态管理
│   │   │   └── auth.ts       # 认证状态
│   │   ├── services/         # API服务
│   │   │   └── api.ts        # Axios实例
│   │   ├── views/            # 页面组件
│   │   │   ├── Home.vue
│   │   │   ├── Login.vue
│   │   │   ├── Register.vue
│   │   │   ├── Dashboard.vue
│   │   │   ├── Assignments.vue
│   │   │   ├── Knowledge.vue
│   │   │   └── KnowledgeGraph.vue
│   │   └── components/       # 可复用组件
│   └── public/               # 静态资源
│
├── CLAUDE.md                 # 项目开发指南
└── README.md                 # 本文档
```

---

## 🔧 开发建议

### 推荐的开发工具

- **IDE**: VSCode, PyCharm, WebStorm
- **VSCode插件**:
  - Python
  - Pylance
  - Vue Language Features (Volar)
  - TypeScript Vue Plugin (Volar)
  - ESLint
  - Prettier

### 代码风格

**后端**:
- 遵循PEP 8
- 使用类型提示(Type Hints)
- 异步函数优先使用`async/await`

**前端**:
- 使用TypeScript
- 遵循Vue 3 Composition API风格
- ESLint + Prettier自动格式化

### 调试技巧

**后端调试**:
```python
# 启用详细日志
import logging
logging.basicConfig(level=logging.DEBUG)
```

**前端调试**:
- 使用Vue DevTools浏览器扩展
- 查看Network标签检查API调用
- 使用`console.log`和断点调试

### 常用命令

```bash
# 后端
cd backend
python main.py                 # 启动服务
pip install -r requirements.txt  # 安装依赖
python -m pytest              # 运行测试(如有)

# 前端
cd frontend
npm run dev                   # 开发模式
npm run build                 # 构建生产版本
npm run preview               # 预览生产版本
npm run lint                  # 代码检查
npm run test                  # 运行测试
```

---

## 🚀 部署建议

### 生产环境部署

#### 后端部署

```bash
# 使用Gunicorn + Uvicorn
pip install gunicorn
gunicorn main:app -w 4 -k uvicorn.workers.UvicornWorker -b 0.0.0.0:8000

# 或直接使用Uvicorn
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

#### 前端部署

```bash
# 构建
npm run build

# 生成的dist目录可以部署到:
# - Nginx
# - Apache
# - Vercel
# - Netlify
# - 任何静态文件服务器
```

### 环境变量(生产)

```env
# 生产环境必须修改
SECRET_KEY=use_strong_random_key_here
OPENROUTER_API_KEY=your_production_key
SILICONFLOW_API_KEY=your_production_key

# 使用PostgreSQL(推荐)
DATABASE_URL=postgresql+asyncpg://user:pass@localhost/eduagent

# CORS(根据实际域名配置)
BACKEND_CORS_ORIGINS=https://yourdomain.com,https://www.yourdomain.com
```

---

## 🤝 贡献指南

欢迎贡献! 请遵循以下步骤:

1. Fork本仓库
2. 创建特性分支 (`git checkout -b feature/AmazingFeature`)
3. 提交更改 (`git commit -m 'Add some AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 开启Pull Request

### 提交规范

- `feat:` 新功能
- `fix:` Bug修复
- `docs:` 文档更新
- `style:` 代码格式调整
- `refactor:` 重构
- `test:` 测试相关
- `chore:` 构建/工具链调整

---

## 📄 许可证

本项目采用 MIT 许可证 - 详见 LICENSE 文件

---

## 📞 联系方式

- **问题反馈**: [GitHub Issues](https://github.com/your-repo/issues)
- **讨论交流**: [GitHub Discussions](https://github.com/your-repo/discussions)
- **Email**: your-email@example.com

---

## 🎉 致谢

- [FastAPI](https://fastapi.tiangolo.com/) - 现代化的Python Web框架
- [Vue 3](https://vuejs.org/) - 渐进式JavaScript框架
- [LightRAG](https://github.com/HKUDS/LightRAG) - 强大的知识图谱RAG引擎
- [SiliconFlow](https://siliconflow.cn/) - 硅基流动AI推理平台
- [Naive UI](https://www.naiveui.com/) - 优雅的Vue 3组件库
- [Qwen](https://github.com/QwenLM/Qwen) - 阿里通义千问大模型系列

---

## 📈 更新日志

### v1.1.0 (2025-01-XX) - SiliconFlow集成

#### ✨ 新功能
- ✅ **SiliconFlow API完整集成**
  - 嵌入模型: Qwen3-Embedding-4B (2560维向量)
  - LLM模型: Qwen3-Next-80B-A3B-Instruct (80B参数, 3B激活)
- ✅ **文档内容提取支持**
  - TXT/MD: UTF-8解码
  - PDF: PyMuPDF (fitz) + pdfplumber双引擎
  - DOCX: python-docx完整支持(段落+表格)
- ✅ **详细日志系统**
  - [Embedding], [LLM], [Document], [RAG Init], [FileProcess]前缀
  - 完整的调试信息输出

#### 🐛 Bug修复
- ✅ **修复LightRAG tokenizer错误**: `Invalid model_name: gpt-4o-mini`
  - 添加 `tiktoken_model_name="gpt-4"` 参数
- ✅ **修复embedding维度不匹配**: 8192 → 2560维
- ✅ **修复API endpoint从OpenRouter切换到SiliconFlow**
- ✅ **改进asyncio事件循环处理**: nest_asyncio + ThreadPoolExecutor

#### 🔧 优化
- ✅ 环境变量配置优化 (SILICONFLOW_API_KEY)
- ✅ 添加集成测试脚本 (test_siliconflow_integration.py)
- ✅ README文档全面更新 (API配置, 故障排查)
- ✅ 改进错误处理和fallback机制

### v1.0.0 (2025-01-XX) - 初始版本

#### ✨ 新功能
- ✅ 多空间知识库管理
- ✅ LightRAG知识检索集成
- ✅ 作业智能批改系统
- ✅ 用户认证与权限管理

#### 🐛 Bug修复
- ✅ 修复API端点重复定义问题
- ✅ 修复asyncio事件循环冲突
- ✅ 修复知识空间切换时文档不刷新
- ✅ 修复CORS配置缺失3001端口
- ✅ 优化多空间架构数据迁移逻辑
- ✅ 改进LightRAG错误处理

#### 🔧 优化
- ✅ API支持space_name查询参数
- ✅ 前端UI简化,移除冗余字段
- ✅ 文档上传参数统一命名

---

<div align="center">

**⭐ 如果这个项目对你有帮助,请给它一个Star! ⭐**

Made with ❤️ by EduAgent Team

</div>
