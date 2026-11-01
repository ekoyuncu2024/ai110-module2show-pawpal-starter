"""Behavior tests for PawPal+."""
from datetime import date
import pytest
from pawpal_system import Owner, Pet, Scheduler, Task

DAY = date(2026, 11, 1)


@pytest.fixture
def scheduler():
    owner = Owner("Alex")
    owner.add_pet(Pet("Luna", "Dog"))
    owner.add_pet(Pet("Milo", "Cat"))
    return Scheduler(owner)


def test_task_completion():
    task = Task("Walk", "08:00", due_date=DAY)
    assert not task.completed
    task.mark_complete()
    assert task.completed


def test_task_addition():
    pet = Pet("Luna", "Dog")
    task = Task("Walk", "08:00", due_date=DAY)
    pet.add_task(task)
    assert pet.tasks == [task]


def test_chronological_sorting_without_mutation(scheduler):
    tasks = [Task("Late", "18:00", due_date=DAY), Task("Early", "08:00", due_date=DAY),
             Task("Tomorrow", "06:00", due_date=date(2026, 11, 2))]
    for task in tasks:
        scheduler.schedule_task("Luna", task)
    assert [t.description for _, t in scheduler.sort_by_time()] == ["Early", "Late", "Tomorrow"]
    assert scheduler.owner.get_pet("Luna").tasks == tasks
    assert scheduler.sort_by_time([]) == []


@pytest.mark.parametrize("frequency,expected", [("daily", date(2027, 1, 1)), ("weekly", date(2027, 1, 7))])
def test_recurrence_year_boundary(scheduler, frequency, expected):
    task = Task("Care", "08:00", frequency, date(2026, 12, 31))
    scheduler.schedule_task("Luna", task)
    successor = scheduler.mark_task_complete(task.task_id, date(2026, 12, 31))
    assert task.completed
    assert successor.due_date == expected
    assert successor.time == "08:00" and successor.frequency == frequency
    assert not successor.completed and successor.task_id != task.task_id
    assert successor in scheduler.owner.get_pet("Luna").tasks
    assert scheduler.mark_task_complete(task.task_id, expected) is None
    assert len(scheduler.owner.get_pet("Luna").tasks) == 2


@pytest.mark.parametrize("completion,expected", [(date(2026, 10, 31), date(2026, 11, 2)), (date(2026, 11, 4), date(2026, 11, 5))])
def test_early_and_overdue_daily_completion(scheduler, completion, expected):
    task = Task("Breakfast", "08:00", "daily", DAY)
    scheduler.schedule_task("Luna", task)
    assert scheduler.mark_task_complete(task.task_id, completion).due_date == expected


def test_one_time_completion_has_no_successor(scheduler):
    task = Task("Vet", "08:00", due_date=DAY)
    scheduler.schedule_task("Luna", task)
    assert scheduler.mark_task_complete(task.task_id, DAY) is None
    assert len(scheduler.owner.get_all_tasks()) == 1


@pytest.mark.parametrize("other_pet", ["Luna", "Milo"])
def test_conflicts_same_and_different_pets(scheduler, other_pet):
    first, second = Task("Walk", "08:00", due_date=DAY), Task("Feed", "08:00", due_date=DAY)
    scheduler.schedule_task("Luna", first)
    scheduler.schedule_task(other_pet, second)
    warnings = scheduler.detect_conflicts(DAY)
    assert len(warnings) == 1
    assert "08:00" in warnings[0] and "Walk" in warnings[0] and "Feed" in warnings[0]
    scheduler.mark_task_complete(first.task_id, DAY)
    assert scheduler.detect_conflicts(DAY) == []


def test_different_dates_do_not_conflict(scheduler):
    scheduler.schedule_task("Luna", Task("Walk", "08:00", due_date=DAY))
    scheduler.schedule_task("Milo", Task("Feed", "08:00", due_date=date(2026, 11, 2)))
    assert scheduler.detect_conflicts() == []


def test_combined_filters(scheduler):
    first, second = Task("Walk", "08:00", due_date=DAY), Task("Feed", "09:00", due_date=DAY)
    scheduler.schedule_task("Luna", first)
    scheduler.schedule_task("Milo", second)
    first.mark_complete()
    assert scheduler.filter_tasks("luna", True, DAY) == [(scheduler.owner.get_pet("Luna"), first)]
    assert [t for _, t in scheduler.get_schedule(completed=False)] == [second]
    assert scheduler.filter_tasks(on_date=date(2026, 11, 2)) == []


def test_empty_owner_and_independent_lists():
    a, b = Owner("A"), Owner("B")
    a.add_pet(Pet("Luna", "Dog"))
    assert b.pets == []
    assert Scheduler(a).get_schedule() == []
    assert Scheduler(a).detect_conflicts() == []
    p, q = Pet("A", "Cat"), Pet("B", "Cat")
    p.add_task(Task("Feed", "08:00"))
    assert q.tasks == []


@pytest.mark.parametrize("clock", ["24:00", "08:60", "8:00", "bad"])
def test_invalid_time(clock):
    with pytest.raises(ValueError, match="HH:MM"):
        Task("Walk", clock)


def test_invalid_inputs_and_duplicates(scheduler):
    with pytest.raises(ValueError):
        Task(" ", "08:00")
    with pytest.raises(ValueError):
        Task("Walk", "08:00", "monthly")
    with pytest.raises(ValueError):
        Task("Walk", "08:00", due_date="2026-11-01")
    with pytest.raises(ValueError):
        Pet("", "Dog")
    with pytest.raises(ValueError):
        Owner("")
    with pytest.raises(ValueError):
        scheduler.owner.add_pet(Pet("luna", "Cat"))
    task = Task("Walk", "08:00")
    scheduler.schedule_task("Luna", task)
    with pytest.raises(ValueError):
        scheduler.schedule_task("Milo", task)
    with pytest.raises(ValueError):
        scheduler.owner.get_pet("Luna").add_task(task)
    with pytest.raises(ValueError):
        scheduler.schedule_task("Unknown", Task("Feed", "09:00"))
    with pytest.raises(ValueError):
        scheduler.mark_task_complete("missing")
