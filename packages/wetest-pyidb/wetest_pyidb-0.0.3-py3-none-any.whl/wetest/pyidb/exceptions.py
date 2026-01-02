class IdbError(Exception):
    def __init__(self, cmd, returncode, stdout):
        self._cmd = cmd
        self._returncode = returncode
        self._stdout = stdout

    @property
    def cmd(self):
        return self._cmd

    @property
    def returncode(self):
        return self._returncode

    @property
    def stdout(self):
        return self._stdout

    def __str__(self):
        return f"{self.cmd} failed with return code {self.returncode}: {self.stdout}"


class IdbProcessError(Exception):
    def __init__(self, bundle_id):
        self._bundle_id = bundle_id

    @property
    def bundle_id(self):
        return self._bundle_id

    def __str__(self) -> str:
        return f"bundle_id <{self.bundle_id}> process not found"
