# TeamFlow Project Constitution

## Purpose
This constitution defines the non-negotiable principles, patterns, and standards for the TeamFlow Agency CRM project. All AI agents (Claude, Copilot, etc.) MUST consult this file before making any architectural or implementation decisions.

## Project Vision
Build a Full CRM for Agencies (10-50 people) that evolves from a simple console app to an AI-powered, cloud-native task distribution system with drag-drop UX and agency-specific features (billing, time tracking, profitability).

---

## Core Principles

### I. Specialized Agents & Skills First (NON-NEGOTIABLE)
**ALWAYS check existing agents and skills BEFORE any implementation.**

- Agents located in: `.claude/agents/`
- Skills located in: `.claude/skills/`
- For ANY task, search for a relevant agent/skill first
- If an agent/skill exists, USE IT instead of manual implementation
- Only proceed with custom implementation when no relevant agent/skill exists

**Existing TeamFlow Agents & Skills:**
| Agent | Purpose | Skill Used |
|-------|---------|-------------|
| `openai-agents-sdk-specialist` | OpenAI Agents SDK implementation | `openai-agents-sdk-gemini` |
| `better-auth-specialist` | Better Auth integration | `better-auth-integration` |
| `chatkit-integrator` | ChatKit UI integration | `chatbot-widget-creator` |
| `deployment-engineer` | CI/CD, Docker, K8s | `deployment-engineer` |
| `rag-specialist` | RAG pipeline | `rag-pipeline-builder` |
| `content-writer` | Documentation | `book-content-writer` |
| `docusaurus-architect` | Docusaurus sites | - |

**Rationale**: Reuses proven patterns, captures institutional knowledge, prevents repeating errors, accelerates development.

### II. SOLID Principles (NON-NEGOTIABLE)

**Single Responsibility Principle (SRP):** Every module/class/function has ONE reason to change.
- `TaskService` ONLY handles task logic (not auth, not notifications)
- `APIRouter` ONLY routes requests (no business logic)
- Component files contain ONE component (no multiple exports)

**Open/Closed Principle (OCP):** Open for extension, closed for modification.
- Use dependency injection for swappable implementations
- Strategy pattern for different AI providers (OpenAI, Anthropic)

**Liskov Substitution Principle (LSP):** Subtypes must be substitutable for their base types.
- All `TaskRepository` implementations must work identically
- MCP tools must have consistent signatures

**Interface Segregation Principle (ISP):** Clients shouldn't depend on unused interfaces.
- Split `UserService` into `UserQuery`, `UserCommand`, `UserAuth`
- Separate read/write interfaces (CQRS pattern)

**Dependency Inversion Principle (DIP):** Depend on abstractions, not concretions.
- Use protocols/abstract base classes
- `FastAPI` depends on `TaskRepositoryProtocol`, not `PostgresTaskRepository`

### III. DRY (Don't Repeat Yourself)

Extract shared logic to utility modules. Use base classes for common patterns. Create composable UI components.

**Shared Libraries Location:**
- `/backend/shared/` — Common utilities, validators
- `/frontend/lib/` — Shared UI components, hooks
- `/shared/types/` — TypeScript types shared by frontend/backend

### IV. Test-Driven Development (NON-NEGOTIABLE)

**Testing Requirements:**
- **Unit Tests**: 80%+ coverage for business logic
- **Integration Tests**: All API endpoints
- **E2E Tests**: Critical user journeys (login → create task → assign)

**Test Structure:**
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

**TDD Workflow Per Feature:**
1. Write failing test (Red)
2. Write minimal code to pass (Green)
3. Refactor for quality (Refactor)
4. Commit with test included

**Testing Tools:**
- Backend: `pytest`, `pytest-cov`, `httpx` (for testing FastAPI)
- Frontend: `vitest`, `@testing-library/react`
- E2E: `playwright` (for browser tests)

### V. Spec-Driven Development (NON-NEGOTIABLE)

**No code without spec.** Every feature starts with `/sp.specify`.

**SDD Workflow:**
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

### VI. Type Safety & Validation

**Python Standards (UV Required):**
- **Package Manager:** Use `uv` for all Python dependency management (fast, modern).
- Use Pydantic for ALL API models
- Type hints for ALL function parameters
- Use `Protocol` for abstract interfaces

**TypeScript Standards (NPM Required):**
- **Package Manager:** Use `npm` for all Frontend/Next.js dependency management.
- Strict mode enabled
- No `any` types without justification
- Prefer interfaces for public APIs, types for internal

### VII. Security Principles

**Authentication & Authorization:**
- All API routes require valid JWT (Phase II+)
- User-scoped data filtering (no data leaks)
- Input validation on ALL endpoints
- SQL injection prevention (use parameterized queries)

**Secrets Management:**
- NEVER commit secrets to git
- Use environment variables for config
- Use Dapr secret store or K8s secrets in production

### VIII. Performance Standards

**Response Time Targets:**
- API endpoints: < 200ms p95
- Database queries: < 50ms p95
- Frontend load: < 2s First Contentful Paint

**Optimization Techniques:**
- Database indexes on foreign keys
- Pagination for list endpoints
- Lazy loading for frontend components
- Async/await for all I/O operations

### IX. Code Style Standards

**Python (PEP 8 + Black):**
- Use black formatter
- Use isort for imports
- Use pylint for linting
- Maximum line length: 100

**TypeScript/JavaScript:**
- Use ESLint + Prettier
- Use 2 space indentation
- Use double quotes
- No semicolons (configured in prettier)

### X. MCP Server Integration Standards

**Required MCP Servers for Development:**
| MCP Server | Purpose | Usage |
|------------|---------|-------|
| **context7** | Get latest library docs | `@context7` for Next.js, FastAPI docs |
| **github** | Repository operations | Create PRs, issues, manage releases |
| **chrome-devtools** | Browser testing | Test UI, take screenshots, debug |
| **web-search** | Research | Look up solutions, best practices |
| **zai-mcp-server** | Vision/Video | Analyze UI screenshots, demos |

**MCP Tool Creation Standards:**
- All tools return structured JSON
- Tools are stateless (store state in DB)
- Tools have clear error messages
- Tools validate all inputs

### XI. Skill Refinement: Continuous Learning

Skills evolve through real-world debugging. Every error is an opportunity to improve the skill's knowledge base.

**Skill Refinement Process:**
1. **CAPTURE**: Document error message, context, stack trace
2. **DIAGNOSE**: Identify root cause, research solution, test fix
3. **UPDATE SKILL**: Add to "Common Pitfalls & Solutions" section
4. **VALIDATE**: Re-run scenario, ensure error is prevented, document version history

**Required Sections in Every Skill:**
1. `LESSONS_LEARNED.md` — All errors encountered and solutions
2. `VERSION_HISTORY.md` — Track skill evolution
3. `PREVENTION_CHECKLIST.md` — Pre-flight checks before using skill

### XII. Mandatory Documentation Lookup (NON-NEGOTIABLE)
**NEVER implement code based on assumptions or stale internal knowledge.**

Before writing a single line of code or finalizing an architectural plan:
1. Use the **context7** MCP tool (`resolve-library-id` then `get-library-docs`) for every primary library in the task.
2. Verify API signatures, latest version features, and recommended patterns.
3. If documentation is unavailable via context7, use **web-search** as a fallback.
4. Document the version of the library consulted in the implementation notes.

---

## Phase-Specific Constraints

### Phase I (Console App)
- NO database (in-memory only)
- NO authentication
- Simple commands, clear output

### Phase II (Web Application)
- Better Auth + JWT required
- Neon PostgreSQL required
- RESTful API documentation

### Phase III (AI Chatbot)
- OpenAI Agents SDK required
- MCP server with tools required
- Conversation state in DB

### Phase IV (Kubernetes Deployment)
- All services containerized
- Minikube deployment
- Helm charts

### Phase V (Cloud Production)
- Kafka event streaming
- Dapr integration
- Production deployment

---

## API Design Principles

### RESTful Standards
- GET: Fetch resources (no side effects)
- POST: Create resources (idempotent with key)
- PUT: Full update (idempotent)
- PATCH: Partial update (idempotent)
- DELETE: Remove resource (idempotent)

### Response Format
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

## Git Workflow

### Commit Message Format
```
<type>(<scope>): <subject>

<body>

<footer>
```

### Types
- `feat`: New feature
- `fix`: Bug fix
- `refactor`: Code change without functional change
- `test`: Adding tests
- `docs`: Documentation
- `chore`: Build/config changes

### Branch Naming
- `feature/phase1-console-app`
- `feature/phase2-web-auth`
- `feature/phase3-chatbot`

### Submission Branch Strategy
For hackathon phase submissions (permanent snapshots):
1. **Freeze**: `git checkout -b submission/phase-X` (from completed main/feature branch)
2. **Push**: `git push origin submission/phase-X`
3. **Submit**: Use the URL `.../tree/submission/phase-X` for the phase submission.
4. **Continue**: Return to `main` for the next phase.

---

## Error Handling Standards

### Never Catch Broad Exceptions
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

### User-Facing Errors
- Clear, actionable error messages
- Never expose stack traces to users
- Log errors with context

---

## Documentation Requirements

### Code Comments
- Docstrings for ALL functions/classes
- Inline comments for complex logic
- Type hints for ALL function parameters

### README Sections
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

## Accessibility & i18n

### Frontend Standards
- ARIA labels for interactive elements
- Keyboard navigation support
- High contrast mode support
- Urdu language support (Phase III+)

---

## Constitution Check

When creating implementation plans, verify:
- [ ] Existing agents/skills consulted first
- [ ] SOLID principles followed
- [ ] DRY applied (no code duplication)
- [ ] Tests written first (TDD)
- [ ] Type safety enforced
- [ ] Security standards met
- [ ] Performance targets defined
- [ ] MCP tools considered for integration
- [ ] Skill refinement documented if errors encountered

---

## Governance

### Amendment Procedure
1. Propose amendment with rationale
2. Document in ADR if architectural decision
3. Update version per semantic versioning
4. Update dependent templates (plan, spec, tasks)
5. Communicate changes to team

### Versioning Policy
- **MAJOR**: Backward incompatible governance/principle removals or redefinitions
- **MINOR**: New principle/section added or materially expanded guidance
- **PATCH**: Clarifications, wording, typo fixes, non-semantic refinements

### Compliance Review
- All PRs must verify compliance with constitution principles
- Complexity must be justified (refer to ADRs)
- Use `CLAUDE.md` for runtime development guidance

---

**Version**: 1.0.0 | **Ratified**: 2025-01-15 | **Last Amended**: 2025-01-15
