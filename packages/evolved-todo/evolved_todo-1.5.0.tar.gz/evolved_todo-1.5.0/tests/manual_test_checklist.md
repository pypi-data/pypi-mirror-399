# Manual Test Checklist: Phase I Todo CLI App

**Date**: 2025-12-29
**Tester**: [To be filled during testing]
**Branch**: 001-todo-cli-app

## Instructions
1. Launch application: `uv run python src/main.py`
2. For each scenario below, execute the steps manually
3. Mark [x] if PASS, [ ] if FAIL
4. Document failures with description and task number where fixed

---

## User Story 1 - Create and View Tasks (Priority: P1)

### Scenario 1.1: Create task with title and description
- [ ] **Given**: Application launched
- [ ] **When**: Select "1" (Add Task), enter title "Team meeting", description "Discuss Q1 goals"
- [ ] **Then**: Task created with unique ID (should be 1), status shows incomplete [ ]
- [ ] **Result**: PASS / FAIL (if fail, describe: _______________________)

### Scenario 1.2: View multiple tasks
- [ ] **Given**: Create 3 tasks (IDs 1, 2, 3)
- [ ] **When**: Select "2" (View Tasks)
- [ ] **Then**: All 3 tasks displayed with IDs, titles, descriptions, status indicators
- [ ] **Result**: PASS / FAIL

### Scenario 1.3: View empty task list
- [ ] **Given**: Fresh application start (no tasks)
- [ ] **When**: Select "2" (View Tasks)
- [ ] **Then**: Message "No tasks found" or similar (not an error)
- [ ] **Result**: PASS / FAIL

---

## User Story 2 - Mark Tasks Complete or Incomplete (Priority: P2)

### Scenario 2.1: Mark incomplete task as complete
- [ ] **Given**: Task ID 5 exists with incomplete status [ ]
- [ ] **When**: Select "5" (Toggle Status), enter ID 5
- [ ] **Then**: Task status changes to complete [✓], next view shows updated status
- [ ] **Result**: PASS / FAIL

### Scenario 2.2: Mark complete task as incomplete
- [ ] **Given**: Task ID 3 exists with complete status [✓]
- [ ] **When**: Select "5" (Toggle Status), enter ID 3
- [ ] **Then**: Task status changes to incomplete [ ], next view reflects change
- [ ] **Result**: PASS / FAIL

### Scenario 2.3: Toggle non-existent task
- [ ] **Given**: No task with ID 999
- [ ] **When**: Select "5" (Toggle Status), enter ID 999
- [ ] **Then**: Error message "Task with ID 999 not found" displayed
- [ ] **Result**: PASS / FAIL

---

## User Story 3 - Update Task Details (Priority: P3)

### Scenario 3.1: Update both title and description
- [ ] **Given**: Task ID 7 exists
- [ ] **When**: Select "3" (Update Task), enter ID 7, new title "New title", new description "New description"
- [ ] **Then**: Task retains ID and status, displays updated title and description
- [ ] **Result**: PASS / FAIL

### Scenario 3.2: Update only title
- [ ] **Given**: Task ID 2 exists
- [ ] **When**: Select "3" (Update Task), enter ID 2, new title "Updated title", press Enter for description
- [ ] **Then**: Only title updated, description and status unchanged
- [ ] **Result**: PASS / FAIL

### Scenario 3.3: Update non-existent task
- [ ] **Given**: No task with ID 999
- [ ] **When**: Select "3" (Update Task), enter ID 999
- [ ] **Then**: Error message "Task with ID 999 not found" displayed
- [ ] **Result**: PASS / FAIL

---

## User Story 4 - Delete Tasks (Priority: P4)

### Scenario 4.1: Delete existing task
- [ ] **Given**: Task ID 4 exists
- [ ] **When**: Select "4" (Delete Task), enter ID 4
- [ ] **Then**: Task removed from system, no longer appears in View Tasks
- [ ] **Result**: PASS / FAIL

### Scenario 4.2: Delete task from middle of list
- [ ] **Given**: Five tasks exist (IDs 1-5)
- [ ] **When**: Select "4" (Delete Task), enter ID 3
- [ ] **Then**: Tasks with IDs 1, 2, 4, 5 remain, ID 3 cannot be found
- [ ] **Result**: PASS / FAIL

### Scenario 4.3: Delete non-existent task
- [ ] **Given**: No task with ID 999
- [ ] **When**: Select "4" (Delete Task), enter ID 999
- [ ] **Then**: Error message "Task with ID 999 not found" displayed
- [ ] **Result**: PASS / FAIL

---

## User Story 5 - Navigate Application Menu (Priority: P5)

### Scenario 5.1: Display menu with all options
- [ ] **Given**: Application launched
- [ ] **When**: Main menu displayed
- [ ] **Then**: All 6 options visible and numbered (Add, View, Update, Delete, Toggle, Exit)
- [ ] **Result**: PASS / FAIL

### Scenario 5.2: Handle invalid menu selection
- [ ] **Given**: Main menu displayed
- [ ] **When**: Enter invalid option (e.g., 99)
- [ ] **Then**: Error displayed, menu re-displayed
- [ ] **Result**: PASS / FAIL

### Scenario 5.3: Return to menu after action
- [ ] **Given**: Any feature action completed
- [ ] **When**: Action finishes
- [ ] **Then**: Automatically returns to main menu
- [ ] **Result**: PASS / FAIL

---

## Summary
- **Total Scenarios**: 15
- **Passed**: ___
- **Failed**: ___
- **Pass Rate**: ___%

**Ready for Phase I Completion**: YES / NO

## Notes
Document any issues found during testing:
-
-
-
