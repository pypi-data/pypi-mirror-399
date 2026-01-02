from rstms_testmail.counter import Counter


def test_counter():
    counter = Counter(dir=".", count=0)
    assert counter.value == 0

    counter.bump()
    assert counter.value == 1

    ret = counter.bump(10)
    assert ret == 10
    assert counter.value == 10

    counter2 = Counter(dir=".")
    assert counter2.value == 10
