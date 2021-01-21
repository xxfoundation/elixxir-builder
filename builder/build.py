"""
building.py - utils for checking out and building
"""

import os
import subprocess

def get_dir(path):
    return path.split(':')[1]

def run(cmd):
    print(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print("Error: ", result)
    return result

def get_branch(repo):
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    print("Path: ", os.getcwd())
    res = run(['git', 'status'])
    os.chdir(cwd)
    for line in res.stdout.splitlines():
        return line[len('On branch '):].decode('utf-8')

def clone(repo):
    if not repo:
        raise("Cannot clone without repository!")

    target_dir = get_dir(repo)
    os.makedirs(target_dir, exist_ok=True)

    cmd = ['git', 'clone', repo, target_dir]
    run(cmd)

def checkout(repo, branch):
    if not repo or not branch:
        raise("Cannot checkout without repo and branch!")

    target_dir = get_dir(repo)
    if not os.path.exists(target_dir):
        clone(repo)

    cwd = os.getcwd()
    os.chdir(target_dir)
    print("Path: ", os.getcwd())
    cmds = [
        ['git', 'checkout', '-B', branch],
        ['git', 'push', '-u', 'origin', branch],
        ['git', 'pull'],
    ]
    for cmd in cmds:
        run(cmd)

    os.chdir(cwd)


def update(repo, dependencies):
    if not repo:
        raise("Cannot update without repo and dependencies")

    if not dependencies:
        print("No dependencies to update")

    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    for dep in dependencies:
        cmd = ['go', 'get', '-u', dep]
        res = run(cmd)
        if res.returncode != 0:
            os.chdir(cwd)
            raise("ERROR!")
    os.chdir(cwd)

def build(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['go', 'build', './...'])
    os.chdir(cwd)
    if res.returncode != 0:
        raise("ERROR!")

def test(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['go', 'test', '-v', './...'])
    os.chdir(cwd)
    if res.returncode != 0:
        raise("ERROR!")

def status(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    run(['git', 'status'])
    os.chdir(cwd)

def push(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['git', 'commit', '-m', 'update deps', '.'])
    res = run(['git', 'push'])
    os.chdir(cwd)
