import os
import sys
import subprocess


def text_to_stream(text):
    p = os.pipe()
    os.write(p[1], text.encode('utf-8'))
    os.close(p[1])
    return os.fdopen(p[0], "r")


def run(cmd, stdin_text=None):
    stdin = text_to_stream(stdin_text) if stdin_text else sys.stdin
    result = subprocess.run(
        cmd, stdout=sys.stdout, stderr=sys.stderr, stdin=stdin)
    result.check_returncode()


run(["/home/ubuntu/scripts/matterTool.sh","interactive","start"], "levelcontrol subscribe current-level 0 1 7483 2")

