import os
import sys
import subprocess
from argparse import ArgumentParser


def runner_wait(proc):
    while proc.poll() is None:
        for line in iter(proc.stdout.readline, ''):
            print(line.strip())

    proc.communicate()
    return proc.returncode == 0


def run_tests(args):
    jobs = []
    playbookdir = os.path.dirname(os.path.abspath(__file__))  # scriptsdir
    playbookdir = os.path.dirname(playbookdir) + "/playbooks"
    for num in range(args.num_parallel):
        test_env = os.environ.copy()
        test_env["BATCHNUM"] = str(num)

        jobs.append(subprocess.Popen(
            "ansible-playbook %s/run-tests.yaml 2>&1" % playbookdir,
            shell=True,
            env=test_env,
            stdout=subprocess.PIPE
        ))

    # All Jobs started in parallel, now wait for each job
    ret = 0
    for job in jobs:
        if not runner_wait(job):
            ret = 1

    sys.exit(ret)


def main():
    parser = ArgumentParser()
    parser.add_argument("--num-parallel", help="Number of parallel executions", type=int)
    parser.add_argument("--sourcedir", help="Glusterfs Source directory")
    args = parser.parse_args()

    run_tests(args)


if __name__ == "__main__":
    main()
