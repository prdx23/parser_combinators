from collections import namedtuple, Callable
from operator import add, or_
from functools import reduce


Result = namedtuple('Result', ['success', 'result', 'input'])


class Parser():

    def __init__(self, parse_func):
        self.parse = parse_func

    def __call__(self, inp):
        return self.parse(inp)

    def __add__(self, parser2):
        def parse_func(inp):
            res1 = self(inp)
            if not res1.success:
                return res1
            res2 = parser2(res1.input)
            if not res2.success:
                return res2
            return Result(True, [res1.result, res2.result], res2.input)
        return Parser(parse_func)

    def __or__(self, parser2):
        def parse_func(inp):
            res1 = self(inp)
            if res1.success:
                return res1
            return parser2(inp)
        return Parser(parse_func)

    def map(self, modify_fn):
        if isinstance(modify_fn, Callable):
            parse_fn = self.parse

            def new_fn(inp):
                return modify_fn(parse_fn(inp))
            self.parse = new_fn
        return self


class Char(Parser):

    def __init__(self, char):
        self.char = char

    def parse(self, inp):
        if not isinstance(inp, str) or inp == "":
            return Result(False, 'No string found to parse', '')
        if inp[0] == str(self.char):
            return Result(True, self.char, inp[1:])
        else:
            return Result(
                False, f'Expected "{self.char}" but got "{inp[0]}"', ''
            )


def choice(list_of_parsers):
    return reduce(or_, list_of_parsers)


def Any(list_of_chars):
    return choice(Char(x) for x in list_of_chars)


def sequence(list_of_parsers):
    return reduce(add, list_of_parsers)


def flatten(r):
    def flatten_list(l):
        if isinstance(l, list):
            return [x for inner in l for x in flatten_list(inner)]
        else:
            return [l]

    if r.success:
        return Result(True, flatten_list(r.result), r.input)
    else:
        return r


def Seq(list_of_chars):
    return sequence(Char(x) for x in list_of_chars).map(flatten)
