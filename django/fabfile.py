from fabric.api import *
env.shell = '/bin/bash -c'


def deploy_test():

    env.host_string = '119.148.77.182'
    env.user = 'vron'

    with open('../infra/fab_pwd') as f:
        my_lines = f.readlines()
        if len(my_lines) > 0:
            env.password = my_lines[0]

    with cd("/vron"):
        sudo("git reset --hard")
        sudo("git pull")

    with prefix('source /vronvenv/bin/activate'):
        sudo("python /vron/django/manage.py migrate")

    sudo("service httpd reload")
