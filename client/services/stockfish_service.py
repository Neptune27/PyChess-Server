import asyncio
import os
import platform
import threading
from collections import deque

from stockfish import Stockfish

from client.services.base_service import BaseService
from client.services.setting import Setting


class StockfishService(BaseService):
    def __init__(self, setting: Setting):
        BaseService.__init__(self)
        self.callback = None
        self.setting = setting

        self.stockfish_path = "stockfish/windows/stockfish.exe" if platform.system() == "Windows" \
            else "stockfish/linux/stockfish"
        absolute_path = os.path.abspath(__package__)
        path = absolute_path + "/../" + self.stockfish_path
        self.logger.info(path)
        self.stockfish = Stockfish(path=path, depth=20, parameters={
            "Debug Log File": "",
            "Contempt": 0,
            "Min Split Depth": 0,
            "Threads": 2,
            # More threads will make the engine stronger, but should be kept at less than the number of logical
            # processors on your computer.
            "Ponder": "false",
            "Hash": 64,
            # Default size is 16 MB. It's recommended that you increase this value, but keep it as some power of 2.
            # E.g., if you're fine using 2 GB of RAM, set Hash to 2048 (11th power of 2).
            "MultiPV": 1,
            "Skill Level": 20,
            "Move Overhead": 10,
            "Minimum Thinking Time": 20,
            "Slow Mover": 100,
            "UCI_Chess960": "false",
            "UCI_LimitStrength": "false",
            "UCI_Elo": 1350
        })

        self.deque = deque()

    def run(self):
        pass

    def set_callback(self, callback):
        self.callback = callback

    def set_fen_position(self, fen_position: str):
        self.stockfish.set_fen_position(fen_position)

    def get_fen_position(self):
        return self.stockfish.get_fen_position()

    def _get_best_move(self, callback):
        best_move = self.stockfish.get_best_move()
        callback(best_move)
        self.deque.popleft()

    def get_best_move(self, callback):
        if len(self.deque) == 0:
            self.deque.append(1)
            threading.Thread(target=self._get_best_move, args=[callback]).start()

    def make_move(self, pgn):
        self.stockfish.make_moves_from_current_position([pgn])
