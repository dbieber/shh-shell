from __future__ import absolute_import

from datetime import datetime
from random import choice
from utils import sayable_datetime

from settings.secure_settings import *

import os
import re
import sys

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

    def execute_if_match(self, cmd_str,
                         scheduler=None,
                         mailer=None,
                         state=None):
        match = self.regex.match(cmd_str)
        if match:
            args = match.groups()
            kwargs = {}

            if self.params.get('require_scheduler'):
                kwargs['scheduler'] = scheduler
            if self.params.get('require_mailer'):
                kwargs['mailer'] = mailer
            if self.params.get('require_state'):
                kwargs['state'] = state

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
    dt = datetime.now().strftime('%k:%M:%S')
    with open('tmp-say', 'w') as tmp:
        print '[{}] Writing "{}" to tmp-say'.format(dt, text)
        tmp.write(text)
    cmd = 'cat tmp-say | say &'
    shell(cmd)

@command('shell {}')
def shell(cmd):
    dt = datetime.now().strftime('%k:%M:%S')
    print "[{}] Executing command: '{}'".format(dt, cmd)
    os.system(cmd)

@command('at {}:{}', require_scheduler=True)
def schedule(at, what, scheduler):
    scheduler.schedule(at, what)

@command('help')
def help():
    set_of_names = sorted(set(cmd.name for cmd in commands))
    list_str = ', '.join(set_of_names)
    help_message = """Welcome to the shh-shell!

The purpose of this shell is to let you use your computer without having to
exert any effort or do anything that might wake you up, even a little. That
means no monitors and no mouse. The shell wants to replace the pad of paper
you keep by your bedside.

All keystrokes are timestamped and logged.
Type :<command> to execute a command.
Type :help to pull up this help message.

Available commands are {}.
"""
    print help_message.format(list_str)

@command('list commands')
def list_commands():
    set_of_names = sorted(set(cmd.name for cmd in commands))
    list_str = ', '.join(set_of_names)
    say(list_str)

@command('list jobs', require_scheduler=True)
def list_jobs(scheduler):
    jobs = scheduler.get_jobs()
    job_list_str = ', '.join('{}, {}'.format(
        sayable_datetime(at), what
    ) for at, what in jobs)
    say(job_list_str)

@command('todo {}', require_scheduler=True, require_state=True)
def save_todo(task, scheduler, state):
    todo_list = state.get('todo_list', [])
    todo_list.append(task)
    state.set('todo_list', todo_list)
    if not state.get('todo_checkup_scheduled'):
        schedule('10pm', 'email_todo_summary', scheduler)
    state.set('todo_checkup_scheduled', True)

@command('list todos', require_state=True)
def list_todos(state):
    todo_list = state.get('todo_list', [])
    say(', '.join(todo_list))

@command('email_todo_summary', require_mailer=True, require_state=True)
def email_todo_summary(mailer, state):
    todo_list = state.get('todo_list', [])
    todo_list_str = '\n'.join('-  {}'.format(item) for item in todo_list)
    contents = """Did you accomplish what you set out to do?

        {}""".format(todo_list_str)
    subject = 'TODO Summary for {}'.format(datetime.now().strftime("%D"))
    mailer.mail(to=DEFAULT_EMAIL_RECIPIENT,
                subject=subject,
                text=contents)

    state.set('todo_checkup_scheduled', False)

@command('clear todos', require_state=True)
def clear_todos(state):
    state.delete('todo_list')

@command('reading list {}', require_state=True)
def reading_list(state):
    books = state.get('reading_list', [])
    say(' ,'.join(books))

@command('reading list {}', require_state=True)
def add_to_reading_list(book, state):
    books = state.get('reading_list', [])
    books.append(book)
    state.set(reading_list, books)

@command('login', require_mailer=True)
@command('mail login', require_mailer=True)
@command('email login', require_mailer=True)
def email_login_default(mailer):
    email_login(DEFAULT_EMAIL, mailer)

@command('login {}', require_mailer=True)
@command('mail login {}', require_mailer=True)
@command('email login {}', require_mailer=True)
def email_login(user, mailer):
    mailer.login(user)

@command('send email {}', require_mailer=True)
@command('email {}', require_mailer=True)
def email(contents, mailer):
    mailer.mail(to=DEFAULT_EMAIL_RECIPIENT,
                subject='shh {}'.format(datetime.now().strftime("%D %H:%M")),
                text=contents)

@command('check mail', require_mailer=True)
@command('check email', require_mailer=True)
def check_email(mailer):
    subjects = [msg.subject() for msg in mailer.check_mail()]
    say(', '.join(subjects))

@command('read mail {}', require_mailer=True)
@command('read email {}', require_mailer=True)
def read_email(subject_bit, mailer):
    for msg in mailer.check_mail():
        if subject_bit.strip().lower() in msg.subject().lower():
            # TODO(Bieber): Say with timeout
            print msg.text()
            return
    print 'Not found'

@command('num messages', require_mailer=True)
def num_messages(mailer):
    count = len(mailer.check_mail())
    say('You have {} unread messages'.format(count))

@command('text {} TO {}')
def send_text(message_text, phone_number):
    script = """
    tell application "Messages"
      send "{}" to buddy "{}" of service {}
    end tell
    """.format(
        message_text,
        phone_number,
        DEFAULT_SERVICE,
    )
    os.system("echo '{}' | osascript".format(script))

@command('reload')
def reload_this():
    reload_module(__name__)

@command('reload {}')
def reload_module(module_name):
    if module_name in sys.modules:
        module = sys.modules[module_name]
        reload(module)
    else:
        say('{} not found'.format(module_name))

@command('goal {}', require_state=True)
def set_goal(goal, state):
    goals = state.get('goals', [])
    goals.append(goal)
    state.set('goals', goals)

@command('list goals', require_state=True)
def list_goals(state):
    goals = state.get('goals', [])
    say(', '.join(goals))
