from __future__ import annotations
from .constants import (
    WHITE,
    BLACK,
    DIAGONALS,
    CARDINALS,
    KNIGHT_OFFSET,
    PAWN, KNIGHT, ROOK, KING, BISHOP, QUEEN
)
from abc import ABC, abstractmethod


class Piece(ABC):
    def __init__(self, color: str, pos : tuple[int, int], has_moved = False):
        """
        Base class used to represent a chess piece.
        """
        self.color = color
        self.has_moved = has_moved
        self.pos = pos
        self.kind = ""

    @abstractmethod
    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        pass

    def update_after_move(self, to_square):
        """
        updates the pieces move related attributes
        """
        if not self.has_moved:
            self.has_moved = True
        self.pos = to_square

    def is_pseudo_legal_move(
        self,
        source_square: tuple[int, int],
        dest_square: tuple[int, int],
        board,
    ) -> bool:
        return dest_square in self.generate_pseudo_legal_moves(source_square, board)

    def is_ally(self, other: Piece) -> bool:
        return self.color == other.color

    def is_enemy(self, other: Piece) -> bool:
        return not self.is_ally(other)

    def is_promotable(self, source_square) -> bool:
        """
        Returns whether a piece can be promoted
        """
        return False


class SlidingPiece(Piece):
    """
    Represents pieces that "slide" i.e., Queens, Rooks, and Bishops.
    Exists primarily so that the method get_sliding_moves is not accessible by other piece
    subclasses.
    """

    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)

    @abstractmethod
    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        pass

    def get_sliding_moves(
        self,
        source_square: tuple[int, int],
        board,
        directions: list[tuple[int, int]],
    ) -> list[tuple[int, int]]:
        """
        Generates pseudo-legal moves for sliding pieces (rook, bishop, queen) by extending in each direction until blocked.
        Includes the first enemy square, stops at allies.
        """
        row, col = source_square
        pseudo_legal_moves = []
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            while board.in_bounds((new_row, new_col)):
                possible_piece = board.get_square_contents((new_row, new_col))
                if (
                    possible_piece is None
                ):  # no piece id found, i.e., empty square then add the move
                    pseudo_legal_moves.append((new_row, new_col))
                elif self.is_enemy(possible_piece):
                    pseudo_legal_moves.append(
                        (new_row, new_col)
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

    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        """
        Generates a list of pseudo-legal pawn moves
        Includes :
            Single and double jumps assuming the path is empty and a piece has not moved for the latter
            Diagonal captures assuming there is an enemy piece
        """
        row, col = source_square
        pseudo_legal_moves = []
        dv = -1 if self.color == WHITE else 1  # vertical direction
        one_forward = row + dv
        two_forward = row + (dv * 2)

        # single jump moves
        if board.in_bounds((one_forward, col)) and board.is_empty((one_forward, col)):
            pseudo_legal_moves.append((one_forward, col))

            # double jump moves (check only if there is a pseudo-legal single move)
            if (
                not self.has_moved
                and board.is_empty((two_forward, col))
                and board.in_bounds((two_forward, col))
            ):
                pseudo_legal_moves.append((two_forward, col))

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
                    pseudo_legal_moves.append((one_forward, new_col))
        return pseudo_legal_moves

    def is_promotable(self, source_square) -> bool:
        """
        Checks if the Pawn can be promoted, must be called after the pawn has been moved.
        """
        row, col = source_square
        dark_main_rank = 0
        light_main_rank = 7
        if type(self) is Pawn:
            if (self.color == WHITE and row == dark_main_rank) or (
                self.color == BLACK and row == light_main_rank
            ):
                return True
        return False


class Knight(Piece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = KNIGHT

    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        """
        Generates a list of pseudo-legal knight moves

        Each move is a row column tuple representing a square that a knight can move to, assuming that the square is
        empty or occupied by an enemy piece.

        Args : board : a Board Object

        Returns : list[tuple[int, int]]: pseudo-legal moves for a knight
        """
        row, col = source_square
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
                    pseudo_legal_moves.append((new_row, new_col))
        return pseudo_legal_moves


class Bishop(SlidingPiece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = BISHOP

    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        """
        Generates the diagonal sliding moves via the get_sliding_moves method.
        """
        return self.get_sliding_moves(source_square, board, DIAGONALS)


class Rook(SlidingPiece):
    def __init__(self, color: str, pos: tuple[int, int]):
        super().__init__(color, pos)
        self.kind = ROOK

    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        """
        Generates the cardinal sliding moves via the get_sliding_moves method.
        """
        return self.get_sliding_moves(source_square, board, CARDINALS)


class Queen(SlidingPiece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.kind = QUEEN

    def generate_pseudo_legal_moves(
        self, source_square, board
    ) -> list[tuple[int, int]]:
        """
        Generates the Queens movements combining digonal and cardinal sliding moves.
        """
        return self.get_sliding_moves(source_square, board, CARDINALS + DIAGONALS)


class King(Piece):
    def __init__(self, color: str, pos : tuple[int, int]):
        super().__init__(color, pos)
        self.in_check = False
        self.long_rook = None
        self.near_rook = None
        self.kind = KING

    def set_in_check(self, value):
        assert type(value) is bool
        self.in_check = value

    def get_check_status(self):
        return self.in_check

    def generate_pseudo_legal_moves(
        self, source_square: tuple[int, int], board
    ) -> list[tuple[int, int]]:
        """
        Generates the pseudo-legal moves for the King piece

        Each move is a (row, col) tuple assuming the move is empty or is occupied by an enemy piece.

        Args : board is a Board object

        Returns: list[tuple[int, int]]: A list of moves.

        """
        row, col = source_square
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
                    pseudo_legal_moves.append((new_row, new_col))

        # Castling Move
        # To castle we need to make some checks
        # King hasn't moved
        """
        long_rook_col = 0
        long_rook : Rook
        near_rook : Rook
        near_rook_col = 7
        if (not self.has_moved) and (not self.in_check):
            # now we'll handle the long rook that is 4 blocks away
            long_rook = board.get_square_contents(self.row, long_rook_col)
            if long_rook and not long_rook.has_moved:
                long_rook_diff = 3
                squares_empty = True
                for i in range(1, long_rook_diff + 1):
                    if board.get_square_contents(self.row, long_rook_col + i) != None:
                        squares_empty = False
                        break
                if squares_empty:
                    pseudo_legal_moves.append((self.row, long_rook.col))






                squares_empty = board.get_square_contents(self.row, long_rook_col + 1) == None




            long_rook = board.get_square_contents(self.row, )
        """

        return pseudo_legal_moves
