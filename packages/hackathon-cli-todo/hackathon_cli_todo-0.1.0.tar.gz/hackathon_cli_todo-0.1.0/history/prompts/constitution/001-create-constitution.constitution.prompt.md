---
id: '001'
title: Create Constitution for CLI Todo App
stage: constitution
date: '2025-12-30'
surface: agent
model: claude-sonnet-4-5-20250929
feature: none
branch: master
user: User
command: /sp.constitution
labels: [constitution, governance, project-setup]
links:
  spec: null
  ticket: null
  adr: null
  pr: null
files:
  - .specify/memory/constitution.md
tests: []
---

## Prompt

Generate a Constitution file for a command-line Todo application.
The project is a Python 3.13+ and uv console-based todo app that stores tasks in memory.
It follows spec-driven development using Claude Code and Spec-Kit Plus.
The Constitution should define:
- Project purpose and scope (console-only, in-memory)
- Core principles (clean code, simplicity)
- Allowed and disallowed features
- Coding standards and structure rules
- Specification-first workflow expectations
Keep it concise, formal, and suitable for an educational software project.
Output only the Constitution content in markdown format.

## Response snapshot

Created comprehensive constitution with 6 core principles: Console-Only Interface, In-Memory Storage, Clean Code Standards, Specification-First Development, Simplicity Over Complexity, and Testable Design. Defined scope (in/out), coding standards, project structure, and development workflow.

## Outcome

- ✅ Impact: Established foundational governance document for CLI Todo App project
- 🧪 Tests: N/A - governance document
- 📁 Files: .specify/memory/constitution.md
- 🔁 Next prompts: /sp.specify for first feature
- 🧠 Reflection: Constitution now guides all future development decisions

## Evaluation notes (flywheel)

- Failure modes observed: N/A
- Graders run and results (PASS/FAIL): N/A
- Prompt variant (if applicable): N/A
- Next experiment (smallest change to try): N/A
