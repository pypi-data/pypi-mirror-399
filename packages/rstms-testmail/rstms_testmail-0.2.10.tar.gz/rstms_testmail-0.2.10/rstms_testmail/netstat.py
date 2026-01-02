import subprocess


def listen_ports():
    output = subprocess.check_output(["netstat", "-lnt"]).decode()
    ports = set()
    for line in output.split("\n"):
        if "LISTEN" in line:
            fields = line.split()
            field = fields[3]
            addr, _, port = field.partition(":")
            ports.add(int(port))
    return ports
