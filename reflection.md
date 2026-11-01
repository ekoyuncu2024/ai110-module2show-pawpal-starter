# PawPal+ reflection

## Authorship and scope

This is an AI-assisted implementation reflection prepared with Codex. It describes decisions and evidence from this build, rather than inventing personal classroom experiences. The student should review the code, run the walkthrough, and add their own learning observations before submitting. No separate algorithm/testing chats were used during this build.

## 1. System Design

### Three core user actions

1. Add a pet to an owner's household.
2. Schedule a feeding, walk, medication reminder, or appointment for a pet.
3. View a chronological schedule, resolve same-time warnings, and mark care complete.

### 1a. Initial design

The initial Mermaid diagram defined four classes. Owner manages pets, Pet stores details and tasks, Task stores a description, time, frequency, and completion status, and Scheduler organizes tasks obtained through Owner. Task and Pet use Python dataclasses with independent lists created through default factories. Owner and Scheduler also use dataclasses. The first Git commit preserves this diagram and the matching skeletons before implementation.

### 1b. Design changes

The draft's time-only Task could not represent tomorrow or distinguish equal times on different dates. The final Task adds due_date, a generated task_id, validation, and next_occurrence(). The identifier lets the UI complete the correct task even if two descriptions match. Owner.get_all_tasks() returns pet-task pairs so filtering and warnings retain pet identity. Scheduler gained schedule_task(), filter_tasks(), get_schedule(), mark_task_complete(), and detect_conflicts(). The final UML records these additions; the draft intentionally preserves the original plan.

Recurrence is coordinated by Scheduler because it can attach the successor to the correct pet. Task.mark_complete() remains a simple status operation; callers wanting automatic recurrence must use Scheduler.mark_task_complete(). The UI and CLI do this consistently.

## 2. Algorithmic Layer

### 2a. Scheduling decisions

Sorting uses a stable sorted() call with a (due_date, time) key. Strict zero-padded HH:MM validation makes string order chronological within a day. Filtering combines pet, status, and date predicates. Conflict detection groups pending tasks by exact date/time and emits one warning per conflicting group, including conflicts across pets.

Daily and weekly completion produces a new pending Task with a fresh identity and the same description/time/frequency. The anchor is the later of the scheduled date and the completion date: normal daily completion creates tomorrow's task; overdue completion avoids creating another overdue task; early completion does not move the routine earlier than its scheduled cycle. A completed task cannot generate another successor on a repeated click.

### 2b. Tradeoffs

The scheduler checks exact times rather than overlapping durations. This is easy to explain and matches the required lightweight behavior, but a long appointment can overlap a later walk without a warning. Dates use the server's local calendar; timezone conversion is outside this project. Recurrence creates only the next task on completion rather than expanding an unlimited future calendar. Data lives in session memory, so durable storage would be a useful next improvement. Domain lists remain mutable for this small educational design; callers should use the provided methods instead of editing fields directly.

Sorting is O(n log n). Filtering is O(n). Conflict grouping is O(n) after obtaining a sorted schedule, so the current full conflict method is O(n log n). This is sufficient for household schedules and preserves chronological warning order.

## 3. Testing and Verification

The suite checks completion, task addition, sorting without mutation, empty schedules, combined filters, daily/weekly recurrence at a year boundary, early and overdue completion, repeat completion, one-time tasks, same-pet and cross-pet conflicts, different dates, independent list defaults, and rejected inputs. Streamlit AppTest checks real form submissions, session retention, completion/recurrence, and conflict visibility while filtering.

The CLI was run before building the UI. Its five tasks were deliberately inserted out of order. It demonstrated the 18:00 conflict and next daily/weekly dates. Successful run output is retained in evidence/ and copied into README.md. No intentionally failing tests were manufactured. If a future failure appears, compare the expected behavior to the documented recurrence/conflict rules before changing either the test or implementation.

## 4. AI Collaboration Strategy

### Most effective assistant features

Codex's file editing and terminal execution connected the UML, backend, demo, tests, and documentation in one workspace. Generating pytest cases was useful for identifying boundaries beyond the minimum happy paths, especially year rollover and repeated completion. Streamlit's official Session State and AppTest documentation guided interface integration and verification. Running the generated code provided evidence stronger than accepting an AI explanation alone.

### A suggestion modified to keep the design clean

The starting time-only design was revised instead of treating every matching HH:MM value as a conflict. Keeping that approach would incorrectly flag tomorrow's breakfast against today's breakfast and could not express recurrence. Adding due_date and grouping by both date and time fixed the model without adding a database, inheritance hierarchy, or extra domain class. Recurrence was placed in the scheduler's completion workflow so the UI did not duplicate it.

### Separate chat sessions

The assignment recommends separate chats for algorithm planning and testing. This build used one continuing chat, so it would be inaccurate to claim that separate sessions helped here. The work was organized into design, CLI/backend verification, scheduling, UI integration, and final documentation checkpoints with Git commits. In a future student-led iteration, a fresh testing chat could provide an independent review using the code, UML, and documented rules as context, reducing the chance of simply repeating the implementation's assumptions.

### Learning about the lead architect role

The architectural responsibility is to define observable rules and keep every layer consistent: what completion means, which date determines recurrence, whether completed tasks conflict, and how task identity reaches the UI. AI can write plausible code, but a reviewer must decide whether those rules satisfy the assignment and whether tests prove them. The final UML and concrete test evidence make those choices reviewable. Student understanding and a personal reflection remain essential when submitting AI-assisted work.
