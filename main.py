"""Run the CLI-first backend demonstration."""
import argparse
from datetime import date
from pawpal_system import Owner, Pet, Scheduler, Task


def build_demo_owner(day: date) -> Owner:
    """Create two pets and five deliberately out-of-order tasks."""
    owner = Owner("Alex")
    owner.add_pet(Pet("Luna", "Dog"))
    owner.add_pet(Pet("Milo", "Cat"))
    scheduler = Scheduler(owner)
    for pet, description, time, frequency in [
        ("Luna", "Evening walk", "18:00", "once"),
        ("Luna", "Breakfast", "08:00", "daily"),
        ("Milo", "Medication reminder", "12:00", "daily"),
        ("Milo", "Grooming", "09:00", "weekly"),
        ("Milo", "Playtime", "18:00", "once"),
    ]:
        scheduler.schedule_task(pet, Task(description, time, frequency, day))
    return owner


def main():
    """Print sorting, filtering, conflict warnings, and recurrence."""
    parser = argparse.ArgumentParser(description="PawPal+ backend demo")
    parser.add_argument("--date", type=date.fromisoformat, default=date.today())
    day = parser.parse_args().date
    owner = build_demo_owner(day)
    scheduler = Scheduler(owner)
    print(f"PawPal+ | Owner: {owner.name} | Pets: {len(owner.pets)}")
    print(f"Today's Schedule ({day.isoformat()})")
    for pet, task in scheduler.get_schedule(on_date=day):
        print(f"{task.time} | {pet.name:4} | {task.description} [{task.frequency}]")
    print("\nPending tasks for Luna:")
    for _, task in scheduler.get_schedule(pet_name="Luna", completed=False):
        print(f"{task.time} | {task.description}")
    print("\nConflict warnings:")
    for warning in scheduler.detect_conflicts(on_date=day):
        print(warning)
    print("\nComplete Breakfast (daily) and Grooming (weekly):")
    for _, task in list(scheduler.get_schedule(on_date=day)):
        if task.description in {"Breakfast", "Grooming"}:
            successor = scheduler.mark_task_complete(task.task_id, completed_on=day)
            print(f"{task.description} completed -> {successor.due_date} {successor.time}")
    print(f"Completed tasks: {len(scheduler.filter_tasks(completed=True))}")


if __name__ == "__main__":
    main()
