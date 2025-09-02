from neonhud.utils.history import HistoryBuffer


def test_history_buffer_push_and_len():
    h = HistoryBuffer(maxlen=3)
    h.push(1.0)
    h.push(2.0)
    h.push(3.0)
    h.push(4.0)  # drop 1
    vals = h.values()
    assert vals == [2.0, 3.0, 4.0]
    assert h.latest() == 4.0
    assert len(h) == 3
