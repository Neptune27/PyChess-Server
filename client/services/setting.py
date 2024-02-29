import json

from client.services.base_service import BaseService


class Setting(BaseService):
    def __init__(self, config_file: str):
        super().__init__()
        self.config_file = config_file
        self.logger.info(self.config_file)
        self.dicts: dict = {}

        self.load()

        self.HEIGHT = 800
        self.WIDTH = 1000

        self.color1 = '#b58863'
        self.color2 = '#f0d9b5'

        self.FPS = 60

    def load(self):
        try:
            with open(self.config_file, mode="r", encoding="UTF-8") as f:
                file_value = f.read()
                self.dicts = json.loads(file_value)
                self.logger.info(self.dicts)
        except (FileNotFoundError, json.decoder.JSONDecodeError) as ex:
            self.logger.warning(ex)
