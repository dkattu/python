from calculator import CalculatorHistory


def test_add_entry_and_retrieve():
    history = CalculatorHistory()
    history.add_entry("2+2", "4")
    history.add_entry("3*4", "12")

    assert history.get_entries() == [("2+2", "4"), ("3*4", "12")]


def test_replay_entry_returns_selected_expression():
    history = CalculatorHistory()
    history.add_entry("6/2", "3")

    assert history.replay(0) == ("6/2", "3")


def test_clear_history_removes_all_entries():
    history = CalculatorHistory()
    history.add_entry("1+1", "2")
    history.clear()

    assert history.get_entries() == []
