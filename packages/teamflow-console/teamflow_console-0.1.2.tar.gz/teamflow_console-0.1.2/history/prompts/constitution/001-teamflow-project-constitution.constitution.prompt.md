---
id: 001
title: TeamFlow Project Constitution
stage: constitution
date: 2025-01-15
surface: agent
model: claude-opus-4-5-20251101
feature: none
branch: master
user: owais_abdullah
command: /sp.constitution
labels: ["constitution", "governance", "spec-driven-development"]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
 - .specify/memory/constitution.md
 - CLAUDE.md
 - TEAMFLOW-PLAN.md
tests:
 - No tests (constitution document)
---

## Prompt

User ran `/sp.constitution` with comprehensive TeamFlow Project Constitution content including:

### Core Principles (11 total):
I. Specialized Agents & Skills First (NON-NEGOTIABLE)
II. SOLID Principles (NON-NEGOTIABLE)
III. DRY (Don't Repeat Yourself)
IV. Test-Driven Development (NON-NEGOTIABLE)
V. Spec-Driven Development (NON-NEGOTIABLE)
VI. Type Safety & Validation
VII. Security Principles
VIII. Performance Standards
IX. Code Style Standards
X. MCP Server Integration Standards
XI. Skill Refinement: Continuous Learning

### Phase-Specific Constraints:
- Phase I (Console App): NO database, NO authentication, simple commands
- Phase II (Web Application): Better Auth + JWT required, Neon PostgreSQL required
- Phase III (AI Chatbot): OpenAI Agents SDK required, MCP server with tools required
- Phase IV (Kubernetes Deployment): All services containerized, Minikube deployment, Helm charts
- Phase V (Cloud Production): Kafka event streaming, Dapr integration, Production deployment

### Additional Sections:
- API Design Principles (RESTful standards, response format)
- Git Workflow (commit message format, types, branch naming)
- Error Handling Standards (never catch broad exceptions, user-facing errors)
- Documentation Requirements (code comments, README sections)
- Accessibility & i18n (ARIA labels, keyboard navigation, Urdu support)
- Constitution Check (compliance verification checklist)
- Governance (amendment procedure, versioning policy, compliance review)

### Key Requirement:
Include existing agents/skills in the project and mention skill refinement process for capturing errors and solutions.

## Response snapshot

Successfully created `.specify/memory/constitution.md` with comprehensive TeamFlow Project Constitution (Version 1.0.0, Ratified 2025-01-15).

**Key highlights:**
- 11 Core Principles with Specialized Agents & Skills First as Principle I
- Existing agents/skills documented: openai-agents-sdk-specialist, better-auth-specialist, chatkit-integrator, deployment-engineer, rag-specialist, content-writer, docusaurus-architect
- Skill refinement process with LESSONS_LEARNED.md, VERSION_HISTORY.md, PREVENTION_CHECKLIST.md templates
- Phase-specific constraints for all 5 phases of TeamFlow evolution
- Governance section with amendment procedure and versioning policy

## Outcome

- ✅ Impact: Constitution established as single source of truth for TeamFlow development standards
- 🧪 Tests: No tests (constitution document)
- 📁 Files: `.specify/memory/constitution.md` created with 381 lines of governance standards
- 🔁 Next prompts: `/sp.specify` for Phase I console app specification
- 🧠 Reflection: Constitution provides guardrails for all AI agents (Claude, Copilot) working on TeamFlow project

## Evaluation notes (flywheel)

- Failure modes observed: None
- Graders run and results (PASS/FAIL): N/A (governance document)
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): Create Phase I specification using `/sp.specify`
