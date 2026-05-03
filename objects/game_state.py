from .constants import (
    SQUARESIZE,
    SQUARECOUNT,
    GAMESTART,
    STARTTURN,
    SELECTPIECE,
    SELECTMOVE,
    SELECTPROMOTION,
    ENDTURN,
    GAMEEND,
    ACTION_QUIT,
    ACTION_MOUSE_PRESSED,
    ACTION_SELECTED_SQUARE,
    COMMAND_HIGHLIGHT_SQUARES,
    COMMAND_CLEAR_HIGHLIGHTS,
    COMMAND_BUILD_PROMO,
    COMMAND_TEARDOWN_PROMO,
    PAYLOAD_COLOR,
    PAYLOAD_SQUARES,
    GREEN,
    RED,
    GOLD,
    BLUE,
    BLACK,
    WHITE,
    BLACKPLAYER,
    WHITEPLAYER,
    INITIAL_POSITION,
    ROOK,
    KNIGHT,
    BISHOP,
    QUEEN,
    KING,
    PAWN,
)
from .board import GameBoard
from pygame.locals import *
from .piece import Piece, Rook, Knight, Bishop, Queen, King, Pawn
from .team import Team
import pygame
import sys

"""
    chessboard.set_pieces(
        black_player.active_pieces, white_player.active_pieces
    ) # Game Data
"""


class GameState:
    def __init__(self):
        self.selected_square: tuple[int, int] | None = None
        # Selected piece for highlighting and moving of pieces
        self.captured_piece: Piece | None = (
            None  # captured pieces during current players turn
        )
        self.move_dict: dict[Piece, list[tuple[int, int]]] | None = None
        # a move dictionary for the legal moves a player can make
        self.checking_pieces: dict[Piece, tuple[int, int]] = (
            {}
        )  # pieces of the other player that are checking the current player
        self.state: int = GAMESTART  # state variable
        self.board = GameBoard(SQUARECOUNT)
        self.dark_team = Team(BLACKPLAYER, BLACK)  # Game Data
        self.light_team = Team(WHITEPLAYER, WHITE)  # Game Data
        self.setup_pieces()
        self.current_player: Team = self.light_team
        self.other_player: Team = self.dark_team
        self.game_is_running = True

    def setup_dark_pieces(self):
        pieces = []
        pieces.append(Rook(self.dark_team.color, INITIAL_POSITION[BLACK][ROOK][0]))
        pieces.append(Knight(self.dark_team.color, INITIAL_POSITION[BLACK][KNIGHT][0]))
        pieces.append(Bishop(self.dark_team.color, INITIAL_POSITION[BLACK][BISHOP][0]))
        pieces.append(Queen(self.dark_team.color, INITIAL_POSITION[BLACK][QUEEN][0]))
        king = King(self.dark_team.color, INITIAL_POSITION[BLACK][KING][0])
        self.dark_team.king = king
        pieces.append(king)
        pieces.append(Bishop(self.dark_team.color, INITIAL_POSITION[BLACK][BISHOP][1]))
        pieces.append(Knight(self.dark_team.color, INITIAL_POSITION[BLACK][KNIGHT][1]))
        pieces.append(Rook(self.dark_team.color, INITIAL_POSITION[BLACK][ROOK][1]))
        for square in INITIAL_POSITION[BLACK][PAWN]:
            pieces.append(Pawn(self.dark_team.color, square))
        self.dark_team.active_pieces += pieces
        for piece in pieces:
            self.board.place_piece(piece)

    def setup_light_pieces(self):
        pieces = []
        pieces.append(Rook(self.light_team.color, INITIAL_POSITION[WHITE][ROOK][0]))
        pieces.append(Knight(self.light_team.color, INITIAL_POSITION[WHITE][KNIGHT][0]))
        pieces.append(Bishop(self.light_team.color, INITIAL_POSITION[WHITE][BISHOP][0]))
        pieces.append(Queen(self.light_team.color, INITIAL_POSITION[WHITE][QUEEN][0]))
        king = King(self.light_team.color, INITIAL_POSITION[WHITE][KING][0])
        self.light_team.king = king
        pieces.append(king)
        pieces.append(Bishop(self.light_team.color, INITIAL_POSITION[WHITE][BISHOP][1]))
        pieces.append(Knight(self.light_team.color, INITIAL_POSITION[WHITE][KNIGHT][1]))
        pieces.append(Rook(self.light_team.color, INITIAL_POSITION[WHITE][ROOK][1]))
        for square in INITIAL_POSITION[WHITE][PAWN]:
            pieces.append(Pawn(self.light_team.color, square))
        self.light_team.active_pieces += pieces
        for piece in pieces:
            self.board.place_piece(piece)

    def setup_pieces(self):
        self.setup_dark_pieces()
        self.setup_light_pieces()

    def update_state(self, actions):
        ## Note that these method depends on hook methods, i.e. the on_enter_new_state method.
        ## To handle changes when entering a new state
        if actions[ACTION_QUIT]:
            pygame.quit()
            sys.exit()
        commands = []
        if self.state == GAMESTART:
            self.handle_game_start(actions, commands)
        elif self.state == STARTTURN:
            self.handle_turn_start(actions, commands)
        elif self.state == SELECTPIECE:
            self.handle_piece_selection(actions, commands)
        elif self.state == SELECTMOVE:
            self.handle_move_selection(actions, commands)
        elif self.state == SELECTPROMOTION:
            self.handle_promotion_selection(actions, commands)
        elif self.state == ENDTURN:
            self.handle_end_turn(actions, commands)
        return commands

    def change_state_to(self, new_state: int, actions, commands):
        self.on_exit_current_state(commands)
        self.state = new_state
        self.on_enter_new_state(self.state, actions, commands)

    def on_exit_current_state(self, commands):
        if self.state == GAMESTART:
            pass
        if self.state == STARTTURN:
            pass
        elif self.state == SELECTPIECE:
            pass
        elif self.state == SELECTMOVE:
            command = {COMMAND_CLEAR_HIGHLIGHTS: None}
            # self.remove_highlighted_squares() # convert to command
            commands.append(command)
        elif self.state == SELECTPROMOTION:
            command = {COMMAND_TEARDOWN_PROMO: None}
            commands.append(command)
            # self.teardown_promo_menu() # convert to command
        elif self.state == ENDTURN:
            self.set_captured_piece(None)  # game state info
            self.set_selected_square(None)  # don't know about this one
            """
            self.other_player.king.set_in_check(
                False
            )  # game state info
            """
            self.checking_pieces = {}  # game state info
            self.move_dict = {}  # game state info

    def on_enter_new_state(self, state: int, actions, commands):
        """
        A hook method. Whenever we change states, sometimes it is necessary to accomplish some task,
        This method does just that, and ensure that for each state, the body of the conditional doesn't need to be
        repeated

        Contains the actual "actions" of a given state
        """
        if state == STARTTURN:
            self.checking_pieces = self.board.get_checking_pieces(
                self.current_player, self.other_player
            )
            if self.checking_pieces:
                self.current_player.set_king_in_check(True)
            else:
                self.current_player.set_king_in_check(False)
            self.move_dict = self.board.build_move_dict(
                self.current_player, self.other_player
            )

        elif state == SELECTPIECE:
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

        elif state == SELECTMOVE:
            assert self.selected_square is not None
            # command
            selected_piece = self.board.get_square_contents(self.selected_square)
            command_highlight_potential_moves = {
                COMMAND_HIGHLIGHT_SQUARES: {
                    PAYLOAD_COLOR: GREEN,
                    PAYLOAD_SQUARES: self.move_dict[selected_piece],
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
        elif state == SELECTPROMOTION:
            assert self.selected_square is not None
            self.selected_square = actions[ACTION_SELECTED_SQUARE]
            selected_piece = self.board.get_square_contents(self.selected_square)
            assert selected_piece.is_promotable(self.selected_square)
            command_build_promotion_menu = {COMMAND_BUILD_PROMO: selected_piece.color}
            commands.append(command_build_promotion_menu)

        elif state == ENDTURN:
            if self.captured_piece is not None:
                print(
                    f"{str(self.current_player).split()[0]} captures {str(self.other_player).split()[0]}'s {self.captured_piece.kind}"
                )
                self.other_player.active_pieces.remove(self.captured_piece)
                self.other_player.captured_pieces.append(self.captured_piece)
        elif state == GAMEEND:
            if self.current_player.king.get_check_status():
                print(f"{self.other_player} Has Won, Game over")
            else:
                print(f"Stalemate, No one has won")
            self.end_game_is_running()

    def handle_game_start(self, actions, commands):
        self.change_state_to(STARTTURN, None, None)

    def handle_turn_start(self, actions, commands):
        if self.move_dict and self.move_dict_is_empty():
            self.change_state_to(GAMEEND, actions, commands)
        else:
            self.change_state_to(SELECTPIECE, actions, commands)

    def handle_piece_selection(self, actions, commands):
        """
        Piece selection state
        """
        if actions[ACTION_MOUSE_PRESSED]:  # event
            # validate event
            if self.valid_square_selected(actions[ACTION_SELECTED_SQUARE]):
                valid_square = actions[ACTION_SELECTED_SQUARE]
                if not self.board.is_empty((valid_square)):
                    selected_piece = self.board.get_square_contents((valid_square))
                    self.set_selected_square(valid_square)
                    if selected_piece and self.current_player.owns(selected_piece):
                        legal_moves = self.move_dict[selected_piece]
                        if legal_moves:
                            self.change_state_to(SELECTMOVE, actions, commands)
                        else:
                            self.reject_selection(
                                actions, commands, "Piece has no valid moves"
                            )
                    else:
                        self.reject_selection(
                            actions,
                            commands,
                            f"{self.print_current_player()} does not own the selected piece",
                        )
                else:
                    self.reject_selection(
                        actions,
                        commands,
                        "Board is empty at selected location",
                    )
            else:
                self.reject_selection(actions, commands, "No Valid Square was selected")
        else:
            self.continue_in_state()

    def handle_move_selection(self, actions, commands):
        """
        Move selection after a piece has been selected

        Note: Valid moves are generated in the 'on_enter_new_state' method
        """
        # generate associated move data
        if actions[ACTION_MOUSE_PRESSED]:
            selected_piece = self.board.get_square_contents(self.selected_square)
            legal_moves = self.move_dict[selected_piece]
            if legal_moves:
                if self.valid_square_selected(actions[ACTION_SELECTED_SQUARE]):
                    dest_row, dest_col = actions[ACTION_SELECTED_SQUARE]
                    if self.valid_move_selected((dest_row, dest_col), legal_moves):
                        self.captured_piece = self.board.move_piece(
                            selected_piece, self.selected_square, (dest_row, dest_col)
                        )
                        if selected_piece.is_promotable((dest_row, dest_col)):
                            print("You can promote your piece!")
                            self.change_state_to(SELECTPROMOTION, actions, commands)
                        else:
                            self.change_state_to(ENDTURN, actions, commands)
                    else:
                        self.reject_selection(
                            actions,
                            commands,
                            "Invalid move for selected piece",
                        )
                else:
                    self.reject_selection(actions, commands, "Invalid Square Selected")
            else:
                self.reject_selection(actions, commands, "Piece has no valid moves")
        else:
            self.continue_in_state()

    def handle_promotion_selection(self, actions, commands):
        """
        Promotion of a pawn into a new piece, must occur.
        """
        if commands:
            ...
        assert (
            self.promotion_menu is not None
        ), "Promotion Menu must exist in the SELCTPROMOTION state"
        if actions[ACTION_MOUSE_PRESSED]:
            promotion_option = self.promotion_menu.get_valid_promotion_option(
                self.mouse_pos
            )
            if promotion_option != None:
                new_type = self.promotion_menu.get_piece_type(promotion_option)
                self.board.upgrade_piece(
                    self.current_player, self.selected_piece, new_type
                )
                self.change_state_to(ENDTURN)
            else:
                print("Invalid promotion option")
                self.continue_in_state()
        else:
            self.continue_in_state()

    def handle_end_turn(self, actions, commands):
        """This method has no operation : End of Turn does not handle user events"""
        "End of turns can only be accessed from other states"
        self.update_current_player()
        self.change_state_to(STARTTURN, actions, commands)

    def reject_selection(
        self,
        actions,
        commands,
        msg: str = None,
    ):
        if msg:
            print(f"{msg}")
        self.change_state_to(SELECTPIECE, actions, commands)

    def continue_in_state(self):
        # does nothing, exists to make non-response explicitly do nothing.
        pass

    def remove_highlighted_squares(self):
        self.board.clear_highlighted_squares()

    def update_current_player(self):
        """
        Changes the current player into the other player. i.e. changes the active player from white to black
        """
        if self.current_player.color == WHITE:
            print("It is now Black's turn")
            self.current_player = self.dark_team
            self.other_player = self.light_team
        else:
            print("It is now White's turn")
            self.current_player = self.light_team
            self.other_player = self.dark_team

    ### State methods, might move

    def valid_square_selected(self, possible_square: tuple[int, int]) -> bool:
        """
        Method that checks if a possible square corresponds to a board square.

        Args:
            mouse_pos (tuple[int, int]): The current mouse_pos corresponding to the last mouse press down

        """
        return possible_square != (None, None)

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
        elif self.current_player == self.light_team:
            return "White Player"

    def move_dict_is_empty(self):
        assert self.move_dict is not None
        for value in self.move_dict.values():
            if value:
                return False
        return True
