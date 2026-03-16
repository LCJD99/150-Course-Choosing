# 150团中学兴趣班选课系统设计文档

## 1. 项目目标

设计并实现一个前后端分离的兴趣班选课系统，满足以下核心目标：

- 学生按姓名 + 身份证登录后，完成周一、周三、周四、周五四天选课。
- 学生每个开放日只能选 1 门课；点击确认后立即生效为最终态。
- 当天已选后，其他课程可执行"替换"，替换后立即覆盖原选择。
- 管理员可通过 CSV 导入课程、课程开设年级、学生数据。
- 管理员可一键开启/关闭选课；关闭时学生端仅支持预览。
- 前端学生端以手机访问体验优先（流式布局）。

> 设计变更说明：已取消"保留态 + 10 分钟 + 最终统一提交"流程，改为"每次确认即最终提交"。

## 2. 技术选型

- 前端：Vue 3
- 后端：FastAPI
- 数据库：SQLite（WAL 模式）

选型理由：交付速度快、部署成本低、适配学校单机/内网环境，满足当前规模需求。

## 3. 业务规则

### 3.1 开放日规则

- 仅开放周一、周三、周四、周五（day = 1/3/4/5）。
- 周二不开放。

### 3.2 学生选课规则

- 登录方式：姓名 + 身份证号。
- 学生只可看到本年级在对应天可选的课程。
- 每位学生每天最多 1 门课程。
- 选择课程点击"确定"后立即写入最终结果。
- 若该天已有课程，其他课程显示"替换"；替换后新课程立即生效。
- 页面显示四天完成进度（X/4）。

### 3.3 系统开关规则

- 管理员关闭选课时：
  - 学生端显示："系统尚未开通，仅支持预览"。
  - 后端禁止所有写入接口（选课/替换）。

## 4. 数据导入规范

### 4.1 课程表（courses.csv）

```csv
course_id,course_name,teacher,capacity,day
C001,非遗剪纸与重彩画,李艳华,15,1
```

校验规则：

- `course_id` 唯一。
- `capacity > 0`。
- `day` 仅允许 1/3/4/5。

### 4.2 课程开设年级表（course_grades.csv）

```csv
course_id,grade
C001,1
C001,2
```

校验规则：

- `course_id` 必须存在于课程表。
- `(course_id, grade)` 不可重复。

### 4.3 学生表（students.csv）

建议字段：`name,class_name,grade,id_card`

校验规则：

- 姓名 + 身份证唯一。
- 身份证格式合法。
- `grade` 为有效整数。

## 5. 数据库设计（SQLite）

### 5.1 students

- `id` INTEGER PK
- `name` TEXT NOT NULL
- `class_name` TEXT NOT NULL
- `grade` INTEGER NOT NULL
- `id_card_hash` TEXT NOT NULL
- `id_card_last4` TEXT NOT NULL
- `created_at` DATETIME NOT NULL
- `updated_at` DATETIME NOT NULL

约束：`UNIQUE(name, id_card_hash)`

### 5.2 courses

- `id` INTEGER PK
- `course_id` TEXT NOT NULL
- `course_name` TEXT NOT NULL
- `teacher` TEXT NOT NULL
- `capacity` INTEGER NOT NULL
- `day` INTEGER NOT NULL
- `is_active` BOOLEAN NOT NULL DEFAULT 1
- `created_at` DATETIME NOT NULL
- `updated_at` DATETIME NOT NULL

约束：

- `UNIQUE(course_id)`
- `CHECK(day IN (1,3,4,5))`

### 5.3 course_grades

- `id` INTEGER PK
- `course_id` INTEGER NOT NULL（FK -> courses.id）
- `grade` INTEGER NOT NULL

约束：`UNIQUE(course_id, grade)`

### 5.4 enrollments

- `id` INTEGER PK
- `student_id` INTEGER NOT NULL（FK -> students.id）
- `day` INTEGER NOT NULL
- `course_id` INTEGER NOT NULL（FK -> courses.id）
- `status` TEXT NOT NULL DEFAULT 'CONFIRMED'
- `created_at` DATETIME NOT NULL
- `updated_at` DATETIME NOT NULL

约束：

- `UNIQUE(student_id, day)`
- `CHECK(day IN (1,3,4,5))`

说明：当前版本所有有效记录均为最终态 `CONFIRMED`。

### 5.5 system_settings

- `key` TEXT PK
- `value` TEXT NOT NULL
- `updated_at` DATETIME NOT NULL

关键配置：`course_selection_open`（true/false）。

### 5.6 import_logs

- `id` INTEGER PK
- `import_type` TEXT NOT NULL
- `total_rows` INTEGER NOT NULL
- `success_rows` INTEGER NOT NULL
- `failed_rows` INTEGER NOT NULL
- `error_report` TEXT
- `created_at` DATETIME NOT NULL

### 5.7 索引

- `idx_courses_day` on `courses(day)`
- `idx_course_grades_grade` on `course_grades(grade)`
- `idx_enrollments_course_day_status` on `enrollments(course_id, day, status)`
- `idx_students_name` on `students(name)`

## 6. API 设计

### 6.1 学生端

- `POST /api/student/login`
  - 入参：`name`, `id_card`
  - 出参：`token`, `student`, `course_selection_open`

- `GET /api/student/courses?day={1|3|4|5}`
  - 出参：当日课程列表（课程名、老师、剩余容量、是否已选）

- `GET /api/student/selections`
  - 出参：该生四天已选结果

- `PUT /api/student/selections/{day}`
  - 入参：`course_id`
  - 行为：选择或替换当天课程，立即生效

- `GET /api/student/progress`
  - 出参：`completed_days`, `is_complete_4_days`

### 6.2 管理端

- `POST /api/admin/import/courses`
- `POST /api/admin/import/course-grades`
- `POST /api/admin/import/students`
- `PUT /api/admin/settings/selection-open`
- `GET /api/admin/enrollments/export`

## 7. 选课并发与一致性

### 7.1 核心原则

- 所有选课/替换写操作在事务中完成（`BEGIN IMMEDIATE`）。
- 先做业务校验（开关、年级、day 对齐、课程有效性），再做容量校验。
- 容量计算：`remaining = capacity - confirmed_count`。

### 7.2 防超卖策略

- 事务内读取当前确认人数并判断余量。
- 成功后写入或更新该生该天记录。
- 若余量不足，事务回滚并返回"课程已满"。

### 7.3 强约束兜底

- `UNIQUE(student_id, day)` 防止同一天多门课。
- 后端统一拦截开关关闭状态，防止前端绕过。

## 8. 前端交互设计（手机优先）

### 8.1 学生端页面

- 登录页：姓名 + 身份证。
- 选课页：按周一/三/四/五分栏展示课程。
- 课程卡：课程名、老师、剩余容量、按钮状态（选择/已选/替换/已满）。
- 顶部进度：已完成 `X/4`。
- 未开启状态提示："系统尚未开通，仅支持预览"。

### 8.2 按钮与确认框

- 选择：弹框确认"确认选择该课程？"，确认后立即生效。
- 替换：弹框确认"是否替换为该课程？"，确认后立即覆盖。

### 8.3 响应式要求

- 适配 320px-430px 主流手机宽度。
- 无横向滚动。
- 关键按钮点击区域 >= 44px。

## 9. 管理端页面设计

- 总览页：按天选课人数、满班课程数、完成度统计。
- 开关控制页：一键开启/关闭选课。
- CSV 导入页：模板下载、上传、预校验、错误明细、导入日志。
- 课程管理页：按天/年级/老师筛选，查看容量与剩余。
- 学生管理页：查询学生四天选课结果。
- 结果导出页：按条件导出。

## 10. 验收标准

### 10.1 功能验收

- 开关关闭时学生端仅预览，写入接口被拒绝。
- 学生仅可见本年级课程。
- 每天仅 1 门；选择与替换立即生效。
- 满员课程不可再选。
- 完成度正确显示（0-4/4）。

### 10.2 并发验收

- 课程容量为 15，并发 30 人抢课，成功人数 <= 15。
- 不出现负库存。
- 不出现同一学生同一天多条有效记录。

### 10.3 移动端验收

- 手机端主流程可在 3 次点击内完成一次选课或替换。
- 弹窗和课程卡在小屏可完整显示。

## 11. 开发里程碑（7 天）

- Day 1：项目骨架 + 数据库迁移 + 鉴权基础
- Day 2：CSV 导入能力 + 校验 + 日志
- Day 3：学生选课主流程 + 替换 + 容量事务
- Day 4：开关控制 + 错误码统一
- Day 5：管理端查询统计 + 导出
- Day 6：移动端优化 + 全链路联调
- Day 7：压测验收 + 部署上线

## 12. 风险与后续扩展

- 风险：SQLite 写并发有限，若未来并发大幅增长，可切换 PostgreSQL。
- 扩展方向：增加管理员手工调课、学生选课记录审计、短信通知、导出模板定制。
