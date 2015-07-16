from fabric.api import *
from fabric.utils import abort
from fabric.contrib.project import rsync_project
from fabric.contrib.files import exists

if not env.hosts:
    env.hosts = ['cotillion.atst.io']

target_dir = '/srv/www/paircasts.com/current'
backup_dir = target_dir+'-backup'
staging_dir = target_dir+'-staging'

@task(default=True)
def deploy():
    puts('> Cleaning up previous backup and staging dir')
    run('rm -rf %s %s' % (backup_dir, staging_dir))

    if exists(target_dir):
        puts('> Preparing staging')
        run('cp -r %s %s' % (target_dir, staging_dir))
    else:
        puts('> Creating staging')
        run('mkdir %s' % (staging_dir))

    puts('> Uploading changes')
    with cd(staging_dir):
        with hide('stdout'):
            extra_opts = '--omit-dir-times'
            rsync_project(
                env.cwd,
                './',
                delete=True,
                exclude=['.git', '*.py', '*.pyc'],
                extra_opts=extra_opts,
            )

    puts('> Switching changes to live')
    if exists(target_dir):
        run('mv %s %s' % (target_dir, backup_dir))

    run('mv %s %s' % (staging_dir, target_dir))

@task
def rollback():
    if exists(backup_dir):
        puts('> Rolling back to previous deploy')
        run('mv %s %s' % (target_dir, staging_dir))
        run('mv %s %s' % (backup_dir, target_dir))
    else:
        abort('Rollback failed, no backup exists')
