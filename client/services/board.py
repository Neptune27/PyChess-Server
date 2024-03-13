import math
import threading
import time
from collections import deque
from typing import List, Tuple
from queue import Queue

import numpy as np
import pygame
from pygame import SurfaceType, Surface

from client.components.piece import Piece, Rook, Pawn, Knight, King, Bishop, Queen
from client.services.base_service import BaseService
from client.services.setting import Setting
from client.services.stockfish_service import StockfishService


class Board(BaseService):
    row_notation = ['a', 'b', 'c', 'd', 'e', 'f', 'g', 'h']
    col_notation = ['8', '7', '6', '5', '4', '3', '2', '1']

    def __init__(self, stockfish: StockfishService, setting: Setting):
        BaseService.__init__(self)
        self.stockfish = stockfish
        self.setting = setting
        self._screen: Surface | SurfaceType
        self._board: Surface | SurfaceType

        self.drawingPos = (100, 0)

        self.minDimension: int = 0
        self.rectDimension = 0

        self.coordinate = np.full((8, 8), None, dtype=Piece)

        pygame.font.init()
        self.font = pygame.font.Font('./assets/fonts/Roboto-Regular.ttf', 15)
        self.selectedPiece: Piece = None

        self._is_white_turn = True
        self.best_move = None
        self.is_ai = True
        self.ai_turn = not self.is_white_turn

        self.deque = deque()

        # self.p = Pawn(False, 0, 0)
        # self.p2 = Pawn(False, 5, 2)
        # self.p1 = Pawn(True, 1, 1)
        # self.r = Rook(True, 2, 2)
        # self.n = Knight(True, 5, 5)
        # self.k = King(False, 7, 2)
        # self.coordinate[0, 0] = self.p
        # self.coordinate[1, 1] = self.p1
        # self.coordinate[5, 2] = self.p2
        # self.coordinate[2, 2] = self.r
        # self.coordinate[5, 5] = self.n
        # self.coordinate[7, 2] = self.k
        #
        self.pgn: list[str] = []

        self.pieces = pygame.sprite.Group()
        # self.pieces.add(self.p)
        # self.pieces.add(self.p1)
        # self.pieces.add(self.p2)
        # self.pieces.add(self.r)
        # self.pieces.add(self.n)
        # self.pieces.add(self.k)

        self.setDefaultBoard()
        # self.setBoardByFEN("2b1kbnr/1P3ppp/8/4p3/8/8/RPP1PPPP/1NB1KBNR b Kk - 0 9")
        # self.setBoardByFEN("k7/p7/8/8/1P6/8/8/K7 w - - 0 1")
        # self.setBoardByFEN("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
        # self.setBoardByFEN("r3k2r/8/8/8/8/8/8/R3K2R w KQkq - 0 1")
        # self.setBoardByFEN("rnbqkb1r/pp1p1ppp/8/2p1p3/8/3N1N2/PPPPPPPP/R1BQKB1R w KQkq - 0 6    ")
        # self.stockfish.set_fen_position("rnbqkbnr/ppp1pppp/8/3p4/4P3/8/PPPP1PPP/RNBQKBNR w KQkq - 0 2")
        self.compute_legal_move()

    def empty_board(self):
        self.coordinate = np.full((8, 8), None, dtype=Piece)
        self.pieces.empty()

    def _compute_all_moves(self):
        for piece in self.pieces:
            if not isinstance(piece, Piece):
                pass

            piece.compute_possible_moves(self.coordinate)

    @property
    def screen(self) -> Surface | SurfaceType:
        return self._screen

    @screen.setter
    def screen(self, screen: Surface | SurfaceType):
        self._screen = screen
        self.minDimension = min(self.screen.get_width(), self.screen.get_height())
        self.rectDimension = math.floor(self.minDimension / 8)
        self.board = pygame.Surface((self.minDimension, self.minDimension))

    @property
    def board(self) -> Surface | SurfaceType:
        return self._board

    @board.setter
    def board(self, board: Surface | SurfaceType):
        self._board = board
        self.minDimension = min(self._board.get_width(), self._board.get_height())
        self.rectDimension = math.floor(self.minDimension / 8)

    @property
    def is_white_turn(self) -> bool:
        return self._is_white_turn

    @is_white_turn.setter
    def is_white_turn(self, turn: bool) -> None:
        self._is_white_turn = turn

    def setDrawingPos(self, startPos: tuple[0, 0]) -> None:
        pass

    def set_piece(self, piece: Piece) -> None:
        x, y = piece.x, piece.y
        self.coordinate[x][y] = piece
        self.pieces.add(piece)

    def setBoardByFEN(self, fen: str):
        self.empty_board()
        self.logger.info(f"Loading FEN Board: {fen}")
        self.stockfish.set_fen_position(fen)

        items = fen.split(" ")

        fenBoard = items[0].split("/")
        self.load_FEN_pieces(fenBoard)

        self.is_white_turn = True if items[1].lower() == 'w' else False
        self.ai_turn = not self.is_white_turn

        pass

    def load_FEN_pieces(self, fenBoard: list[str]) -> None:
        for y, item in enumerate(fenBoard):
            offset = 0
            for char in item:
                if offset > 7:
                    break

                p = char
                match p:
                    case "r":
                        self.set_piece(Rook(False, offset, y))
                    case "R":
                        self.set_piece(Rook(True, offset, y))
                    case "n":
                        self.set_piece(Knight(False, offset, y))
                    case "N":
                        self.set_piece(Knight(True, offset, y))
                    case "b":
                        self.set_piece(Bishop(False, offset, y))
                    case "B":
                        self.set_piece(Bishop(True, offset, y))
                    case "q":
                        self.set_piece(Queen(False, offset, y))
                    case "Q":
                        self.set_piece(Queen(True, offset, y))
                    case "k":
                        self.set_piece(King(False, offset, y))
                    case "K":
                        self.set_piece(King(True, offset, y))
                    case "p":
                        self.set_piece(Pawn(False, offset, y))
                    case "P":
                        self.set_piece(Pawn(True, offset, y))
                    case _:
                        if p.isnumeric():
                            offset += int(p) - 1
                        else:
                            raise ValueError(f"p is not a number: {p}")
                offset += 1

    def setBoardByNotations(self, notations: list[str]) -> None:
        self.logger.log(f"Loading Notations Board: {notations}")
        raise NotImplementedError("")

    def setDefaultBoard(self):
        self.logger.info("Loading default board...")
        self.setBoardByFEN("rnbqkbnr/pppppppp/8/8/8/8/PPPPPPPP/RNBQKBNR w KQkq - 0 1")

    def drawBoard(self, rectDimension: int):
        for i in range(64):
            column = i % 8
            row = i // 8
            # self.logger.info(f"Column: {column}, Row: {row}")
            if (column + row) % 2 == 0:
                # pygame.draw.rect(self.screen, '#b58863', [relativeDimension[0] + (column * rectDimension),
                #                                           row * rectDimension, rectDimension, rectDimension])
                pygame.draw.rect(self.board, self.setting.color1, [(column * rectDimension),
                                                                   (row * rectDimension),
                                                                   rectDimension, rectDimension])
            else:
                pygame.draw.rect(self.board, self.setting.color2, [(column * rectDimension),
                                                                   (row * rectDimension),
                                                                   rectDimension, rectDimension])

    def drawNotations(self):
        for i in range(8):
            numberImg = None
            alphabetImg = None
            if i % 2 == 0:
                numberImg = self.font.render(Board.col_notation[i], True, self.setting.color1)
                alphabetImg = self.font.render(Board.row_notation[i], True, self.setting.color1)

            else:
                numberImg = self.font.render(Board.col_notation[i], True, self.setting.color2)
                alphabetImg = self.font.render(Board.row_notation[i], True, self.setting.color2)

            # Setup draw position at the end of the column
            numberRect = numberImg.get_rect()
            numberRect.x = self.minDimension - 15
            numberRect.y = self.rectDimension * i + 10
            self.board.blit(numberImg, numberRect)

            # Setup draw position at the bottom
            alphabetRect = numberImg.get_rect()
            alphabetRect.x = 10 + self.rectDimension * i
            alphabetRect.y = self.minDimension - 20
            self.board.blit(alphabetImg, alphabetRect)

    def handle_event(self, event):
        # proceed events
        if event.type == pygame.MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            rel_x, rel_y = pos[0] - self.drawingPos[0], pos[1] - self.drawingPos[1]
            self.handle_moving((rel_x, rel_y))
            #

    def handle_queue(self):
        if len(self.deque) == 0:
            return

        item: str = self.deque.popleft()
        items = item.split("|")
        self.logger.info(items)
        match items[0]:
            case "ai":
                notation = items[1]
                self.make_turn_by_square_notation(notation)

    def draw(self):

        if self.screen is None:
            self.logger.error(f"Screen is not defined")
            raise Exception("Screen is not defined")

        self.drawBoard(self.rectDimension)

        self.handle_queue()

        self.pieces.draw(self.board)
        self.pieces.update(screen=self.board)

        self.drawNotations()

        self.screen.blit(self.board, self.drawingPos)

    def handle_moving(self, pos: tuple[int, int]):
        clicked_sprites = [s for s in self.pieces if s.rect.collidepoint(pos)]
        if len(clicked_sprites) > 0:
            if clicked_sprites[0].is_white != self.is_white_turn and self.selectedPiece is None:
                return
            self._handle_piece_selection(clicked_sprites[0], pos)
        else:
            self._handle_click_empty(pos)

    def _handle_piece_selection(self, piece: Piece, pos):

        if self.selectedPiece is not None:
            self._handle_click_empty(pos)
            return

        self.selectedPiece = piece
        # self.logger.info(f"Selected Piece: {piece} at {piece.x} and {piece.y}")
        self.selectedPiece.is_selected = True

        # if self.is_white_turn != piece.is_white:
        #     self.make_turn((piece.x, piece.y))
        #     return

    def compute_legal_move(self):
        self._compute_all_moves()
        self.filter_invalid_moves()
        # self.best_move = self.stockfish.get_best_move()
        # self.logger.info(f"Best move: {self.best_move}")

    def to_pgn(self):
        result = ""
        for i, move in enumerate(self.pgn):
            if i % 2 == 0:
                result += f"{math.floor(i / 2) + 1}. "
            result += move + " "
        return result

    def _handle_best_move(self, return_value):
        self.best_move = return_value
        self.logger.info(f"Best move: {self.best_move}")

    def next_turn(self):
        self.is_white_turn = not self.is_white_turn
        if self.is_ai and self.is_white_turn == self.ai_turn:
            self.make_turn_by_stockfish()
            self.ai_turn = not self.ai_turn

        self.stockfish.get_best_move(self._handle_best_move)
        self.compute_legal_move()

    def _handle_click_empty(self, pos: tuple[int, int]):
        if self.selectedPiece is None:
            return

        extra = ""
        clicked_sprites = []

        if isinstance(self.selectedPiece, Pawn) and self.selectedPiece.is_promoting:
            clicked_sprites = [s for s in self.selectedPiece.possibleMoves if s.rect.collidepoint(pos)
                               and isinstance(s, Piece)]

            if len(clicked_sprites) != 0:
                piece = clicked_sprites[0]
                extra = piece.shortName
            else:
                return
        else:
            clicked_sprites = [s for s in self.selectedPiece.possibleMoves if s.hidden_rect.collidepoint(pos)]

        if len(clicked_sprites) > 0:
            self.logger.info(f"Move to pos: {clicked_sprites[0].x}, {clicked_sprites[0].y}")
            self.make_turn((clicked_sprites[0].x, clicked_sprites[0].y), False, extra)
            if isinstance(self.selectedPiece, Pawn):
                if self.selectedPiece.is_promoting:
                    self.selectedPiece.is_selected = True
                    return
            self.next_turn()

        else:
            self.selectedPiece.is_selected = False
            self.selectedPiece = None
            self.logger.info(f"Click none")

    def _handle_en_passant(self, pawn: Pawn, dest: tuple[int, int]):
        if self.coordinate[dest[0], dest[1]] is not None:
            return None

        check_pos = 2 if pawn.is_white else 5
        adder = 1 if pawn.is_white else -1
        if dest[1] != check_pos:
            return

        x, y = dest[0], dest[1] + adder
        item = self.coordinate[x][y]
        if isinstance(item, Pawn) and item.is_white != pawn.is_white and item.is_first_move:
            self.coordinate[x][y] = None
            self.pieces.remove(item)
            return item
        return None

    def _handle_castle(self, from_piece: Piece, x, y, test_mode=False):
        x_distance = from_piece.x - x
        rook_pos = x + 1 if x_distance == 2 else x - 1
        if abs(x_distance) == 2:
            rook = self.coordinate[0, y] if rook_pos == 3 else self.coordinate[7, y]
            prev_selected = from_piece
            self.selectedPiece = rook
            self.make_turn((rook_pos, y), True)
            self.selectedPiece = from_piece
            # rook.compute_possible_moves(self.coordinate)

    def make_turn(self, dest: tuple[int, int], test_mode=False, extra="") -> None | Piece:
        x, y = dest[0], dest[1]

        from_piece = self.selectedPiece
        dest_item = self.coordinate[x, y]

        from_piece.is_selected = False
        self.selectedPiece = None

        (from_x, from_y) = from_piece.x, from_piece.y
        if (from_x, from_y) == (x, y):
            return None

        self.coordinate[from_x, from_y] = None

        if isinstance(from_piece, Pawn):
            if not test_mode and extra == "" and (y == 7 or y == 0):
                from_piece.is_promoting = True
                from_piece.compute_possible_moves(self.coordinate)
                self.selectedPiece = from_piece
                test_mode = True
            else:
                from_piece.is_promoting = False

            dest_item = self._handle_en_passant(from_piece, dest)
            dest_item = self.coordinate[x, y] if dest_item is None else dest_item

        if isinstance(from_piece, King):
            if not test_mode:
                from_piece.can_castle = False

            if from_piece.x == 4:
                self._handle_castle(from_piece, x, y, test_mode)

        if not test_mode:
            pgn = self.create_pgn_turn(from_piece, dest, dest_item, extra)
            square_name = self.create_square_name(from_piece, dest, extra)
            self.logger.info(f"Square name: {square_name}")

            if self.is_ai:
                self.stockfish.make_move(square_name)
            self.pgn.append(pgn)
            self.logger.info(self.to_pgn())
            # self.logger.info(f"PGN: {self.pgn}")
            # self.logger.info(f"Long PGN: {square_name}")

        if extra != "" and isinstance(from_piece, Pawn):
            match extra:
                case "Q":
                    self.set_piece(Queen(from_piece.is_white, from_piece.x, from_piece.y))
                case "R":
                    self.set_piece(Rook(from_piece.is_white, from_piece.x, from_piece.y))
                case "B":
                    self.set_piece(Bishop(from_piece.is_white, from_piece.x, from_piece.y))
                case "K":
                    self.set_piece(Knight(from_piece.is_white, from_piece.x, from_piece.y))
        else:
            from_piece.move(x, y)

        self.coordinate[x, y] = from_piece

        if dest_item is not None:
            self.pieces.remove(dest_item)

        #         Play capture sound

        #    Play move sound

        return dest_item

    def make_turn_by_stockfish(self):
        def callback(pgn):
            if "O-O" in pgn:
                self.logger.info(f"PGN: {self.pgn}")
                raise NotImplementedError("Castling not implemented yet")

            self.deque.append(f"ai|{pgn}")

        self.stockfish.get_best_move(callback)

    def make_turn_by_square_notation(self, notation):
        moves = []
        for i, char in enumerate(notation):
            if char in Board.row_notation:
                moves.append(notation[i:i + 2])

        self.logger.info(f"Moves: {moves}")

        from_pos, to_pos = moves
        from_x = Board.row_notation.index(from_pos[0])
        from_y = Board.col_notation.index(from_pos[1])

        to_x = Board.row_notation.index(to_pos[0])
        to_y = Board.col_notation.index(to_pos[1])
        item = self.coordinate[from_x][from_y]
        self.selectedPiece = item
        self.logger.info(f"PGN: {self.pgn}")
        self.logger.info(f"{from_x}, {from_y}, {to_x}, {to_y}, selectedPiece: {self.selectedPiece}")
        self.make_turn((to_x, to_y))
        self.next_turn()

    def create_pgn_turn(self, piece: Piece, dest: tuple[int, int], capture=None, extra="") -> str:
        x, y = dest[0], dest[1]
        adder = ""

        if isinstance(piece, King):
            dist = piece.x - dest[0]
            if dist == 2:
                return "O-O-O"
            elif dist == -2:
                return "O-O"

        if capture is None:
            capture = self.coordinate[x][y]

        if isinstance(piece, Rook) or isinstance(piece, Knight):
            adder += self.pgn_for_pairs(piece, dest)

        if capture is not None:
            if isinstance(piece, Pawn):
                adder += Board.row_notation[piece.x]
            adder += "x"

        pos = Board.row_notation[x] + Board.col_notation[y]

        if extra != "":
            extra = "=" + extra
            pos = pos[0]+ Board.col_notation[piece.y]

        return piece.shortName + adder + pos + extra

    def create_square_name(self, piece: Piece, dest: tuple[int, int], extra=""):
        x, y = dest[0], dest[1]
        adder = ""

        # if capture is None:
        #     capture = self.coordinate[x][y]

        long = Board.row_notation[piece.x] + Board.col_notation[piece.y]

        # if isinstance(piece, Rook) or isinstance(piece, Knight):
        #     adder += self.pgn_for_pairs(piece, dest)
        #
        # if capture is not None:
        #     if isinstance(piece, Pawn):
        #         adder += Board.row_notation[piece.x]
        #     adder += "x"
        #
        pos = Board.row_notation[x] + Board.col_notation[y]
        if extra != "":
            long = Board.row_notation[piece.prev_x] + Board.col_notation[piece.prev_y]
            pos = Board.row_notation[piece.x] + Board.col_notation[piece.y]

        return long + pos + extra.lower()

    def pgn_for_pairs(self, piece: Piece, dest: tuple[int, int]) -> str:
        x, y = dest[0], dest[1]
        another = [p for p in self.pieces if type(p) == type(piece) and p.is_white == piece.is_white and p != piece]
        if len(another) == 0:
            return ""
        other = another[0]
        if not isinstance(other, Piece):
            self.logger.error(f"{other} is not a Piece")
            raise ValueError(f"{other} is not a Piece")

        can_other_move_to_dest = [move for move in other.possibleMoves if move.x == x and move.y == y]
        self.logger.info(can_other_move_to_dest)
        return Board.row_notation[piece.x] if len(can_other_move_to_dest) > 0 else ""

    def handle_king(self, piece: Piece, x, y):
        x_distance = piece.x - x
        if abs(x_distance) != 2:
            return

        rook_pos = x - 1 if piece.x == 2 else x + 1

        rook = self.coordinate[rook_pos, piece.y]
        self.selectedPiece = rook
        if x_distance == 2:
            self.make_turn((7, y), True)
        elif x_distance == -2:
            self.make_turn((0, y), True)

        self.selectedPiece = piece

    def filter_invalid_moves(self) -> None:
        black_king, white_king = self.get_black_and_white_king()
        team_king = white_king if self.is_white_turn else black_king
        opponents = [p for p in self.pieces if p.is_white != self.is_white_turn]
        teams = [p for p in self.pieces if p.is_white == self.is_white_turn]

        illegal_move_dict = {}

        for piece in teams:
            if not isinstance(piece, Piece):
                self.logger.info(f"Invalid piece type: {piece}")
                raise ValueError(f"Invalid piece type: {piece}")

            x, y = piece.x, piece.y

            for move in piece.possibleMoves:

                self.selectedPiece = piece
                remove_piece = self.make_turn((move.x, move.y), True)

                if remove_piece is not None:
                    remove_piece.possibleMoves.empty()

                self._compute_all_moves()
                illegal_moves = []
                for opponent_piece in opponents:
                    inner_illegal_moves = [move for move in opponent_piece.possibleMoves if move.x == team_king.x
                                           and move.y == team_king.y]
                    if len(inner_illegal_moves) > 0:
                        illegal_moves.append(move)
                        break

                # Undo
                self.selectedPiece = piece

                if isinstance(piece, King):
                    self.handle_king(piece, x, y)

                self.make_turn((x, y), True)

                if remove_piece is not None:
                    self.set_piece(remove_piece)
                self._compute_all_moves()

                # Add to remove list
                if illegal_move_dict.get((x, y)) is None:
                    illegal_move_dict[(x, y)] = []

                illegal_move_dict[(x, y)] += illegal_moves

        for piece in teams:
            x, y = piece.x, piece.y
            # self.logger.info(illegal_move_dict)
            # self.logger.info(piece)
            # self.logger.info([(p.x, p.y) for p in [p for p in piece.possibleMoves]])
            possible = filter(lambda possible_move: self._compare(possible_move, illegal_move_dict[(x, y)]),
                              piece.possibleMoves)
            # [move for move in piece.possibleMoves if move not in illegal_move_dict[piece]]
            piece.possibleMoves.empty()
            [piece.possibleMoves.add(move) for move in possible]

    def _compare(self, move, illegal_moves):
        for illegal_move in illegal_moves:
            if move.x != illegal_move.x or move.y != illegal_move.y:
                continue
            return False
        return True

    def get_black_and_white_king(self):
        white_king: King
        black_king: King
        for piece in self.pieces:
            if not isinstance(piece, King):
                continue

            if piece.is_white:
                white_king = piece
            else:
                black_king = piece

        return black_king, white_king

    def drawPieces(self):
        pass

    def getCurrentFEN(self) -> str:
        pass

    def getCurrentNotations(self) -> List[str]:
        pass
