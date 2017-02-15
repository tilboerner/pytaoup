#! /usr/bin/python3

""" The tao of unix programming, Python-adapted from github:globalcitizen/taoup

Quotes via:
https://raw.githubusercontent.com/globalcitizen/taoup/master/taoup
"""
import itertools
import os
import random
import re
import shutil
import sys
import textwrap

TAOFILE = os.path.expanduser('~/.taoup.txt')
QUOTES_URL = (
    'https://raw.githubusercontent.com/globalcitizen/taoup/master/taoup'
)


def wrap(txt):
    """Wrap txt to width of terminal"""
    global _wrapper
    width, height = shutil.get_terminal_size((80, 20))
    try:
        _wrapper.width = width
    except NameError:
        _wrapper = textwrap.TextWrapper(width=width)
    return '\n'.join(_wrapper.wrap(txt))


def fetch_quotes(url=QUOTES_URL, encoding='utf-8'):
    """Yield quotes fetched from original repo at github:globalcitizen/taoup"""
    from urllib.request import urlopen
    with urlopen(url, timeout=5) as response:
        if response.status != 200:
            raise ValueError('{status} {reason}'.format(**response.__dict__))
        body = response.read()
    text = body.decode(encoding)

    quoted = re.compile(
        r'"(?:[^"\\]|\\.)+"'  # double-quoted substrings
        '|'
        r"'(?:[^'\\]|\\.)+'"  # single-quoted substrings
    )
    for line in text.splitlines():
        if not line.strip().startswith('puts '):  # not a quote
            continue
        parts = quoted.findall(line)
        parts = (
            p[1:-1].replace(r'\"', '"').replace(r"\'", "'") for p in parts
        )
        quote = ''.join(parts).strip()
        if quote:
            yield quote


def write_quotes(quotes, append=False):
    """Write quotes to TAOFILE"""
    mode = 'a' if append else 'w'
    with open(TAOFILE, mode, encoding='UTF-8') as taofile:
        for quote in quotes:
            print(quote, file=taofile)


def random_item(iterable):
    # http://nedbatchelder.com/blog/201208/selecting_randomly_from_an_unknown_sequence.html
    # http://stackoverflow.com/questions/12128948/python-random-lines-from-subfolders/12134726#12134726
    choice = None
    for i, item in enumerate(iterable):
        if random.randint(0, i) == 0:
            choice = item
    return choice


def yield_quotes(path):
    with open(path) as infile:
        yield from (line for line in infile if line.strip())


def all(lines, jump=None):
    """print all non-blank lines in file, waiting for enter after each one"""
    count = 0
    for line in lines:
        if jump and jump(line):
            print('\n', wrap(line))
        else:
            count += 1
            print(wrap('({:,}) {}'.format(count, line)))
            input('<enter>')
            print('\033[A' + ' ' * len('<enter>'))


def usage(script):
    print('''{script} [random|all]

The Tao of Unix Programming, lines from https://github.com/globalcitizen/taoup/
'''.format(script=script))


def main(script='taoup', mode='random'):

    def is_header(line):
        return line.startswith('-----')

    if not os.path.exists(TAOFILE):
        quotes = list(fetch_quotes(QUOTES_URL))
        write_quotes(quotes)
    else:
        quotes = yield_quotes(TAOFILE)
    try:
        if mode == 'random':
            quote = random_item(q for q in quotes if not is_header(q))
            if quote:
                print(repr(quote))
        elif mode == 'all':
            all(quotes, jump=is_header)
            print('Done, thank you!')
        else:
            usage(script)
            exit(0 if mode in {'-h', '--help'} else 1)
    except KeyboardInterrupt:
        if mode == 'all':
            print('\b\b', end='')  # erase "^C" from terminal
            print('Okay, bye.')


if __name__ == '__main__':
    script, *args = sys.argv
    *_, script = os.path.split(script)
    main(script, *args)
