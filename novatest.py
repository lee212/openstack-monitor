#!/usr/bin/env python

import tests
import failures
import time
import os
from os.path import expanduser, abspath
import uuid


def fullpath(path):
    return abspath(expanduser(path))


def getopts(args=None):
    from argparse import ArgumentParser, ArgumentDefaultsHelpFormatter
    p = ArgumentParser(formatter_class=ArgumentDefaultsHelpFormatter)

    default_name_format = '{user}-{pid}-{uuid}'

    p.add_argument('-n', '--name', default='<'+default_name_format+'>',
                   help='Name of the instance'.
                   format(default_name_format))
    p.add_argument('-k', '--key-name', required=True,
                   help='The key name to use')
    p.add_argument('-f', '--ssh-key-path', default='~/.ssh/id_rsa',
                   help='Path to the private ssh key')
    p.add_argument('-t', '--times', default='times.txt',
                   help='Save execution times here')
    p.add_argument('-x', '--failures', default='failures.txt',
                   help='Save the type of failures here')

    opts = p.parse_args(args=args)

    if opts.name.startswith('<') and opts.name.endswith('>'):
        opts.name = default_name_format.format(
            user=os.getenv('LOGNAME'),
            pid=os.getpid(),
            uuid=uuid.uuid1().hex)

    opts.ssh_key_path = fullpath(opts.ssh_key_path)

    return opts


def run_tests(name=None, key=None, ssh_key=None):
    assert name is not None
    assert key is not None
    assert ssh_key is not None

    tester = tests.NovaTester()
    tester.boot(name=name, key_name=key)

    try:
        tester.get_ip()
        tester.ping()
        tester.wait_for_sshd()
        tester.ssh(key=ssh_key)
    finally:
        tester.cleanup()


def main(opts):
    today = int(time.time())
    t0 = time.time()

    try:
        run_tests(name=opts.name, key=opts.key_name, ssh_key=opts.ssh_key_path)
    except failures.TestFailure, e:
        with open(opts.failures, 'a') as fd:
            fd.write('{today},{name}\n'
                     .format(today=today, name=e.name))
        raise

    t = time.time() - t0

    with open(opts.times, 'a') as fd:
        fd.write('{today},{time}\n'
                 .format(today=today, time=t))


if __name__ == '__main__':
    opts = getopts()
    print opts
    main(opts)
