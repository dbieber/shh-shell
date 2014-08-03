# shh: the shell for when you're mostly asleep

from datetime import datetime

import Tkinter as tk
import os

from command_executor import execute_command

LOG_DIR = 'logs'
TEXT_DIR = 'texts'

class ShhShell(object):

    def __init__(self):
        self.root = tk.Tk()
        self.text = tk.Text(self.root,
                            background='black',
                            foreground='white',
                            font=('Roboto Slab', 12))
        self.initialize_gui()
        self.initialize_logging()

        self.current_cmd = ''

    def initialize_gui(self):
        self.root.attributes('-topmost', 1)
        self.root.focus_set()
        self.root.geometry('300x200')
        self.text.pack()
        self.root.bind('<KeyPress>', self.onKeyPress)
        self.root.bind('<FocusIn>', self.onFocusIn)
        self.text.bind('<FocusIn>', self.onTextFocusIn)
        self.text.bind('<FocusOut>', self.onFocusOut)

    def initialize_logging(self):
        os.system("mkdir -p {}".format(LOG_DIR))
        os.system("mkdir -p {}".format(TEXT_DIR))

        now_str = str(datetime.now()).replace(" ", "_")
        log_filename = "{}/log-{}".format(LOG_DIR, now_str)
        self.log_file = open(log_filename, 'w')
        text_filename = "{}/text-{}".format(TEXT_DIR, now_str)
        self.text_file = open(text_filename, 'w')

        os.system("touch shh-text && rm shh-text")
        os.system("touch shh-log && rm shh-log")
        os.system("ln -s {} shh-text".format(text_filename))
        os.system("ln -s {} shh-log".format(log_filename))

    def start(self):
        self.root.mainloop()

    def onFocusIn(self, event):
        self.text.focus_set()

    def onTextFocusIn(self, event):
        self.root.attributes('-topmost', 1)
        self.root.attributes('-topmost', 0)
        os.system('say focused &')

    def onFocusOut(self, event):
        os.system('say focus lost &')

    def onKeyPress(self, event):
        # Log event
        log_str = "{}:{},{},{},{},{},{}\n".format(
            datetime.now(),
            event.num,
            event.keysym_num,
            event.keysym,
            event.serial,
            event.state,
            event.char,
        )
        self.log_file.write(log_str)
        self.log_file.flush()

        text_str = event.char

        # Handle commands
        if event.keysym == 'BackSpace':
            self.current_cmd = self.current_cmd[:-1]
        elif event.keysym == 'Return':
            text_str = '\n'
            cmd = self.current_cmd.strip()
            self.current_cmd = ''
            if cmd and cmd[0] == ':':
                execute_command(cmd[1:])
        elif event.char:
            self.current_cmd += event.char

        # Edit text file
        self.text_file.write(text_str)
        self.text_file.flush()

def main():
    app = ShhShell()
    app.start()

if __name__ == '__main__':
    main()
