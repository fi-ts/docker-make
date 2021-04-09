

try:
    from termcolor import colored

    HAS_TERMCOLOR = True
except ImportError:
    HAS_TERMCOLOR = False


def info(msg, color=None, end="\n"):
    print(_try_color(msg, color), end=end)


def warn(msg):
    print(_try_color(msg, "yellow"))


def error(msg):
    print(_try_color(msg, "red"))


def banner(color="white"):
    print(_try_color(80 * "*", color))


def _try_color(msg, color):
    if HAS_TERMCOLOR:
        return colored(msg, color)
    return msg
