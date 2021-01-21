"""
building.py - utils for checking out and building
"""

import os
import subprocess

from termcolor import colored

def get_dir(path):
    return path.split(':')[1]

def run(cmd):
    print(" ".join(cmd))
    result = subprocess.run(cmd, capture_output=True)
    if result.returncode != 0:
        print(result.args, ' process returned: ', result.returncode)
        print(result.stdout.decode('utf-8'))
        print(colored(result.stderr.decode('utf-8'), 'red'))
    return result

def get_branch(repo):
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    print("Path: ", os.getcwd())
    res = subprocess.run(['git', 'status'], capture_output=True)
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
        ['git', 'pull'],
        ['git', 'push', '-u', 'origin', branch],
        ['git', 'pull'],
    ]
    for cmd in cmds:
        run(cmd)

    os.chdir(cwd)

def check_changes():
    res = run(['git', 'status'])
    modified_fns = []
    for line in res.stdout.decode('utf-8'):
        if "Untracked files" in line:
            print(colored(res.stdout, "red"))
            print("Commit or delete 'Untracked files' before continuing")
            return False
        if "modified" in line:
            modified_fns.append(line.split(":   ")[1])
    for fn in modified_fns:
        if 'go.sum' in fn:
            continue
        if 'go.mod' in fn:
            continue
        print(colored(res.stdout, "red"))
        print("Commit your changes before continuing")
        return False

    return True

def update(repo, dependencies):
    if not repo:
        raise("Cannot update without repo and dependencies")

    if not dependencies:
        print("No dependencies to update")

    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    try:
        res = run(['git', 'pull'])
        if res.returncode != 0:
            raise("fix pull then try again")
        for dep in dependencies:
            cmd = ['go', 'get', '-u', dep]
            res = run(cmd)
            if res.returncode != 0:
                raise("Update failure")
        if not check_changes():
            raise("bad repository state, will not update")
        res = run(['git', 'commit', 'go.mod', 'go.sum', '-m',
                   'update deps'])
        # 1 means nothing to commit, not an error
        if res.returncode != 0 and res.returncode != 1:
            raise("could not commit")
        res = run(['git', 'push'])
        if res.returncode != 0:
            raise("could not push")
    except:
        os.chdir(cwd)
        raise
    os.chdir(cwd)

def build(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['go', 'build', './...'])
    os.chdir(cwd)

def test(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['go', 'test', '-v', './...'])
    os.chdir(cwd)

def status(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['git', 'status'])
    os.chdir(cwd)
    return res

def merge(repo):
    if not repo:
        raise("need repo to build!")
    cwd = os.getcwd()
    os.chdir(get_dir(repo))
    res = run(['git', 'status'])
    #res = run(['git', 'commit', '-m', 'update deps', '.'])
    #res = run(['git', 'push'])
    os.chdir(cwd)
