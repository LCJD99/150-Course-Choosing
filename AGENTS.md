Goal
Implement a complete course selection system (兴趣班选课系统) for 150团中学 based on the design document at docs/plans/2026-03-11-course-selection-design.md. The system is a full-stack application with Vue 3 frontend and FastAPI backend, featuring student course selection with immediate confirmation, admin CSV import capabilities, and mobile-first responsive design.
Instructions
- Use executing-plans skill to implement the project in batches
- Create an isolated git worktree for development
- Follow the 7-day milestone plan from the design document
- Technology stack: Vue 3 + FastAPI + SQLite with Alembic migrations
- Key requirements:
  - Student login with name + ID card number (ID card hashed with SHA256)
  - 4-day selection: Monday (1), Wednesday (3), Thursday (4), Friday (5)
  - Immediate confirmation upon selection (no 10-minute reservation)
  - Course replacement allowed (immediate override)
  - Admin CSV import: courses, course_grades, students
  - System toggle to enable/disable course selection
  - Mobile-first design (320px-430px optimization)
  - Prevent overbooking with transaction-level capacity control
  - All API endpoints documented via FastAPI Swagger UI
Discoveries
- SQLite isolation level: SQLite doesn't support IMMEDIATE isolation level - had to remove it from database.py
- JavaScript syntax error: Python-style triple quotes """ don't work in JavaScript files - had to change to // comments
- Alembic model detection: Initial migration was empty because models weren't being imported in alembic/env.py - had to add explicit imports
- FastAPI authentication: Initially implemented token as query parameter, but needed to switch to HTTPBearer security scheme with Security(security) dependency
- Package.json issue: Initial npm install didn't create proper package.json - had to manually recreate it with dev script
- Database transaction error: Using with db.begin() inside an existing transaction caused errors - had to use db.commit() directly
- Vue Router lazy loading: Routes needed to use dynamic imports for proper lazy loading
Accomplished
Completed tasks:
- ✅ Created git worktree at .worktrees/course-selection/feature/course-selection
- ✅ Initialized Vue 3 frontend with Vite and installed dependencies
- ✅ Set up FastAPI backend with all dependencies
- ✅ Created SQLite database with Alembic migrations (7 tables: students, courses, course_grades, enrollments, system_settings, import_logs, alembic_version)
- ✅ Implemented authentication system (JWT tokens, ID card SHA256 hashing)
- ✅ Built all student APIs (login, get courses, select/replace course, get progress, get selections)
- ✅ Built all admin APIs (CSV import for 3 entities, toggle selection open, get status)
- ✅ Implemented capacity control with transaction-level concurrency protection
- ✅ Created student login page with gradient design
- ✅ Created student selection page with day tabs, course cards, progress bar, confirmation dialogs
- ✅ Created admin dashboard with statistics, toggle switch, quick actions
- ✅ Created CSV import page with drag-drop upload, result display, error details
- ✅ Created course management page with filtering, enable/disable, delete actions
- ✅ Implemented responsive mobile-first design (320px-430px optimized)
- ✅ Added comprehensive documentation in README.md
- ✅ All services running: Backend on port 8000, Frontend on port 5173
All tasks marked as completed in todo list. The project is functionally complete according to the original design specifications.
Relevant files / directories
Backend (.worktrees/course-selection/backend/)
Core application:
- main.py - FastAPI application with router includes, CORS middleware, startup lifespan
- database.py - SQLAlchemy engine configuration, session management, get_db dependency
- requirements.txt - All Python dependencies (FastAPI 0.109.0, SQLAlchemy 2.0.25, Alembic 1.13.1, etc.)
Database:
- models/__init__.py - All SQLAlchemy models (Student, Course, CourseGrade, Enrollment, SystemSetting, ImportLog)
- alembic/versions/f84add151dda_initial_migration.py - Initial migration creating all tables
- alembic/env.py - Alembic environment with model imports
- data/course_selection.db - SQLite database with test data (4 courses, 5 course_grades, 2 students)
API routes:
- api/student/__init__.py - Student endpoints: /login, /courses, /selections, /progress, /selections/{day}
- api/admin/__init__.py - Admin endpoints: /import/courses, /import/course-grades, /import/students, /settings/selection-open
Business logic:
- services/auth.py - JWT token creation/verification, ID card hashing
- schemas.py - Pydantic models for request/response validation
Frontend (.worktrees/course-selection/frontend/)
Application structure:
- index.html - HTML entry point with Chinese language settings and mobile viewport meta
- package.json - NPM configuration with vue-router dependency
- src/main.js - Vue app initialization with router
- src/App.vue - Root component with global styles
- src/router/index.js - Vue Router configuration with lazy-loaded routes and auth guards
Pages/Views:
- src/views/LoginView.vue - Student login page with gradient background, form validation, error handling
- src/views/SelectionView.vue - Main selection page with day tabs, course cards, progress bar, confirmation dialogs
- src/views/DashboardView.vue - Admin dashboard with statistics cards, day-based charts, quick actions
- src/views/ImportView.vue - CSV import page with drag-drop, tabbed interface, result display
- src/views/CoursesView.vue - Course management with filters, progress bars, enable/disable actions
Services & State:
- src/services/api.js - API service layer wrapping all backend endpoints with error handling
- src/stores/auth.js - Authentication state management with localStorage persistence
Configuration files:
- backend/alembic.ini - Alembic configuration with SQLite URL
- frontend/vite.config.js - Vite build configuration
Documentation:
- .worktrees/course-selection/README.md - Complete project documentation with setup instructions, API info, deployment guide
Test data files (backend/):
- test_courses.csv - 4 test courses
- test_course_grades.csv - 5 course-grade mappings
- test_students.csv - 2 test students
Git worktree location:
- Worktree path: .worktrees/course-selection/
- Branch: feature/course-selection
- Main repo: Current working directory /Users/lcjd/code-workspace/150/new-course-scheduler/
- .gitignore was added to exclude .worktrees/ from commits

