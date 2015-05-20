

class TestFailure(Exception):
    pass


class CleanupTestFailure(TestFailure):
    name = 'cleanup'


class BootTestFailure(TestFailure):
    name = 'boot'


class GetIPTestFailure(TestFailure):
    name = 'get_ip'


class PingTestFailure(TestFailure):
    name = 'ping'


class SSHDTestFailure(TestFailure):
    name = 'sshd'


class SSHTestFailure(TestFailure):
    name = 'ssh'
