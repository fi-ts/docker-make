from dockermake.utils.helpers import System


def check_if_git_is_installed():
    cmd = ["git", "version"]
    System.run_command(cmd)
