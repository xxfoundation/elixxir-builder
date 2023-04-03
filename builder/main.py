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
        'repo': 'git@git.xx.network:xx_network/primitives',
        'dependencies': [],
    },
    'grpc-web-go-client': {
        'repo': 'git@git.xx.network:elixxir/grpc-web-go-client',
        'dependencies': [],
    },
    'xxcrypto': {
        'repo': 'git@git.xx.network:xx_network/crypto',
        'dependencies': ['xxprimitives'],
    },
    'xxcomms': {
        'repo': 'git@git.xx.network:xx_network/comms',
        'dependencies': ['xxprimitives', 'xxcrypto', 'grpc-web-go-client'],
    },
    'primitives': {
        'repo': 'git@git.xx.network:elixxir/primitives',
        'dependencies': ['xxprimitives'],
    },
    'crypto': {
        'repo': 'git@git.xx.network:elixxir/crypto',
        'dependencies': ['xxprimitives', 'xxcrypto', 'primitives'],
    },
    'ring': {
        'repo': 'git@git.xx.network:xx_network/ring',
        'dependencies': [],
    },
    'comms': {
        'repo': 'git@git.xx.network:elixxir/comms',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'grpc-web-go-client'],
    },
    'server': { # Note -- leaving out GPU, ekv, and others for now!
        'repo': 'git@git.xx.network:elixxir/server',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'comms',
                         'grpc-web-go-client'],
    },
    'permissioning': {
        'repo': 'git@git.xx.network:elixxir/registration',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'comms',
                         'grpc-web-go-client'],
    },
    'client-registrar': {
        'repo': 'git@git.xx.network:elixxir/client-registrar',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'comms',
                         'permissioning',
                         'grpc-web-go-client'],
    },
    'gateway': {
        'repo': 'git@git.xx.network:elixxir/gateway',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'comms',
                         'grpc-web-go-client'],
    },
    'client': {
        'repo': 'git@git.xx.network:elixxir/client/v4',
        'dependencies': ['xxprimitives', 'xxcrypto', 'grpc-web-go-client',
                         'xxcomms', 'primitives', 'crypto', 'ring', 'comms'],
    },
    'udb': {
        'repo': 'git@git.xx.network:elixxir/user-discovery-bot',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'comms', 'client'],
    },
    'xxdk-wasm': {
        'repo': 'git@git.xx.network:elixxir/xxdk-wasm',
        'dependencies': ['xxprimitives', 'xxcrypto', 'grpc-web-go-client',
                         'xxcomms', 'primitives', 'crypto', 'ring',
                         'comms', 'client'],
    },
    'notifications-bot': {
        'repo': 'git@git.xx.network:elixxir/notifications-bot',
        'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
                         'primitives', 'crypto', 'ring', 'comms', 'grpc-web-go-client'],
    },
    # 'coupon-bot': {
    #     'repo': 'git@git.xx.network:elixxir/coupon-bot',
    #     'dependencies': ['xxprimitives', 'xxcrypto', 'xxcomms',
    #                      'primitives', 'crypto', 'ring', 'comms', 'client'],
    # },
}

#@click.command(help='XX Network Builder')
@click.group(chain=True)
def cli():
    os.chdir(os.path.join(pathlib.Path.home(), 'builder'))
    print("Path: ", os.getcwd())

#@cli.argument('pkg', help=('Any of {}'.format(','.join(proj_conf.keys()))))

@cli.command('clone', help=('clones fresh copies of everything, will fail '
                            'if anything is pre-existing. Delete your '
                            'xx_network and elixxir directories before '
                            'running this command'))
def clone():
    for k, v in proj_conf.items():
        build.clone(v['repo'])

@cli.command('checkout', help=('create a new branch, if needed, and checkout'))
@click.argument('branch')
def checkout(branch):
    for k, v in proj_conf.items():
        build.checkout(v['repo'], branch)

@cli.command('build', help=('Status command, runs build on everything'))
def buildcmd():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@git.xx.network:', 'git.xx.network/') for repo in dep_repos]
        build.build(v['repo'])

@cli.command('update', help=('Runs go get on each dependency, then pushes '
                             'go.mod and go.sum back up to the repository. '
                             'This will fail if you have uncommitted changes '
                             'in a repository.'))
def update():
    for k, v in proj_conf.items():
        # if k != "client":
        #      continue
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@git.xx.network:', "git.xx.network/") for repo in dep_repos]
        build.update(v['repo'], deps)

@cli.command('test', help=('Status command, runs go test on everything'))
def test():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@git.xx.network:', "git.xx.network/") for repo in dep_repos]
        build.test(v['repo'])

@cli.command('mergeinto', help=('Merge all changes from this branch, then'
                                ' merge into it if go.sum and go.mod are the'
                                ' only changes'))
@click.argument('target')
def mergeinto(target):
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@git.xx.network:', "git.xx.network/") for repo in dep_repos]
        build.mergeinto(v['repo'], target)

@cli.command('mergefrom', help=('Merge all changes from this branch'))
@click.argument('target')
def mergefrom(target):
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@git.xx.network:', "git.xx.network/") for repo in dep_repos]
        build.mergefrom(v['repo'], target)


@cli.command('status', help=('Report changes between us and release'))
def status():
    for k, v in proj_conf.items():
        branch = str(build.get_branch(v['repo']))
        dep_repos = [proj_conf[dep]['repo'] for dep in v['dependencies']]
        deps = ['{}@{}'.format(repo, branch).replace(
            'git@git.xx.network:', "git.xx.network/") for repo in dep_repos]
        build.status(v['repo'])

if __name__ == '__main__':
    cli()
