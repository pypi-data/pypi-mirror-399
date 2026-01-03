from nanokv.encoder import Encoder
from nanokv.decoder import Decoder

__all__ = ["dumps", "loads"]


def dumps(d: dict) -> str:
    return Encoder.encode(d)


def loads(s: str) -> dict:
    return Decoder.decode(s)
