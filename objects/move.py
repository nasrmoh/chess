from .constants import (
    MOVE_NORMAL,
    MOVE_CAPTURE,
    MOVE_ENPASSANT,
    MOVE_CASTLE,
)


class Move:
    def __init__(self, from_square, to_square, kind=MOVE_NORMAL, payload=None):
        self.from_square: tuple[int, int] = from_square
        self.to_square: tuple[int, int] = to_square
        self.kind: str = kind
        self.payload: tuple[int, int] | list[tuple[int, int]] | None = payload

    def set_kind(self, kind):
        self.kind: str = kind

    def set_payload(self, payload):
        self.payload: tuple[int, int] | list[tuple[int, int]] | None = payload
