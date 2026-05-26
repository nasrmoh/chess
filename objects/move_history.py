from dataclasses import dataclass

@dataclass
class CapturedData:
        kind: str
        color: str
        from_square: tuple[int, int]
@dataclass
class CastlingData:
        color: str
        from_square: tuple[int, int]
        to_square: tuple[int, int]


@dataclass
class HistoryEntry:
    kind: str # kind of piece
    color: str
    from_square: tuple[int, int]
    to_square: tuple[int, int]
    captured: CapturedData | None
    promotion: str | None
    castling: CastlingData | None
