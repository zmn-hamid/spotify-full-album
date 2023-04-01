import termcolor

BLOCK = '\u2588'
LINE = '|'


class Style:
    @staticmethod
    def header(text: str):
        return termcolor.colored(text, 'red', attrs=['bold'])

    @staticmethod
    def album(text: str):
        return termcolor.colored(text, 'cyan', attrs=['bold'])

    @staticmethod
    def new_track(text: str):
        return termcolor.colored(text, 'green', attrs=['bold'])

    @staticmethod
    def old_track(text: str):
        return '\x1B[9m' + termcolor.colored(text, 'yellow') + '\x1B[29m'

    @staticmethod
    def question(text: str):
        return termcolor.colored(text, attrs=['blink', 'bold'])

    @staticmethod
    def intro(text: str):
        return termcolor.colored(text, 'green', attrs=[])
