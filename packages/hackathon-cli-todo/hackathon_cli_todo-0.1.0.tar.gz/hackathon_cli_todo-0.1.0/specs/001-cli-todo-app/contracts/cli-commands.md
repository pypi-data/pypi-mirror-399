# CLI Command Contract: CLI Todo App - Phase 1

**Feature Branch**: `001-cli-todo-app` | **Date**: 2025-12-30
**Source**: [spec.md](../spec.md) | **Plan**: [plan.md](../plan.md)

## Command Interface

The CLI uses an interactive text-based menu loop. No command-line arguments in Phase 1.

```
$ python -m src
```

## Main Menu

```
=== Todo App ===
1. Add task
2. List tasks
3. Complete task
4. Delete task
5. Exit
```

## Commands

### 1. Add Task

**Prompt**: `Enter task title: `

**Input**: String (1-200 chars, non-empty after strip)

**Success Output**:
```
Task added: "{title}"
```

**Error Output**:
```
Error: Task title cannot be empty.
```

**Exit Code**: 1 (on error)

---

### 2. List Tasks

**Prompt**: None (immediate display)

**Output Format**:
```
=== Tasks ===
1. [ ] Buy groceries
2. [x] Call dentist
3. [ ] Finish report
```

**Empty State**:
```
No tasks yet. Add one!
```

**Legend**: `[ ]` = pending, `[x]` = completed

---

### 3. Complete Task

**Prompt**: `Enter task number to complete: `

**Input**: Integer (1-based index)

**Success Output**:
```
Task "{title}" marked as complete.
```

**Error Output**:
```
Error: Invalid task number: {n}.
```

---

### 4. Delete Task

**Prompt**: `Enter task number to delete: `

**Input**: Integer (1-based index)

**Success Output**:
```
Task "{title}" deleted.
```

**Error Output**:
```
Error: Invalid task number: {n}.
```

---

### 5. Exit

**Output**: None

**Exit Code**: 0

## Error Handling

All errors output to stderr with descriptive messages. The application continues running after errors (no crash).

### Common Error Messages

| Condition | Message |
|-----------|---------|
| Empty title | `Error: Task title cannot be empty.` |
| Invalid index | `Error: Invalid task number: {n}.` |
| Already completed | `Error: Task is already complete.` |

## Session Behavior

- Application starts with empty task list
- Tasks persist in memory for session duration only
- Exit command (5) terminates with code 0
- Keyboard interrupt (Ctrl+C) terminates gracefully with code 0
