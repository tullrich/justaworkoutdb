from fabric.api import *

env.hosts = ['wwwhost@fitness.tullrich.com']
code_dir = '/home/wwwhost/justaworkoutdb'


def push():
    local("git push origin master")


def start():
	with cd(code_dir):
		run("uwsgi uwsgi.ini")


def stop():
	run("echo q > /tmp/justaworkoutdb.fifo")


def reload():
	run("echo r > /tmp/justaworkoutdb.fifo")


def deploy():
	with cd(code_dir):
		run("git pull")
		run("bower update")
		run("alembic upgrade head")
		run("echo r > /tmp/justaworkoutdb.fifo")
