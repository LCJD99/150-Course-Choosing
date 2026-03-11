# 150团中学兴趣班选课系统

## 项目概述

这是一个基于 Vue 3 + FastAPI 的前后端分离选课系统，专为学校场景设计。

### 技术栈

**前端:**
- Vue 3 (Composition API)
- Vue Router 4
- Vite 6
- 原生 Fetch API

**后端:**
- FastAPI 0.109.0
- SQLAlchemy 2.0.25
- Alembic 1.13.1
- SQLite (WAL模式)

### 核心功能

#### 学生端
- 🔐 身份证 + 姓名登录
- 📚 四天选课（周一、周三、周四、周五）
- 🔄 即时选课/替换
- 📊 实时进度显示
- 🔒 选课开关控制

#### 管理端
- 📤 CSV 数据导入（课程、开设年级、学生）
- 📊 实时统计仪表盘
- 📋 课程管理
- ⚙️ 系统开关控制

### 安全特性
- 身份证号 SHA256 哈希存储
- JWT Token 认证
- 事务级容量控制
- 防超卖并发保护

## 快速开始

### 后端启动

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 前端启动

```bash
cd frontend
npm install
npm run dev
```

### 访问地址

- **前端**: http://localhost:5173
- **后端 API**: http://localhost:8000
- **API 文档**: http://localhost:8000/docs

## 项目结构

```
├── backend/                 # FastAPI 后端
│   ├── api/                # API 路由
│   ├── models/             # 数据库模型
│   ├── services/            # 业务逻辑
│   ├── alembic/            # 数据库迁移
│   ├── data/               # SQLite 数据库
│   └── main.py             # 应用入口
└── frontend/               # Vue 3 前端
    ├── src/
    │   ├── views/         # 页面组件
    │   ├── services/      # API 服务
    │   ├── stores/        # 状态管理
    │   └── router/        # 路由配置
    └── index.html         # HTML 入口
```

## 数据导入格式

### 课程表 (courses.csv)
```csv
course_id,course_name,teacher,capacity,day,bundle_id
C001,非遗剪纸与重彩画,李艳华,15,1,
C101A,机器人基础-上,张老师,30,1,B1001
C101B,机器人基础-下,张老师,30,4,B1001
```

字段说明：
- `bundle_id` 可选；为空表示普通单节课。
- 相同 `bundle_id` 表示组合课（需同时报名整组）。

校验规则：
- `course_id` 唯一。
- `capacity > 0`。
- `day` 仅允许 `1/3/4/5`。
- 若填写 `bundle_id`：
  - 同组至少 2 条课程。
  - 同组 `day` 不可重复。
  - 同组 `capacity` 必须一致。

### 课程开设年级表 (course_grades.csv)
```csv
course_id,grade
C001,1
C001,2
```

### 学生表 (students.csv)
```csv
name,class_name,grade,id_card
张三,1班,1,110101199001011234
```

## 开发指南

### 添加新的 API 端点

1. 在 `backend/api/` 中创建或修改路由
2. 在 `backend/schemas.py` 中定义 Pydantic 模型
3. 在 `frontend/src/services/api.js` 中添加前端调用

### 数据库迁移

```bash
cd backend
alembic revision --autogenerate -m "描述"
alembic upgrade head
```

## 部署说明

### 生产环境配置

1. 修改 `backend/services/auth.py` 中的 SECRET_KEY
2. 配置数据库路径
3. 设置 CORS 允许的域名

### Docker 部署

```bash
docker-compose up -d
```

## 许可证

MIT License
