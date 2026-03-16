# Bundled Course Selection (方案A) Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** 支持“一周两节必须同时报名”的组合课（bundle），通过 `courses.csv` 的 `bundle_id` 字段导入，并在学生选课时以事务方式原子性完成整组报名/替换。

**Architecture:** 在 `courses` 表新增可空字段 `bundle_id`，保持现有课程模型不拆表。导入时校验同一 `bundle_id` 的课程规则（至少两条、day 不重复、容量一致）；选课接口检测目标课程是否属于 bundle，若是则在单事务中校验与写入整组 enrollments。课程列表和已选结果增加 bundle 元信息，供前端显示“连报课”。

**Tech Stack:** FastAPI, SQLAlchemy, Alembic, SQLite, Pandas, Vue 3

---

### Task 1: 扩展数据模型与迁移（bundle_id）

**Files:**
- Modify: `backend/models/__init__.py`
- Create: `backend/alembic/versions/<new_revision>_add_bundle_id_to_courses.py`

**Step 1: Write the failing test**

新增测试文件（后续 Task 5 会创建测试基建），写一个最小测试：创建课程时写入 `bundle_id`，查询返回应包含 `bundle_id`。

```python
def test_course_model_supports_bundle_id(db_session):
    course = Course(
        course_id="C101A",
        course_name="机器人基础-上",
        teacher="张老师",
        capacity=30,
        day=1,
        bundle_id="B1001",
    )
    db_session.add(course)
    db_session.commit()
    assert db_session.query(Course).first().bundle_id == "B1001"
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_bundle_model.py::test_course_model_supports_bundle_id -v`
Expected: FAIL（`Course` 无 `bundle_id` 字段）

**Step 3: Write minimal implementation**

- 在 `Course` 模型新增：`bundle_id = Column(String(50), nullable=True, index=True)`
- 创建 Alembic migration：为 `courses` 表增加 `bundle_id` 列和索引。

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_bundle_model.py::test_course_model_supports_bundle_id -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/models/__init__.py backend/alembic/versions/*.py
git commit -m "feat: add bundle_id to courses model"
```

### Task 2: 更新 courses.csv 导入规则

**Files:**
- Modify: `backend/api/admin/__init__.py`
- Modify: `backend/README.md` (或项目根 README 对应 CSV 规范章节)

**Step 1: Write the failing test**

```python
def test_import_courses_validates_bundle_rules(client, csv_file):
    # 同 bundle 重复 day 或容量不一致应失败
    response = client.post("/api/admin/import/courses", files={"file": csv_file})
    assert response.status_code == 200
    body = response.json()
    assert body["failed_rows"] > 0
    assert any("bundle" in e.lower() for e in body["errors"])
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_admin_course_import_bundle.py::test_import_courses_validates_bundle_rules -v`
Expected: FAIL（当前未校验 bundle 规则）

**Step 3: Write minimal implementation**

- `required_columns` 改为支持新列：`bundle_id`（可选，不强制必填）
- 读入后先按 `bundle_id`（非空）分组，增加校验：
  - 组内课程数 >= 2（当前需求一周两节，可先限制 `==2`，并在代码注释留扩展点）
  - 组内 `day` 不重复
  - 组内 `capacity` 一致（避免一组两节容量不一致导致体验混乱）
- 写入 `Course` 时持久化 `bundle_id`（空值写 `None`）
- 错误信息写入 `error_report`，返回给前端。

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_admin_course_import_bundle.py::test_import_courses_validates_bundle_rules -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/api/admin/__init__.py backend/README.md README.md
git commit -m "feat: validate and import bundled courses from CSV"
```

### Task 3: 学生选课接口支持整组原子报名/替换

**Files:**
- Modify: `backend/api/student/__init__.py`
- Modify: `backend/schemas.py`

**Step 1: Write the failing test**

```python
def test_selecting_one_bundle_course_enrolls_all_bundle_days(client, auth_header, seeded_bundle_courses):
    response = client.put(
        "/api/student/selections/1",
        json={"course_id": seeded_bundle_courses["C101A"].id},
        headers=auth_header,
    )
    assert response.status_code == 200

    selections = client.get("/api/student/selections", headers=auth_header).json()
    selected_days = sorted([item["day"] for item in selections])
    assert selected_days == [1, 4]
```

再补 2 个失败测试：
- 组合中任一节满员 -> 整组失败且不写入任何 enrollment
- 已有其中一天单课时选择组合 -> 按整组替换，最终两天均为新组合。

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_student_bundle_selection.py -v`
Expected: FAIL（当前只处理单 day）

**Step 3: Write minimal implementation**

- 新增辅助函数（同文件即可，保持最小改动）：
  - `get_bundle_courses(course, db)`：若 `bundle_id` 非空返回同组课程列表（按 day 排序）
  - `validate_bundle_courses_for_student(bundle_courses, student, db)`：校验年级、开关、容量
- 改造 `PUT /api/student/selections/{day}`：
  - 先校验请求 `course.day == day`
  - 若无 `bundle_id`，保留单课逻辑
  - 若有 `bundle_id`，在同一事务里循环处理组内每个 day：
    - 查询该学生该 day 既有记录
    - 有则替换为目标课程 id，无则新增
    - 任何一节校验失败直接抛错，整体回滚
- 返回消息增加 bundle 信息：例如 `"Bundled course selected successfully"`

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_student_bundle_selection.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/api/student/__init__.py backend/schemas.py
git commit -m "feat: support atomic bundled course selection"
```

### Task 4: 课程查询/已选结果增加 bundle 元信息

**Files:**
- Modify: `backend/schemas.py`
- Modify: `backend/api/student/__init__.py`

**Step 1: Write the failing test**

```python
def test_courses_api_returns_bundle_metadata(client, auth_header):
    response = client.get("/api/student/courses?day=1", headers=auth_header)
    assert response.status_code == 200
    first = response.json()[0]
    assert "bundle_id" in first
    assert "bundle_size" in first
    assert "is_bundle" in first
```

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_student_courses_bundle_metadata.py -v`
Expected: FAIL（schema 当前无这些字段）

**Step 3: Write minimal implementation**

- `CourseResponse` 新增可选字段：`bundle_id: Optional[str]`, `bundle_size: Optional[int]`, `is_bundle: bool = False`
- `get_courses` / `get_selections` 组装响应时填充上述字段。

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests/test_student_courses_bundle_metadata.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/schemas.py backend/api/student/__init__.py
git commit -m "feat: expose bundled course metadata in student APIs"
```

### Task 5: 新增后端测试基建与回归测试

**Files:**
- Create: `backend/tests/conftest.py`
- Create: `backend/tests/test_bundle_model.py`
- Create: `backend/tests/test_admin_course_import_bundle.py`
- Create: `backend/tests/test_student_bundle_selection.py`
- Create: `backend/tests/test_student_courses_bundle_metadata.py`
- Modify: `backend/requirements.txt` (如需增加 `pytest`)

**Step 1: Write the failing test**

先建立最小 fixture（临时 sqlite db + TestClient + 测试学生/课程种子数据），随后让至少一个 bundle 测试先失败。

**Step 2: Run test to verify it fails**

Run: `pytest backend/tests/test_student_bundle_selection.py::test_selecting_one_bundle_course_enrolls_all_bundle_days -v`
Expected: FAIL

**Step 3: Write minimal implementation**

- 完成 fixture 与数据工厂
- 保证测试隔离（每个测试重建表）
- 按前述任务补全所有测试用例。

**Step 4: Run test to verify it passes**

Run: `pytest backend/tests -v`
Expected: PASS

**Step 5: Commit**

```bash
git add backend/tests backend/requirements.txt
git commit -m "test: add coverage for bundled course import and selection"
```

### Task 6: 前端最小联动改造（显示连报课信息）

**Files:**
- Modify: `frontend/src/services/api.js`
- Modify: `frontend/src/views/SelectionView.vue`

**Step 1: Write the failing test**

若当前前端无测试框架，先写一个手工验收脚本（README 中）并记录失败预期：
- 连报课卡片未显示“2节连报”
- 确认弹窗未提示“将同时报名”

**Step 2: Run verification to show current behavior fails**

Run: `npm run dev`（frontend）并手测上述两点。
Expected: 不满足新需求

**Step 3: Write minimal implementation**

- API 层透传后端新增字段
- 课程卡增加标识：`is_bundle ? '连报课' : ''`
- 确认弹窗文案根据 `is_bundle` 切换：
  - 普通课：确认选择该课程？
  - 连报课：该课程需同时报名本组全部课时，是否继续？

**Step 4: Run verification to show pass**

Run: `npm run dev`（frontend）并手测。
Expected: 页面正确显示并可触发连报提示。

**Step 5: Commit**

```bash
git add frontend/src/services/api.js frontend/src/views/SelectionView.vue
git commit -m "feat: show bundled-course labels and confirmation copy"
```

### Task 7: 文档与发布前验证

**Files:**
- Modify: `README.md`
- Modify: `docs/plans/2026-03-11-course-selection-design.md`

**Step 1: Write the failing test**

文档验收清单（人工）：
- 是否包含 `courses.csv` 新列 `bundle_id`
- 是否说明“组合课原子报名规则”
- 是否说明“替换为整组替换”

**Step 2: Run verification to show current docs are incomplete**

Run: 手工对照检查
Expected: 缺失 bundle 说明

**Step 3: Write minimal implementation**

- 更新 CSV 示例、规则、API 行为说明
- 增加错误码/错误信息示例（组合课满员、组合校验失败）

**Step 4: Run verification to show docs are complete**

Run: 手工复核 + Swagger 检查字段是否对齐
Expected: 文档与实际接口一致

**Step 5: Commit**

```bash
git add README.md docs/plans/2026-03-11-course-selection-design.md
git commit -m "docs: document bundled course CSV and API behavior"
```

### Final Verification (必须执行)

1. 迁移：`cd backend && alembic upgrade head`
2. 后端测试：`pytest backend/tests -v`
3. 冒烟：
   - `PUT /api/admin/settings/selection-open` 开关正常
   - 导入含 `bundle_id` 的 `courses.csv` 成功
   - 学生选择 bundle 任一课程后，`/api/student/selections` 返回整组已选
4. 前端手测（320px-430px）：连报标识、确认文案、替换行为。
