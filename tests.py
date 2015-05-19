from pyshc.sh import Sh
from time import sleep
import subprocess
import pipes


nova = Sh('nova')
ping = Sh('ping')
ssh = Sh('ssh')
nc = Sh('nc')


class TestFailure(Exception):
    pass


def get_machine_property(nova_show_output, property):
    def get_value(line, key, sep='|'):
        split = line.split(sep)

        if not len(split) == 4:
            return None

        key_found = split[1].strip()
        if key_found == key:
            return split[2].strip()

        else:
            return None

    if type(nova_show_output) is str:
        nova_show_output = nova_show_output.split('\n')

    for line in nova_show_output:
        val = get_value(line, property)
        if val:
            return val


def get_machine_id(output):
    return get_machine_property(output, 'id')


def get_machine_intnet(output):
    return get_machine_property(output, 'int-net network')


class NovaTester(object):
    def __init__(self, attempts=10, delay=10):
        self._machine = None  # the machine id
        self._int_ip = None  # the internal ipv4

        self.attempts = attempts  # no. attempts to retreive instance info
        self.delay = delay        # delay between attempts in seconds

    def cleanup(self):
        "Deletes the instance"
        print('Deleting {}'.format(self._machine))
        try:
            nova(['delete', self._machine])
        except subprocess.CalledProcessError, e:
            raise TestFailure(
                'Could not delete instance {machine} exit {ret}\n{out}'
                .format(machine=self._machine, ret=e.returncode, out=e.output))

    def boot(self, name=None, key_name=None,
             image='futuresystems/ubuntu-14.04', flavor='m1.small'):

        assert self._machine is None
        assert name is not None
        assert key_name is not None

        boot = ['boot',
                '--flavor', flavor,
                '--image', image,
                '--key_name', key_name,
                name
                ]

        print('Executing {}'.format(' '.join(map(pipes.quote, boot))))

        try:
            out = nova(boot)
        except subprocess.CalledProcessError, e:
            raise TestFailure(
                ' '.join([
                    'Boot command {cmd} failed with non-zero status {ret}\n'
                    .format(cmd=e.cmd, ret=e.returncode),
                    '\nSTDERR\n########################################\n',
                    e.output
                    ]))

        machine = get_machine_id(out)
        self._machine = machine
        print('Machine {}'.format(machine))

    def get_ip(self):
        assert self._machine is not None

        print('Getting IPv4')
        for i in xrange(self.attempts):
            output = nova(['show', self._machine])
            ip = get_machine_intnet(output)
            if ip:
                self._int_ip = ip
                return ip
            sleep(self.delay)
        raise TestFailure(
            'Exceeded max attempts {max} to retrieve IP address for {machine}'
            .format(max=self.attempts, machine=self._machine))

    def ping(self, count=10):
        if not self._int_ip:
            self.get_ip()
        print('Ping {addr}'.format(addr=self._int_ip))
        try:
            ping(['-c', str(count), self._int_ip])
        except subprocess.CalledProcessError, e:
            raise TestFailure(
                ('Command {cmd} failed {ret}'
                 + ' when pinging machine {machine} at {addr}'
                 + '\n'
                 + 'ERROR########################################\n'
                 + '{err}\n')
                .format(cmd=e.cmd,
                        ret=e.returncode,
                        machine=self._machine,
                        addr=self._int_ip,
                        err=e.output))

    def wait_for_sshd(self, attempts=None):
        assert self._int_ip is not None
        attempts = attempts or self.attempts

        print('Waiting for sshd to start on {addr}'.format(addr=self._int_ip))

        for i in xrange(attempts):
            try:
                nc(['-z', '-v', self._int_ip, '22'])
            except subprocess.CalledProcessError:
                sleep(self.delay)
                continue
            return True

        raise TestFailure('Timeout waiting for sshd to start')

    def ssh(self, user='ubuntu', key='~/.ssh/id_rsa', remote_cmd='ifconfig'):
        assert self._int_ip is not None
        ssh_args = ['-o', 'StrictHostKeyChecking=no',
                    '-o', 'UserKnownHostsFile=/dev/null'
                    ]
        cmd = ssh_args + ['{user}@{addr}'.format(user=user, addr=self._int_ip),
                          remote_cmd]
        try:
            out = ssh(cmd)
        except subprocess.CalledProcessError, e:
            raise TestFailure(
                ('Failed to ssh to machine {machine} at {addr} with {ret}\n',
                 + 'STDOUT\n########################################\n',
                 + out + '\n',
                 + 'STDERR\n########################################\n',
                 + e.output)
                .format(machine=self._machine,
                        addr=self._int_ip,
                        ret=e.returncode))
