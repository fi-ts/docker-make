import logging
try:
    import urlparse
except ModuleNotFoundError:
    import urllib.parse as urlparse

from dockermake.utils.helpers import System


def get_gitsha1_hash_of_head():
    cmd = ["git", "rev-parse", "--short=8", "HEAD"]
    out, _, _ = System.run_command(cmd, fail_on_bad_return_code=False)
    return out


def get_git_remote_origin_url():
    cmd = ["git", "config", "--get", "remote.origin.url"]
    url, _, _ = System.run_command(cmd, fail_on_bad_return_code=False)
    return url


def extract_git_repository(url):
    parts = []

    if url:
        parsed_url = urlparse.urlparse(url)
        if "@" in parsed_url.netloc:
            parts.append(parsed_url.netloc.split("@")[-1])
        else:
            parts.append(parsed_url.netloc)
        if "/" in parsed_url.path:
            parts.append(parsed_url.path.split("/")[1])
        else:
            parts.append(parsed_url.path)

    if parts:
        group = "/".join(parts)
    else:
        group = None

    logging.debug("Git server and repository (derived from git remote url) is: %s", group)
    return group
