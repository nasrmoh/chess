from .constants import (
    SQUARE_COUNT,
    GAMESTART,
    START_TURN,
    SELECT_PIECE,
    SELECT_MOVE,
    SELECT_PROMOTION,
    END_TURN,
    GAME_END,
    ACTION_QUIT,
    ACTION_MOUSE_PRESSED,
    ACTION_SELECTED_SQUARE,
    ACTION_PROMOTION_OPTION,
    COMMAND_HIGHLIGHT_SQUARES,
    COMMAND_CLEAR_HIGHLIGHTS,
    COMMAND_BUILD_PROMO,
    COMMAND_TEARDOWN_PROMO,
    COMMAND_INITIALIZE_GAME_UI,
    COMMAND_MOVE_PIECE,
    COMMAND_PROMOTE_PAWN,
    PAYLOAD_COLOR,
    PAYLOAD_SQUARES,
    PAYLOAD_UPGRADE_TYPE,
    GREEN,
    RED,
    GOLD,
    BLUE,
    BLACK,
    WHITE,
    BLACK_PLAYER,
    WHITE_PLAYER,
    INITIAL_POSITION,
    ROOK,
    KNIGHT,
    BISHOP,
    QUEEN,
    KING,
    PAWN, PAYLOAD_FROM_SQUARE, PAYLOAD_TO_SQUARE, PAYLOAD_TEAM_COLOR,
)
from .board import GameBoard
from .piece import Piece, Rook, Knight, Bishop, Queen, King, Pawn
from .team import Team
from .Move import Move, CapturedData
import pygame
import sys


class GameState:
    def __init__(self):
        self.selected_square: tuple[int, int] | None = None
        # Selected square for highlighting and moving of pieces
        self.selected_piece : Piece | None = None
        self.captured_piece: Piece | None = None  # captured pieces during current players turn
        self.castled_rook: Rook | None = None
        self.current_move: Move | None = None # current move being built in a given turn
        self.move_delta : list[Move] = [] # the actual move delta / historical record
        self.promotion_type: str | None = None
        self.moved_piece : Piece | None = None
        self.from_square : tuple[int, int] | None = None
        self.to_square : tuple[int, int] | None = None
        self.move_dict: dict[Piece, list[tuple[int, int]]] | None = None
        # a move dictionary for the legal moves a player can make
        self.attacked_pieces: dict[Piece, tuple[int, int]] | None = None  # all moves the enemy can make.
        self.checking_pieces: dict[Piece, tuple[int, int]] | None = None  # pieces of the other player that are checking the current player
        self.state: int = GAMESTART  # state variable
        self.board = GameBoard(SQUARE_COUNT)
        self.dark_team = Team(BLACK)  # Game Data
        self.light_team = Team(WHITE)  # Game Data
        self.setup_pieces()
        self.current_player: Team = self.light_team
        self.other_player: Team = self.dark_team
        self.game_is_running = True

    def get_init_commands(self):
        commands = []
        pieces_by_square = {}
        for piece in (self.dark_team.active_pieces + self.light_team.active_pieces):
            square = piece.pos
            pieces_by_square[square] = (piece.kind, piece.color)
        command = {COMMAND_INITIALIZE_GAME_UI : pieces_by_square}
        commands.append(command)
        return commands

    def setup_dark_pieces(self):
        pieces = []
        qs_rook = Rook(self.dark_team.color, INITIAL_POSITION[BLACK][ROOK][0])
        ks_rook = Rook(self.dark_team.color, INITIAL_POSITION[BLACK][ROOK][1])
        pieces.append(qs_rook)
        pieces.append(ks_rook)
        pieces.append(Knight(self.dark_team.color, INITIAL_POSITION[BLACK][KNIGHT][0]))
        pieces.append(Bishop(self.dark_team.color, INITIAL_POSITION[BLACK][BISHOP][0]))
        pieces.append(Queen(self.dark_team.color, INITIAL_POSITION[BLACK][QUEEN][0]))
        pieces.append(Bishop(self.dark_team.color, INITIAL_POSITION[BLACK][BISHOP][1]))
        pieces.append(Knight(self.dark_team.color, INITIAL_POSITION[BLACK][KNIGHT][1]))
        king = King(self.dark_team.color, INITIAL_POSITION[BLACK][KING][0], ks_rook, qs_rook)
        self.dark_team.king = king
        pieces.append(king)
        for square in INITIAL_POSITION[BLACK][PAWN]:
            pieces.append(Pawn(self.dark_team.color, square))
        self.dark_team.active_pieces += pieces
        for piece in pieces:
            self.board.place_piece(piece)

    def setup_light_pieces(self):
        pieces = []
        qs_rook = Rook(self.light_team.color, INITIAL_POSITION[WHITE][ROOK][0])
        ks_rook = Rook(self.light_team.color, INITIAL_POSITION[WHITE][ROOK][1])
        pieces.append(qs_rook)
        pieces.append(ks_rook)
        pieces.append(Knight(self.light_team.color, INITIAL_POSITION[WHITE][KNIGHT][0]))
        pieces.append(Bishop(self.light_team.color, INITIAL_POSITION[WHITE][BISHOP][0]))
        pieces.append(Queen(self.light_team.color, INITIAL_POSITION[WHITE][QUEEN][0]))
        king = King(self.light_team.color, INITIAL_POSITION[WHITE][KING][0], ks_rook, qs_rook)
        self.light_team.king = king
        pieces.append(king)
        pieces.append(Bishop(self.light_team.color, INITIAL_POSITION[WHITE][BISHOP][1]))
        pieces.append(Knight(self.light_team.color, INITIAL_POSITION[WHITE][KNIGHT][1]))
        for square in INITIAL_POSITION[WHITE][PAWN]:
            pieces.append(Pawn(self.light_team.color, square))
        self.light_team.active_pieces += pieces
        for piece in pieces:
            self.board.place_piece(piece)

    def setup_pieces(self):
        self.setup_dark_pieces()
        self.setup_light_pieces()

    def update_state(self, actions):
        ## hook-dependent methods, i.e., the on_enter_new_state method.
        ## To handle changes when entering a new state
        if actions[ACTION_QUIT]:
            sys.exit()
            pygame.quit() # for some reason this doesn't want to work anymore.
        commands = []
        if self.state == GAMESTART:
            commands = self.handle_game_start(actions)
        elif self.state == START_TURN:
            commands = self.handle_turn_start(actions)
        elif self.state == SELECT_PIECE:
            commands = self.handle_piece_selection(actions)
        elif self.state == SELECT_MOVE:
            commands = self.handle_move_selection(actions)
        elif self.state == SELECT_PROMOTION:
            commands = self.handle_promotion_selection(actions)
        elif self.state == END_TURN:
            commands = self.handle_end_turn(actions)
        return commands

    def change_state_to(self, new_state: int, actions):
        commands = []
        commands += self.on_exit_state()
        self.state = new_state
        commands += self.on_enter_new_state(self.state, actions)
        return commands

    def on_exit_state(self):
        commands = []
        if self.state == GAMESTART:
            pass
        if self.state == START_TURN:
            pass
        elif self.state == SELECT_PIECE:
            pass
        elif self.state == SELECT_MOVE:
            commands.append({COMMAND_CLEAR_HIGHLIGHTS: None})
            if self.moved_piece:
                payload = {PAYLOAD_FROM_SQUARE: self.from_square, PAYLOAD_TO_SQUARE: self.moved_piece.pos}
                commands.append({COMMAND_MOVE_PIECE : payload})
        elif self.state == SELECT_PROMOTION:
            commands.append({COMMAND_TEARDOWN_PROMO: None})
            piece_color = self.board.get_square_contents(self.selected_piece.pos).color
            payload = {PAYLOAD_UPGRADE_TYPE: self.promotion_type, PAYLOAD_TEAM_COLOR: piece_color, PAYLOAD_FROM_SQUARE : self.selected_square}
            commands.append({COMMAND_PROMOTE_PAWN : payload})
        elif self.state == END_TURN:
            self.selected_square= None   # don't know about this one
            self.selected_piece= None
            self.captured_piece = None  # game state info
            self.promotion_type = None
            self.moved_piece = None
            self.from_square = None
            self.to_square = None
            self.move_dict = None  # game state info
            self.attacked_pieces = None
            self.checking_pieces = None  # game state info
            self.current_move = None
            self.castled_rook = None
            """
            self.other_player.king.set_in_check(
                False
            )  # game state info
            """
        return commands

    def on_enter_new_state(self, state: int, actions):
        """
        A hook method. Whenever we change states, sometimes it is necessary to achieve some task,
        This method does just that and ensures that for each state, the body of the conditional doesn't need to be
        repeated

        Contains the actual "actions" of a given state
        """
        commands = []
        if state == START_TURN:
            self.attacked_pieces, self.checking_pieces = self.board.get_board_threats(
                self.current_player, self.other_player
            )
            if self.checking_pieces:
                self.current_player.set_king_in_check(True)
            else:
                self.current_player.set_king_in_check(False)
            self.move_dict = self.board.build_move_dict(
                self.current_player, self.other_player
            )
        elif state == SELECT_PIECE:
            if self.checking_pieces:
                # add
                command_highlight_attacking = {
                    COMMAND_HIGHLIGHT_SQUARES: {
                        PAYLOAD_COLOR: RED,
                        PAYLOAD_SQUARES: list(self.checking_pieces.values()),
                    }
                }
                square = self.current_player.get_king().pos
                command_highlight_checked_king = {
                    COMMAND_HIGHLIGHT_SQUARES: {
                        PAYLOAD_COLOR: GOLD,
                        PAYLOAD_SQUARES: [square],
                    }
                }

                """self.board.add_highlighted_squares(
                    GOLD,
                    [
                        self.current_player.king.get_grid_pos(),
                    ],
                ) # command"""
                commands.append(command_highlight_attacking)
                commands.append(command_highlight_checked_king)
        elif state == SELECT_MOVE:
            assert self.selected_square is not None
            # command
            self.selected_piece = self.board.get_square_contents(self.selected_square)
            command_highlight_potential_moves = {
                COMMAND_HIGHLIGHT_SQUARES: {
                    PAYLOAD_COLOR: GREEN,
                    PAYLOAD_SQUARES: self.move_dict[self.selected_piece],
                }
            }
            command_highlight_selected_piece_square = {
                COMMAND_HIGHLIGHT_SQUARES: {
                    PAYLOAD_COLOR: BLUE,
                    PAYLOAD_SQUARES: [self.selected_square],
                }
            }
            commands.append(command_highlight_potential_moves)
            commands.append(command_highlight_selected_piece_square)
        elif state == SELECT_PROMOTION:
            assert self.selected_square is not None
            self.selected_square = actions[ACTION_SELECTED_SQUARE]
            self.selected_piece = self.board.get_square_contents(self.selected_square)
            assert self.selected_piece.is_promotable()
            command_build_promotion_menu = {COMMAND_BUILD_PROMO: self.selected_piece.color}
            commands.append(command_build_promotion_menu)
        elif state == END_TURN:
            if self.captured_piece is not None:
                print(
                    f"{str(self.current_player).split()[0]} captures {str(self.other_player).split()[0]}'s {self.captured_piece.kind}"
                )
                self.captured_piece.captured()
                self.other_player.active_pieces.remove(self.captured_piece)
                self.other_player.lost_pieces.append(self.captured_piece)
            self.move_delta.append(self.current_move)
        elif state == GAME_END:
            if self.current_player.king.get_check_status():
                print(f"{self.other_player} Has Won, Game over")
            else:
                print(f"Stalemate, No one has won")
            self.end_game_is_running()
        return commands

    def handle_game_start(self, actions):
        return self.change_state_to(START_TURN, None)

    def handle_turn_start(self, actions):
        if self.move_dict and self.move_dict_is_empty():
           return self.change_state_to(GAME_END, actions)
        else:
            return self.change_state_to(SELECT_PIECE, actions)

    def handle_piece_selection(self, actions):
        """
        Piece selection state
        """
        if actions[ACTION_MOUSE_PRESSED]:  # event
            # validate event
            if self.valid_square_selected(actions[ACTION_SELECTED_SQUARE]):
                valid_square = actions[ACTION_SELECTED_SQUARE]
                if not self.board.is_empty(valid_square):
                    self.selected_piece = self.board.get_square_contents(valid_square)
                    self.set_selected_square(valid_square)
                    if self.selected_piece and self.current_player.owns(self.selected_piece):
                        legal_moves = self.move_dict[self.selected_piece]
                        if legal_moves:
                            return self.change_state_to(SELECT_MOVE, actions)
                        else:
                            return self.reject_selection(
                                actions, "Piece has no valid moves"
                            )
                    else:
                        return self.reject_selection(
                            actions,
                            f"{self.print_current_player()} does not own the selected piece",
                        )
                else:
                    return self.reject_selection(
                        actions,
                        "Board is empty at selected location",
                    )
            else:
                return self.reject_selection(actions, "No Valid Square was selected")
        else:
            return self.continue_in_state()

    def handle_move_selection(self, actions):
        """
        Move selection after a piece has been selected

        Note: Valid moves are generated in the 'on_enter_new_state' method
        """
        # generate associated move data
        if actions[ACTION_MOUSE_PRESSED]:
            self.selected_piece = self.board.get_square_contents(self.selected_square)
            legal_moves = self.move_dict[self.selected_piece]
            if legal_moves:
                if self.valid_square_selected(actions[ACTION_SELECTED_SQUARE]):
                    dest_row, dest_col = actions[ACTION_SELECTED_SQUARE]
                    if self.valid_move_selected((dest_row, dest_col), legal_moves):
                        self.from_square = self.selected_piece.pos
                        self.moved_piece = self.selected_piece
                        self.to_square = (dest_row, dest_col)
                        self.captured_piece = self.board.move_piece(
                            self.selected_piece, (dest_row, dest_col),
                        )
                        self.current_move = self.load_current_move()
                        if self.selected_piece.is_promotable():
                            print("You can promote your piece!")
                            return self.change_state_to(SELECT_PROMOTION, actions)
                        else:
                            return self.change_state_to(END_TURN, actions)
                    else:
                        return self.reject_selection(
                            actions,
                            "Invalid move for selected piece",
                        )
                else:
                    return self.reject_selection(actions, "Invalid Square Selected")
            else:
                return self.reject_selection(actions, "Piece has no valid moves")
        else:
            return self.continue_in_state()

    def handle_promotion_selection(self, actions):
        """
        Promotion of a pawn into a new piece must occur.
        """
        if actions[ACTION_MOUSE_PRESSED]:
            if actions[ACTION_PROMOTION_OPTION] is not None:
                new_type =  actions[ACTION_PROMOTION_OPTION]
                self.board.upgrade_piece(
                    self.current_player, self.selected_piece, new_type
                )
                self.promotion_type = new_type
                self.current_move = self.load_current_move(True)
                return self.change_state_to(END_TURN, actions)
            else:
                print("Invalid promotion option")
                return self.continue_in_state()
        else:
            return self.continue_in_state()

    def handle_end_turn(self, actions):
        """This method has no operation : End of Turn does not handle user events"""
        "End of turns can only be accessed from other states"
        self.update_current_player()
        return self.change_state_to(START_TURN, actions)

    def reject_selection(
        self,
        actions,
        msg: str = None,
    ):
        if msg:
            print(f"{msg}")
        return self.change_state_to(SELECT_PIECE, actions)

    def continue_in_state(self):
        # does nothing, exists to make non-response explicitly do nothing.
        return []

    def remove_highlighted_squares(self):
        self.board.clear_highlighted_squares()

    def update_current_player(self):
        """
        Changes the current player into the other player. I.e., changes the active player from white to black
        """
        if self.current_player.color == WHITE:
            print("It is now Black's turn")
            self.current_player = self.dark_team
            self.other_player = self.light_team
        else:
            print("It is now White's turn")
            self.current_player = self.light_team
            self.other_player = self.dark_team

    ### State methods might move

    def valid_square_selected(self, possible_square: tuple[int, int]) -> bool:
        """
        Method that checks if a possible square corresponds to a board square.

        Args:
            mouse_pos (tuple[int, int]): The current mouse_pos corresponding to the last mouse press down

        """
        return possible_square != (None, None)

    def load_current_move(self, promotion = False):
        captured_data = None
        promotion_kind = None
        # castling_data = None
        if self.captured_piece:
            captured_data = CapturedData(self.captured_piece.kind, self.captured_piece.color, self.captured_piece.pos)
        if promotion:
                promotion_kind = self.promotion_type
        return  Move(self.selected_piece.kind,
                    self.selected_piece.color,
                    self.from_square,
                    self.to_square,
                     captured_data,
                    promotion_kind)

    def valid_move_selected(self, square, valid_moves):
        return square in valid_moves

    def get_mouse_pressed(self):
        return self.mouse_pressed

    def set_mouse_pressed(self, value):
        self.mouse_pressed = value

    def get_mouse_pos(self):
        return self.mouse_pos

    def set_mouse_pos(self, x, y):
        self.mouse_pos = (x, y)

    def get_selected_piece(self):
        return self.selected_piece

    def set_selected_piece(self, option):
        self.selected_piece = option

    def set_selected_square(self, square):
        self.selected_square = square

    def set_captured_piece(self, piece):
        self.captured_piece = piece

    def get_state(self):
        return self.state

    def get_game_is_running(self):
        return self.game_is_running

    def end_game_is_running(self):
        self.game_is_running = False

    def print_current_player(self):
        if self.current_player == self.dark_team:
            return "Black Player"
        else: #self.current_player == self.light_team:
            return "White Player"


    def move_dict_is_empty(self):
        assert self.move_dict is not None
        for value in self.move_dict.values():
            if value:
                return False
        return True
