import shlex
import subprocess
import threading
import time
from logging import info

from .netstat import listen_ports


class PortWatcher:
    """runs a command when a new listening port appears, kills the command when the port disappears"""

    def __init__(self, command):
        info(f"{self} init")
        self.command = command
        self.ports = listen_ports()
        self.port = None
        self.proc = None
        self.watch_thread = None
        self.stop_event = threading.Event()

    def running(self):
        ret = self.stop_event.is_set() is False
        info(f"{self} running returning {ret}")
        return ret

    def watch(self):
        ports = listen_ports()

        if ports == self.ports:
            info(f"{self} no change in ports")
            ret = None
        elif self.port is None:
            info(f"{self} port is none")
            new_port = ports.difference(self.ports)
            if new_port:
                self.port = new_port.pop()
                self.ports = ports
                info(f"{self} new port {self.port} detected")
                command = self.command.replace("{}", str(self.port))
                self.proc = subprocess.Popen(shlex.split(command))
                info(f"{self} started {command} pid={self.proc.pid}")
            ret = None
        elif self.port in ports:
            info(f"{self} {self.port=} still in {ports=}")
            ret = None
        else:
            info(f"{self} stopping: pid={self.proc.pid}")
            self.proc.terminate()
            ret = self.proc.wait()
            info(f"{self} stopped: pid={self.proc.pid} ret={ret}")
            self.stop_event.set()
        info(f"{self} watch returning {ret}")
        return ret

    def start(self):
        info(f"{self} starting")
        self.watch_thread = threading.Thread(target=self.run)
        self.watch_thread.start()
        info(f"{self} started")

    def stop(self):
        info(f"{self} stopping")
        self.stop_event.set()
        if self.watch_thread is not None:
            self.watch_thread.join()
            self.watch_thread = None
        info(f"{self} stopped")

    def __enter__(self):
        info(f"{self} enter")
        self.start()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb):
        info(f"{self} exit")
        self.stop()

    def run(self):
        info(f"{self} run: called")
        while self.stop_event.is_set() is False:
            ret = self.watch()
            info(f"{self} run: watch returned {ret}")
            if ret:
                break
            else:
                time.sleep(1)
        info(f"{self} run: returning")
