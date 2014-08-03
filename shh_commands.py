import os
import re
import sys
from datetime import datetime
from random import choice

from utils import sayable_datetime

commands = []

def command(pattern, **params):
    def command_decorator(func):
        def newfunc(*args, **kwargs):
            value = func(*args, **kwargs)
            return value
        newfunc.func_name = func.func_name

        regex_str = pattern.replace('{}', '(.*)')
        regex = re.compile(regex_str)
        name = params.get('name', func.func_name)

        command = Command(
            name=name,
            func=newfunc,
            regex=regex,
            params=params,
        )
        commands.append(command)

        return newfunc
    return command_decorator

class Command(object):

    def __init__(self, name, func, regex, params=None):
        self.name = name
        self.func = func
        self.regex = regex
        self.params = params

    def execute_if_match(self, cmd_str, scheduler=None, mailer=None):
        match = self.regex.match(cmd_str)
        if match:
            args = match.groups()
            kwargs = {}

            if self.params.get('require_scheduler'):
                kwargs['scheduler'] = scheduler
            if self.params.get('require_mailer'):
                kwargs['mailer'] = mailer

            self.func(*args, **kwargs)
            return True
        return False

@command('alarm')
def alarm():
    query = choice([
        'tell her about it YouTube',
        'wake me up when September ends YouTube',
        'piano man YouTube',
        'rhapsody in blue YouTube',
    ])
    feel_lucky(query)

@command('lucky {}')
def feel_lucky(query):
    query = query.replace(" ", "+")
    cmd = 'open "http://www.google.com/search?q={}&btnI"'.format(query)
    shell(cmd)

@command('time')
def time():
    shell('say `date "+%A, %B%e %l:%M%p"` &')

@command('status')
def status():
    say('ok')

@command('say {}')
def say(text):
    cmd = 'say "{}" &'.format(text)
    shell(cmd)

@command('shell {}')
def shell(cmd):
    dt = datetime.now().strftime('%k:%M:%S')
    print "[{}] Executing command: '{}'".format(dt, cmd)
    os.system(cmd)

@command('at {}:{}', require_scheduler=True)
def schedule(at, what, scheduler):
    scheduler.schedule(at, what)

@command('list commands')
def list_commands():
    list_str = ', '.join(cmd.name for cmd in commands)
    say(list_str)

@command('list jobs', require_scheduler=True)
def list_jobs(scheduler):
    jobs = scheduler.get_jobs()
    job_list_str = ', '.join('{}, {}'.format(
        sayable_datetime(at), what
    ) for at, what in jobs)
    say(job_list_str)

@command('todo {}', require_scheduler=True)
def save_todo(task, scheduler):
    pass

@command('email login', require_mailer=True)
def email_login_default(mailer):
    email_login('david810@gmail.com', mailer)

@command('email login {}', require_mailer=True)
def email_login(user, mailer):
    mailer.login(user)

@command('email {}', require_mailer=True)
def email(contents, mailer):
    mailer.mail(to='david810+shh@gmail.com',
                subject='shh {}'.format(datetime.now().strftime("%D %H:%M")),
                text=contents)

@command('check email', require_mailer=True)
def email(mailer):
    subjects = [msg['Subject'] for msg in mailer.check_mail()]
    say(', '.join(subjects))

@command('num messages', require_mailer=True)
def num_messages(mailer):
    count = len(mailer.check_mail())
    say('You have {} unread messages'.format(count))

@command('reload {}')
def reload_module(module_name):
    if module_name in sys.modules:
        module = sys.modules[module_name]
        reload(module)
