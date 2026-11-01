# PawPal+: AI-Assisted Application Development

PawPal+ helps an owner manage pet-care routines: feedings, walks, medication reminders, and appointments. Four Python dataclasses form a reusable backend; a terminal demo verifies it independently, and a Streamlit interface calls the same backend methods.

## Features

- Add an owner and multiple pets; schedule dated care tasks.
- View a chronological schedule and filter by pet, completion status, or date.
- Complete one-time tasks or generate the next daily/weekly occurrence.
- See readable warnings for tasks sharing an exact date/time across any pets.
- Retain the Owner object through Streamlit reruns using `st.session_state`.
- Validate required text, unique pet names, frequency, and zero-padded 24-hour times.

## Setup and run

Requires Python 3.12 or newer. Tested with Python 3.12.14. From this project's folder:

```console
python -m venv .venv
```

Activate on Windows PowerShell with `.venv\Scripts\Activate.ps1`; on macOS/Linux use `source .venv/bin/activate`. Then:

```console
python -m pip install -r requirements.txt
python main.py
python -m pytest
python -m streamlit run app.py
```

Open the local address printed by Streamlit. If PowerShell blocks activation, use `.venv\Scripts\python.exe` in place of `python` in these commands. The backend and CLI use only Python's standard library. Streamlit 1.50.0 avoids a local test-runner networking issue observed with 1.66.1 on this Windows environment. Streamlit and pytest versions are pinned in requirements.txt; requirements-lock.txt records the full tested environment.

## Project structure and architecture

```text
PawPal/
  pawpal_system.py       Owner, Pet, Task, Scheduler
  main.py                CLI demonstration and demo household factory
  app.py                 Streamlit presentation layer
  tests/test_pawpal.py   Domain behavior tests
  tests/test_app.py      Streamlit interaction tests
  diagrams/uml_draft.mmd Original pre-implementation design
  diagrams/uml_final.mmd Final class diagram
  evidence/              Actual command output
  reflection.md          Design, tradeoffs, testing, AI collaboration
```

Owner owns Pets; each Pet holds Tasks. Scheduler retrieves `(Pet, Task)` pairs through Owner instead of copying the data. Task stores description, time, frequency, due_date, completed, and a generated task_id. Pet and Owner collections use `default_factory=list`. The draft UML is intentionally the initial design; the final UML includes the date-aware scheduling methods added during implementation. View the Mermaid sources using a Mermaid-enabled editor.

## Smarter Scheduling

| Feature | Backend method | Rule |
|---|---|---|
| Sorting | `Scheduler.sort_by_time()` | Stable copy sorted by date and validated HH:MM; source lists retain insertion order. |
| Filtering | `Scheduler.filter_tasks()` | Combine case-insensitive pet name, completion status, and exact date; None disables a filter. |
| Display schedule | `Scheduler.get_schedule()` | Apply filters then sort. |
| Task assignment | `Scheduler.schedule_task()` | Resolve the registered pet and reject reusing an assigned task ID. |
| Recurrence | `Scheduler.mark_task_complete()` and `Task.next_occurrence()` | Complete the original and add one pending successor for daily (+1 day) or weekly (+7 days). |
| Conflict detection | `Scheduler.detect_conflicts()` | Group pending tasks by exact date/time; return warning strings for groups of two or more. |

Recurrence uses the later of the original due date and the completion date as its anchor. A task completed on its due day produces tomorrow's daily occurrence; a late completion produces tomorrow relative to completion; early completion preserves the scheduled cycle. The optional `completed_on` argument makes tests and demos deterministic. Repeated completion does not create duplicates. `Task.mark_complete()` alone only sets status; use the scheduler method for the complete recurrence workflow.

Conflicts include the same pet or different pets, omit completed tasks, and distinguish different dates. Warnings do not prevent scheduling. The UI checks all pets within the selected date range even when display filters hide a conflicting task.

Sorting costs O(n log n), filtering O(n), and conflict grouping O(n) after sorting. The full conflict method is O(n log n). The design favors clarity for household-sized schedules.

## Demo Walkthrough

1. Start the app. Add a pet name and species, or choose **Load demo household** in the sidebar while the household is empty.
2. Use **Schedule care** to select a pet, description, date, time, and once/daily/weekly frequency.
3. The schedule displays tasks in date/time order. Filter by pet or status, select a date, or check **Show all dates**.
4. Add two pending tasks at the same time/date to see a conflict warning naming both activities. Demo data already includes Luna's evening walk and Milo's playtime at 18:00.
5. Click a **Complete** button. One-time work leaves the pending list; daily/weekly work creates its next occurrence. Select all dates to see the successor, or Completed to inspect the original.
6. Change filters and add another pet: the same Owner and Pet objects stay in session state across these reruns.

### Sample CLI Output

Actual output from `python main.py --date 2026-11-01` (plain `python main.py` uses today's date):

```text
PawPal+ | Owner: Alex | Pets: 2
Today's Schedule (2026-11-01)
08:00 | Luna | Breakfast [daily]
09:00 | Milo | Grooming [weekly]
12:00 | Milo | Medication reminder [daily]
18:00 | Luna | Evening walk [once]
18:00 | Milo | Playtime [once]

Pending tasks for Luna:
08:00 | Breakfast
18:00 | Evening walk

Conflict warnings:
Conflict on 2026-11-01 at 18:00: Luna: Evening walk; Milo: Playtime

Complete Breakfast (daily) and Grooming (weekly):
Breakfast completed -> 2026-11-02 08:00
Grooming completed -> 2026-11-08 09:00
Completed tasks: 2
```

The demo inserts five tasks out of order across two pets, shows sorted/filter results, prints a same-time warning, and demonstrates both recurrence intervals.

## Testing PawPal+

```console
python -m pytest
```

Tests cover task completion/addition, chronological sorting without mutation, daily and weekly recurrence across a year boundary, early/overdue completion, duplicate completion prevention, one-time completion, same-pet/cross-pet conflicts, different dates, combined filters, empty schedules, independent list defaults, validation, and duplicate assignment. Streamlit AppTest exercises pet creation, scheduling, completion, state retention, demo warnings, and filtering. The tests do not require a running browser.

Successful output from the verification run (full transcript in evidence/pytest-output.txt):

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-9.2.0, pluggy-1.7.0
rootdir: C:\Users\emirk\Documents\Codex\2026-11-01\referenced-chatgpt-conversation-this-is-an\outputs\PawPal
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.16.0
collected 21 items

tests\test_app.py ...                                                    [ 14%]
tests\test_pawpal.py ..................                                  [100%]

============================= 21 passed in 1.93s ==============================
```

**Confidence Level: 4/5 stars.** Automated checks cover the required rules and key UI workflows. Limits: there is no durable database, timezone conversion, interval/duration overlap detection, or background notifications. Session state survives reruns but can reset on reload, disconnect, or restart. Recurrence creates the next task on completion; it does not expand an entire future calendar. Use backend methods rather than directly mutating domain lists or task scheduling fields.

## AI collaboration and references

Codex assisted with the UML, code, tests, and documentation. See reflection.md for specific decisions and an honest account of the workflow. The reflection is an AI-assisted project record for the student to review and personalize; it does not claim unperformed separate chats or personal learning experiences.

Official references used for integration: [Streamlit Session State](https://docs.streamlit.io/develop/api-reference/caching-and-state/st.session_state) and [Streamlit AppTest](https://docs.streamlit.io/develop/api-reference/app-testing/st.testing.v1.apptest).

## Submission checklist

- Required code, draft/final UML, tests, README, reflection, and run evidence are included.
- The local Git repository records meaningful design, implementation, integration, and documentation commits. The companion Git bundle preserves that history; clone it with `git clone ../PawPal.bundle PawPal-restored` from an appropriate destination folder.
- Review and personalize the reflection after running the project.
- Push the main branch to your correct public CodePath GitHub fork and verify all files and commits are visible. This delivery does not create or publish a remote repository.
- Submit the repository through the course's Week 5 submit button and complete the separate Canvas → Modules weekly CHECK-IN, as directed in the uploaded instructions.
