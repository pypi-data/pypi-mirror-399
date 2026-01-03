from typing import Any


class Decoder:
    def __init__(self, src: str = "[]") -> None:
        self.src = self.strip(src, " \t\n\r")
        self.cursor = 0

    # helper
    @staticmethod
    def strip(s: str, chars: str):
        for char in chars:
            s = s.replace(char, "")
        return s

    @staticmethod
    def error(expected: str, got: str, pos: int):
        raise Exception(f"Expected `{expected}` got `{got}` at pos={pos}`")

    # methods
    def eof(self) -> bool:
        return self.cursor >= len(self.src)

    def peek(self) -> str:
        if self.eof():
            return ""
        return self.src[self.cursor]

    def consume(self) -> str:
        if self.eof():
            return ""

        curr = self.peek()
        self.cursor += 1
        return curr

    def expect(self, expected: str, consume: bool = False):
        got = (self.consume if consume else self.peek)()
        if got != expected:
            self.error(expected, got, self.cursor)

    def parse_literal(self) -> str:
        start = self.cursor

        while self.peek() not in '"=[]{},"':
            self.consume()

        res = self.src[start : self.cursor]
        if len(res) == 0:
            self.error("Literal", self.peek(), self.cursor)

        return res

    def parse_int(self) -> int:
        start = end = self.cursor

        while self.peek().isnumeric():
            end += 1
            self.consume()

        res = self.src[start:end]
        if len(res) == 0:
            self.error("Integer", self.peek(), self.cursor)

        return int(res)

    def parse_str(self) -> str:
        self.expect('"', consume=True)  # "
        if self.peek() == '"':
            self.consume()  # "
            return ""
        s = self.parse_literal()
        self.expect('"', consume=True)  # "
        return s

    def parse_value(self) -> int | str | bool:
        # VALUE := INTEGER | [QUOTE LITERAL QUOTE] | BOOL
        if self.peek() == '"':
            return self.parse_str()
        if self.src[self.cursor : self.cursor + 4] == "true":
            self.cursor += 4
            return True
        if self.src[self.cursor : self.cursor + 5] == "false":
            self.cursor += 5
            return False
        return self.parse_int()

    def parse_list(self) -> list[Any]:
        result = []
        self.expect("{", consume=True)

        if self.peek() == "}":
            self.consume()  # }
            return result

        value = self.parse_value()
        result.append(value)
        while self.peek() == ",":
            self.consume()  # ,
            value = self.parse_value()
            result.append(value)
        self.expect("}", consume=True)

        return result

    def parse_kv(self) -> tuple[str, Any]:
        # KV := KEY EQ [VALUE | EXPR]
        key = self.parse_literal()
        self.expect("=", consume=True)
        if self.peek() == "[":
            value = self.parse()
        elif self.peek() == "{":
            value = self.parse_list()
        else:
            value = self.parse_value()
        return (key, value)

    def parse(self) -> dict:
        # LBRACKET KV (COMMA KV)* RBRACKET
        result = {}
        self.expect("[", consume=True)
        if self.peek() == "]":
            self.consume()
            return result
        key, value = self.parse_kv()
        result[key] = value
        while self.peek() == ",":
            self.consume()  # ,
            key, value = self.parse_kv()
            result[key] = value
        self.expect("]", consume=True)
        return result

    @staticmethod
    def decode(s: str) -> dict:
        return Decoder(s).parse()
