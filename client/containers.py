import logging.config
from dependency_injector import containers, providers

from client.services.board import Board
from client.services.game import Game
from client.services.setting import Setting


class Container(containers.DeclarativeContainer):
    config = providers.Configuration(ini_files=["config.ini"])

    logging = providers.Resource(
        logging.config.fileConfig,
        fname="logging.ini"
    )

    # Gateways
    setting = providers.Singleton(
        Setting,
        config_file=config.setting.location
    )

    # Services
    board = providers.Factory(Board, setting=setting)

    game = providers.Factory(Game, setting=setting, board=board)
    




