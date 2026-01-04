import pygame
from .constants import (
    WHITE,
    BLACK,
    SQUARESIZE,
    DIAGONALS,
    CARDINALS,
    KNIGHT_OFFSET,
)


class Piece:
    def __init__(self, color: pygame.Color, kind: str):
        """
        Base class used to represent a chess piece.
        """
        self.size = SQUARESIZE
        self.kind = kind
        self.color = color
        self.has_moved = False

    def generate_valid_moves(self, from_square : tuple[int, int], board):
        # exists purely to be over written by subclasses
        raise NotImplementedError

    def update_after_move(self):
        """
        On successful movement, updates the self.has_moved attribute to prevent "double-jumps".
        """
        if not self.has_moved:
            self.has_moved = True

    def is_valid_move(self, to_square : tuple[int, int], board):
        """
        Checks if a move is valid, return True. Otherwise False
        """
        return to_square in self.generate_valid_moves(board)

    def is_ally(self, other) -> bool:
        """
        Checks if the other piece is of the same team. i.e. is an ally

        Returns:
            Bool
        """
        assert isinstance(other, Piece)
        return self.color == other.color

    def is_enemy(self, other) -> bool:
        """
        Checks if the other piece is of a different team. i.e. is an enemy
        Returns:
            Bool
        """
        assert isinstance(other, Piece)
        return self.color != other.color

    def is_promotable(self) -> bool:
        """
        Checks if the Piece can be promoted, if it is a pawn this method will be overwritten, otherwise returns False.
        """
        return False

    def set_id(self, id : int):
        self.id = id

    def get_kind(self):
        return self.kind


class SlidingPiece(Piece):
    """
    Represents pieces that "slide" i.e. Queens, Rooks, and Bishops.
    Exists primarily so that the method get_sliding_moves is not accessible by other piece
    sub-classes.
    """

    def __init__(self, color: pygame.Color, kind: str):
        super().__init__(color, kind)

    def get_sliding_moves(
        self, from_square : tuple[int, int], board, directions: list[tuple[int, int]]
    ) -> list[tuple[int, int]]:
        """
        Generates valid sliding moves for the following pieces Bishop, Rook, Queen.

        Slides in the direction specified by directions argument until either blocked by an ally or blocked by an enemy, if blocked
        by an enemy adds that final square as a valid move

        Args:
            board is a Board Object directions
            list[tuple[int, int]: directions relative to the original position of the piece.

        Returns:
            list[tuple[int, int]] : A list of valid (row, col) moves.
        """
        row, col = from_square
        valid_moves = []
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            while board.in_bounds(new_row, new_col):
                piece = board.get_square_contents(new_row, new_col)
                if not piece:  # no piece, add move
                    valid_moves.append((new_row, new_col))
                elif self.is_enemy(piece):
                    valid_moves.append(
                        (new_row, new_col)
                    )  # enemy, add, then stop sliding
                    break
                else:
                    # ally, stop sliding
                    break
                new_row += dr
                new_col += dc
        return valid_moves


class Pawn(Piece):
    def __init__(self, color: pygame.Color, kind: str):
        super().__init__(color, kind)
        self.has_moved = False

    def generate_valid_moves(self, from_square : tuple[int, int], board) -> list[tuple[int, int]]:
        """
        Generates a list of valid pawn moves

        Includes :
            Single and double jumps assuming the path is empty and piece has not moved for the latter
            Diagonal captures assuming there is an enemy piece

        Args : board a Board Object

        Returns : list[tuple[int, int]]:  Valid moves for a pawn
        """
        row, col = from_square
        valid_moves = []
        dv = -1 if self.color == WHITE else 1  # vertical direction
        one_forward = row + dv
        two_forward = row + (dv * 2)

        # single jump moves
        if board.is_empty(one_forward, col) and board.in_bounds(
            one_forward, col
        ):
            valid_moves.append((one_forward, col))

            # double jump moves (check only if there is a valid single move)
            if (
                not self.has_moved
                and board.is_empty(two_forward, col)
                and board.in_bounds(two_forward,col)
            ):
                valid_moves.append((two_forward, col))

        # Diagonals
        for dh in [-1, 1]:
            new_col = self.col + dh
            if board.in_bounds(one_forward, new_col) and not board.is_empty(
                one_forward, new_col
            ):
                piece = board.get_square_contents(one_forward, new_col)
                if piece and self.is_enemy(piece):
                    valid_moves.append((one_forward, new_col))
        return valid_moves

    

    def is_promotable(self, from_square) -> bool:
        """
        Checks if the Pawn can be promoted, must be called after the pawn has been moved.
        """
        row, col = from_square
        dark_main_rank = 0
        light_main_rank = 7
        if self.kind == "pawn":
            if (self.color == WHITE and row == dark_main_rank) or (
                self.color == BLACK and row == light_main_rank
            ):
                return True
        return False


class Knight(Piece):
    def __init__(self, color: pygame.Color, kind: str):
        super().__init__(color,  kind)

    def generate_valid_moves(self, from_square : tuple[int, int],  board) -> list[tuple[int, int]]:
        """
        Generates a list of valid knight moves

        Each move is a row column tuple representing a square that a knight can move to, assuming that the square is
        empty or occupied by an enemy piece.

        Args : board : a Board Object

        Returns : list[tuple[int, int]]:  Valid moves for a knight
        """
        row, col = from_square
        valid_moves = []
        for dr, dc in KNIGHT_OFFSET:
            new_row, new_col = row + dr, col + dc
            if board.in_bounds(new_row, new_col):  # check move is actually on the board
                piece = board.get_square_contents(
                    new_row, new_col
                )  # check if there is a piece to be captured
                if not piece or self.is_enemy(piece):
                    valid_moves.append((new_row, new_col))
        return valid_moves


class Bishop(SlidingPiece):
    def __init__(self, color: pygame.Color, kind: str):
        super().__init__(color, kind)

    def generate_valid_moves(self, board) -> list[tuple[int, int]]:
        """
        Generates the diagonal sliding moves via the get_sliding_moves method.
        """
        return self.get_sliding_moves(board, DIAGONALS)


class Rook(SlidingPiece):
    def __init__(self, color: pygame.Color, kind: str):
        super().__init__(color, kind)

    def generate_valid_moves(self, from_square : tuple[int, int], board) -> list[tuple[int, int]]:
        """
        Generates the cardinal sliding moves via the get_sliding_moves method.
        """
        return self.get_sliding_moves(board, from_square,  CARDINALS)


class Queen(SlidingPiece):
    def __init__(self, color: pygame.Color,  kind: str):
        super().__init__(color, kind)

    def generate_valid_moves(self, from_square, board) -> list[tuple[int, int]]:
        """
        Generates the Queens movements combinging digonal and cardinal sliding moves.
        """
        return self.get_sliding_moves(board, from_square, CARDINALS + DIAGONALS)


class King(Piece):

    def __init__(self, color: pygame.Color, kind: str):
        super().__init__(color, kind)
        self.in_check = False
        self.long_rook = None
        self.near_rook = None

    def set_in_check(self, value):
        assert type(value) is bool
        self.in_check = value

    def get_check_status(self):
        return self.in_check

    def generate_valid_moves(self, from_square : tuple[int, int], board):
        """
        Generates the valid moves for the King piece

        Each move is a (row, col) tuple assuming the move is empty or is occupied by an enemy piece.

        Args : board is a Board object

        Returns :list[tuple[int, int]] : A list of moves.

        """
        row, col = from_square
        valid_moves = []
        # Directional Moves
        directions = CARDINALS + DIAGONALS
        for dr, dc in directions:
            new_row = row + dr
            new_col = col + dc
            if board.in_bounds(new_row, new_col):
                # now validate
                piece = board.get_square_contents(new_row, new_col)
                if not piece or self.is_enemy(piece):
                    valid_moves.append((new_row, new_col))

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
                    valid_moves.append((self.row, long_rook.col))






                squares_empty = board.get_square_contents(self.row, long_rook_col + 1) == None




            long_rook = board.get_square_contents(self.row, )
        """

        return valid_moves
