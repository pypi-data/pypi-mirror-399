# CLI Todo App Constitution

## Core Principles

### I. Console-Only Interface

This application MUST operate exclusively through a command-line interface. No graphical user interface, web interface, or TUI library with complex visual components is permitted. User interaction occurs via stdin/stdout/stderr with text-based output. This constraint ensures educational clarity and minimal dependency complexity.

### II. In-Memory Storage

All task data MUST be stored in memory only. No file I/O, database connections, or external persistence mechanisms are permitted. Data persists only for the duration of a single process execution. This constraint emphasizes application logic over data management complexity.

### III. Clean Code Standards

All code MUST adhere to PEP 8 style guidelines with strict typing using Python 3.13+ type hints and uv package. Functions MUST have single responsibilities and be under 30 lines where practical. Variable names MUST be descriptive and self-documenting. Magic numbers and hardcoded values MUST be replaced with named constants. Comments explain "why", not "what"—code should be self-explanatory. Use simple file structure and minimized code with clean structure.

### IV. Specification-First Development

All features MUST originate from a formal feature specification before implementation begins. Specifications MUST include user stories with acceptance criteria, functional requirements, and success metrics. No feature may be implemented without documented requirements approved through the specification process defined in `.specify/templates/spec-template.md`.

### V. Simplicity Over Complexity

The application MUST prioritize the simplest viable solution for every problem. YAGNI (You Aren't Gonna Need It) principles guide feature selection. Over-engineering, premature abstraction, and speculative functionality are prohibited. Each feature MUST justify its existence through clear user value.

### VI. Testable Design

All core functionality MUST be independently testable through unit tests. Pure functions are preferred over those with side effects. Dependencies MUST be injectable to enable mocking in tests. Integration tests verify CLI behavior without external dependencies.

## Scope and Constraints

### In Scope

- Adding, listing, completing, and deleting tasks
- Task priority and categorization
- Command-line argument parsing
- In-memory task collection management
- Basic input validation and error handling
- Specification-driven development workflow
- Runs until the user ends the session

### Out of Scope

- Persistent storage (files, databases)
- User authentication or accounts
- Data synchronization across sessions
- GUI, web, or rich TUI interfaces
- Network communication or APIs
- Plugins or extension systems

## Coding Standards

### Project Structure

```
src/
├── main.py        # App entry point (menu + loop)
├── todo.py        # Task CRUD logic
└── models.py      # Task data model
```

### Code Quality Rules

- All public functions MUST have type annotations and docstrings
- All modules MUST include `from __future__ import annotations`
- Cyclomatic complexity MUST NOT exceed 10 per function
- Tests MUST achieve 80% coverage on core logic
- Imports MUST be sorted alphabetically within categories

### Error Handling

- Errors MUST output to stderr with clear messages
- Exit codes MUST follow convention: 0 for success, 1 for errors
- Invalid input MUST produce helpful usage guidance
- Exceptions MUST NOT leak internal details to users

## Development Workflow

### Specification-Driven Process

1. User provides feature description
2. Architect creates specification using `/sp.specify`
3. Plan created using `/sp.plan` with architecture decisions
4. Tasks generated using `/sp.tasks` from specification
5. Implementation follows Red-Green-Refactor cycle
6. All changes verified against specification

### Compliance Verification

All pull requests and implementations MUST verify:
- Specification coverage: All acceptance criteria met
- Code quality: Type checks pass, no linting errors
- Tests: All tests pass with adequate coverage
- Simplicity: No unnecessary complexity added

## Governance

This constitution establishes the foundational rules for the CLI Todo App project. Amendments require documentation of rationale, impact assessment, and migration plan where applicable. All team members MUST verify compliance with these principles before merging changes. Runtime development guidance is documented in feature-specific quickstart files.

**Version**: 1.0.0 | **Ratified**: 2025-12-30 | **Last Amended**: 2025-12-30
