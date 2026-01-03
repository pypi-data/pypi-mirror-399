import threading
from statecrumbs import crumb, snapshot, clear, enable

def worker(i):
    crumb("worker", id=i)

def test_thread_safety():
    clear()
    enable(max_crumbs=100)
    threads = [threading.Thread(target=worker, args=(i,)) for i in range(10)]
    for t in threads:
        t.start()
    for t in threads:
        t.join()

    crumbs = snapshot()
    assert len(crumbs) == 10
