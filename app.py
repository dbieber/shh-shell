# shh: the shell for when you're mostly asleep

from datetime import date
from datetime import datetime

import Tkinter as tk
import os
from random import choice

now_str = str(datetime.now()).replace(" ","_")
log_filename = "logs/nighttype-log-{}".format(now_str)
log_file = open(log_filename, 'w')
text_filename = "text/nighttype-text-{}".format(now_str)
text_file = open(text_filename, 'w')

os.system("rm nighttype-text")
os.system("rm nighttype-log")
os.system("ln -s {} nighttype-text".format(text_filename))
os.system("ln -s {} nighttype-log".format(log_filename))

current_cmd = ""


def feel_lucky(query):
    os.system('open "http://www.google.com/search?q={}&btnI"'.format(query))


def onKeyPress(event):
    global current_cmd

    log_str = "{}:{},{},{},{},{},{}\n".format(
        datetime.now(),
        event.num,
        event.keysym_num,
        event.keysym,
        event.serial,
        event.state,
        event.char,
    )
    log_file.write(log_str)
    log_file.flush()

    if event.char:
        current_cmd += event.char

    text_str = event.char
    if event.keysym == 'Return':
        text_str = '\n'

        if current_cmd[:6].upper() == 'STATUS':
            os.system('say ok')

        if current_cmd[:5].upper() == 'LUCKY':
            query = current_cmd[5:].replace(" ", "+")
            feel_lucky(query)

        if current_cmd[:5].upper() == 'ALARM':
            queries = [
                'tell her about it youtube',
                'wake me up when september ends youtube',
            ]
            query = choice(queries)
            feel_lucky(query)

        if current_cmd[:3].upper() == 'CMD':
            pass
            # os.system(current_cmd[3:])

        current_cmd = ''

    # TODO(Bieber): Bring to front a bunch

    text_file.write(text_str)
    text_file.flush()


if __name__ == '__main__':
    root = tk.Tk()
    root.attributes('-topmost', 1)
    root.focus_set()
    root.geometry('300x200')
    text = tk.Text(root, background='black', foreground='white', font=('Roboto Slab', 12))
    text.pack()
    root.bind('<KeyPress>', onKeyPress)
    root.mainloop()
