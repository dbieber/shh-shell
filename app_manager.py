from command_executor import setup_executor
from command_executor import execute_command

class AppManager(object):

    def __init__(self):
        self.current_app = None
        setup_executor(app_manager=self)

    def in_app(self):
        return self.current_app is not None

    def quit_app(self):
        # TODO(Bieber): Use decorator to check that you're in an app
        self.current_app = None

    def handle_line(self, line):
        if self.in_app():
            func = self.current_app.get('handle_line')
            func and func(line)
        elif line and line[0] == ':':
            # TODO(Bieber): These commands should be treated like any other app
            execute_command(line[1:])

    def start_app(self, handle_line=None):
        self.current_app = {
            'handle_line': handle_line
        }
