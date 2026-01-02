# TeamFlow - Agency Task Management System
## Implementation Plan for Hackathon II

### Project Vision
Build a **Full CRM for Agencies (10-50 people)** that evolves from a simple console app to an AI-powered, cloud-native task distribution system with drag-drop UX and agency-specific features (billing, time tracking, profitability).

---

## Phase I: Console App - Task Distribution Foundation (100 pts)

### Objective
Build a Python console app demonstrating task CRUD with assignment capabilities, stored in-memory.

### Data Model (In-Memory)
```python
# Core entities for Phase I
- User: id, name, role (admin/member), skills[]
- Task: id, title, description, status, assigned_to (User), priority, created_at
- Team: id, name, members[]  # simplified for agency context
```

### Features to Implement
1. **Task CRUD**
   - Create task with title, description, priority
   - List all tasks (with assignee names)
   - Update task details
   - Delete task by ID
   - Mark task as complete

2. **Assignment System**
   - Create users/teams
   - Assign task to user
   - View tasks by assignee

3. **Console Commands**
   ```
   > create task "Fix client bug" --priority high --assign to john
   > list tasks --assignee john
   > assign task 3 to jane
   > complete task 3
   ```

### Tech Stack
- Python 3.13+, UV for package management
- SpecKit Plus + Claude Code (spec-driven)
- No manual coding - all via specs

### Deliverables
- `/src/console_app.py` - Main entry point
- `/src/models.py` - Data models
- `/src/commands.py` - Command handlers
- `specs/phase1-spec.md` - Feature specification
- Demo: Show creating tasks, assigning to users, listing by assignee

---

## Phase II: Full-Stack Web App - Full CRM (150 pts)

### Objective
Transform console app into a multi-user web application with persistent database, authentication, and full CRM entities.

### Data Model (Neon PostgreSQL + SQLModel)
```python
# Expanded entities for Phase II
- Client: id, name, email, company, billing_rate
- Project: id, name, client_id, budget, status, deadline
- Task: id, title, description, project_id, status, assigned_to_id, priority, due_date, time_spent
- User: id, name, email, role, hourly_rate, skills[]
- Team: id, name, members[], description
- TimeEntry: id, task_id, user_id, hours, date, notes
```

### Features to Implement
1. **Better Auth Integration**
   - User signup/signin
   - JWT token-based API authentication
   - Team/agency-level access control

2. **RESTful API Endpoints**
   ```
   # Tasks
   GET    /api/{user_id}/tasks                    - List all tasks
   GET    /api/{user_id}/tasks?project_id=X       - Filter by project
   POST   /api/{user_id}/tasks                    - Create task
   GET    /api/{user_id}/tasks/{id}               - Get task details
   PUT    /api/{user_id}/tasks/{id}               - Update task
   DELETE /api/{user_id}/tasks/{id}               - Delete task
   PATCH  /api/{user_id}/tasks/{id}/complete      - Toggle completion
   PATCH  /api/{user_id}/tasks/{id}/assign        - Assign to user

   # Clients & Projects
   GET    /api/clients                            - List clients
   POST   /api/clients                            - Create client
   GET    /api/projects                           - List projects
   POST   /api/projects                           - Create project
   GET    /api/projects/{id}/tasks                - Project tasks

   # Time Tracking
   POST   /api/tasks/{id}/time                    - Log time
   GET    /api/tasks/{id}/time                    - Get time entries

   # Agency Analytics
   GET    /api/projects/{id}/profitability        - Project profit
   GET    /api/users/{id}/workload                - User workload
   ```

3. **Frontend (Next.js 16 + App Router)**
   - Dashboard with task overview
   - Drag-drop Kanban board (Todo → In Progress → Done)
   - Client management page
   - Project management with task breakdown
   - Time tracking modal
   - User workload view

### Tech Stack
| Layer | Technology |
|-------|------------|
| Frontend | Next.js 16, TypeScript, Tailwind CSS, dnd-kit (drag-drop) |
| Backend | FastAPI, SQLModel, Pydantic |
| Database | Neon Serverless PostgreSQL |
| Auth | Better Auth + JWT |
| Spec-Driven | Claude Code + SpecKit Plus |

### Deliverables
- `/frontend/` - Next.js app with pages
- `/backend/` - FastAPI application
- `specs/phase2-spec.md` - Full CRM specification
- Demo: Show drag-drop Kanban, time logging, project profitability

---

## Phase III: AI-Powered Task Chatbot (200 pts)

### Objective
Add conversational interface using OpenAI Agents SDK and MCP tools for natural language task management.

### MCP Tools Specification
```yaml
# Core Task Tools
tools:
  add_task:
    description: Create a new task
    parameters: user_id, title, description, priority, project_id, assign_to
    returns: task_id, status

  list_tasks:
    description: List tasks with filters
    parameters: user_id, status, project_id, assignee_id
    returns: tasks[]

  assign_task:
    description: Assign task to user (AI suggests best assignee)
    parameters: user_id, task_id, assign_to_id
    returns: task_id, assignee, reasoning

  complete_task:
    description: Mark task as complete
    parameters: user_id, task_id
    returns: task_id, status

  log_time:
    description: Log time spent on task
    parameters: user_id, task_id, hours, notes
    returns: time_entry_id

# Agency-Specific Tools
  create_project:
    description: Create new project for client
    parameters: client_name, project_name, budget, deadline
    returns: project_id, client_id

  get_profitability:
    description: Calculate project profitability
    parameters: project_id
    returns: revenue, cost, profit, margin

  suggest_assignee:
    description: AI suggests best person for task
    parameters: task_id, skills_required
    returns: user_id, reasoning, workload_score

  workload_summary:
    description: Get team workload overview
    parameters: team_id
    returns: users[] with task_count, hours_assigned
```

### Natural Language Commands
```
User: "Create a task for the Acme project to fix the login bug, assign it to Sarah"
Bot: [calls add_task, assign_task] Created task "Fix login bug" for Acme project, assigned to Sarah.

User: "Show me John's workload"
Bot: [calls workload_summary] John has 5 tasks in progress (24 hours), 3 completed this week.

User: "Who should handle the database migration task?"
Bot: [calls suggest_assignee] Based on skills and current workload, I recommend Ahmed (SQL expert, 4 tasks vs team avg of 7).

User: "Log 3 hours for task 12"
Bot: [calls log_time] Logged 3 hours for "Database Schema Update". Total: 8.5 hours.
```

### Architecture
```
┌─────────────────┐     ┌──────────────────────────────────────────────┐
│  ChatKit UI     │────▶│  FastAPI Server                             │
│  (Frontend)     │     │  ┌────────────────────────────────────────┐  │
└─────────────────┘     │  │  POST /api/{user_id}/chat               │  │
                        │  └───────────────┬────────────────────────┘  │
                        │                  │                           │
                        │                  ▼                           │
                        │  ┌────────────────────────────────────────┐  │
                        │  │  OpenAI Agents SDK                     │  │
                        │  │  (Agent + Runner)                      │  │
                        │  └───────────────┬────────────────────────┘  │
                        │                  │                           │
                        │                  ▼                           │
                        │  ┌────────────────────────────────────────┐  │
                        │  │  MCP Server (Tools)                    │  │
                        │  │  - add_task, assign_task, etc.         │  │
                        │  │  - suggest_assignee (AI logic)         │  │
                        │  │  - get_profitability                    │  │
                        │  └────────────────────────────────────────┘  │
                        └──────────────────────────────────────────────┘
```

### Database Models (Additions)
```python
# Conversation state
- Conversation: id, user_id, created_at
- Message: id, conversation_id, role, content, created_at
```

### Deliverables
- `/frontend/` - Updated with ChatKit UI
- `/backend/mcp_server/` - MCP server implementation
- `/backend/agents/` - OpenAI Agents SDK integration
- `specs/phase3-spec.md` - Chatbot specification
- Demo: Voice/text commands, AI assignee suggestions

---

## Phase IV: Kubernetes Deployment (250 pts)

### Objective
Containerize and deploy the chatbot on local Minikube cluster using Helm charts and AI-assisted operations.

### Architecture
```
┌─────────────────────────────────────────────────────────────────┐
│                      MINIKUBE CLUSTER                           │
│                                                                 │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐           │
│  │  Frontend   │   │  Backend    │   │  Neon DB    │           │
│  │  (Next.js)  │──▶│  (FastAPI)  │──▶│  (External) │           │
│  │  Pod        │   │  Pod        │   └─────────────┘           │
│  └─────────────┘   └─────────────┘                              │
│         │                 │                                     │
│         └─────────────────┼─────────────────┐                   │
│                          ▼                 ▼                   │
│                   ┌─────────────┐   ┌─────────────┐             │
│                   │   Service   │   │ Ingress     │             │
│                   │  (LoadBal)  │   │  (Routing)  │             │
│                   └─────────────┘   └─────────────┘             │
└─────────────────────────────────────────────────────────────────┘
```

### Containerization (Docker)
```dockerfile
# Frontend Dockerfile
FROM node:20-alpine
WORKDIR /app
COPY frontend/package*.json ./
RUN npm ci
COPY frontend/ ./
RUN npm run build
EXPOSE 3000
CMD ["npm", "start"]

# Backend Dockerfile
FROM python:3.13-slim
WORKDIR /app
COPY backend/requirements.txt ./
RUN pip install -r requirements.txt
COPY backend/ ./
EXPOSE 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0"]
```

### Helm Chart Structure
```
helm/teamflow/
├── Chart.yaml
├── values.yaml
├── templates/
│   ├── frontend-deployment.yaml
│   ├── frontend-service.yaml
│   ├── backend-deployment.yaml
│   ├── backend-service.yaml
│   ├── ingress.yaml
│   └── configmap.yaml
```

### AIOps Commands
```bash
# Using kubectl-ai for intelligent operations
kubectl-ai "deploy teamflow backend with 3 replicas"
kubectl-ai "scale frontend based on CPU > 70%"
kubectl-ai "check why backend pods are failing"

# Using kagent for optimization
kagent "analyze cluster resource usage"
kagent "optimize deployment for cost"

# Using Gordon (Docker AI)
docker ai "optimize this Dockerfile for size"
docker ai "create multi-stage build for backend"
```

### Deliverables
- `Dockerfile.frontend`, `Dockerfile.backend`
- `helm/teamflow/` - Complete Helm charts
- `specs/phase4-spec.md` - K8s deployment spec
- Demo: Deploy on Minikube, scale pods, show AI operations

---

## Phase V: Advanced Cloud Deployment (300 pts)

### Objective
Deploy to production Kubernetes with event-driven architecture (Kafka), Dapr integration, advanced features.

### Event-Driven Architecture (Kafka)
```yaml
# Kafka Topics
topics:
  task-events:
    purpose: All task CRUD operations (create, assign, complete)
    producer: Backend API
    consumers: Recurring Task Service, Audit Service, Notification Service

  reminders:
    purpose: Scheduled reminders for due tasks
    producer: Reminder Scheduler
    consumers: Notification Service

  time-logged:
    purpose: Real-time profitability updates
    producer: Time Tracking Service
    consumers: Billing Service, Analytics Service

  assignee-suggested:
    purpose: AI assignee recommendations
    producer: AI Suggestion Engine
    consumers: Notification Service, Analytics Service
```

### Event Schemas
```json
// Task Event
{
  "event_type": "task_assigned",
  "task_id": 123,
  "project_id": 5,
  "assignee_id": "user_789",
  "suggested_by": "ai",  // or "manual"
  "reasoning": "Low workload, has required skills",
  "timestamp": "2025-01-15T10:30:00Z"
}

// Time Logged Event
{
  "event_type": "time_logged",
  "task_id": 123,
  "user_id": "user_789",
  "hours": 3.5,
  "project_id": 5,
  "cost": 175.00,  // hours * hourly_rate
  "timestamp": "2025-01-15T14:00:00Z"
}
```

### Dapr Integration
```yaml
# Dapr Components
components:
  kafka-pubsub:
    type: pubsub.kafka
    metadata:
      - name: brokers
        value: "kafka:9092"
      - name: consumerGroup
        value: "teamflow-services"

  state-store:
    type: state.postgresql
    metadata:
      - name: connectionString
        value: "postgresql://user:pass@neon-db/db"

  secret-store:
    type: secretstores.kubernetes
    # Stores: OpenAI API key, DB credentials

  cron-binding:
    type: bindings.cron
    metadata:
      - name: schedule
        value: "0 */1 * * * *"  # Every hour
```

### Advanced Features
1. **Recurring Tasks**
   - "Weekly client report" auto-creates next instance
   - "Monthly billing reminder" schedules automatically

2. **Due Date Reminders**
   - Browser push notifications
   - Email reminders via Kafka event

3. **Real-Time Updates**
   - WebSocket sync across all clients
   - Live assignment notifications

4. **Agency Analytics**
   - Project profitability (revenue - cost)
   - Team utilization rates
   - Client billing summaries

### Cloud Deployment (DigitalOcean / Oracle OKE)
```
┌─────────────────────────────────────────────────────────────────────────┐
│                       KUBERNETES CLUSTER (DOKS)                         │
│                                                                          │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Frontend Pod (3 replicas)                     │    │
│  │  ┌───────────┐ ┌───────────┐                                     │    │
│  │  │ Next.js   ││   Dapr    │                                     │    │
│  │  └───────────┘ └───────────┘                                     │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                │                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Backend Pod (3 replicas)                      │    │
│  │  ┌───────────┐ ┌───────────┐ ┌───────────────┐                   │    │
│  │  │  FastAPI  ││   Dapr    │ │   MCP Tools   │                   │    │
│  │  │ + Agents  ││  Sidecar  │ │               │                   │    │
│  │  └───────────┘ └───────────┘ └───────────────┘                   │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                │                                       │
│                                ▼                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                         KAFKA CLUSTER                            │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │    │
│  │  │task-events  │ │  reminders  │ │ time-logged │                │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
│                                │                                       │
│  ┌─────────────────────────────────────────────────────────────────┐    │
│  │                    Microservice Pods                            │    │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────┐                │    │
│  │  │ Notification│ │  Recurring  │ │   Billing   │                │    │
│  │  │   Service   │ │  Task Svc   │ │   Service   │                │    │
│  │  └─────────────┘ └─────────────┘ └─────────────┘                │    │
│  └─────────────────────────────────────────────────────────────────┘    │
└─────────────────────────────────────────────────────────────────────────┘
```

### CI/CD Pipeline (GitHub Actions)
```yaml
# .github/workflows/deploy.yml
on:
  push:
    branches: [main]

jobs:
  test:
    - Run tests
    - Build containers

  deploy-minikube:
    - Deploy to local for testing

  deploy-production:
    - Deploy to DigitalOcean
    - Run smoke tests
    - Notify on Slack
```

### Deliverables
- `helm/teamflow-prod/` - Production Helm charts with Dapr
- `dapr-components/` - All Dapr component YAMLs
- `kafka/` - Kafka configuration and Strimzi setup
- `.github/workflows/` - CI/CD pipeline
- `specs/phase5-spec.md` - Advanced features specification
- Demo: Live deployment, real-time sync, Kafka event flow

---

## Bonus Points Opportunities

| Bonus Feature | Points | Implementation |
|---------------|--------|----------------|
| Reusable Intelligence | +200 | Create Claude Code subagent skills for common operations |
| Cloud-Native Blueprints | +200 | Agent skills for K8s deployment patterns |
| Multi-language (Urdu) | +100 | Chatbot supports Urdu commands |
| Voice Commands | +200 | Web Speech API integration |

---

## Development Workflow (Spec-Driven)

### For Each Phase:
1. **Run `/sp.specify`** - Create feature specification
2. **Run `/sp.plan`** - Generate architecture design
3. **Run `/sp.tasks`** - Break into actionable tasks
4. **Run `/sp.implement`** - Execute via Claude Code
5. **Run `/sp.adr`** - Document architectural decisions

### Critical Files
| File | Purpose |
|------|---------|
| `.specify/memory/constitution.md` | Project principles (update first) |
| `specs/{phase}/spec.md` | WHAT to build |
| `specs/{phase}/plan.md` | HOW to build it |
| `specs/{phase}/tasks.md` | Atomic implementation steps |
| `history/adr/*.md` | Architectural decisions |

---

## Phase Submission Checklist

Each phase submission requires:
- [ ] GitHub repository with clean history
- [ ] Spec files in `/specs/` folder
- [ ] Working demo (video < 90 seconds)
- [ ] Published app link (Phase II+)
- [ ] PHR records for all prompts used

---

## Next Steps

1. **Create Constitution** - Define project principles
2. **Phase I Spec** - Write specification for console app
3. **Phase I Plan** - Design data model and command structure
4. **Phase I Tasks** - Break into implementation steps
5. **Implement Phase I** - Use Claude Code with `/sp.implement`
6. **Submit Phase I** - Demo video + GitHub link

---

## Key Architectural Decisions to Document (ADRs)

1. **Data Model Evolution**: In-memory → Neon PostgreSQL → Event-sourced
2. **Authentication**: None → Better Auth + JWT → OAuth scopes
3. **State Management**: In-memory → Database → Dapr State Store
4. **Event Streaming**: None → Kafka + Dapr PubSub
5. **AI Integration**: None → OpenAI Agents → MCP Tools → AI Suggestions

---

---

## Part 2: Constitution Design Prompt

### Objective
Create a comprehensive constitution for TeamFlow using best practices that will guide all AI agents (Claude, Copilot, etc.) in spec-driven development.

### Constitution Prompt Structure

```markdown
# TeamFlow Project Constitution

## Purpose
This constitution defines the non-negotiable principles, patterns, and standards for the TeamFlow Agency CRM project. All AI agents MUST consult this file before making any architectural or implementation decisions.

## Project Vision
Build a Full CRM for Agencies (10-50 people) that evolves from console app to cloud-native AI-powered system.

---

## 1. SOLID Principles (Non-Negotiable)

### Single Responsibility Principle (SRP)
- Every module/class/function has ONE reason to change
- Examples:
  - `TaskService` ONLY handles task logic (not auth, not notifications)
  - `APIRouter` ONLY routes requests (no business logic)
  - Component files contain ONE component (no multiple exports)

### Open/Closed Principle (OCP)
- Open for extension, closed for modification
- Use dependency injection for swappable implementations
- Strategy pattern for different AI providers (OpenAI, Anthropic)

### Liskov Substitution Principle (LSP)
- Subtypes must be substitutable for their base types
- All `TaskRepository` implementations must work identically
- MCP tools must have consistent signatures

### Interface Segregation Principle (ISP)
- Clients shouldn't depend on unused interfaces
- Split `UserService` into `UserQuery`, `UserCommand`, `UserAuth`
- Separate read/write interfaces (CQRS pattern)

### Dependency Inversion Principle (DIP)
- Depend on abstractions, not concretions
- Use protocols/abstract base classes
- `FastAPI` depends on `TaskRepositoryProtocol`, not `PostgresTaskRepository`

---

## 2. DRY (Don't Repeat Yourself)

### Code Reuse Standards
- Extract shared logic to utility modules
- Use base classes for common patterns
- Create composable UI components

### Examples:
```python
# BAD - Repeated validation
def create_task(name: str): validate_name(name)
def update_task(name: str): validate_name(name)

# GOOD - Reusable validator
@validate_task_name
def create_task(name: str): ...
@validate_task_name
def update_task(name: str): ...
```

### Shared Libraries Location:
- `/backend/shared/` - Common utilities, validators
- `/frontend/lib/` - Shared UI components, hooks
- `/shared/types/` - TypeScript types shared by frontend/backend

---

## 3. Test-Driven Development (TDD)

### Testing Requirements
- **Unit Tests**: 80%+ coverage for business logic
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user journeys (login → create task → assign)

### Test Structure
```
/tests/
├── unit/
│   ├── test_models.py
│   ├── test_services.py
│   └── test_mcp_tools.py
├── integration/
│   ├── test_api_endpoints.py
│   └── test_database.py
└── e2e/
    └── test_user_journeys.spec.ts
```

### TDD Workflow Per Feature:
1. Write failing test (Red)
2. Write minimal code to pass (Green)
3. Refactor for quality (Refactor)
4. Commit with test included

### Testing Tools:
- Backend: `pytest`, `pytest-cov`, `httpx` (for testing FastAPI)
- Frontend: `vitest`, `@testing-library/react`
- E2E: `playwright` (for browser tests)

---

## 4. Reusable Intelligence (Agent Skills & Subagents)

### Existing Agents & Skills in Project
TeamFlow leverages the following existing specialized agents and skills:

**Agents (@.claude/agents/):**
| Agent | Purpose | Skills Used |
|-------|---------|-------------|
| `openai-agents-sdk-specialist` | OpenAI Agents SDK implementation, debugging | `openai-agents-sdk-gemini` |
| `better-auth-specialist` | Better Auth integration expertise | `better-auth-integration` |
| `chatkit-integrator` | ChatKit UI integration | `chatbot-widget-creator` |
| `deployment-engineer` | CI/CD, Docker, K8s deployment | `deployment-engineer` |
| `rag-specialist` | RAG pipeline implementation | `rag-pipeline-builder` |
| `content-writer` | Documentation, content creation | `book-content-writer` |
| `docusaurus-architect` | Docusaurus site architecture | - |

**Skills (@.claude/skills/):**
| Skill | Purpose | Key Templates |
|-------|---------|---------------|
| `better-auth-integration` | Production auth with OAuth, 2FA, RBAC | Config schemas, React client, middleware |
| `deployment-engineer` | Battle-tested deployment patterns | Dockerfiles, CI/CD, K8s manifests |
| `chatbot-widget-creator` | ChatKit-based UI components | Complete widget system |
| `openai-agents-sdk-gemini` | OpenAI Agents SDK integration | MCP examples, agent patterns |
| `rag-pipeline-builder` | RAG implementation with vector search | Ingestion, chunking, FastAPI endpoints |
| `frontend-designer` | Frontend design with animations | Component patterns, animation strategies |
| `gemini-frontend-assistant` | AI-powered frontend generation | React component generation |

### When to Use Each Agent/Skill:
```yaml
# For authentication (Phase II+)
use_agent: better-auth-specialist
use_skill: better-auth-integration
when: "Implementing Better Auth with JWT, OAuth providers"

# For AI chatbot (Phase III)
use_agent: openai-agents-sdk-specialist
use_skill: openai-agents-sdk-gemini
when: "Building OpenAI Agents with MCP tools"

# For deployment (Phase IV+)
use_agent: deployment-engineer
use_skill: deployment-engineer
when: "Containerization, K8s, CI/CD setup"

# For frontend (Phase II+)
use_agent: chatkit-integrator
use_skill: chatbot-widget-creator
when: "Building chat UI with ChatKit"
```

### Create Additional TeamFlow-Specific Skills:
1. **Task CRUD Operations** - Reusable pattern for creating entities
2. **API Endpoint Generation** - Auto-generate CRUD routes
3. **Dockerfile Optimization** - Multi-stage builds
4. **K8s Deployment Patterns** - Service, Ingress, ConfigMap templates
5. **MCP Tool Creation** - Standard tool signature patterns
6. **Time Tracking** - Agency-specific time logging
7. **Profitability Calculator** - Project margin calculations

### Subagent Usage Rules:
- Launch subagent for files > 200 lines
- Use Explore agent for codebase discovery
- Use Plan agent for architecture decisions
- Each subagent has single, clear purpose

---

### Skill Refinement: Continuous Learning from Errors

**Principle**: Skills evolve through real-world debugging. Every error is an opportunity to improve the skill's knowledge base.

#### Skill Refinement Process:

```yaml
# When encountering an error during skill execution:
1. CAPTURE:
   - Document the exact error message
   - Note the context (framework version, environment, dependencies)
   - Record the stack trace
   - Save the code that caused the error

2. DIAGNOSE:
   - Identify root cause (version mismatch, missing config, incorrect pattern)
   - Research the solution (docs, community, debugging)
   - Test the fix locally

3. UPDATE SKILL:
   - Add to "Common Pitfalls & Solutions" section
   - Include: Problem → Cause → Solution → Files Affected
   - Add preventive checks to templates
   - Update version constraints if needed

4. VALIDATE:
   - Re-run scenario with updated skill
   - Ensure error is prevented
   - Document in skill version history
```

#### Skill Documentation Template (for each skill):

```markdown
## Common Pitfalls & Solutions (Version History)

### Error #N: [Brief Error Title]
**Problem**: [Exact error message]
```python
# Code that caused the error
```
**Root Cause**: [Why it happened]
**Solution**: [How to fix it]
```python
# Fixed code
```
**Files Affected**: [Which files need updating]
**Prevention**: [What to add to skill to prevent this]
**Skill Version**: [When this was added]
```

#### Example from deployment-engineer Skill:

```markdown
### Error #6: Hatchling README.md Not Found Error
**Problem**: `OSError: Readme file does not exist: README.md`

```dockerfile
# ❌ Wrong - README.md not copied before pip install
COPY pyproject.toml ./
RUN pip install --no-cache-dir -e .

# ✅ Correct - Copy README.md with pyproject.toml
COPY pyproject.toml README.md ./
RUN pip install --no-cache-dir -e .
```

**Root Cause**: `pyproject.toml` has `readme = "README.md"` but hatchling can't find it during install.

**Files Affected**: `Dockerfile`, `Dockerfile.hf`

**Prevention**: Updated Dockerfile template to always copy README.md with pyproject.toml

**Skill Version**: 1.2.0 - Added 2025-01-10
```

#### Skill Version History Template:

```markdown
## Skill Version History

| Version | Date | Changes | Errors Fixed |
|---------|------|---------|--------------|
| 1.0.0 | 2025-01-01 | Initial release | - |
| 1.1.0 | 2025-01-08 | Added SSR guard patterns | Docusaurus build errors |
| 1.2.0 | 2025-01-10 | Fixed Dockerfile pattern | Hatchling README errors |
| 1.3.0 | 2025-01-12 | Added async SQLAlchemy patterns | AsyncSession query errors |
```

#### Skill Refinement Commands:

```bash
# After debugging an error, update the skill:
/sp.phr --title "Fixed [Error Name] in [Skill Name]" \
         --stage general \
         --feature skill-refinement

# Document in skill file:
.claude/skills/[skill-name]/LESSONS_LEARNED.md
```

#### Required Sections in Every Skill:

1. **LESSONS_LEARNED.md** - All errors encountered and solutions
2. **VERSION_HISTORY.md** - Track skill evolution
3. **PREVENTION_CHECKLIST.md** - Pre-flight checks before using skill

#### Example LESSONS_LEARNED.md Structure:

```markdown
# [Skill Name] - Lessons Learned

## Critical Errors Fixed

### [Error 1]
- **When**: [Date]
- **Error**: [Message]
- **Impact**: [What broke]
- **Fix**: [Solution]
- **Prevention**: [Updated template/Check]

### [Error 2]
...

## Emerging Patterns

### Pattern 1: [Name]
- **Symptom**: [What we see]
- **Root Cause**: [Why it happens]
- **Standard Solution**: [How we fix it]

## Version-Specific Issues

### [Framework/Tool] Version [X.Y.Z]
- **Issue**: [Description]
- **Workaround**: [Temporary fix]
- **Permanent Fix**: [What we changed]
```

### Example Subagent Skills:
```yaml
skills:
  generate-crud-endpoints:
    description: Generate FastAPI CRUD endpoints for a model
    input: model_class, table_name
    output: full_router_with_validation

  optimize-dockerfile:
    description: Optimize Dockerfile for size and security
    input: Dockerfile
    output: multi-stage_optimized_version

  create-k8s-deployment:
    description: Create K8s Deployment + Service + Ingress
    input: app_name, image, port
    output: complete_yaml_manifests
```

---

## 5. MCP Server Integration Standards

### Required MCP Servers for Development:

| MCP Server | Purpose | Usage |
|------------|---------|-------|
| **context7** | Get latest library docs | `@context7` for Next.js, FastAPI docs |
| **github** | Repository operations | Create PRs, issues, manage releases |
| **chrome-devtools** | Browser testing | Test UI, take screenshots, debug |
| **web-search** | Research | Look up solutions, best practices |
| **zai-mcp-server** | Vision/Video | Analyze UI screenshots, demos |

### MCP Tool Usage Patterns:
```python
# When needing library docs
mcp_context7.get_library_docs("fastapi", topic="dependency injection")

# When managing GitHub
mcp_github.create_pull_request(title, body, head, base)

# When testing frontend
mcp_chrome.navigate_to(url)
mcp_chrome.take_snapshot()
mcp_chrome.click(uid="button-123")

# When researching approach
mcp_web_search("best practices FastAPI SQLModel")
```

### MCP Tool Creation Standards:
- All tools return structured JSON
- Tools are stateless (store state in DB)
- Tools have clear error messages
- Tools validate all inputs

---

## 6. Type Safety & Validation

### Python Standards:
```python
from typing import Protocol, TypeVar, Generic
from pydantic import BaseModel, Field, validator

# Use Pydantic for ALL API models
class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    priority: Priority = Field(default=Priority.MEDIUM)

    @validator('title')
    def title_not_empty(cls, v):
        if not v.strip():
            raise ValueError('Title cannot be empty')
        return v
```

### TypeScript Standards:
```typescript
// Use strict mode
// No `any` types without justification
// Prefer interfaces for public APIs, types for internal
```

---

## 7. API Design Principles

### RESTful Standards:
- GET: Fetch resources (no side effects)
- POST: Create resources (idempotent with key)
- PUT: Full update (idempotent)
- PATCH: Partial update (idempotent)
- DELETE: Remove resource (idempotent)

### Response Format:
```python
# Success
{
  "data": {...},
  "meta": {"page": 1, "total": 100}
}

# Error
{
  "error": {
    "code": "TASK_NOT_FOUND",
    "message": "Task 123 not found",
    "details": {"task_id": 123}
  }
}
```

---

## 8. Security Principles

### Authentication & Authorization:
- All API routes require valid JWT (Phase II+)
- User-scoped data filtering (no data leaks)
- Input validation on ALL endpoints
- SQL injection prevention (use parameterized queries)

### Secrets Management:
- NEVER commit secrets to git
- Use environment variables for config
- Use Dapr secret store or K8s secrets in production

---

## 9. Performance Standards

### Response Time Targets:
- API endpoints: < 200ms p95
- Database queries: < 50ms p95
- Frontend load: < 2s First Contentful Paint

### Optimization Techniques:
- Database indexes on foreign keys
- Pagination for list endpoints
- Lazy loading for frontend components
- Async/await for all I/O operations

---

## 10. Code Style Standards

### Python (PEP 8 + Black):
```python
# Use black formatter
# Use isort for imports
# Use pylint for linting
# Maximum line length: 100
```

### TypeScript/JavaScript:
```typescript
// Use ESLint + Prettier
// Use 2 space indentation
// Use double quotes
// No semicolons (configured in prettier)
```

---

## 11. Git Workflow

### Commit Message Format:
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types:
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change without functional change
- `test`: Adding tests
- `docs`: Documentation
- `chore`: Build/config changes

### Branch Naming:
- `feature/phase1-console-app`
- `feature/phase2-web-auth`
- `feature/phase3-chatbot`

---

## 12. Spec-Driven Development (SDD) Rules

### Non-Negotiable Rules:
1. **No code without spec** - Every feature starts with `/sp.specify`
2. **No code without task** - Every line maps to a task in `/sp.tasks`
3. **Update spec when changing requirements**
4. **Create ADR for architectural decisions**

### SDD Workflow:
```
User Request
    ↓
/sp.specify → Define WHAT
    ↓
/sp.plan → Define HOW
    ↓
/sp.tasks → Break down
    ↓
/sp.implement → Execute
    ↓
/sp.adr (if needed) → Document decisions
```

---

## 13. Phase-Specific Constraints

### Phase I (Console):
- NO database (in-memory only)
- NO authentication
- Simple commands, clear output

### Phase II (Web):
- Better Auth + JWT required
- Neon PostgreSQL required
- RESTful API documentation

### Phase III (Chatbot):
- OpenAI Agents SDK required
- MCP server with tools required
- Conversation state in DB

### Phase IV (K8s):
- All services containerized
- Minikube deployment
- Helm charts

### Phase V (Cloud):
- Kafka event streaming
- Dapr integration
- Production deployment

---

## 14. Documentation Requirements

### Code Comments:
- Docstrings for ALL functions/classes
- Inline comments for complex logic
- Type hints for ALL function parameters

### README Sections:
```markdown
# TeamFlow

## Overview
## Features
## Tech Stack
## Setup Instructions
## API Documentation
## Contributing
## License
```

---

## 15. Error Handling Standards

### Never Catch Broad Exceptions:
```python
# BAD
try:
    ...
except Exception:
    pass

# GOOD
try:
    ...
except TaskNotFoundError as e:
    logger.error(f"Task not found: {e}")
    raise HTTPException(404, str(e))
```

### User-Facing Errors:
- Clear, actionable error messages
- Never expose stack traces to users
- Log errors with context

---

## 16. Accessibility & i18n

### Frontend Standards:
- ARIA labels for interactive elements
- Keyboard navigation support
- High contrast mode support
- Urdu language support (Phase III+)

---

## Constitution Version History

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2025-01-15 | Initial constitution for TeamFlow |

---

## How Agents Use This Constitution

1. **Before ANY code change**: Read relevant sections
2. **When uncertain**: Consult constitution, don't guess
3. **When suggesting changes**: Reference constitution principles
4. **When reviewing**: Check against constitution standards

---

*This constitution is the single source of truth for TeamFlow development standards.*
*All AI agents (Claude, Copilot, etc.) MUST follow these principles.*
```

---

## Creating the Constitution: Next Steps

1. **Use `/sp.constitution` skill** - This will create/update `.specify/memory/constitution.md`
2. **Customize for TeamFlow** - Add agency-specific requirements
3. **Reference in CLAUDE.md** - Ensure agents read it first

---

*Plan and Constitution Design created by Claude Code using SpecKit Plus workflow*
