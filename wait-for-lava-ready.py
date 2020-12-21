#!/usr/bin/python3
import argparse
import datetime as dt
import json
import subprocess
import sys

import requests


class Options(object):
    pass

opts = Options()


def sprint(s):
    if not opts.quiet:
        print(s)


def Run(args, **kwargs):
    sprint("Running: %s " % " ".join(args))
    return subprocess.Popen(args, **kwargs)


def lava_ready(host):
    r = requests.get("http://%s/api/v0.2/system/version" % host)
    try:
        r.json()
        return True
    except ValueError:
        return False


def wait_for_lava(cli):
    start = dt.datetime.now()
    if cli.timeout == 0:
        sprint("waiting for Lava without a timeout")
        wait_until = 0
    else:
        sprint("waiting %s seconds for Lava" %  cli.timeout)
        wait_until = start + dt.timedelta(seconds=cli.timeout)
    ready = False
    timed_out = True
    current = start
    while current < wait_until:
        if lava_ready(cli.host):
            sprint("Lava is available after %s seconds" % (current - start))
            ready = True
            timed_out = False
            break
        current = dt.datetime.now()
    if timed_out:
        sprint("timeout occurred after waiting %s seconds for Lava" % cli.timeout)
    return ready


def parse_cli():
    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-H", "--lava-host", metavar="host", dest="host", required=True,
        help="Lava hostname"
    )
    parser.add_argument(
        "-s", "--strict", action="store_true",
        help="Only execute subcommand if the test succeeds"
    )
    parser.add_argument(
        "-q", "--quiet", action="store_true",
        help="Don't output any status messages"
    )
    parser.add_argument(
        "-t", "--timeout", action="store", type=int,
        help="Timeout in seconds, zero for no timeout"
    )
    parser.add_argument(
        "--", metavar="COMMAND ARGS", nargs=argparse.REMAINDER, dest="command",
        help="Execute command with args after the test finishes"
    )

    args, remainder = parser.parse_known_args(sys.argv[1:])
    return args, remainder[1:]


def main():
    cli, command = parse_cli()
    opts.quiet = cli.quiet

    ready = wait_for_lava(cli)
    if cli.strict and not ready:
        sprint("strict mode, refusing to execute command")
        sys.exit(1)
    else:
        p = Run(command, stdout=subprocess.PIPE)
        stdout, stderr = p.communicate()
        if p.returncode != 0:
            sprint("command failed")
            sys.exit(1)


if __name__ == '__main__':
    main()