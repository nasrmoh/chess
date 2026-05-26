from __future__ import annotations
from copy import copy
from .constants import (
    SQUARE_COUNT,
    PAWN,
    ROOK,
    BISHOP,
    KNIGHT,
    QUEEN,
    MOVE_NORMAL,
    MOVE_CAPTURE,
    MOVE_ENPASSANT,
    MOVE_CASTLE,
)
from .piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from .team import Team
from .move import Move


class GameBoard:
    def __init__(
        self,
        square_count: int,
    ):
        self.square_count = square_count
        self.grid = self._create_board_grid()
        self.attacked_squares = []
        self.double_jumped_pawn = None

    @classmethod
    def ghost_for_simulation(cls, square_count, grid, double_jumped_pawn):
        ghostboard = cls.__new__(cls)
        ghostboard.square_count = square_count
        ghostboard.grid = grid
        ghostboard.double_jumped_pawn = double_jumped_pawn
        return ghostboard

    def _create_board_grid(self) -> list[list[Piece | None]]:
        """
        Initializes the grid of the board as a 2D list.
        """
        grid = []
        for row_index in range(self.square_count):
            row = []
            for col_index in range(self.square_count):
                row.append(None)
            grid.append(row)
        return grid

    def place_piece(self, piece: Piece):
        """
        Used for setting up pieces on the board, not to be used to move a piece
        """
        if not self.in_bounds(piece.pos):
            raise IndexError(
                f"Board position out of bounds: ({piece.pos[0]}, {piece.pos[1]})"
            )
        if self.get_square_contents(piece.pos) is None:
            self.set_square_contents(piece.pos, piece)
        else:
            raise ValueError(f"Square is occupied at ({piece.pos[0]}, {piece.pos[1]})")

    def is_empty(self, square: tuple[int, int]) -> bool:
        if not self.in_bounds(square):
            raise IndexError(f"Position out of bounds: ({square[0]}, {square[1]})")
        return self.get_square_contents(square) is None

    def get_square_contents(self, square: tuple[int, int]) -> Piece | None:
        """
        returns the contents of a square, either a piece or None indicating the square is empty
        """
        row, col = square
        if not (0 <= row < SQUARE_COUNT and 0 <= col < SQUARE_COUNT):
            raise ValueError("Invalid row or column")
        return self.grid[row][col]

    def set_square_contents(self, square: tuple[int, int], contents: Piece | None):
        row, col = square
        if not (0 <= row < SQUARE_COUNT and 0 <= col < SQUARE_COUNT):
            raise ValueError("Invalid row or column")
        self.grid[row][col] = contents

    def generate_pseudo_legal_moves(self, piece: Piece):
        if piece is not None:
            pseudo_legal_moves = piece.generate_pseudo_legal_moves(self)
            return pseudo_legal_moves
        else:
            return None

    def generate_legal_moves(
        self,
        piece: Piece | None,
        team: Team,
        enemy: Team,
    ) -> list[Move]:
        """
        Returns the legal moves for a given piece.
        """
        is_king = type(piece) is King
        legal_moves = []
        # first generate valid moves.
        pseudo_legal_moves = piece.generate_pseudo_legal_moves(self)
        # now filter for legal moves
        for move in pseudo_legal_moves:
            ghost_piece = copy(piece)
            ghost_board = GameBoard.ghost_for_simulation(
                self.square_count, self.clone_grid(), copy(self.double_jumped_pawn)
            )
            # apply the move
            ghost_board.apply_move(ghost_piece, move)
            attacked_squares, checking_pieces = ghost_board.get_board_threats(
                team, enemy, move, is_king
            )
            if not checking_pieces:  # king isn't in check
                if move.kind == MOVE_NORMAL and self.get_square_contents(
                    move.to_square
                ):
                    move.set_kind(MOVE_CAPTURE)
                    move.set_payload(move.to_square)
                legal_moves.append(move)
        # This is done by simulating the move and checking if the king is in check
        return legal_moves

    def build_move_dict(self, team: Team, enemy: Team) -> dict[Piece, Move]:
        move_dict = {}
        found_count = 0
        ally_count = team.get_count_active()
        for row in range(SQUARE_COUNT):
            for col in range(SQUARE_COUNT):
                if found_count == ally_count:
                    break
                piece = self.get_square_contents((row, col))
                if (piece is not None) and (piece.color == team.color):
                    found_count += 1
                    move_dict[piece] = self.generate_legal_moves(piece, team, enemy)
        return move_dict

    def in_bounds(self, square: tuple[int, int]) -> bool:
        row, col = square
        return (0 <= row < SQUARE_COUNT) and (0 <= col < SQUARE_COUNT)

    def apply_move(
        self,
        piece: Piece,
        move: Move,
    ) -> Piece | None:
        """
        applies a legal move onto the board, note this method assumes that the move is legal
        Returns:
            Piece | None: Returns the auxiliary if the move kind is a capture, enpassant, or castling, otherwise None
        """

        payload_piece = None  # assume normal with no payload
        # handle special cases first
        if move.kind in [MOVE_CAPTURE, MOVE_ENPASSANT]:
            payload_piece = self.get_square_contents(move.payload)
            # remove the captured piece from the board
            self.set_square_contents(move.payload, None)

        elif move.kind == MOVE_CASTLE:
            rook_from_square, rook_to_square = move.payload
            payload_piece = self.get_square_contents(rook_from_square)
            # we know that the square is empty, apply the move
            self.set_square_contents(rook_from_square, None)
            self.set_square_contents(rook_to_square, payload_piece)
            # since the rook moved, we need to update the rook
            payload_piece.update_after_move(rook_to_square)

        self.set_square_contents(piece.pos, None)
        piece.update_after_move(move.to_square)
        if (
            isinstance(piece, Pawn)
            and abs(move.to_square[0] - move.from_square[0]) == 2
        ):
            self.double_jumped_pawn = piece
        else:
            self.double_jumped_pawn = None
        self.set_square_contents(move.to_square, piece)
        return payload_piece

    def upgrade_piece(self, team: Team, piece: Piece, dest_kind: str) -> Piece:
        """
        Upgrades a pawn piece into a new type (rook, bishop, knight, or queen).

        Args:
            team (Team): The team the pawn belongs to.
            Piece (Piece): The pawn piece to be upgraded
            dest_type (str): The type the piece will be upgraded to

        Returns:
            Piece: The upgraded piece

        Raises:
            TypeError: If the piece is not a pawn, or if the piece does not belong to the given player / team
            ValueError: If the dest_type is invalid
        """
        color = piece.color
        upgrade_selection = {
            ROOK: Rook,
            BISHOP: Bishop,
            KNIGHT: Knight,
            QUEEN: Queen,
        }
        if piece.kind != PAWN:
            raise TypeError(f"piece : {piece.kind} cannot be promoted")
        if not team.owns(piece):
            raise TypeError(f"piece : {piece.kind} does not belong to team")
        if dest_kind not in upgrade_selection:
            raise ValueError(f"Invalid upgrade type : {dest_kind}")
        piece_class = upgrade_selection[dest_kind]
        new_piece = piece_class(color, piece.pos)
        new_row, new_col = new_piece.pos
        self.grid[new_row][new_col] = new_piece
        team.replace_piece(piece, new_piece)
        return new_piece

    def get_board_threats(
        self, current_player: Team, enemy_team: Team, move=None, is_king=False
    ):
        attacked_pieces = {}
        checking_pieces = {}
        self.attacked_squares = []
        if is_king:
            kings_grid_pos = move.to_square
        else:
            king = current_player.get_king()
            kings_grid_pos = king.pos

        enemy_count = enemy_team.get_count_active()
        found_count = 0
        for row in range(SQUARE_COUNT):
            for col in range(SQUARE_COUNT):
                if found_count == enemy_count:  # found all enemies stop
                    break
                possible_enemy = self.grid[row][col]
                if (possible_enemy is not None) and (
                    possible_enemy.color == enemy_team.color
                ):
                    found_count += 1
                    if (row, col) == move:  # king captures
                        continue
                    enemy_pieces_moves = self.generate_pseudo_legal_moves(
                        possible_enemy
                    )
                    enemy_attacked_squares = [
                        move.to_square for move in enemy_pieces_moves
                    ]
                    self.attacked_squares += enemy_attacked_squares
                    attacked_pieces[possible_enemy] = enemy_pieces_moves
                    if kings_grid_pos in enemy_attacked_squares:
                        checking_pieces[possible_enemy] = enemy_pieces_moves
        return attacked_pieces, checking_pieces

    def clone_grid(self):
        grid = []
        for row in range(self.square_count):
            grid_row = []
            for col in range(self.square_count):
                grid_row.append(self.grid[row][col])
            grid.append(grid_row)
        return grid

    def squares_between_empty(self, piece_one, piece_two):
        # checks specifically columns between.
        row_one, col_one = piece_one.pos
        row_two, col_two = piece_two.pos
        if col_one < col_two:
            col_lower = col_one
            col_upper = col_two
        else:
            col_lower = col_two
            col_upper = col_one
        for col in range(col_lower + 1, col_upper):
            if self.get_square_contents((row_one, col)):
                return False
        return True

    def path_safe(self, piece_one, piece_two):
        row_one, col_one = piece_one.pos
        row_two, col_two = piece_two.pos
        if col_one < col_two:
            col_lower = col_one
            col_upper = col_two
        else:
            col_lower = col_two
            col_upper = col_one
        for col in range(col_lower + 1, col_upper):
            if not self.square_safe((row_one, col)):
                return False
        return True

    def square_safe(self, square):
        return square not in self.attacked_squares

    def dest_square_to_move(
        self, to_square: tuple[int, int], moves: list[Move]
    ) -> Move:
        for move in moves:
            if move.to_square == to_square:
                return move
        raise ValueError
