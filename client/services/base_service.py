import logging


class BaseService:
    def __init__(self) -> None:
        self.logger = logging.getLogger(
            f"{self.__class__.__name__}",
        )