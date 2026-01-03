from statecrumbs import enable, crumb, snapshot, clear

def test_basic_crumb():
    clear()
    enable(max_crumbs=5)

    crumb("step1", a=1)
    crumb("step2", b=2)

    crumbs = snapshot()
    assert len(crumbs) == 2
    assert crumbs[0]["event"] == "step1"
