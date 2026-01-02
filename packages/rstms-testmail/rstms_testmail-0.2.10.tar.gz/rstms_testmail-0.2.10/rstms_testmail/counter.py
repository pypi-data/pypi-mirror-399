# persistent counter

from pathlib import Path


class Counter:
    def __init__(self, dir=None, label=None, count=None):

        if dir in ["~", None]:
            dir = Path.home()
        else:
            dir = Path(dir)

        if label is None:
            filename = ".counter"
        else:
            filename = f".{label}.counter"

        self.file = dir / filename

        if count is None:
            self.read()
        else:
            self.value = int(count)
            self.write()

        self.initial_value = self.value

    def read(self):
        if not self.file.is_file():
            self.value = 0
            return self.write()
        self.value = int(self.file.read_text() or "0")
        return self.value

    def write(self):
        self.file.write_text(str(self.value) + "\n")
        return self.value

    def bump(self, value=None):
        if value:
            self.value = value
        else:
            self.value += 1

        return self.write()

    def rewind(self):
        self.value = self.initial_value
        self.write()
