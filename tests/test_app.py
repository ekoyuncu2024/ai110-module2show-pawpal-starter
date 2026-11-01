"""Integration checks of real Streamlit widgets and backend session state."""
from pathlib import Path
from streamlit.testing.v1 import AppTest

APP = str(Path(__file__).resolve().parents[1] / "app.py")


def click_label(app, label):
    next(b for b in app.button if b.label == label).click().run()
    assert not app.exception


def test_add_pet_schedule_complete_and_retain_session():
    app = AppTest.from_file(APP).run()
    assert not app.exception
    app.text_input(key="pet_name").input("Nori")
    app.text_input(key="species").input("Cat")
    click_label(app, "Add pet")
    owner = app.session_state.owner
    assert owner.get_pet("Nori").species == "Cat"
    app.text_input(key="description").input("Breakfast")
    app.selectbox(key="frequency").select("daily")
    click_label(app, "Schedule task")
    task = owner.get_pet("Nori").tasks[0]
    assert task.description == "Breakfast"
    next(b for b in app.button if b.key == f"complete_{task.task_id}").click().run()
    assert not app.exception
    assert task.completed and len(owner.get_pet("Nori").tasks) == 2
    app.checkbox(key="all_dates").check().run()
    assert app.session_state.owner is owner
    assert len(app.table[0].value) == 1


def test_demo_conflict_and_filter():
    app = AppTest.from_file(APP).run()
    click_label(app, "Load demo household")
    assert len(app.session_state.owner.pets) == 2
    assert len(app.warning) == 1
    app.selectbox(key="filter_pet").select("Luna").run()
    assert len(app.table[0].value) == 2
    assert len(app.warning) == 1


def test_blank_pet_rejected():
    app = AppTest.from_file(APP).run()
    click_label(app, "Add pet")
    assert app.error
    assert app.session_state.owner.pets == []


def test_pet_named_all_pets_can_be_filtered():
    app = AppTest.from_file(APP).run()
    for name, description in [("All pets", "Breakfast"), ("Nori", "Playtime")]:
        app.text_input(key="pet_name").input(name)
        app.text_input(key="species").input("Cat")
        click_label(app, "Add pet")
        app.selectbox(key="task_pet").select(name)
        app.text_input(key="description").input(description)
        click_label(app, "Schedule task")
    app.selectbox(key="filter_pet").select("All pets").run()
    assert not app.exception
    assert app.table[0].value["Pet"].tolist() == ["All pets"]


def test_demo_owner_name_matches_edit_field():
    app = AppTest.from_file(APP).run()
    click_label(app, "Load demo household")
    assert app.text_input(key="owner_name").value == app.session_state.owner.name
