"""
main.py - main functionality for xxbuilder tool
"""

import click
import sys
import os
import pathlib

from builder import build

proj_conf = {
    'xxprimitives': {
        'repo': 'git@gitlab.com:xx_network/primitives',
        'dependencies': [],
    },
    'xxcrypto': {
        'repo': 'git@gitlab.com:xx_network/crypto',
        'dependencies': ['xxprimitives'],
    },
    'xxcomms': {
        'repo': 'git@gitlab.com:xx_network/comms',
        'dependencies': ['xxprimitives', 'xxcrypto'],
    },
    'primitives': {
        'repo': 'git@gitlab.com:elixxir/primitives',
        'dependencies': ['xxprimitives'],
    },
    'crypto': {
        'repo': 'git@gitlab.com:elixxir/crypto',
        'dependencies': ['xxprimitives', 'xxcrypto', 'primitives'],
    },
    'comms': {
        'repo': 'git@gitlab.com:elixxir/comms',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto'],
    },
    'server': { # Note -- leaving out GPU, ekv, and others for now!
        'repo': 'git@gitlab.com:elixxir/server',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'comms'],
    },
    'gateway': {
        'repo': 'git@gitlab.com:elixxir/gateway',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'comms'],
    },
    'client': {
        'repo': 'git@gitlab.com:elixxir/client',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'comms'],
    },
    'udb': {
        'repo': 'git@gitlab.com:elixxir/user-discovery-bot',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'comms', 'client'],
    },
}


#@click.command(help='XX Network Builder')
@click.group(chain=True)
def cli():
    os.chdir(os.path.join(pathlib.Path.home(), 'builder'))
    print("Path: ", os.getcwd())

#@cli.argument('pkg', help=('Any of {}'.format(','.join(proj_conf.keys()))))

@cli.command('clone')
def clone():
    for k, v in proj_conf.items():
        build.clone(v['repo'])

@cli.command('checkout')
@click.argument('branch')
def checkout(branch):
    for k, v in proj_conf.items():
        build.checkout(v['repo'], branch)

@cli.command('build')
def buildcmd():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@gitlab.com:', 'gitlab.com/') for repo in dep_repos]
        build.build(v['repo'])

@cli.command('update')
def update():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@gitlab.com:', "gitlab.com/") for repo in dep_repos]
        build.update(v['repo'], deps)

@cli.command('test')
def test():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@gitlab.com:', "gitlab.com/") for repo in dep_repos]
        build.test(v['repo'])


@cli.command('push')
def push():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@gitlab.com:', "gitlab.com/") for repo in dep_repos]
        build.push(v['repo'])


if __name__ == '__main__':
    cli()
