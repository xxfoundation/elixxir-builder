"""
building.py - utils for checking out and building
"""

import os
import subprocess
import shutil

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
    if os.path.exists(target_dir):
        shutil.rmtree(target_dir)
    clone(repo)

    cwd = os.getcwd()
    os.chdir(target_dir)
    print("Path: ", os.getcwd())
    cmds = [
        ['git', 'fetch' ],
        ['git', 'checkout', '-B', branch],
        #['git', 'branch', '--set-upstream-to=origin/{}'.format(branch), branch],
        ['git', 'pull'],
        ['git', 'push', '-u', 'origin', branch],
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
            cmd = ['go', 'get', dep]
            res = run(cmd)
            if res.returncode != 0:
                raise("Update failure")
            res = run(cmd)
            if res.returncode != 0:
                raise("Second update failure")
        if not check_changes():
            raise("bad repository state, will not update")
        run(['go', 'mod', 'tidy'])
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
    if not check_changes():
        print(colored("{} needs changes committed".format(repo), "red"))
    res = run(['git', 'diff', '--name-only', 'release'])
    changed_fns = []
    for line in res.stdout.decode('utf-8').splitlines():
        if 'go.sum' in line or 'go.mod' in line:
            continue
        changed_fns.append(line)
    if len(changed_fns) != 0:
            print(colored(("Changed files present for {}: "
                          "{}").format(repo, changed_fns), "red"))
    os.chdir(cwd)
    return res

def mergeinto(repo, target):
    if not repo or not target:
        raise("need repo and target to build!")
    cwd = os.getcwd()
    branch = get_branch(repo)
    os.chdir(get_dir(repo))
    try:
        run(['git', 'pull'])
        run(['git', 'merge', target])
        run(['git', 'checkout', '--ours', 'go.mod', 'go.sum'])
        run(['git', 'commit'])
        res = run(['git', 'push'])
        if res.returncode != 0:
            raise("fix errors and rerurn")
        res = run(['git', 'diff', '--name-only', target])
        changed_fns = []
        for line in res.stdout.decode('utf-8'):
            if 'go.sum' in line or 'go.mod' in line:
                continue
            changed_fns.append(line)
        if len(changed_fns) != 0:
            print(colored(("Changed files present, not merging: "
                          "{}").format(changed_fns), "red"))
        else:
            res = run(['git', 'checkout', target])
            if res.returncode != 0:
                raise("unable to checkout target")
            res = run(['git', 'merge', branch])
            if res.returncode != 0:
                raise("unable to merge branch")
            res = run(['git', 'push'])
            if res.returncode != 0:
                raise("unable to push to target")
    except:
        os.chdir(cwd)
        raise
    os.chdir(cwd)

def mergefrom(repo, target):
    if not repo or not target:
        raise("need repo and target to build!")
    cwd = os.getcwd()
    branch = get_branch(repo)
    os.chdir(get_dir(repo))
    try:
        run(['git', 'pull'])
        run(['git', 'merge', target])
        run(['git', 'checkout', '--ours', 'go.mod', 'go.sum'])
        run(['git', 'commit'])
        res = run(['git', 'push'])
        if res.returncode != 0:
            raise("fix errors and rerurn")
    except:
        os.chdir(cwd)
        raise
    os.chdir(cwd)
