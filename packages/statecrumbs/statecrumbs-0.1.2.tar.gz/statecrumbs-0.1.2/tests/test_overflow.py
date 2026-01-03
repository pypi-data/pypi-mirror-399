from statecrumbs import enable, crumb, snapshot, clear

def test_ring_buffer_overflow():
    clear()
    enable(max_crumbs=2)

    crumb("a")
    crumb("b")
    crumb("c")

    crumbs = snapshot()
    assert len(crumbs) == 2
    assert crumbs[0]["event"] == "b"
    assert crumbs[1]["event"] == "c"
