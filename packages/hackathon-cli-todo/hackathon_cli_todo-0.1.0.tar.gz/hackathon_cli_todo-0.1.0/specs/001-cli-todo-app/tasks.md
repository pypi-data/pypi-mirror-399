# Tasks: CLI Todo App - Phase 1

**Input**: Design documents from `/specs/001-cli-todo-app/`
**Prerequisites**: plan.md, spec.md, data-model.md, contracts/cli-commands.md, quickstart.md
**Feature Branch**: `001-cli-todo-app` | **Generated**: 2025-12-30

**Tests**: Unit tests and integration tests included per Constitution VI (80% coverage target)

**Project Structure** (flat, per plan.md):
```
src/
├── main.py        # App entry point (menu + loop)
├── todo.py        # Task CRUD logic
└── models.py      # Task data model

pyproject.toml           # uv project config
uv.lock                  # Dependency lock file
README.md                # User-facing documentation
tests/                   # Test files
```

## Format: `[ID] [P?] [Story] Description`

- **[P]**: Can run in parallel (different files, no dependencies)
- **[Story]**: Which user story this task belongs to (e.g., US1, US2, US3)
- Include exact file paths in descriptions

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Project initialization and basic structure

- [ ] T001 Create `pyproject.toml` with Python 3.13+, uv, pytest, mypy, ruff
- [ ] T002 [P] Configure ruff (linting + formatting) in `pyproject.toml`
- [ ] T003 [P] Configure mypy for type checking in `pyproject.toml`
- [ ] T004 Create `src/` directory with `__init__.py`
- [ ] T005 Create `tests/` directory

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Core infrastructure that MUST be complete before ANY user story can be implemented

**CRITICAL**: No user story work can begin until this phase is complete

- [ ] T006 [P] Implement `TaskStatus` enum in `src/models.py`
- [ ] T007 [P] Implement `Task` dataclass in `src/models.py` with validation
- [ ] T008 [P] Implement `TodoError`, `ValidationError`, `IndexOutOfBoundsError` in `src/models.py`
- [ ] T009 Create `TodoService` class skeleton in `src/todo.py`

**Checkpoint**: Foundation ready - user story implementation can now begin in parallel

---

## Phase 3: User Story 1 - Add Tasks (Priority: P1) MVP

**Goal**: Users can add new tasks to their todo list with title validation

**Independent Test**: Run CLI, add tasks, verify tasks appear in list output with correct title and "pending" status

### Tests for User Story 1

> **NOTE: Write these tests FIRST, ensure they FAIL before implementation**

- [ ] T010 [P] [US1] Unit test for Task validation in `tests/test_models.py`
- [ ] T011 [P] [US1] Unit test for TodoService.add_task() in `tests/test_todo.py`
- [ ] T012 [P] [US1] Integration test for add task CLI flow in `tests/test_cli.py`

### Implementation for User Story 1

- [ ] T013 [US1] Implement TodoService.add_task() in `src/todo.py`
- [ ] T014 [US1] Implement CLI add command in `src/main.py`
- [ ] T015 [US1] Add input validation for empty/whitespace-only titles
- [ ] T016 [US1] Connect CLI add command to TodoService.add_task()

**Checkpoint**: User Story 1 complete - users can add validated tasks to the list

---

## Phase 4: User Story 2 - List Tasks (Priority: P1)

**Goal**: Users can view all tasks with their titles and completion status

**Independent Test**: Add tasks, run list command, verify output shows all tasks with correct titles and status indicators

### Tests for User Story 2

- [ ] T017 [P] [US2] Unit test for TodoService.list_tasks() in `tests/test_todo.py`
- [ ] T018 [P] [US2] Integration test for list tasks CLI flow in `tests/test_cli.py`

### Implementation for User Story 2

- [ ] T019 [US2] Implement TodoService.list_tasks() in `src/todo.py`
- [ ] T020 [US2] Implement CLI list command in `src/main.py`
- [ ] T021 [US2] Handle empty state ("No tasks yet. Add one!")
- [ ] T022 [US2] Format output with `[ ]` for pending, `[x]` for completed

**Checkpoint**: User Story 2 complete - users can view all tasks

---

## Phase 5: User Story 3 - Mark Tasks Complete (Priority: P1)

**Goal**: Users can mark any task by index as completed

**Independent Test**: Add tasks, complete one, verify list shows correct status for that task

### Tests for User Story 3

- [ ] T023 [P] [US3] Unit test for TodoService.complete_task() in `tests/test_todo.py`
- [ ] T024 [P] [US3] Integration test for complete task CLI flow in `tests/test_cli.py`

### Implementation for User Story 3

- [ ] T025 [US3] Implement TodoService.complete_task() in `src/todo.py`
- [ ] T026 [US3] Implement CLI complete command in `src/main.py`
- [ ] T027 [US3] Validate task index exists before marking complete
- [ ] T028 [US3] Handle already-completed tasks gracefully

**Checkpoint**: User Story 3 complete - users can mark tasks as complete

---

## Phase 6: User Story 4 - Delete Tasks (Priority: P2)

**Goal**: Users can remove tasks by index, with automatic index renumbering

**Independent Test**: Add tasks, delete one, verify remaining tasks have updated indices

### Tests for User Story 4

- [ ] T029 [P] [US4] Unit test for TodoService.delete_task() in `tests/test_todo.py`
- [ ] T030 [P] [US4] Integration test for delete task CLI flow in `tests/test_cli.py`

### Implementation for User Story 4

- [ ] T031 [US4] Implement TodoService.delete_task() in `src/todo.py`
- [ ] T032 [US4] Implement CLI delete command in `src/main.py`
- [ ] T033 [US4] Validate task index exists before deleting
- [ ] T034 [US4] Ensure remaining tasks are renumbered correctly

**Checkpoint**: User Story 4 complete - users can delete tasks

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Improvements that affect multiple user stories

- [ ] T035 Create `src/__main__.py` entry point for `python -m src`
- [ ] T036 Implement main menu loop in `src/main.py`
- [ ] T037 [P] Implement exit command with exit code 0
- [ ] T038 [P] Handle keyboard interrupt (Ctrl+C) gracefully
- [ ] T039 [P] Ensure all errors print to stderr with appropriate messages
- [ ] T040 [P] Run full test suite with `uv run pytest --cov=src`
- [ ] T041 [P] Run type check with `uv run mypy src/`
- [ ] T042 [P] Run lint check with `uv run ruff check src/`
- [ ] T043 [P] Run format check with `uv run ruff format src/`
- [ ] T044 [P] Verify startup time < 2 seconds
- [ ] T045 [P] Verify task operations < 100ms
- [ ] T046 [P] Update/create `README.md` with usage instructions

---

## Dependencies & Execution Order

### Phase Dependencies

| Phase | Depends On | Blocks |
|-------|-----------|--------|
| Phase 1: Setup | None | Phase 2 |
| Phase 2: Foundational | Phase 1 | All User Stories |
| Phase 3: US1 - Add Tasks | Phase 2 | Phase 7 |
| Phase 4: US2 - List Tasks | Phase 2 | Phase 7 |
| Phase 5: US3 - Complete Tasks | Phase 2 | Phase 7 |
| Phase 6: US4 - Delete Tasks | Phase 2 | Phase 7 |
| Phase 7: Polish | All User Stories | None |

### User Story Dependencies

- **User Story 1 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 2 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 3 (P1)**: Can start after Foundational - No dependencies on other stories
- **User Story 4 (P2)**: Can start after Foundational - No dependencies on other stories

**Note**: All user stories can proceed in parallel after Foundational phase completes since they share the same models and service layer.

### Within Each User Story

1. Tests (Txxx) MUST be written and FAIL before implementation
2. Models → Service methods → CLI commands within each story
3. Core implementation → Validation → Integration
4. Story complete before moving to Polish phase

### Parallel Opportunities

| Within Phase | Parallel Tasks |
|--------------|----------------|
| Phase 1 | T001, T002, T003, T004, T005 (all different files) |
| Phase 2 | T006, T007, T008, T009 (models/service parallel) |
| US1 Tests | T010, T011, T012 (different test files) |
| US1 Implementation | T013, T014 (service and CLI parallel) |
| US2 Tests | T017, T018 |
| US2 Implementation | T019, T020, T021, T022 |
| US3 Tests | T023, T024 |
| US3 Implementation | T025, T026, T027, T028 |
| US4 Tests | T029, T030 |
| US4 Implementation | T031, T032, T033, T034 |
| Phase 7 | T035, T036, T037, T038, T039, T040, T041, T042, T043, T044, T045, T046 |

---

## Parallel Example: User Story 1

```bash
# Launch all tests for User Story 1 together:
Task T010: tests/test_models.py (Task validation)
Task T011: tests/test_todo.py (TodoService.add_task)
Task T012: tests/test_cli.py (CLI add flow)

# Launch all implementation for User Story 1 together:
Task T013: src/todo.py (add_task method)
Task T014: src/main.py (add command)
```

---

## Implementation Strategy

### MVP First (User Story 1 Only)

1. Complete Phase 1: Setup
2. Complete Phase 2: Foundational
3. Complete Phase 3: User Story 1
4. **STOP and VALIDATE**: Test User Story 1 independently
5. Deploy/demo if ready (add tasks only)

### Incremental Delivery

1. Complete Setup + Foundational → Foundation ready
2. Add User Story 1 → Test independently → Deploy/Demo (MVP!)
3. Add User Story 2 → Test independently → Deploy/Demo
4. Add User Story 3 → Test independently → Deploy/Demo
5. Add User Story 4 → Test independently → Deploy/Demo
6. Polish phase → Final release
7. Each story adds value without breaking previous stories

### Parallel Team Strategy

With multiple developers:

1. Team completes Setup + Foundational together
2. Once Foundational is done:
   - Developer A: User Story 1 (Add Tasks)
   - Developer B: User Story 2 (List Tasks)
   - Developer C: User Story 3 (Complete Tasks) + User Story 4 (Delete Tasks)
3. Stories complete and integrate independently

---

## Summary

| Metric | Value |
|--------|-------|
| **Total Tasks** | 46 |
| **Parallelizable Tasks** | 23 (marked with [P]) |
| **User Stories** | 4 (3 P1, 1 P2) |
| **Phases** | 7 |
| **Source Files** | 3 (src/models.py, src/todo.py, src/main.py) |
| **Test Files** | 3 (tests/test_models.py, tests/test_todo.py, tests/test_cli.py) |

### Tasks per User Story

| User Story | Tasks | Priority |
|------------|-------|----------|
| US1: Add Tasks | T010-T016 | P1 (MVP) |
| US2: List Tasks | T017-T022 | P1 |
| US3: Complete Tasks | T023-T028 | P1 |
| US4: Delete Tasks | T029-T034 | P2 |

### Suggested MVP Scope

**User Story 1 only** (Add Tasks) delivers a minimal viable product:
- Users can start the app
- Users can add tasks with validation
- Tasks are stored in memory
- Users can see basic help/feedback

This MVP can be demoed and validated before implementing remaining stories.

---

## Notes

- **[P]** tasks = different files, no dependencies on incomplete tasks
- **[Story]** label maps task to specific user story for traceability
- Each user story should be independently completable and testable
- Verify tests fail before implementing (TDD approach)
- Commit after each task or logical group
- Stop at any checkpoint to validate story independently
- All error messages go to stderr; exit codes 0 (success) / 1 (error)
