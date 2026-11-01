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
