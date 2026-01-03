from typing import Any


class Encoder:
    @staticmethod
    def serialize(v: Any) -> str:
        if isinstance(v, dict):
            return Encoder.encode(v)
        elif isinstance(v, bool):
            return "true" if v else "false"
        elif isinstance(v, str):
            return '"' + v + '"'
        elif isinstance(v, int):
            return str(v)
        elif isinstance(v, list):
            parts = [Encoder.serialize(el) for el in v]
            return "{" + ",".join(parts) + "}"
        else:
            raise Exception(f"Type {type(v)} not implemented")

    @staticmethod
    def encode(d: dict):
        parts = []
        for k, v in d.items():
            parts.append(k + "=" + Encoder.serialize(v))
        return "[" + ",".join(parts) + "]"
