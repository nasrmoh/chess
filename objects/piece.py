from __future__ import annotations
from typing import TYPE_CHECKING
from .constants import (
    WHITE,
    BLACK,
    DIAGONALS,
    CARDINALS,
    KNIGHT_OFFSET,
    KSK_COL, QSK_COL,
    PAWN, KNIGHT, ROOK, KING, BISHOP, QUEEN, MOVE_NORMAL, MOVE_CASTLE, CASTLE_POSITION, KING_SIDE, QUEEN_SIDE
)
if TYPE_CHECKING:
    from .board import GameBoard
from abc import ABC, abstractmethod
from .move import Move


class Piece(ABC):
    def __init__(self, color: str, pos : tuple[int, int], has_moved = False):
        self.color = color
        self.has_moved = has_moved
        self.is_active = True
        self.pos = pos
        self.kind = ""

    @abstractmethod
    def generate_pseudo_legal_moves(self, board : GameBoard) -> list[Move]:
        """
           See `is_pseudo_legal_move` for the definition of a pseudo-legal move
        """
        pass

    def update_after_move(self, to_square : tuple[int, int]):
        if not self.has_moved:
            self.has_moved = True
        self.pos = to_square

    def is_pseudo_legal_move(
        self,
        dest_square: tuple[int, int],
        board : GameBoard,
    ) -> bool:
        """
            A move is pseudo-legal if it is within bounds of the board, and it is not blocked by an ally,
            does not account for checks.
        """
        return dest_square in self.generate_pseudo_legal_moves(board)

    def is_ally(self, other: Piece) -> bool:
        return self.color == other.color

    def is_enemy(self, other: Piece) -> bool:
        return not self.is_ally(other)

    def is_promotable(self) -> bool:
        return False

    def captured(self):
        self.is_active = False


class SlidingPiece(Piece):
    """
    Represents pieces that "slide" i.e., Queens, Rooks, and Bishops.
    Exists primarily so that the method get_sliding_moves is not accessible by other piece
    subclasses.
    """

    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)

    @abstractmethod
    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        pass

    def get_sliding_moves(
        self,
        board : GameBoard,
        directions: list[tuple[int, int]],
    ) -> list[Move]:
        """
        Generates pseudo-legal moves for sliding pieces (rook, bishop, queen) by extending in each direction until blocked.
        Includes the first enemy square, stops at allies.
        """
        row, col = self.pos
        pseudo_legal_moves = []
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            while board.in_bounds((new_row, new_col)):
                possible_piece = board.get_square_contents((new_row, new_col))
                if (
                    possible_piece is None
                ):  # no piece id found, i.e., empty square then add the move
                    pseudo_legal_moves.append(Move(self.pos, (new_row, new_col)))
                elif self.is_enemy(possible_piece):
                    pseudo_legal_moves.append(
                        Move(self.pos, (new_row, new_col))
                    )  # enemy, add, then stop sliding
                    break
                else:
                    # ally, stop sliding
                    break
                new_row += dr
                new_col += dc
        return pseudo_legal_moves


class Pawn(Piece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = PAWN

    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        """
        Includes :
            Single and double jumps assuming the path is empty and a piece has not moved for the latter
            Diagonal captures assuming there is an enemy piece
        """
        row, col = self.pos
        pseudo_legal_moves = []
        dv = -1 if self.color == WHITE else 1  # vertical direction
        one_forward = row + dv
        two_forward = row + (dv * 2)

        # single jump moves
        if board.in_bounds((one_forward, col)) and board.is_empty((one_forward, col)):
            pseudo_legal_moves.append(Move(self.pos, (one_forward, col)))

            # double jump moves (check only if there is a pseudo-legal single move)
            if (
                not self.has_moved
                and board.is_empty((two_forward, col))
                and board.in_bounds((two_forward, col))
            ):
                pseudo_legal_moves.append(Move(self.pos, (two_forward, col)))

        # Diagonals
        for dh in [-1, 1]:
            new_col = col + dh
            if board.in_bounds((one_forward, new_col)) and not board.is_empty(
                (one_forward, new_col)
            ):
                possible_piece = board.get_square_contents((one_forward, new_col))
                if (possible_piece is not None) and self.is_enemy(
                    possible_piece
                ):
                    pseudo_legal_moves.append(Move(self.pos, (one_forward, new_col)))
        return pseudo_legal_moves

    def is_promotable(self) -> bool:
        """
        Checks if the Pawn can be promoted, must be called after the pawn has been moved.
        """
        row, col = self.pos
        dark_main_rank = 0
        light_main_rank = 7
        if (self.color == WHITE and row == dark_main_rank) or (
            self.color == BLACK and row == light_main_rank
            ):
                return True
        return False


class Knight(Piece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = KNIGHT

    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        row, col = self.pos
        pseudo_legal_moves = []
        for dr, dc in KNIGHT_OFFSET:
            new_row, new_col = row + dr, col + dc
            if board.in_bounds(
                (new_row, new_col)
            ):  # check move is actually on the board
                possible_piece = board.get_square_contents(
                    (new_row, new_col)
                )  # check if there is a piece to be captured
                if (possible_piece is None) or self.is_enemy(
                    possible_piece
                ):
                    pseudo_legal_moves.append(Move(self.pos, (new_row, new_col), MOVE_NORMAL, None))
        return pseudo_legal_moves


class Bishop(SlidingPiece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = BISHOP

    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        """
        Generates the diagonal sliding moves via the get_sliding_moves method.
        """
        return self.get_sliding_moves(board, DIAGONALS)


class Rook(SlidingPiece):
    def __init__(self, color: str, pos: tuple[int, int]):
        super().__init__(color, pos)
        self.kind = ROOK

    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        """
        Generates the cardinal sliding moves via the get_sliding_moves method.
        """
        return self.get_sliding_moves(board, CARDINALS)


class Queen(SlidingPiece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = QUEEN

    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        """
        Generates the Queens movements combining digonal and cardinal sliding moves.
        """
        return self.get_sliding_moves(board, CARDINALS + DIAGONALS)


class King(Piece):
    def __init__(self, color: str, pos : tuple[int, int], ks_rook : Rook, qs_rook : Rook):
        super().__init__(color, pos)
        self.in_check = False
        self.kind = KING
        self.ks_rook = ks_rook
        self.qs_rook = qs_rook

    def set_in_check(self, value):
        assert type(value) is bool
        self.in_check = value

    def get_check_status(self):
        return self.in_check

    def generate_pseudo_legal_moves(self, board: GameBoard) -> list[Move]:
        row, col = self.pos
        pseudo_legal_moves = []
        # Directional Moves
        directions = CARDINALS + DIAGONALS
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            if board.in_bounds((new_row, new_col)):
                # now validate
                possible_piece = board.get_square_contents((new_row, new_col))
                if (possible_piece is None) or self.is_enemy(
                    possible_piece
                ):
                    pseudo_legal_moves.append(Move(self.pos, (new_row, new_col), MOVE_NORMAL, None))

        # castling moves

        if not self.in_check and not self.has_moved:
            if self.ks_rook.is_active and not self.ks_rook.has_moved:
                if board.squares_between_empty(self, self.ks_rook):
                    if board.path_safe(self, self.ks_rook):
                        # king side rooks from and to squares
                        castle_from_square = self.ks_rook.pos
                        castle_to_square = CASTLE_POSITION[self.color][KING_SIDE][ROOK]
                        payload = [castle_from_square, castle_to_square]
                        king_to_square = CASTLE_POSITION[self.color][KING_SIDE][KING]
                        pseudo_legal_moves.append(Move(self.pos, king_to_square, MOVE_CASTLE, payload))

            if self.qs_rook.is_active and not self.qs_rook.has_moved:
                if board.squares_between_empty(self, self.qs_rook):
                    if board.path_safe(self, self.qs_rook):
                        castle_from_square = self.qs_rook.pos
                        castle_to_square = CASTLE_POSITION[self.color][QUEEN_SIDE][ROOK]
                        payload = [castle_from_square, castle_to_square]
                        king_to_square = CASTLE_POSITION[self.color][QUEEN_SIDE][KING]
                        pseudo_legal_moves.append(Move(self.pos, king_to_square, MOVE_CASTLE, payload))
        return pseudo_legal_moves
