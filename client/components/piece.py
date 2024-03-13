import math
from abc import abstractmethod
from typing import Any, Callable, Tuple

import pygame
from numpy import ndarray, dtype
from pygame.sprite import Sprite

from client.services.base_service import BaseService


class Piece(BaseService, Sprite):
    move_dict = {
        "P": {"movements": (1, -1), "continuous": False},
        "R": {"movements": [(1, 0), (0, 1), (-1, 0), (0, -1)], "continuous": True},
        "N": {"movements": [(-2, -1), (-2, 1), (2, -1), (2, 1), (-1, -2), (1, -2), (-1, 2), (1, 2), ],
              "continuous": False},
        "B": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1)], "continuous": True},
        "Q": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1), ],
              "continuous": True},
        "K": {"movements": [(1, 1), (-1, 1), (1, -1), (-1, -1), (1, 0), (0, 1), (-1, 0), (0, -1), ],
              "continuous": False},
    }

    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__()
        Sprite.__init__(self)
        self.is_selected = is_selected
        self._x = x
        self._y = y
        self.is_white = is_white
        self.name = "Piece"
        self.shortName = "P"

        self.possibleMoves = pygame.sprite.Group()

    @property
    def x(self) -> int:
        return self._x

    @property
    def y(self) -> int:
        return self._y

    def move(self, x, y):
        self._x = x
        self._y = y
        self._recompute()

    def get_FEN_name(self):
        return self.shortName if self.is_white \
            else self.shortName.lower()

    def _compute_center(self):
        value = 100
        pos_x = self.x * value + math.floor(value / 2)
        pos_y = self.y * value + math.floor(value / 2)

        return pos_x, pos_y

    def _recompute(self):
        self.rect.center = self._compute_center()

    @staticmethod
    def get_piece_moves_dict(piece_type: str) -> tuple[list[tuple[int, int]], bool]:
        """Return info: (dict) on ghow a particular piece moves"""
        piece_move_info: dict = Piece.move_dict[piece_type]
        movements: list[tuple[int, int]] = piece_move_info["movements"]
        continuous: bool = piece_move_info["continuous"]
        return movements, continuous

    def clone(self):
        return Piece(self.is_white, self.x, self.y)

    def _generate_non_pawn_move(self, board: ndarray) -> None:
        piece_type = self.shortName
        movements, is_continuous = self.get_piece_moves_dict(piece_type)

        for add_x, add_y in movements:  # Loop through piece movements list
            new_x, new_y = self.x + add_x, self.y + add_y  # Get new starting pos
            while not _is_out_of_bounds(new_x, new_y):

                item = board[new_x][new_y]

                # Check if the square is empty
                if item is None:
                    self.possibleMoves.add(GreenDot(new_x, new_y))

                    if not is_continuous:  # If piece type doesn't continuously move e.g Knight, Pawn, King etc..
                        break
                    new_x += add_x
                    new_y += add_y
                else:
                    if not isinstance(item, Piece):
                        self.logger.error("Item is not a Piece, what?")
                        raise ValueError("WTF")

                    # Collides with team piece
                    if item.is_white == self.is_white:
                        break
                    # Collides with enemy piece
                    self.possibleMoves.add(GreenDot(new_x, new_y))
                    break

    def compute_possible_moves(self, board: ndarray):
        self.possibleMoves.empty()
        self._generate_non_pawn_move(board)

        # pin_items = self.is_pin(board)

        # if len(pin_items) > 1:
        #     return

        # if len(pin_items) == 1:
        #     pinned_item = pin_items[0]
        #     can_remove = [p for p in self.possibleMoves if p.x == pinned_item.x and p.y == pinned_item.y]
        #     self.possibleMoves.empty()
        #
        #     if len(can_remove):
        #         self.possibleMoves.add(GreenDot(pinned_item.x, pinned_item.y))

    def update(self, *args, **kwargs):
        if self.is_selected:
            self.possibleMoves.draw(kwargs['screen'])


class GreenDot(Piece, Sprite):
    def __init__(self, x: int, y: int, is_selected=False) -> None:
        Piece.__init__(self, False, x, y, is_selected)
        Sprite.__init__(self)

        self.image = pygame.Surface((10, 10))
        self.image.fill((0, 125, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()
        self.hidden_rect = self.rect.inflate(90, 90)


class PromotionBoard(Sprite):
    def __init__(self, x: int, y: int) -> None:
        Sprite.__init__(self)
        self.y = y
        self.x = x
        self.image = pygame.Surface((100, 400))
        self.image.fill((0, 125, 0))
        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()

    def _compute_center(self):
        value = 100
        pos_x = self.x * value + math.floor(value / 2)
        pos_y = self.y * value + math.floor(value / 2)

        return pos_x, pos_y


def _is_out_of_bounds(x, y):
    if x < 0 or y < 0 or x > 7 or y > 7:
        return True
    else:
        return False


class Pawn(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_first_move=False, is_selected=False,
                 is_promoting=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.is_promoting = is_promoting
        self.name = "Pawn"
        self.shortName = ""
        self.is_first_move = is_first_move
        self.first_move_y = -1

        # For promoting
        self.prev_x = x
        self.prev_y = y

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_pawn.png", )
        else:
            self.image = pygame.image.load("assets/img/black_pawn.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()

    def move(self, x, y):
        if self.can_two_square_move():
            self.is_first_move = True
        else:
            self.is_first_move = False

        self.prev_x, self.prev_y = self.x, self.y
        Piece.move(self, x, y)

    def _compute(self, board: ndarray[Any, dtype]):
        """Generate pawn moves"""

        # -------------------------------------
        x, y = self.x, self.y
        direction = -1 if self.is_white else 1
        # -------------------------------------
        movements, _ = self.get_piece_moves_dict("P")

        # Check if its inbounds
        if _is_out_of_bounds(x, y + direction):
            return

        # One square move
        cas = board[x][y + direction]
        if board[x][y + direction] is None:  # If empty
            self.possibleMoves.add(GreenDot(x, y + direction))
            # Two square move

            if self.can_two_square_move() and board[x][y + (direction * 2)] is None:
                # If its empty and pawn hasn't moved
                # f"{col}{row}:{col}{row + (direction * 2)}:N")
                self.possibleMoves.add(GreenDot(x, y + (direction * 2)))

        # Captures
        for add_x in movements:
            new_x = x + add_x  # type: ignore
            new_y = y + direction  # type: ignore

            if _is_out_of_bounds(new_x, y + direction):
                continue

            item = board[new_x][new_y]
            if item is None:  # Not empty square
                self._add_en_passant(board, (new_x, new_y))
                continue

            if not isinstance(item, Piece):
                raise ValueError("item is not a Piece")

            if item.is_white != self.is_white:  # Collides with enemy
                self.possibleMoves.add(GreenDot(new_x, new_y))

    def _add_en_passant(self, board: ndarray, move: tuple[int, int]) -> None:
        check_pos = 2 if self.is_white else 5
        adder = 1 if self.is_white else -1
        if move[1] != check_pos:
            return

        x, y = move[0], move[1] + adder
        item = board[x][y]
        if isinstance(item, Pawn) and item.is_white != self.is_white and item.is_first_move:
            self.possibleMoves.add(GreenDot(move[0], move[1]))

    def can_two_square_move(self):
        y = 6 if self.is_white else 1
        return self.y == y

    def make_promote(self):
        x = self.x + 1 if self.x < 7 else self.x - 1
        y = 0 if self.is_white else 4
        self.possibleMoves.add(PromotionBoard(x, y))
        self.possibleMoves.add(Queen(self.is_white, x, y))
        self.possibleMoves.add(Rook(self.is_white, x, y + 1))
        self.possibleMoves.add(Bishop(self.is_white, x, y + 2))
        self.possibleMoves.add(Knight(self.is_white, x, y + 3))

    def compute_possible_moves(self, board: ndarray[Any, dtype]):
        self.possibleMoves.empty()

        if self.is_promoting:
            self.make_promote()
        else:
            self._compute(board)


class Rook(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Rook"
        self.shortName = "R"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_rook.png", )
        else:
            self.image = pygame.image.load("assets/img/black_rook.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class Knight(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Knight"
        self.shortName = "N"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_knight.png", )
        else:
            self.image = pygame.image.load("assets/img/black_knight.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class Bishop(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Bishop"
        self.shortName = "B"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_bishop.png", )
        else:
            self.image = pygame.image.load("assets/img/black_bishop.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()


class King(Piece):
    def __init__(self, is_white: bool, x: int, y: int, can_castle_king: bool = True, can_castle_queen: bool = True,
                 is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.can_castle_queen = can_castle_queen
        self.can_castle_king = can_castle_king
        self.name = "King"
        self.shortName = "K"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_king.png", )
        else:
            self.image = pygame.image.load("assets/img/black_king.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()

    def _is_range_none(self, from_x: int, to_x, y: int, board: ndarray) -> bool:
        for i in range(from_x, to_x):
            item = board[i, y]
            if item is not None:
                return False

        return True

    def compute_castle(self, board: ndarray):
        if not self.can_castle_queen and not self.can_castle_king:
            return

        x = 4
        y = 7 if self.is_white else 0

        if self.x != x or self.y != y:
            return

        left_rook = board[0, y]
        if left_rook is None:
            self.can_castle_queen = False

        if (self.can_castle_queen and left_rook and isinstance(left_rook, Rook)
                and self._is_range_none(1, 4, y, board) and left_rook.is_white == self.is_white):
            self.possibleMoves.add(GreenDot(2, y))

        right_rook = board[7, y]
        if right_rook is None:
            self.can_castle_king = False
        if (self.can_castle_king and isinstance(right_rook, Rook)
                and self._is_range_none(5, 7, y, board) and left_rook.is_white == self.is_white):
            self.possibleMoves.add(GreenDot(6, y))

    def compute_possible_moves(self, board: ndarray):
        Piece.compute_possible_moves(self, board)
        self.compute_castle(board)


class Queen(Piece):
    def __init__(self, is_white: bool, x: int, y: int, is_selected=False) -> None:
        super().__init__(is_white, x, y, is_selected)
        self.name = "Queen"
        self.shortName = "Q"

        if self.is_white:
            self.image = pygame.image.load("assets/img/white_queen.png", )
        else:
            self.image = pygame.image.load("assets/img/black_queen.png")

        # TODO: Temp
        self.image = pygame.transform.smoothscale(self.image, (100, 100))

        self.rect = self.image.get_rect()
        self.rect.center = self._compute_center()
