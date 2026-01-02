from os import system
from subprocess import Popen
from time import sleep

import pytest

from rstms_testmail.netstat import listen_ports
from rstms_testmail.watcher import PortWatcher


@pytest.fixture
def context():
    system("pkill nc")
    yield None
    system("pkill nc")
    system("pgrep -a ssh | grep 10000")


def test_watcher_listen(context):
    with PortWatcher("ssh -q -N -R {}:localhost:{} beaker") as watcher:
        assert watcher.running()
        assert not watcher.proc
        assert 10000 not in listen_ports()
        netcat = Popen(["nc", "-lp", "10000"])
        sleep(1)
        assert 10000 in listen_ports()
        sleep(2)
        assert watcher.proc
        netcat.terminate()
        netcat.wait()
        assert 10000 not in listen_ports()
        while watcher.running() is True:
            print("tick")
            sleep(1)
    assert not watcher.running()
    assert 10000 not in listen_ports()


def test_watcher_none(context):
    with PortWatcher("ssh -q -N -R {}:localhost:{} beaker") as watcher:
        assert watcher.running()
        assert not watcher.proc
        sleep(1)
    assert not watcher.running()
