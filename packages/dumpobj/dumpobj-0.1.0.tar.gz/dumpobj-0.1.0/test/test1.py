import sys

from dumpobj.formatter.color_formatter import ColorFormatter

from dumpobj import dump, Dump

from dumpobj.formatter.json_formatter import JSONFormatter

from dumpobj.formatter.plain_formatter import PlainFormatter

if __name__ == "__main__":
    class A:
        PROP1 = "abc"
        PROP2 = [12, 34, 56]
        PROP3 = {"a": 1, "b": 2}

        def __init__(self):
            self.member1 = 1
            self.member2 = 2 + 3j
            self.member3 = "ABCDEFG"
            self.member4 = object()
            self.member5 = [5, 6, 7, 8]
            self.member6 = (5, 6, 7, 8)
            self.member7 = lambda x: x
            self.member8 = type
            self.member9 = range(100)

        class B:
            class C:
                PROP = "Hello, World!"

        PROP = B()

    def handle_A(node, obj: A, depth: int):
        raise RuntimeError("Custom handler error for testing.")

    from colortty import ColorTTY

    #ColorTTY.EscapeChar = r'\e'

    b = {
        "a": [1, 2, 3, 4, 5],
        "b": "ABCDEFG",
        "c": {"x": 1, "y": 2},
    }

    d = Dump()
    #d.register_handle(A, handle_A)
    d.set_inline(False)
    d.head_count = 100
    d.set_formatter(PlainFormatter())
    for l in d.dump(b):
        print(l)
