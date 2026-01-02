from pprint import pprint

from rstms_testmail import netstat


def test_netstat_listen_ports():
    ports = netstat.listen_ports()
    assert isinstance(ports, set)
    assert ports
    pprint(ports)
