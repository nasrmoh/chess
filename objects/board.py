from __future__ import annotations
from copy import copy
from .constants import (
    SQUARE_COUNT,
    PAWN,
    ROOK,
    BISHOP,
    KNIGHT,
    QUEEN,
)
from .piece import Piece, Pawn, Knight, Bishop, Rook, Queen, King
from .team import Team


class GameBoard:
    def __init__(
        self,
        square_count: int,
    ):
        self.square_count = square_count
        self.grid = self._create_board_grid()

    @classmethod
    def ghost_for_simulation(cls, square_count, grid):
        ghostboard = cls.__new__(cls)
        ghostboard.square_count = square_count
        ghostboard.grid = grid
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
        row, col = piece.pos
        if not self.in_bounds((row, col)):
            raise IndexError(f"Board position out of bounds: ({row}, {col})")
        if self.grid[row][col] is None:
            self.grid[row][col] = piece
        else:
            raise ValueError(f"Square is occupied at ({row}, {col})")

    def is_empty(self, square: tuple[int, int]) -> bool:
        row, col = square
        if not self.in_bounds(square):
            raise IndexError(f"Position out of bounds: ({row}, {col})")
        return self.get_square_contents(square) is None

    def get_square_contents(self, square: tuple[int, int]) -> Piece | None:
        """
        returns the contents of a square, either a piece, or None indicating the square is empty
        """
        row, col = square
        if not (0 <= row < SQUARE_COUNT and 0 <= col < SQUARE_COUNT):
            raise ValueError("Invalid row or column")
        return self.grid[row][col]

    def generate_pseudo_legal_moves(self, piece: Piece, from_square: tuple[int, int]):
        if piece is not None:
            pseudo_legal_moves = piece.generate_pseudo_legal_moves(from_square, self)
            return pseudo_legal_moves
        else:
            return None

    def generate_legal_moves(
        self,
        piece: Piece | None,
        from_square: tuple[int, int],
        team: Team,
        enemy: Team,
    ) -> list[tuple[int, int]]:
        """
        Returns the legal moves for a given piece.
        """
        is_king = type(piece) is King
        legal_moves = []
        # first generate valid moves.
        pseudo_legal_moves = piece.generate_pseudo_legal_moves(from_square, self)
        # now filter for legal moves
        for move in pseudo_legal_moves:
            ghost_piece = copy(piece)
            ghost_board = GameBoard.ghost_for_simulation(
                self.square_count, self.clone_grid()
            )
            # apply the move
            ghost_board.move_piece(ghost_piece, from_square, move)
            if not ghost_board.get_checking_pieces(
                team, enemy, move, is_king
            ):  # king isn't in check
                legal_moves.append(move)
        # This is done by simulating the move and checking if the king is in check
        return legal_moves

    def build_move_dict(
        self, team: Team, enemy: Team
    ) -> dict[Piece, list[tuple[int, int]]]:
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
                    move_dict[piece] = self.generate_legal_moves(
                        piece, (row, col), team, enemy
                    )
        return move_dict

    def in_bounds(self, square: tuple[int, int]) -> bool:
        row, col = square
        return (0 <= row < SQUARE_COUNT) and (0 <= col < SQUARE_COUNT)

    def move_piece(
        self,
        piece: Piece,
        from_square: tuple[int, int],
        to_square: tuple[int, int],
    ) -> Piece | None:
        """
        applies a legal move onto the board, note this method assumes that the move is legal
        Returns:
            (Piece | None): Returns a captured piece if any, else returns None
        """

        # Move piece by updating piece parameters

        old_row, old_col = from_square
        self.grid[old_row][old_col] = None
        dest_row, dest_col = to_square
        captured_piece = self.get_square_contents(to_square)
        piece.update_after_move(to_square)
        self.grid[dest_row][dest_col] = piece
        return captured_piece

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
        row, col, color = piece.row, piece.col, piece.color
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
        new_piece = piece_class(color, row, col, dest_kind)
        self.grid[new_piece.row][new_piece.col] = new_piece
        team.active_pieces.remove(piece)
        team.active_pieces.append(new_piece)
        return new_piece


    def get_checking_pieces(
        self, current_player: Team, enemy_team: Team, move=None, is_king=False
    ):
        checking_pieces = {}
        if is_king:
            kings_grid_pos = move
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
                        possible_enemy, (row, col)
                    )
                    if kings_grid_pos in enemy_pieces_moves:
                        checking_pieces[possible_enemy] = (row, col)
        return checking_pieces

    def clone_grid(self):
        grid = []
        for row in range(self.square_count):
            grid_row = []
            for col in range(self.square_count):
                grid_row.append(self.grid[row][col])
            grid.append(grid_row)
        return grid
